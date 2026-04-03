import flask
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import logging
import tempfile
import time
import shutil


import TraificNPR.application.config as config
from TraificNPR.application.model_loader import load_models

from TraificNPR.application.image_processing import process_file

from TraificNPR.application.utils import to_base64


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s')

try:
    os.makedirs(config.UPLOAD_FOLDER_PATH, exist_ok=True)
    logging.info(f"Upload folder ready: {config.UPLOAD_FOLDER_PATH}")
except OSError as e:
    logging.error(f"Could not create upload folder '{config.UPLOAD_FOLDER_PATH}': {e}", exc_info=True)


logging.info("----- Initializing ANPR Application - Loading Models -----")
try:
    plate_detection_model, char_seg_model, char_recog_model, device, ocr_font_path = load_models()
    models_loaded = all([plate_detection_model, char_seg_model, char_recog_model])
    if not models_loaded:
        logging.error("One or more models failed to load. Application might not function correctly.")
except Exception as load_err:
     logging.error(f"A critical error occurred during model loading: {load_err}", exc_info=True)
     plate_detection_model, char_seg_model, char_recog_model, device, ocr_font_path = None, None, None, "cpu", None
     models_loaded = False

logging.info("Model Load")


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER_PATH
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.secret_key = config.FLASK_SECRET_KEY
logging.info(f"OCR API token protection: {'ENABLED' if (config.OCR_API_TOKEN or '').strip() else 'DISABLED'}")

app.jinja_env.filters['to_base64'] = to_base64
app.jinja_env.globals.update(zip=zip)


def get_request_api_token(req):
    header_token = (req.headers.get('X-API-Token') or '').strip()
    if header_token:
        return header_token

    auth_header = (req.headers.get('Authorization') or '').strip()
    if auth_header.lower().startswith('bearer '):
        return auth_header[7:].strip()

    return ''


def is_api_token_valid(req):
    expected_token = (config.OCR_API_TOKEN or '').strip()
    if not expected_token:
        return True
    return get_request_api_token(req) == expected_token


def api_error(message, status_code, code):
    response = jsonify({
        'error': {
            'code': code,
            'message': message,
        }
    })
    response.status_code = status_code
    return response


@app.route('/', methods=['GET', 'POST'])
def upload_file_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(request.url)

        if file:
            original_filename = file.filename
            _, file_extension = os.path.splitext(original_filename)
            file_extension = file_extension.lower()

            if file_extension not in config.ALLOWED_EXTENSIONS:
                allowed_str = ", ".join(config.ALLOWED_EXTENSIONS)
                flash(f'Unsupported file type: "{file_extension}". Allowed types: {allowed_str}', 'error')
                logging.warning(f"Upload rejected: Unsupported file type '{file_extension}' from file '{original_filename}'")
                return redirect(request.url)

            temp_path = None
            fd = None
            try:
                fd, temp_path = tempfile.mkstemp(suffix=file_extension, dir=app.config['UPLOAD_FOLDER'], text=False)
                file.save(temp_path)
                logging.info(f"File '{original_filename}' saved temporarily to '{temp_path}'")

                if fd is not None:
                    os.close(fd)
                    fd = None

                if not models_loaded:
                     flash('Models are not loaded correctly. Cannot process file.', 'error')
                     logging.error("Processing aborted: Models not loaded.")
                     return redirect(url_for('upload_file_route'))

                start_process_time = time.time()
                results = process_file(
                    temp_path,
                    plate_detection_model,
                    char_seg_model,
                    char_recog_model,
                    device,
                    ocr_font_path
                 )
                end_process_time = time.time()
                logging.info(f"Processing '{original_filename}' completed in {end_process_time - start_process_time:.3f} seconds. Found {len(results)} plates.")

                return render_template('results.html', results=results, filename=original_filename)

            except Exception as e:
                logging.error(f"Error processing uploaded file '{original_filename}': {e}", exc_info=True)
                flash(f'An error occurred during processing: {str(e)}', 'error')
                return redirect(url_for('upload_file_route'))

            finally:
                if fd is not None:
                    try:
                        os.close(fd)
                    except OSError as close_err:
                         logging.warning(f"Warning: Could not close temp file descriptor {fd}: {close_err}")
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                        logging.info(f"Removed temporary file: {temp_path}")
                    except Exception as rm_err:
                        logging.warning(f"Could not remove temporary file '{temp_path}': {rm_err}")

    return render_template('upload.html')


@app.route('/api/v1/ocr', methods=['POST'])
def api_ocr_route():
    if not is_api_token_valid(request):
        logging.warning("Unauthorized OCR API request received.")
        return api_error('Unauthorized: invalid or missing API token.', 401, 'unauthorized')

    if not models_loaded:
        logging.error("OCR API request rejected: models are not loaded.")
        return api_error('OCR models are unavailable.', 503, 'models_unavailable')

    if 'file' not in request.files:
        return api_error('Missing required form field: file.', 400, 'bad_request')

    file = request.files['file']
    if file.filename == '':
        return api_error('Uploaded file has an empty filename.', 400, 'bad_request')

    original_filename = file.filename
    _, file_extension = os.path.splitext(original_filename)
    file_extension = file_extension.lower()
    if file_extension not in config.ALLOWED_EXTENSIONS:
        return api_error(
            f'Unsupported file type: {file_extension}.',
            400,
            'bad_request'
        )

    temp_path = None
    fd = None
    try:
        fd, temp_path = tempfile.mkstemp(suffix=file_extension, dir=app.config['UPLOAD_FOLDER'], text=False)
        file.save(temp_path)

        if fd is not None:
            os.close(fd)
            fd = None

        start_process_time = time.time()
        results = process_file(
            temp_path,
            plate_detection_model,
            char_seg_model,
            char_recog_model,
            device,
            ocr_font_path
        )
        processing_time = time.time() - start_process_time

        return jsonify({
            'filename': original_filename,
            'processing_time_seconds': processing_time,
            'plate_count': len(results),
            'plates': results,
        })
    except Exception as api_err:
        logging.error(f"Error processing OCR API request for '{original_filename}': {api_err}", exc_info=True)
        return api_error('Internal server error during OCR processing.', 500, 'internal_error')
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError as close_err:
                logging.warning(f"Warning: Could not close temp file descriptor {fd}: {close_err}")
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as rm_err:
                logging.warning(f"Could not remove temporary file '{temp_path}': {rm_err}")

if __name__ == '__main__':
    logging.info("----- Starting ANPR Flask Application Web Server -----")
    logging.info(f"Flask Secret Key: {'Set' if config.FLASK_SECRET_KEY != 'your_very_secret_key_change_me' else '!!! Using Default !!!'}")
    logging.info(f"Max Upload Size: {config.MAX_CONTENT_LENGTH / (1024*1024):.1f} MB")
    logging.info(f"Allowed Extensions: {', '.join(config.ALLOWED_EXTENSIONS)}")
    logging.info(f"Models Loaded: {models_loaded}")
    logging.info(f"OCR API token protection: {'ENABLED' if (config.OCR_API_TOKEN or '').strip() else 'DISABLED'}")
    if not models_loaded:
        logging.warning("Running with one or more models missing!")

    app.run(host='0.0.0.0', port=5001, debug=True)
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import whisper
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'wav', 'm4a', 'flac'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        model = whisper.load_model("base")
        result = model.transcribe(filepath)

        os.remove(filepath)
        return jsonify({'transcription': result['text']})

    return jsonify({'error': 'File type not allowed'}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5500)


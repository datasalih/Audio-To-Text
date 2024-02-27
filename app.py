from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from google.cloud import speech
import os

project_id = os.environ.get('audio-to-text-415611')



app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'wav', 'm4a', 'flac'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

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

        try:
            # Instantiates a client
            client = speech.SpeechClient(project=project_id)

            # Loads the audio into memory
            with open(filepath, "rb") as audio_file:
                content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)

            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )

            # Detects speech in the audio file
            response = client.recognize(config=config, audio=audio)

            transcript = " ".join([result.alternatives[0].transcript for result in response.results])

            return jsonify({'transcription': transcript})
        finally:
            os.remove(filepath)  
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == "__main__":
    app.run()

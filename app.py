from flask import Flask, request, render_template, jsonify
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configure this environment variable with your Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "audio-to-text-415611-5f6954a6802b.json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)

        # Transcribe the audio file
        transcription = transcribe_audio(file_path)
        os.remove(file_path)  # Clean up the uploaded file
        return jsonify({'transcription': transcription})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'mp3', 'wav', 'flac'}

def transcribe_audio(file_path):
    client = speech.SpeechClient()
    with open(file_path, 'rb') as audio_file:
        content = audio_file.read()
    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US')

    response = client.recognize(config=config, audio=audio)

    transcription = ''
    for result in response.results:
        transcription += result.alternatives[0].transcript + ' '

    return transcription.strip()

if __name__ == '__main__':
    app.run(debug=True)

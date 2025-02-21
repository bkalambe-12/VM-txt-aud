from flask import Flask, request, render_template, send_file
import os
import re
from PyPDF2 import PdfReader
import pyttsx3

app = Flask(__name__)

# removing unwanted symbolds, replacing mul .'s with single .
def preprocess_text(text):
    
    text = re.sub(r'[^\w\s.,!?]', '', text)  
    text = re.sub(r'\s+', ' ', text) 
    text = re.sub(r'\.{2,}', '.', text)  
    text = text.strip()  
    return text

def extract_text_from_pdf(pdf_path):
    text = ''
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return preprocess_text(text)  
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

# t-> a pyttsx3 (offline TTS)
def text_to_audio(text):
    try:
        engine = pyttsx3.init()

        
        engine.setProperty('rate', 150) # WPM speed
        engine.setProperty('volume', 1.0)  
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)  # Used a female voice ; can be changed 

        
        audio_file = 'output.mp3'
        engine.save_to_file(text, audio_file)
        engine.runAndWait()
        return audio_file
    except Exception as e:
        print(f"Error converting text to audio: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    
    text = extract_text_from_pdf(file_path)
    if not text:
        return "Failed to extract text from the PDF", 400

# t-> a
    audio_file = text_to_audio(text)
    if not audio_file:
        return "Failed to convert text to audio", 400

    return send_file(audio_file, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

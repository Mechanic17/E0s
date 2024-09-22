import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# URL сервиса модели
MODEL_SERVICE_URL = 'http://model_service:5001'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    text = data.get('message')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Отправляем запрос в сервис модели
    response = requests.post(f'{MODEL_SERVICE_URL}/generate', json={'text': text})
    if response.status_code != 200:
        return jsonify({'error': 'Error from model service'}), 500

    result = response.json()
    generated_text = result.get('generated_text')
    audio_hex = result.get('audio')

    # Преобразуем hex обратно в байты
    audio_bytes = bytes.fromhex(audio_hex)

    # Сохраняем аудио файл
    audio_file = 'static/output.wav'
    with open(audio_file, 'wb') as f:
        f.write(audio_bytes)

    return jsonify({
        'reply': generated_text,
        'audio_file': f'/{audio_file}'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

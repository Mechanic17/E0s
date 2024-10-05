# app/app.py

import os
from flask import Flask, request, jsonify, render_template
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import soundfile as sf
import uuid  # Добавлено для генерации уникальных имён файлов

app = Flask(__name__)

# Путь к директории с моделями
MODELS_DIR = 'models'

# Инициализация GPT-2 модели и токенизатора
gpt2_model_path = os.path.join(MODELS_DIR, 'gpt2')
tokenizer = AutoTokenizer.from_pretrained(gpt2_model_path)
model = AutoModelForCausalLM.from_pretrained(gpt2_model_path)

# Инициализация моделей SpeechT5
speecht5_processor_path = os.path.join(MODELS_DIR, 'speecht5_tts_processor')
speecht5_model_path = os.path.join(MODELS_DIR, 'speecht5_tts_model')
speecht5_vocoder_path = os.path.join(MODELS_DIR, 'speecht5_hifigan_vocoder')

processor = SpeechT5Processor.from_pretrained(speecht5_processor_path)
speech_model = SpeechT5ForTextToSpeech.from_pretrained(speecht5_model_path)
vocoder = SpeechT5HifiGan.from_pretrained(speecht5_vocoder_path)

# Загрузка эмбеддингов голоса (здесь используется заранее сохранённый эмбеддинг)
speaker_embeddings_path = os.path.join(MODELS_DIR, 'speaker_embeddings.pt')
if os.path.exists(speaker_embeddings_path):
    speaker_embeddings = torch.load(speaker_embeddings_path)
else:
    # Если файл с эмбеддингами не найден, используем нулевой тензор
    speaker_embeddings = torch.zeros((1, 768))

@app.route('/')
def index():
    # Отображение главной страницы
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    text = data.get('message')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Генерация ответа с помощью GPT-2
        input_ids = tokenizer.encode(text, return_tensors='pt')
        output_ids = model.generate(
            input_ids,
            max_length=100,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            early_stopping=True
        )
        generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        # Генерация аудио с помощью SpeechT5
        inputs = processor(text=generated_text, return_tensors="pt")
        speech = speech_model.generate_speech(
            inputs["input_ids"],
            speaker_embeddings,
            vocoder=vocoder
        )

        # Генерация уникального имени файла для аудио
        unique_id = str(uuid.uuid4())
        audio_file = f'static/output_{unique_id}.wav'

        # Сохраняем аудио файл
        sf.write(audio_file, speech.numpy(), samplerate=16000)

        return jsonify({
            'reply': generated_text,
            'audio_file': f'/{audio_file}'
        })

    except Exception as e:
        # Обработка ошибок и возврат сообщения об ошибке
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Запуск приложения Flask на порту 8000
    app.run(host='0.0.0.0', port=8000)

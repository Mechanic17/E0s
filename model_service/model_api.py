import os
import torch
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan

app = Flask(__name__)

# Загружаем модели
model_name = "models/gpt2"
llama_tokenizer = AutoTokenizer.from_pretrained(model_name)
llama_model = AutoModelForCausalLM.from_pretrained(model_name)

processor = SpeechT5Processor.from_pretrained("models/speecht5_tts_processor")
speech_model = SpeechT5ForTextToSpeech.from_pretrained("models/speecht5_tts_model")
vocoder = SpeechT5HifiGan.from_pretrained("models/speecht5_hifigan_vocoder")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Генерация текста с помощью GPT-2
    inputs = llama_tokenizer.encode(text, return_tensors='pt')
    outputs = llama_model.generate(inputs, max_length=50)
    generated_text = llama_tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Генерация речи с помощью SpeechT5
    inputs = processor(generated_text, return_tensors="pt")
    speaker_embeddings = torch.zeros(1, 512)
    with torch.no_grad():
        speech = speech_model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
    
    # Сохраняем аудио в виде байтового массива
    audio_bytes = speech.numpy().tobytes()
    
    response = {
        'generated_text': generated_text,
        'audio': audio_bytes.hex()  # Преобразуем в hex для передачи
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

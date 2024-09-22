import os
from transformers import AutoModelForCausalLM, AutoTokenizer, SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from dotenv import load_dotenv

def download_models():
    # Загрузка переменных окружения из файла .env
    load_dotenv()
    HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
    
    # Проверяем, установлен ли токен
    if not HUGGINGFACE_TOKEN:
        raise ValueError("Необходимо установить переменную окружения HUGGINGFACE_TOKEN")

    # Модель GPT-2
    model_name = "gpt2"
    llama_model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=HUGGINGFACE_TOKEN)
    llama_tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=HUGGINGFACE_TOKEN)
    llama_model.save_pretrained('models/gpt2')
    llama_tokenizer.save_pretrained('models/gpt2')
    print("Модель GPT-2 успешно загружена.")
    
    # Модели SpeechT5
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts", use_auth_token=HUGGINGFACE_TOKEN)
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts", use_auth_token=HUGGINGFACE_TOKEN)
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan", use_auth_token=HUGGINGFACE_TOKEN)
    
    processor.save_pretrained("models/speecht5_tts_processor")
    model.save_pretrained("models/speecht5_tts_model")
    vocoder.save_pretrained("models/speecht5_hifigan_vocoder")
    print("Модели SpeechT5 и компоненты успешно загружены.")

if __name__ == "__main__":
    os.makedirs('models', exist_ok=True)
    download_models()

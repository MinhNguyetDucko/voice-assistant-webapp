import requests

def ask_llm(message):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "phi3",
        "prompt": message,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['response'].strip()
    except requests.RequestException:
        return "Xin lỗi, tôi không thể trả lời ngay bây giờ."

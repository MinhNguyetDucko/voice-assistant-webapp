import speech_recognition as sr

def listen(update_status=None):
    r = sr.Recognizer()
    with sr.Microphone() as mic:
        if update_status: update_status("Đang lắng nghe...")
        r.adjust_for_ambient_noise(mic, duration=1)
        try:
            audio = r.listen(mic, timeout=3, phrase_time_limit=5)
            text = r.recognize_google(audio, language='en-EN')
            return text
        except:
            return None

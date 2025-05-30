from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
# Chỉ cần chạy con này houy được rồi
import tkinter as tk
from tkinter import Canvas
from tkinter import font
import threading
import speech_recognition as sr
from gtts import gTTS
import requests
import playsound
import os

# ========= TTS ==========
def speak(text):
    tts = gTTS(text=text, lang='en')  # đổi sang tiếng Việt nếu cần
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

# ---------LLM ==========

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

# ========= STT ---------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as mic:
        update_status("🎤 Đang lắng nghe...")
        r.adjust_for_ambient_noise(mic, duration=1)
        try:
            audio = r.listen(mic, timeout=3, phrase_time_limit=5)
            text = r.recognize_google(audio, language='en-EN')
            return text
        except:
            return None

# ========= utils ---------
def update_status(text):
    status_label.config(text=text)

def add_message(text, is_user=False):
    bubble = tk.Frame(chat_frame, bg="#F1F0F0" if is_user else "#F1F0F0", bd=0, padx=10, pady=8)
    msg = tk.Label(bubble, text=text, wraplength=300, justify="left", font=("Segoe UI", 11),
                   bg="#F1F0F0" if is_user else "#F1F0F0", fg="black")
    msg.pack()
    bubble.pack(anchor="e" if is_user else "w", pady=5, padx=10, fill="x", expand=True)
    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1)

def handle_interaction():
    update_status("Đang xử lý...")
    user_input = listen()
    if not user_input:
        update_status("Không nhận được âm thanh.")
        return

    add_message(user_input, is_user=True)
    if user_input.lower() in ["thoát", "tạm biệt", "bye", "dừng lại"]:
        speak("Tạm biệt, hẹn gặp lại!")
        root.quit()
    else:
        reply = ask_llm(user_input)
        add_message(reply, is_user=False)
        speak(reply)
        update_status("✅ Xong")

def start_listening():
    threading.Thread(target=handle_interaction).start()

# ========= Giao diện ==========
root = tk.Tk()
root.title("Trợ lý ảo")
root.geometry("430x650")
root.resizable(False, False)

# Gradient bằng canvas nền
gradient_bg = tk.Canvas(root, width=430, height=650)
gradient_bg.place(x=0, y=0)

# Tô màu gradient thủ công
for i in range(0, 650):
    r = 224 + int((255 - 224) * (i / 650))  # trắng dần
    g = 242 + int((255 - 242) * (i / 650))
    b = 255
    color = f'#{r:02x}{g:02x}{b:02x}'
    gradient_bg.create_line(0, i, 430, i, fill=color)

# Scrollable chat zone
chat_canvas = tk.Canvas(root, bg="white", highlightthickness=0, width=410, height=480)
scrollbar = tk.Scrollbar(root, orient="vertical", command=chat_canvas.yview)
chat_frame = tk.Frame(chat_canvas, bg="white")

chat_frame.bind(
    "<Configure>",
    lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
)

chat_canvas.create_window((0, 0), window=chat_frame, anchor="nw")
chat_canvas.configure(yscrollcommand=scrollbar.set)

chat_canvas.place(x=10, y=20)
scrollbar.place(x=410, y=20, height=480)

# Thanh trạng thái
status_label = tk.Label(root, text="🎙️ Nhấn nút để nói...", font=("Segoe UI", 11), fg="#333", bg="#ffffff")
status_label.place(x=10, y=510)

# Nút nói hình tròn ở giữa dưới
def round_button(canvas, x, y, r, command=None):
    # Đổ bóng
    shadow = canvas.create_oval(x - r + 3, y - r + 3, x + r + 3, y + r + 3, fill="#0097A7", outline="")

    # Nút chính với màu xanh đẹp
    button = canvas.create_oval(x - r, y - r, x + r, y + r, fill="#00BCD4", outline="")

    # Icon mic
    mic_icon = canvas.create_text(x, y, text="🎤", font=("Segoe UI", 22, "bold"), fill="white")

    def on_click(event):
        if command:
            command()

    # Hover effect
    def on_enter(event):
        canvas.itemconfig(button, fill="#26C6DA")
    def on_leave(event):
        canvas.itemconfig(button, fill="#00BCD4")

    # Gắn sự kiện chuột
    for item in [button, mic_icon]:
        canvas.tag_bind(item, "<Button-1>", on_click)
        canvas.tag_bind(item, "<Enter>", on_enter)
        canvas.tag_bind(item, "<Leave>", on_leave)

button_canvas = Canvas(root, width=100, height=100, bg="#ffffff", highlightthickness=0)
button_canvas.place(x=165, y=540)  # Chính giữa
round_button(button_canvas, 50, 50, 35, command=start_listening)

root.mainloop()

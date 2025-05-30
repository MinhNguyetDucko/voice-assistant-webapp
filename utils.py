import tkinter as tk
import threading
from stt import listen
from tts import speak
from llm import ask_llm
import tkinter as tk

def update_status(label, text):
    label.config(text=text)

def add_message(chat_frame, canvas, text, is_user=False):
    bubble = tk.Frame(chat_frame, bg="#000000" if is_user else "#F1F0F0", bd=0, padx=10, pady=8)
    msg = tk.Label(bubble, text=text, wraplength=300, justify="left", font=("Segoe UI", 11),
                   bg="#DCF8C6" if is_user else "#F1F0F0", fg="black")
    msg.pack()
    bubble.pack(anchor="e" if is_user else "w", pady=5, padx=10, fill="x", expand=True)
    canvas.update_idletasks()
    canvas.yview_moveto(1)
def handle_interaction(root):
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

def start_listening(root):
    threading.Thread(target=handle_interaction, args=(root,)).start()
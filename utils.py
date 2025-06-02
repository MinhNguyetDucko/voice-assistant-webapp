import tkinter as tk
from tkinter import Canvas
import threading
import playsound
import os
from stt import listen
from tts import speak
from llm import ask_llm


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
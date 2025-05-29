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

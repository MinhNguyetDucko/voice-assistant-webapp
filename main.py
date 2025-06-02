import tkinter as tk
from tkinter import Canvas, messagebox
import threading
import time
from datetime import datetime
# Import các module
from tts import speak
from stt import listen
from improved_llm_handler import create_voice_assistant
import os

class VoiceAssistantGUI:
    def __init__(self):
        # Khởi tạo LLM Assistant với memory
        self.assistant = create_voice_assistant()
        self.session_id = self.assistant.start_new_session("main_user")
        
        # Trạng thái
        self.is_listening = False
        self.chat_messages = []
        
        # Khởi tạo GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Thiết lập giao diện người dùng"""
        self.root = tk.Tk()
        self.root.title("Trợ lý ảo thông minh")
        self.root.geometry("430x650")
        self.root.resizable(False, False)
        
        # Gradient background
        self.create_gradient_background()
        
        # Chat area
        self.setup_chat_area()
        
        # Status bar
        self.setup_status_bar()
        
        # Voice button
        self.setup_voice_button()
        
        # Welcome message
        self.add_message("AI", "Xin chào! Tôi là trợ lý ảo của bạn. Hãy nhấn nút mic để nói nhé! 🎤")
        
    def create_gradient_background(self):
        """Tạo nền gradient"""
        self.gradient_bg = tk.Canvas(self.root, width=430, height=650)
        self.gradient_bg.place(x=0, y=0)
        
        # Tạo gradient từ xanh nhạt đến trắng
        for i in range(0, 650):
            r = 224 + int((255 - 224) * (i / 650))
            g = 242 + int((255 - 242) * (i / 650))  
            b = 255
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.gradient_bg.create_line(0, i, 430, i, fill=color)
    
    def setup_chat_area(self):
        """Thiết lập khu vực chat"""
        # Scrollable chat zone
        self.chat_canvas = tk.Canvas(self.root, bg="white", highlightthickness=0, width=410, height=480)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.chat_canvas.yview)
        self.chat_frame = tk.Frame(self.chat_canvas, bg="white")
        
        self.chat_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        
        self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.chat_canvas.place(x=10, y=20)
        self.scrollbar.place(x=420, y=20, height=480)
    
    def setup_status_bar(self):
        """Thiết lập thanh trạng thái"""
        self.status_label = tk.Label(
            self.root, 
            text="🎙️ Nhấn nút để nói...", 
            font=("Segoe UI", 11), 
            fg="#333", 
            bg="#ffffff"
        )
        self.status_label.place(x=10, y=510)
    
    def setup_voice_button(self):
        """Thiết lập nút voice"""
        self.button_canvas = Canvas(self.root, width=100, height=100, bg="#ffffff", highlightthickness=0)
        self.button_canvas.place(x=165, y=540)
        
        self.create_round_button(self.button_canvas, 50, 50, 35, command=self.start_listening)
    
    def create_round_button(self, canvas, x, y, r, command=None):
        """Tạo nút tròn với hiệu ứng"""
        # Đổ bóng
        shadow = canvas.create_oval(x - r + 3, y - r + 3, x + r + 3, y + r + 3, fill="#0097A7", outline="")
        
        # Nút chính
        button = canvas.create_oval(x - r, y - r, x + r, y + r, fill="#00BCD4", outline="")
        
        # Icon mic
        self.mic_icon = canvas.create_text(x, y, text="🎤", font=("Segoe UI", 22, "bold"), fill="white")
        
        def on_click(event):
            if command:
                command()
        
        # Hover effects
        def on_enter(event):
            canvas.itemconfig(button, fill="#26C6DA")
        
        def on_leave(event):
            canvas.itemconfig(button, fill="#00BCD4")
        
        # Bind events
        for item in [button, self.mic_icon]:
            canvas.tag_bind(item, "<Button-1>", on_click)
            canvas.tag_bind(item, "<Enter>", on_enter)
            canvas.tag_bind(item, "<Leave>", on_leave)
        
        self.button_item = button
    
    def update_status(self, message):
        """Cập nhật trạng thái"""
        self.status_label.config(text=message)
        self.root.update()
    
    def add_message(self, sender, message):
        """Thêm tin nhắn vào chat"""
        timestamp = datetime.now().strftime("%H:%M")
        
        # Frame cho message
        msg_frame = tk.Frame(self.chat_frame, bg="white", pady=5)
        msg_frame.pack(fill="x", padx=10)
        
        # Style cho user và AI khác nhau
        if sender == "Bạn":
            # Message của user - căn phải, màu xanh
            bubble_color = "#E3F2FD"
            text_color = "#1976D2"
            anchor = "e"
            side = "right"
        else:
            # Message của AI - căn trái, màu xám
            bubble_color = "#F5F5F5"
            text_color = "#424242"
            anchor = "w"
            side = "left"
        
        # Bubble message
        bubble_frame = tk.Frame(msg_frame, bg=bubble_color, relief="solid", bd=1)
        bubble_frame.pack(anchor=anchor, padx=(0 if side=="right" else 0, 0 if side=="left" else 50))
        
        # Sender label
        sender_label = tk.Label(
            bubble_frame, 
            text=f"{sender} • {timestamp}", 
            font=("Segoe UI", 8), 
            fg="#666",
            bg=bubble_color
        )
        sender_label.pack(anchor="w" if side=="left" else "e", padx=10, pady=(5,0))
        
        # Message content
        msg_label = tk.Label(
            bubble_frame, 
            text=message, 
            font=("Segoe UI", 10), 
            fg=text_color,
            bg=bubble_color,
            wraplength=300,
            justify="left"
        )
        msg_label.pack(anchor="w", padx=10, pady=(0,5))
        
        # Auto scroll to bottom
        self.root.update()
        self.chat_canvas.yview_moveto(1)
    
    def start_listening(self):
        """Bắt đầu lắng nghe giọng nói"""
        if self.is_listening:
            return
        
        self.is_listening = True
        # Đổi icon thành đang ghi âm
        self.button_canvas.itemconfig(self.mic_icon, text="🔴")
        self.button_canvas.itemconfig(self.button_item, fill="#F44336")
        
        # Chạy trong thread riêng để không block UI
        threading.Thread(target=self.handle_voice_interaction, daemon=True).start()
    
    def handle_voice_interaction(self):
        """Xử lý tương tác giọng nói"""
        try:
            # Lắng nghe
            self.update_status("🎧 Đang lắng nghe... Hãy nói điều gì đó!")
            
            user_input = listen(self.update_status)
            
            if user_input:
                # Hiển thị input của user
                self.add_message("Bạn", user_input)
                
                # Xử lý với LLM
                self.update_status("🤖 Đang suy nghĩ...")
                
                try:
                    ai_response = self.assistant.ask_llm(user_input)
                    
                    # Hiển thị response
                    self.add_message("AI", ai_response)
                    
                    # Đọc response
                    self.update_status("🔊 Đang trả lời...")
                    speak(ai_response)
                    
                except Exception as e:
                    error_msg = "Xin lỗi, tôi gặp sự cố khi xử lý câu hỏi."
                    self.add_message("AI", error_msg)
                    speak(error_msg)
                    print(f"LLM Error: {e}")
            
            else:
                self.update_status("Không nghe được. Thử lại nhé!")
                
        except Exception as e:
            self.update_status("Lỗi microphone. Kiểm tra thiết bị!")
            print(f"Voice Error: {e}")
        
        finally:
            # Reset button state
            self.is_listening = False
            self.button_canvas.itemconfig(self.mic_icon, text="🎤")
            self.button_canvas.itemconfig(self.button_item, fill="#00BCD4")
            self.update_status("🎙️ Nhấn nút để nói...")
    
    def on_closing(self):
        """Xử lý khi đóng app"""
        try:
            self.assistant.close()
        except:
            pass
        self.root.destroy()
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Hàm main chính"""
    try:
        # Kiểm tra dependencies
        required_files = ['tts.py', 'stt.py', 'improved_llm_handler.py', 'conversation_memory.py']
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ Thiếu file: {file}")
                return
        
        print("Khởi động Voice Assistant...")
        
        # Tạo và chạy ứng dụng
        print("Đang khởi động GUI...")
        app = VoiceAssistantGUI()
        app.run()
        
    except Exception as e:
        print(f"Lỗi khởi động: {e}")
        messagebox.showerror("Lỗi", f"Không thể khởi động ứng dụng:\n{e}")

if __name__ == "__main__":
    main()
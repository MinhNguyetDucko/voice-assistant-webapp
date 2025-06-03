
from langchain_ollama import OllamaLLM
from conversation_memory import ConversationMemory
from datetime import datetime
import re

class ImprovedLLMHandler:
    def __init__(self, model_name: str = "llama3:8b", mongo_uri: str = "mongodb://localhost:27017/"):
        """
        Khởi tạo LLM handler với memory
        """
        self.model = OllamaLLM(model=model_name)
        self.memory = ConversationMemory(mongo_uri)
        self.current_session = None
        
        # System prompt được tối ưu cho câu trả lời ngắn gọn
        self.system_prompt = """Bạn là trợ lý AI người Việt Nam thông minh và thân thiện.

QUAN TRỌNG - LUẬT TRỰC TIẾP:
1. LUÔN trả lời bằng tiếng Việt
2. Trả lời NGẮN GỌN, tối đa 1-2 câu
3. Đi thẳng vào vấn đề, không lan man
4. Nếu câu hỏi phức tạp, hỏi lại để làm rõ
5. Giữ giọng điệu tự nhiên, thân thiện

Ví dụ tốt:
- "Hôm nay trời đẹp quá!" → "Vâng, thời tiết hôm nay thật tuyệt!"
- "Mấy giờ rồi?" → "Xin lỗi, tôi không thể xem đồng hồ được."

Tránh câu trả lời dài dòng hay giải thích chi tiết trừ khi được yêu cầu."""

    def start_new_session(self, user_id: str = "default_user") -> str:
        """
        Bắt đầu session mới
        """
        self.current_session = self.memory.create_session(user_id)
        return self.current_session
    
    def set_session(self, session_id: str):
        """
        Thiết lập session hiện tại
        """
        self.current_session = session_id
    
    def ask_llm(self, message: str) -> str:
        """
        Hỏi LLM với ngữ cảnh và constraints
        """
        if not self.current_session:
            self.start_new_session()
        
        try:
            # Lưu câu hỏi của user
            self.memory.add_message(self.current_session, "user", message)
            
            # Lấy ngữ cảnh gần đây
            context = self.memory.get_context_string(self.current_session, limit=4)
            
            # Tạo prompt với ngữ cảnh
            if context:
                full_prompt = f"""{self.system_prompt}

                Ngữ cảnh cuộc trò chuyện gần đây: {context}

                Câu hỏi mới: {message}

                Trả lời (nhớ: NGẮN GỌN, 1-2 câu):"""
            else:
                full_prompt = f"""{self.system_prompt}

                Câu hỏi: {message}

                Trả lời (nhớ: NGẮN GỌN, 1-2 câu):"""
            
            # Gọi model
            response = self.model.invoke(full_prompt)
            
            # Làm sạch response và giới hạn độ dài
            cleaned_response = self._clean_response(response)
            
            # Lưu câu trả lời
            self.memory.add_message(self.current_session, "assistant", cleaned_response)
            
            return cleaned_response
            
        except Exception as e:
            error_msg = "Xin lỗi, tôi gặp sự cố. Bạn có thể thử lại không?"
            if self.current_session:
                self.memory.add_message(self.current_session, "assistant", error_msg)
            return error_msg
    
    def _clean_response(self, response: str) -> str:
        """
        Làm sạch và rút gọn response
        """
        # Xóa các phần thừa
        response = response.strip()
        
        # Loại bỏ các pattern không mong muốn
        patterns_to_remove = [
            r"^(Trả lời:|Câu trả lời:|Response:)",
            r"^(Xin chào|Hello)",
            r"\n\n+",  # Nhiều dòng trống
        ]
        
        for pattern in patterns_to_remove:
            response = re.sub(pattern, "", response, flags=re.IGNORECASE | re.MULTILINE)
        
        response = response.strip()
        
        # Giới hạn độ dài (tối đa 2 câu)
        sentences = re.split(r'[.!?]+', response)
        if len(sentences) > 2:
            response = '. '.join(sentences[:2]) + '.'
        
        # Giới hạn ký tự (tối đa 200 ký tự)
        if len(response) > 200:
            response = response[:197] + "..."
        
        return response
    
    def get_conversation_history(self, limit: int = 10) -> list:
        """
        Lấy lịch sử hội thoại
        """
        if not self.current_session:
            return []
        return self.memory.get_recent_context(self.current_session, limit)
    
    def clear_conversation(self):
        """
        Xóa hội thoại hiện tại
        """
        if self.current_session:
            self.memory.clear_session(self.current_session)
            self.current_session = None
    
    def close(self):
        """
        Đóng kết nối
        """
        self.memory.close()

# Sử dụng đơn giản
def create_voice_assistant():
    """
    Tạo voice assistant instance
    """
    return ImprovedLLMHandler()

# Test function
if __name__ == "__main__":
    assistant = create_voice_assistant()
    
    # Bắt đầu session mới
    session_id = assistant.start_new_session("test_user")
    print(f"Đã tạo session: {session_id}")
    
    # Test chat
    while True:
        user_input = input("\nBạn: ")
        if user_input.lower() in ['quit', 'exit', 'thoát']:
            break
            
        response = assistant.ask_llm(user_input)
        print(f"AI: {response}")
    
    assistant.close()
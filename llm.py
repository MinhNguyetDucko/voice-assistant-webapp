# llm.py - Wrapper đơn giản để tương thích với code cũ
from improved_llm_handler import create_voice_assistant

# Tạo instance global
_assistant = None

def get_assistant():
    """Lấy hoặc tạo assistant instance"""
    global _assistant
    if _assistant is None:
        _assistant = create_voice_assistant()
        _assistant.start_new_session("default_user")
    return _assistant

def ask_llm(message: str) -> str:
    """
    Hàm wrapper đơn giản cho compatibility với code cũ
    """
    try:
        assistant = get_assistant()
        return assistant.ask_llm(message)
    except Exception as e:
        return "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại."

# Cleanup function
def cleanup():
    global _assistant
    if _assistant:
        _assistant.close()
        _assistant = None
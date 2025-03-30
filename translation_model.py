import logging
import random
import time

logger = logging.getLogger(__name__)

class TranslationModel:
    def __init__(self):
        """Initialize the demo translation model"""
        logger.info("Initializing demo translation model...")
        
        # Some example translations for demonstration (English to various languages)
        self.demo_translations = {
            "ja": {  # Japanese
                "Hello": "こんにちは",
                "Thank you": "ありがとう",
                "How are you?": "お元気ですか？",
                "Welcome": "ようこそ",
                "Good morning": "おはようございます",
                "My name is": "私の名前は",
                "I love languages": "私は言語が大好きです",
                "This is a demonstration": "これはデモンストレーションです"
            },
            "ko": {  # Korean
                "Hello": "안녕하세요",
                "Thank you": "감사합니다",
                "How are you?": "어떻게 지내세요?",
                "Welcome": "환영합니다",
                "Good morning": "좋은 아침이에요",
                "My name is": "제 이름은",
                "I love languages": "저는 언어를 사랑합니다",
                "This is a demonstration": "이것은 데모입니다"
            },
            "zh": {  # Chinese
                "Hello": "你好",
                "Thank you": "谢谢",
                "How are you?": "你好吗？",
                "Welcome": "欢迎",
                "Good morning": "早上好",
                "My name is": "我的名字是",
                "I love languages": "我喜欢语言",
                "This is a demonstration": "这是一个演示"
            },
            "th": {  # Thai
                "Hello": "สวัสดี",
                "Thank you": "ขอบคุณ",
                "How are you?": "คุณเป็นอย่างไรบ้าง?",
                "Welcome": "ยินดีต้อนรับ",
                "Good morning": "สวัสดีตอนเช้า",
                "My name is": "ฉันชื่อ",
                "I love languages": "ฉันรักภาษา",
                "This is a demonstration": "นี่คือการสาธิต"
            },
            "vi": {  # Vietnamese
                "Hello": "Xin chào",
                "Thank you": "Cảm ơn bạn",
                "How are you?": "Bạn khỏe không?",
                "Welcome": "Chào mừng",
                "Good morning": "Chào buổi sáng",
                "My name is": "Tên tôi là",
                "I love languages": "Tôi yêu ngôn ngữ",
                "This is a demonstration": "Đây là một bản demo"
            },
            "my": {  # Burmese
                "Hello": "မင်္ဂလာပါ",
                "Thank you": "ကျေးဇူးတင်ပါတယ်",
                "How are you?": "နေကောင်းလား?",
                "Welcome": "ကြိုဆိုပါတယ်",
                "Good morning": "မင်္ဂလာနံနက်ခင်းပါ",
                "My name is": "ကျွန်တော်နာမည်က",
                "I love languages": "ကျွန်တော် ဘာသာစကားများကို နှစ်သက်သည်",
                "This is a demonstration": "ဤသည်မှာ သရုပ်ပြမှုဖြစ်သည်"
            },
            "id": {  # Indonesian
                "Hello": "Halo",
                "Thank you": "Terima kasih",
                "How are you?": "Apa kabar?",
                "Welcome": "Selamat datang",
                "Good morning": "Selamat pagi",
                "My name is": "Nama saya adalah",
                "I love languages": "Saya suka bahasa",
                "This is a demonstration": "Ini adalah demonstrasi"
            }
        }
        
        logger.info("Demo translation model initialized")
    
    def translate(self, text, target_lang):
        """
        Simulate translation of the input English text to the specified target language
        
        Args:
            text (str): The English text to translate
            target_lang (str): Target language code (e.g., 'ja', 'ko', 'zh')
            
        Returns:
            str: Translated text
        """
        try:
            # Simulate processing time for realistic effect
            time.sleep(0.5 + random.random())
            
            # If the target language is not supported, default to Japanese
            if target_lang not in self.demo_translations:
                target_lang = "ja"
            
            # Check if we have an exact match in our demo translations
            if text in self.demo_translations[target_lang]:
                return self.demo_translations[target_lang][text]
            
            # For longer text, we can combine some of our demo translations
            words = text.split()
            result = []
            
            # Add a note that this is a simulated translation
            result.append("[Demo Translation]")
            
            # Process the text word by word, looking for known phrases
            i = 0
            while i < len(words):
                # Try to match the longest phrase possible
                found = False
                for j in range(min(5, len(words) - i), 0, -1):
                    phrase = " ".join(words[i:i+j])
                    if phrase in self.demo_translations[target_lang]:
                        result.append(self.demo_translations[target_lang][phrase])
                        i += j
                        found = True
                        break
                
                # If no known phrase found, keep the original word
                if not found:
                    result.append(words[i])
                    i += 1
            
            return " ".join(result)
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return f"[Demo] Translation error: {str(e)}"

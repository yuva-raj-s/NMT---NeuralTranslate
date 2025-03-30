import logging
import random
import time

logger = logging.getLogger(__name__)

class TranslationModel:
    def __init__(self):
        """Initialize the demo translation model"""
        logger.info("Initializing demo translation model...")
        
        # Sample translations for all 13 languages in the ALT dataset
        self.demo_translations = {
            "bn": {  # Bengali
                "Hello": "হ্যালো",
                "Thank you": "ধন্যবাদ",
                "How are you?": "আপনি কেমন আছেন?",
                "Welcome": "স্বাগতম",
                "Good morning": "সুপ্রভাত",
                "My name is": "আমার নাম",
                "I love languages": "আমি ভাষা ভালবাসি",
                "This is a demonstration": "এটি একটি প্রদর্শন"
            },
            "en": {  # English (for reference)
                "Hello": "Hello",
                "Thank you": "Thank you",
                "How are you?": "How are you?",
                "Welcome": "Welcome",
                "Good morning": "Good morning",
                "My name is": "My name is",
                "I love languages": "I love languages",
                "This is a demonstration": "This is a demonstration"
            },
            "fil": {  # Filipino
                "Hello": "Kamusta",
                "Thank you": "Salamat",
                "How are you?": "Kumusta ka?",
                "Welcome": "Maligayang pagdating",
                "Good morning": "Magandang umaga",
                "My name is": "Ang pangalan ko ay",
                "I love languages": "Mahilig ako sa mga wika",
                "This is a demonstration": "Ito ay isang pagpapakita"
            },
            "hi": {  # Hindi
                "Hello": "नमस्ते",
                "Thank you": "धन्यवाद",
                "How are you?": "आप कैसे हैं?",
                "Welcome": "स्वागत है",
                "Good morning": "सुप्रभात",
                "My name is": "मेरा नाम है",
                "I love languages": "मुझे भाषाएँ पसंद हैं",
                "This is a demonstration": "यह एक प्रदर्शन है"
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
            },
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
            "km": {  # Khmer
                "Hello": "សួស្តី",
                "Thank you": "អរគុណ",
                "How are you?": "តើអ្នកសុខសប្បាយទេ?",
                "Welcome": "សូមស្វាគមន៍",
                "Good morning": "អរុណសួស្តី",
                "My name is": "ខ្ញុំឈ្មោះ",
                "I love languages": "ខ្ញុំស្រលាញ់ភាសា",
                "This is a demonstration": "នេះគឺជាការបង្ហាញ"
            },
            "lo": {  # Lao
                "Hello": "ສະບາຍດີ",
                "Thank you": "ຂອບໃຈ",
                "How are you?": "ສະບາຍດີບໍ?",
                "Welcome": "ຍິນດີຕ້ອນຮັບ",
                "Good morning": "ອາລຸນສະຫວັດ",
                "My name is": "ຂ້ອຍຊື່",
                "I love languages": "ຂ້ອຍຮັກພາສາ",
                "This is a demonstration": "ນີ້ແມ່ນການສາທິດ"
            },
            "ms": {  # Malay
                "Hello": "Hello",
                "Thank you": "Terima kasih",
                "How are you?": "Apa khabar?",
                "Welcome": "Selamat datang",
                "Good morning": "Selamat pagi",
                "My name is": "Nama saya ialah",
                "I love languages": "Saya suka bahasa",
                "This is a demonstration": "Ini adalah demonstrasi"
            },
            "my": {  # Myanmar (Burmese)
                "Hello": "မင်္ဂလာပါ",
                "Thank you": "ကျေးဇူးတင်ပါတယ်",
                "How are you?": "နေကောင်းလား?",
                "Welcome": "ကြိုဆိုပါတယ်",
                "Good morning": "မင်္ဂလာနံနက်ခင်းပါ",
                "My name is": "ကျွန်တော်နာမည်က",
                "I love languages": "ကျွန်တော် ဘာသာစကားများကို နှစ်သက်သည်",
                "This is a demonstration": "ဤသည်မှာ သရုပ်ပြမှုဖြစ်သည်"
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
            "zh": {  # Chinese (Simplified)
                "Hello": "你好",
                "Thank you": "谢谢",
                "How are you?": "你好吗？",
                "Welcome": "欢迎",
                "Good morning": "早上好",
                "My name is": "我的名字是",
                "I love languages": "我喜欢语言",
                "This is a demonstration": "这是一个演示"
            }
        }
        
        logger.info("Demo translation model initialized with all 13 ALT dataset languages")
    
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

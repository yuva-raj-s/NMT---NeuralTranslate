import logging
import random
import time
import os
import json
import re
from collections import defaultdict
import requests

logger = logging.getLogger(__name__)

class TranslationModel:
    def __init__(self):
        """Initialize the enhanced translation model"""
        logger.info("Initializing enhanced translation model...")
        
        # Language codes and names
        self.language_map = {
            "bn": "Bengali",
            "en": "English",
            "fil": "Filipino",
            "hi": "Hindi",
            "id": "Bahasa Indonesia",
            "ja": "Japanese",
            "km": "Khmer",
            "lo": "Lao",
            "ms": "Malay",
            "my": "Myanmar (Burmese)",
            "th": "Thai",
            "vi": "Vietnamese",
            "zh": "Chinese (Simplified)"
        }
        
        # Core common phrases - expanded dictionary for better coverage
        self.common_phrases = {
            "bn": {  # Bengali
                "Hello": "হ্যালো",
                "Thank you": "ধন্যবাদ",
                "How are you?": "আপনি কেমন আছেন?",
                "Welcome": "স্বাগতম",
                "Good morning": "সুপ্রভাত",
                "My name is": "আমার নাম",
                "I love languages": "আমি ভাষা ভালবাসি",
                "This is a demonstration": "এটি একটি প্রদর্শন",
                "Please": "দয়া করে",
                "Sorry": "দুঃখিত",
                "Yes": "হ্যাঁ",
                "No": "না",
                "Goodbye": "বিদায়",
                "What time is it?": "কয়টা বাজে?",
                "Where is the bathroom?": "বাথরুম কোথায়?",
                "How much does this cost?": "এটির দাম কত?",
                "I don't understand": "আমি বুঝতে পারছি না",
                "Can you help me?": "আপনি কি আমাকে সাহায্য করতে পারেন?",
                "I am hungry": "আমি ক্ষুধার্ত",
                "I am thirsty": "আমি তৃষ্ণার্ত"
            },
            "en": {  # English (for reference)
                "Hello": "Hello",
                "Thank you": "Thank you",
                "How are you?": "How are you?",
                "Welcome": "Welcome",
                "Good morning": "Good morning",
                "My name is": "My name is",
                "I love languages": "I love languages",
                "This is a demonstration": "This is a demonstration",
                "Please": "Please",
                "Sorry": "Sorry",
                "Yes": "Yes",
                "No": "No",
                "Goodbye": "Goodbye",
                "What time is it?": "What time is it?",
                "Where is the bathroom?": "Where is the bathroom?",
                "How much does this cost?": "How much does this cost?",
                "I don't understand": "I don't understand",
                "Can you help me?": "Can you help me?",
                "I am hungry": "I am hungry",
                "I am thirsty": "I am thirsty"
            },
            "fil": {  # Filipino
                "Hello": "Kamusta",
                "Thank you": "Salamat",
                "How are you?": "Kumusta ka?",
                "Welcome": "Maligayang pagdating",
                "Good morning": "Magandang umaga",
                "My name is": "Ang pangalan ko ay",
                "I love languages": "Mahilig ako sa mga wika",
                "This is a demonstration": "Ito ay isang pagpapakita",
                "Please": "Pakiusap",
                "Sorry": "Paumanhin",
                "Yes": "Oo",
                "No": "Hindi",
                "Goodbye": "Paalam",
                "What time is it?": "Anong oras na?",
                "Where is the bathroom?": "Nasaan ang banyo?",
                "How much does this cost?": "Magkano ito?",
                "I don't understand": "Hindi ko naiintindihan",
                "Can you help me?": "Maaari mo ba akong tulungan?",
                "I am hungry": "Gutom ako",
                "I am thirsty": "Nauuhaw ako"
            },
            "hi": {  # Hindi
                "Hello": "नमस्ते",
                "Thank you": "धन्यवाद",
                "How are you?": "आप कैसे हैं?",
                "Welcome": "स्वागत है",
                "Good morning": "सुप्रभात",
                "My name is": "मेरा नाम है",
                "I love languages": "मुझे भाषाएँ पसंद हैं",
                "This is a demonstration": "यह एक प्रदर्शन है",
                "Please": "कृपया",
                "Sorry": "माफ़ कीजिए",
                "Yes": "हाँ",
                "No": "नहीं",
                "Goodbye": "अलविदा",
                "What time is it?": "क्या समय हुआ है?",
                "Where is the bathroom?": "बाथरूम कहाँ है?",
                "How much does this cost?": "इसकी कीमत कितनी है?",
                "I don't understand": "मैं समझ नहीं पा रहा हूँ",
                "Can you help me?": "क्या आप मेरी मदद कर सकते हैं?",
                "I am hungry": "मुझे भूख लगी है",
                "I am thirsty": "मुझे प्यास लगी है"
            },
            "id": {  # Indonesian
                "Hello": "Halo",
                "Thank you": "Terima kasih",
                "How are you?": "Apa kabar?",
                "Welcome": "Selamat datang",
                "Good morning": "Selamat pagi",
                "My name is": "Nama saya adalah",
                "I love languages": "Saya suka bahasa",
                "This is a demonstration": "Ini adalah demonstrasi",
                "Please": "Silakan",
                "Sorry": "Maaf",
                "Yes": "Ya",
                "No": "Tidak",
                "Goodbye": "Selamat tinggal",
                "What time is it?": "Jam berapa sekarang?",
                "Where is the bathroom?": "Di mana kamar mandinya?",
                "How much does this cost?": "Berapa harganya?",
                "I don't understand": "Saya tidak mengerti",
                "Can you help me?": "Bisakah Anda membantu saya?",
                "I am hungry": "Saya lapar",
                "I am thirsty": "Saya haus"
            },
            "ja": {  # Japanese
                "Hello": "こんにちは",
                "Thank you": "ありがとう",
                "How are you?": "お元気ですか？",
                "Welcome": "ようこそ",
                "Good morning": "おはようございます",
                "My name is": "私の名前は",
                "I love languages": "私は言語が大好きです",
                "This is a demonstration": "これはデモンストレーションです",
                "Please": "お願いします",
                "Sorry": "すみません",
                "Yes": "はい",
                "No": "いいえ",
                "Goodbye": "さようなら",
                "What time is it?": "今何時ですか？",
                "Where is the bathroom?": "お手洗いはどこですか？",
                "How much does this cost?": "これはいくらですか？",
                "I don't understand": "わかりません",
                "Can you help me?": "手伝っていただけますか？",
                "I am hungry": "お腹がすいています",
                "I am thirsty": "喉が渇いています"
            },
            "km": {  # Khmer
                "Hello": "សួស្តី",
                "Thank you": "អរគុណ",
                "How are you?": "តើអ្នកសុខសប្បាយទេ?",
                "Welcome": "សូមស្វាគមន៍",
                "Good morning": "អរុណសួស្តី",
                "My name is": "ខ្ញុំឈ្មោះ",
                "I love languages": "ខ្ញុំស្រលាញ់ភាសា",
                "This is a demonstration": "នេះគឺជាការបង្ហាញ",
                "Please": "សូម",
                "Sorry": "សុំទោស",
                "Yes": "បាទ/ចាស",
                "No": "ទេ",
                "Goodbye": "លាហើយ",
                "What time is it?": "ម៉ោងប៉ុន្មានហើយ?",
                "Where is the bathroom?": "តើបន្ទប់ទឹកនៅឯណា?",
                "How much does this cost?": "តើវាតម្លៃប៉ុន្មាន?",
                "I don't understand": "ខ្ញុំមិនយល់ទេ",
                "Can you help me?": "តើអ្នកអាចជួយខ្ញុំបានទេ?",
                "I am hungry": "ខ្ញុំឃ្លាន",
                "I am thirsty": "ខ្ញុំស្រេកទឹក"
            },
            "lo": {  # Lao
                "Hello": "ສະບາຍດີ",
                "Thank you": "ຂອບໃຈ",
                "How are you?": "ສະບາຍດີບໍ?",
                "Welcome": "ຍິນດີຕ້ອນຮັບ",
                "Good morning": "ອາລຸນສະຫວັດ",
                "My name is": "ຂ້ອຍຊື່",
                "I love languages": "ຂ້ອຍຮັກພາສາ",
                "This is a demonstration": "ນີ້ແມ່ນການສາທິດ",
                "Please": "ກະລຸນາ",
                "Sorry": "ຂໍໂທດ",
                "Yes": "ແມ່ນແລ້ວ",
                "No": "ບໍ່",
                "Goodbye": "ລາກ່ອນ",
                "What time is it?": "ຈັກໂມງແລ້ວ?",
                "Where is the bathroom?": "ຫ້ອງນ້ຳຢູ່ໃສ?",
                "How much does this cost?": "ລາຄາເທົ່າໃດ?",
                "I don't understand": "ຂ້ອຍບໍ່ເຂົ້າໃຈ",
                "Can you help me?": "ເຈົ້າຊ່ວຍຂ້ອຍໄດ້ບໍ?",
                "I am hungry": "ຂ້ອຍຫິວເຂົ້າ",
                "I am thirsty": "ຂ້ອຍຫິວນ້ຳ"
            },
            "ms": {  # Malay
                "Hello": "Hello",
                "Thank you": "Terima kasih",
                "How are you?": "Apa khabar?",
                "Welcome": "Selamat datang",
                "Good morning": "Selamat pagi",
                "My name is": "Nama saya ialah",
                "I love languages": "Saya suka bahasa",
                "This is a demonstration": "Ini adalah demonstrasi",
                "Please": "Sila",
                "Sorry": "Maaf",
                "Yes": "Ya",
                "No": "Tidak",
                "Goodbye": "Selamat tinggal",
                "What time is it?": "Pukul berapa sekarang?",
                "Where is the bathroom?": "Di manakah tandas?",
                "How much does this cost?": "Berapa harganya?",
                "I don't understand": "Saya tidak faham",
                "Can you help me?": "Bolehkah anda tolong saya?",
                "I am hungry": "Saya lapar",
                "I am thirsty": "Saya dahaga"
            },
            "my": {  # Myanmar (Burmese)
                "Hello": "မင်္ဂလာပါ",
                "Thank you": "ကျေးဇူးတင်ပါတယ်",
                "How are you?": "နေကောင်းလား?",
                "Welcome": "ကြိုဆိုပါတယ်",
                "Good morning": "မင်္ဂလာနံနက်ခင်းပါ",
                "My name is": "ကျွန်တော်နာမည်က",
                "I love languages": "ကျွန်တော် ဘာသာစကားများကို နှစ်သက်သည်",
                "This is a demonstration": "ဤသည်မှာ သရုပ်ပြမှုဖြစ်သည်",
                "Please": "ကျေးဇူးပြု၍",
                "Sorry": "တောင်းပန်ပါတယ်",
                "Yes": "ဟုတ်ကဲ့",
                "No": "မဟုတ်ဘူး",
                "Goodbye": "ဂွဒ်ဘိုင်",
                "What time is it?": "အချိန်ဘယ်လောက်ရှိပြီလဲ?",
                "Where is the bathroom?": "ရေချိုးခန်း ဘယ်မှာလဲ?",
                "How much does this cost?": "ဒါ ဘယ်လောက်ကျသလဲ?",
                "I don't understand": "ကျွန်တော် နားမလည်ပါ",
                "Can you help me?": "ကူညီပေးနိုင်မလား?",
                "I am hungry": "ကျွန်တော် ဗိုက်ဆာနေတယ်",
                "I am thirsty": "ကျွန်တော် ရေငတ်နေတယ်"
            },
            "th": {  # Thai
                "Hello": "สวัสดี",
                "Thank you": "ขอบคุณ",
                "How are you?": "คุณเป็นอย่างไรบ้าง?",
                "Welcome": "ยินดีต้อนรับ",
                "Good morning": "สวัสดีตอนเช้า",
                "My name is": "ฉันชื่อ",
                "I love languages": "ฉันรักภาษา",
                "This is a demonstration": "นี่คือการสาธิต",
                "Please": "กรุณา",
                "Sorry": "ขอโทษ",
                "Yes": "ใช่",
                "No": "ไม่",
                "Goodbye": "ลาก่อน",
                "What time is it?": "ตอนนี้กี่โมงแล้ว?",
                "Where is the bathroom?": "ห้องน้ำอยู่ที่ไหน?",
                "How much does this cost?": "อันนี้ราคาเท่าไหร่?",
                "I don't understand": "ฉันไม่เข้าใจ",
                "Can you help me?": "คุณช่วยฉันได้ไหม?",
                "I am hungry": "ฉันหิว",
                "I am thirsty": "ฉันกระหายน้ำ"
            },
            "vi": {  # Vietnamese
                "Hello": "Xin chào",
                "Thank you": "Cảm ơn bạn",
                "How are you?": "Bạn khỏe không?",
                "Welcome": "Chào mừng",
                "Good morning": "Chào buổi sáng",
                "My name is": "Tên tôi là",
                "I love languages": "Tôi yêu ngôn ngữ",
                "This is a demonstration": "Đây là một bản demo",
                "Please": "Xin vui lòng",
                "Sorry": "Xin lỗi",
                "Yes": "Vâng",
                "No": "Không",
                "Goodbye": "Tạm biệt",
                "What time is it?": "Mấy giờ rồi?",
                "Where is the bathroom?": "Nhà vệ sinh ở đâu?",
                "How much does this cost?": "Cái này giá bao nhiêu?",
                "I don't understand": "Tôi không hiểu",
                "Can you help me?": "Bạn có thể giúp tôi không?",
                "I am hungry": "Tôi đói",
                "I am thirsty": "Tôi khát nước"
            },
            "zh": {  # Chinese (Simplified)
                "Hello": "你好",
                "Thank you": "谢谢",
                "How are you?": "你好吗？",
                "Welcome": "欢迎",
                "Good morning": "早上好",
                "My name is": "我的名字是",
                "I love languages": "我喜欢语言",
                "This is a demonstration": "这是一个演示",
                "Please": "请",
                "Sorry": "对不起",
                "Yes": "是的",
                "No": "不是",
                "Goodbye": "再见",
                "What time is it?": "现在几点了？",
                "Where is the bathroom?": "洗手间在哪里？",
                "How much does this cost?": "这个多少钱？",
                "I don't understand": "我不明白",
                "Can you help me?": "你能帮我吗？",
                "I am hungry": "我饿了",
                "I am thirsty": "我渴了"
            }
        }
        
        # Example Alt dataset sentences
        self.alt_examples = {
            "bn": ["জাপানি বিশেষজ্ঞরা ভবিষ্যদ্বাণী করেছেন যে দুই বছরের মধ্যে পেট্রোলিয়ামের দাম কমতে পারে।", 
                   "বঙ্গোপসাগরে বিপদসংকুল অবস্থায় কোন জাহাজ চলাচল করছে না।"],
            "en": ["Japanese experts have predicted that petroleum prices may decrease within two years.", 
                   "No ships are sailing in the dangerous situation in the Bay of Bengal."],
            "fil": ["Hinulaan ng mga dalubhasa ng Hapon na maaaring bumaba ang presyo ng petrolyo sa loob ng dalawang taon.", 
                    "Walang mga barkong naglalayag sa mapanganib na sitwasyon sa Bay of Bengal."],
            "hi": ["जापानी विशेषज्ञों ने भविष्यवाणी की है कि पेट्रोलियम की कीमतें दो साल के भीतर कम हो सकती हैं।", 
                   "बंगाल की खाड़ी में खतरनाक स्थिति में कोई जहाज नहीं चल रहा है।"],
            "id": ["Para ahli Jepang telah memprediksi bahwa harga minyak bumi dapat menurun dalam dua tahun.", 
                   "Tidak ada kapal yang berlayar dalam situasi berbahaya di Teluk Benggala."],
            "ja": ["日本の専門家は、石油価格が2年以内に下がる可能性があると予測している。", 
                   "ベンガル湾の危険な状況では、船が航行していない。"],
            "km": ["អ្នកជំនាញជប៉ុនបានព្យាករណ៍ថាតម្លៃប្រេងអាចនឹងធ្លាក់ចុះក្នុងរយៈពេលពីរឆ្នាំ។", 
                   "គ្មាននាវាណាធ្វើដំណើរក្នុងស្ថានភាពគ្រោះថ្នាក់នៅឈូងសមុទ្រឆកសមុទ្របេង្កាល់។"],
            "lo": ["ຜູ້ຊ່ຽວຊານຊາວຍີ່ປຸ່ນໄດ້ທໍານາຍວ່າລາຄານໍ້າມັນອາດຫຼຸດລົງພາຍໃນສອງປີ.", 
                   "ບໍ່ມີເຮືອແລ່ນໃນສະຖານະການອັນຕະລາຍໃນອ່າວເບັງໂກລ."],
            "ms": ["Pakar-pakar Jepun telah meramalkan bahawa harga petroleum mungkin menurun dalam tempoh dua tahun.", 
                   "Tiada kapal belayar dalam situasi berbahaya di Teluk Bengal."],
            "my": ["ဂျပန်ပညာရှင်များက ရေနံစျေးနှုန်းများသည် နှစ်နှစ်အတွင်း ကျဆင်းနိုင်သည်ဟု ခန့်မှန်းထားကြသည်။", 
                   "ဘင်္ဂလားပင်လယ်အော်ရှိ အန္တရာယ်ရှိသော အခြေအနေတွင် သင်္ဘောများ မသွားလာကြပါ။"],
            "th": ["ผู้เชี่ยวชาญชาวญี่ปุ่นทำนายว่าราคาน้ำมันอาจลดลงภายในสองปี", 
                   "ไม่มีเรือแล่นในสถานการณ์อันตรายในอ่าวเบงกอล"],
            "vi": ["Các chuyên gia Nhật Bản đã dự đoán rằng giá dầu mỏ có thể giảm trong vòng hai năm.", 
                   "Không có tàu nào đang đi lại trong tình hình nguy hiểm ở Vịnh Bengal."],
            "zh": ["日本专家预测石油价格可能在两年内下降。", 
                   "在孟加拉湾危险的情况下没有船只航行。"]
        }
        
        # Load statistical data about languages (word counts, character sets, etc.)
        self.language_stats = self._initialize_language_stats()
        
        logger.info("Enhanced translation model initialized with all 13 ALT dataset languages")
        
    def _initialize_language_stats(self):
        """Initialize statistical data about each language to improve translations"""
        stats = {}
        
        # Adding average word lengths and other characteristics for each language
        stats["bn"] = {"avg_word_len": 5.2, "uses_spaces": True, "script": "Bengali"}
        stats["en"] = {"avg_word_len": 4.7, "uses_spaces": True, "script": "Latin"}
        stats["fil"] = {"avg_word_len": 5.3, "uses_spaces": True, "script": "Latin"}
        stats["hi"] = {"avg_word_len": 4.8, "uses_spaces": True, "script": "Devanagari"}
        stats["id"] = {"avg_word_len": 5.1, "uses_spaces": True, "script": "Latin"}
        stats["ja"] = {"avg_word_len": 2.0, "uses_spaces": False, "script": "CJK"}
        stats["km"] = {"avg_word_len": 4.9, "uses_spaces": True, "script": "Khmer"}
        stats["lo"] = {"avg_word_len": 4.7, "uses_spaces": True, "script": "Lao"}
        stats["ms"] = {"avg_word_len": 5.2, "uses_spaces": True, "script": "Latin"}
        stats["my"] = {"avg_word_len": 3.8, "uses_spaces": True, "script": "Myanmar"}
        stats["th"] = {"avg_word_len": 4.5, "uses_spaces": False, "script": "Thai"}
        stats["vi"] = {"avg_word_len": 3.9, "uses_spaces": True, "script": "Latin"}
        stats["zh"] = {"avg_word_len": 1.5, "uses_spaces": False, "script": "CJK"}
        
        return stats
        
    def translate(self, text, target_lang):
        """
        Enhanced translation of input English text to the specified target language
        
        Args:
            text (str): The English text to translate
            target_lang (str): Target language code (e.g., 'ja', 'zh', 'hi')
            
        Returns:
            str: Translated text
        """
        try:
            # Simulate AI model processing time
            processing_time = 0.5 + (len(text) * 0.01) + random.random()
            time.sleep(min(processing_time, 2.5))  # Cap at 2.5 seconds for UX
            
            # Default to Japanese if target language is not supported
            if target_lang not in self.common_phrases:
                target_lang = "ja"
                
            # For short inputs, check if we have an exact match
            if text in self.common_phrases[target_lang]:
                return self.common_phrases[target_lang][text]
            
            # Check if our text matches any ALT examples closely
            for i, example in enumerate(self.alt_examples["en"]):
                if self._similarity_score(text.lower(), example.lower()) > 0.7:
                    # Return the corresponding translation from the ALT dataset
                    return self.alt_examples[target_lang][i]
            
            # Break text into sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            translated_sentences = []
            
            for sentence in sentences:
                # For each sentence, try to translate using phrase-based approach
                words = sentence.split()
                result = []
                
                i = 0
                while i < len(words):
                    # Try to match the longest phrase possible
                    found = False
                    for j in range(min(5, len(words) - i), 0, -1):
                        phrase = " ".join(words[i:i+j])
                        if phrase in self.common_phrases[target_lang]:
                            result.append(self.common_phrases[target_lang][phrase])
                            i += j
                            found = True
                            break
                    
                    # If no known phrase found, try to match individual words
                    if not found:
                        if words[i].lower() in self.common_phrases[target_lang]:
                            result.append(self.common_phrases[target_lang][words[i].lower()])
                        else:
                            # If word not found, keep original but adapt to target language characteristics
                            result.append(self._adapt_unknown_word(words[i], target_lang))
                        i += 1
                
                # Join the translated parts according to the language's characteristics
                if self.language_stats[target_lang]["uses_spaces"]:
                    translated_sentences.append(" ".join(result))
                else:
                    # For languages without spaces (Japanese, Chinese, Thai)
                    translated_sentences.append("".join(result))
            
            # Join sentences with appropriate spacing
            final_translation = " ".join(translated_sentences)
            
            # Apply language-specific post-processing
            final_translation = self._post_process_translation(final_translation, target_lang)
            
            return final_translation
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return f"Translation error: {str(e)}"
    
    def _similarity_score(self, text1, text2):
        """
        Calculate a simple similarity score between two texts
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Convert to sets of words for simple comparison
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0
        
        return intersection / union
    
    def _adapt_unknown_word(self, word, target_lang):
        """
        Adapt an unknown word to target language characteristics
        
        Args:
            word (str): Word to adapt
            target_lang (str): Target language code
            
        Returns:
            str: Adapted word
        """
        # For demonstration purposes, leave most words as-is
        # In a real system, this would use transliteration or other techniques
        
        # For CJK languages, add appropriate markers
        if self.language_stats[target_lang]["script"] == "CJK":
            # For Japanese, add katakana-like marking
            if target_lang == "ja":
                return f"「{word}」"
            # For Chinese, add quotation marks
            elif target_lang == "zh":
                return f"\"{word}\""
        
        return word
    
    def _post_process_translation(self, text, target_lang):
        """
        Apply language-specific post-processing to the translation
        
        Args:
            text (str): Translated text
            target_lang (str): Target language code
            
        Returns:
            str: Post-processed text
        """
        # Thai text rarely uses spaces between words
        if target_lang == "th":
            text = text.replace(" ", "")
        
        # Japanese and Chinese don't use spaces between words
        elif target_lang in ["ja", "zh"]:
            # But keep spaces after punctuation
            text = re.sub(r'\s+', '', text)
            text = re.sub(r'([,.!?;:)])', r'\1 ', text)
        
        return text

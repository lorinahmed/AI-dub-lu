import os
import asyncio
from typing import Optional
from googletrans import Translator as GoogleTranslator

class Translator:
    def __init__(self):
        self.translator = GoogleTranslator()
        self.service = os.getenv("TRANSLATION_SERVICE", "google")
    
    async def translate(self, text: str, target_language: str, source_language: Optional[str] = None) -> str:
        """Translate text to target language"""
        try:
            if not text or not text.strip():
                raise Exception("No text provided for translation")
            
            if not target_language:
                raise Exception("Target language not specified")
            
            # Call the async translation method directly
            translated_text = await self._translate_sync(text, target_language, source_language)
            
            return translated_text
            
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
    
    async def _translate_sync(self, text: str, target_language: str, source_language: Optional[str] = None) -> str:
        """Synchronous translation using Google Translate"""
        try:
            # Detect source language if not provided
            if not source_language:
                detected = await self.translator.detect(text)
                source_language = detected.lang
            
            # Translate the text
            result = await self.translator.translate(
                text, 
                dest=target_language, 
                src=source_language
            )
            
            translated_text = result.text
            
            if not translated_text:
                raise Exception("Translation returned empty result")
            
            return translated_text
            
        except Exception as e:
            raise Exception(f"Google Translate error: {str(e)}")
    
    async def translate_segments(self, segments: list, target_language: str, source_language: Optional[str] = None) -> list:
        """Translate a list of text segments with timestamps"""
        try:
            translated_segments = []
            
            for segment in segments:
                # Translate the text
                translated_text = await self.translate(
                    segment.get("text", ""), 
                    target_language, 
                    source_language
                )
                
                # Create new segment with translated text
                translated_segment = {
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "original_text": segment.get("text", ""),
                    "translated_text": translated_text,
                    "words": segment.get("words", [])
                }
                
                translated_segments.append(translated_segment)
            
            return translated_segments
            
        except Exception as e:
            raise Exception(f"Segment translation failed: {str(e)}")
    
    def get_supported_languages(self) -> dict:
        """Get list of supported languages for translation"""
        return {
            "af": "Afrikaans",
            "sq": "Albanian",
            "am": "Amharic",
            "ar": "Arabic",
            "hy": "Armenian",
            "az": "Azerbaijani",
            "eu": "Basque",
            "be": "Belarusian",
            "bn": "Bengali",
            "bs": "Bosnian",
            "bg": "Bulgarian",
            "ca": "Catalan",
            "ceb": "Cebuano",
            "zh": "Chinese (Simplified)",
            "zh-tw": "Chinese (Traditional)",
            "co": "Corsican",
            "hr": "Croatian",
            "cs": "Czech",
            "da": "Danish",
            "nl": "Dutch",
            "en": "English",
            "eo": "Esperanto",
            "et": "Estonian",
            "fi": "Finnish",
            "fr": "French",
            "fy": "Frisian",
            "gl": "Galician",
            "ka": "Georgian",
            "de": "German",
            "el": "Greek",
            "gu": "Gujarati",
            "ht": "Haitian Creole",
            "ha": "Hausa",
            "haw": "Hawaiian",
            "he": "Hebrew",
            "hi": "Hindi",
            "hmn": "Hmong",
            "hu": "Hungarian",
            "is": "Icelandic",
            "ig": "Igbo",
            "id": "Indonesian",
            "ga": "Irish",
            "it": "Italian",
            "ja": "Japanese",
            "jv": "Javanese",
            "kn": "Kannada",
            "kk": "Kazakh",
            "km": "Khmer",
            "ko": "Korean",
            "ku": "Kurdish",
            "ky": "Kyrgyz",
            "lo": "Lao",
            "la": "Latin",
            "lv": "Latvian",
            "lt": "Lithuanian",
            "lb": "Luxembourgish",
            "mk": "Macedonian",
            "mg": "Malagasy",
            "ms": "Malay",
            "ml": "Malayalam",
            "mt": "Maltese",
            "mi": "Maori",
            "mr": "Marathi",
            "mn": "Mongolian",
            "my": "Myanmar (Burmese)",
            "ne": "Nepali",
            "no": "Norwegian",
            "ny": "Nyanja (Chichewa)",
            "or": "Odia (Oriya)",
            "ps": "Pashto",
            "fa": "Persian",
            "pl": "Polish",
            "pt": "Portuguese",
            "pa": "Punjabi",
            "ro": "Romanian",
            "ru": "Russian",
            "sm": "Samoan",
            "gd": "Scots Gaelic",
            "sr": "Serbian",
            "st": "Sesotho",
            "sn": "Shona",
            "sd": "Sindhi",
            "si": "Sinhala (Sinhalese)",
            "sk": "Slovak",
            "sl": "Slovenian",
            "so": "Somali",
            "es": "Spanish",
            "su": "Sundanese",
            "sw": "Swahili",
            "sv": "Swedish",
            "tl": "Tagalog (Filipino)",
            "tg": "Tajik",
            "ta": "Tamil",
            "tt": "Tatar",
            "te": "Telugu",
            "th": "Thai",
            "tr": "Turkish",
            "tk": "Turkmen",
            "uk": "Ukrainian",
            "ur": "Urdu",
            "ug": "Uyghur",
            "uz": "Uzbek",
            "vi": "Vietnamese",
            "cy": "Welsh",
            "xh": "Xhosa",
            "yi": "Yiddish",
            "yo": "Yoruba",
            "zu": "Zulu"
        }
    
    async def detect_language(self, text: str) -> str:
        """Detect the language of the given text"""
        try:
            detected = await self.translator.detect(text)
            return detected.lang
        except Exception as e:
            raise Exception(f"Language detection failed: {str(e)}") 
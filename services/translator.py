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
    
    async def translate_segments(self, segments: list, target_language: str, source_language: Optional[str] = None, timing_aware: bool = False) -> list:
        """Translate a list of text segments with timestamps"""
        try:
            translated_segments = []
            
            for segment in segments:
                original_text = segment.get("text", "").strip()
                if not original_text:
                    continue
                
                # Calculate target word count if timing-aware translation is enabled
                target_word_count = None
                if timing_aware:
                    original_duration = segment.get("end", 0) - segment.get("start", 0)
                    target_word_count = self._calculate_target_word_count(original_duration)
                
                # Translate the text with timing constraints if needed
                if timing_aware and target_word_count:
                    translated_text = await self._timing_aware_translate(
                        original_text, target_language, target_word_count, source_language
                    )
                else:
                    translated_text = await self.translate(original_text, target_language, source_language)
                
                # Create new segment with translated text
                translated_segment = {
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "original_duration": segment.get("end", 0) - segment.get("start", 0),
                    "target_word_count": target_word_count,
                    "words": segment.get("words", [])
                }
                
                translated_segments.append(translated_segment)
            
            return translated_segments
            
        except Exception as e:
            raise Exception(f"Segment translation failed: {str(e)}")
    
    def _calculate_target_word_count(self, duration: float) -> int:
        """Calculate target word count based on duration and speaking rate"""
        # Average speaking rate: 150 words per minute
        words_per_minute = 150
        duration_minutes = duration / 60.0
        target_words = int(duration_minutes * words_per_minute)
        return max(target_words, 1)
    
    async def _timing_aware_translate(self, text: str, target_language: str, target_word_count: int, source_language: Optional[str] = None) -> str:
        """Use GPT for timing-aware translation if available, otherwise fallback to regular translation"""
        try:
            # Try to use OpenAI for timing-aware translation
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                return await self._gpt_timing_aware_translate(text, target_language, target_word_count, source_language)
            else:
                # Fallback to regular translation
                return await self.translate(text, target_language, source_language)
        except Exception as e:
            print(f"Timing-aware translation failed, using fallback: {str(e)}")
            return await self.translate(text, target_language, source_language)
    
    async def _gpt_timing_aware_translate(self, text: str, target_language: str, target_word_count: int, source_language: Optional[str] = None) -> str:
        """Use GPT for timing-aware translation"""
        try:
            import openai
            
            # Language name mapping
            language_names = {
                "es": "Spanish", "fr": "French", "de": "German", "it": "Italian",
                "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "ko": "Korean",
                "zh": "Chinese", "hi": "Hindi", "ar": "Arabic", "nl": "Dutch",
                "sv": "Swedish", "no": "Norwegian", "da": "Danish", "fi": "Finnish"
            }
            
            target_lang_name = language_names.get(target_language, target_language)
            
            prompt = f"""
            Translate the following text to {target_lang_name}, keeping it concise enough to be spoken in approximately {target_word_count} words (target: {target_word_count} words).

            IMPORTANT: 
            - Preserve the meaning and intent, not exact word-for-word translation
            - Keep the translation natural and conversational
            - Aim for exactly {target_word_count} words (±1 word)
            - If the original is too long, condense it while keeping key information
            - If the original is too short, expand slightly while maintaining natural flow

            Original text: "{text}"

            Translation ({target_lang_name}):
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in timing-aware translations for dubbing."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Clean up the response
            import re
            translated_text = re.sub(r'^["\']|["\']$', '', translated_text)
            
            return translated_text
            
        except Exception as e:
            raise Exception(f"GPT timing-aware translation failed: {str(e)}")
    
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
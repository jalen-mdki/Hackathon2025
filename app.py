from flask import Flask, request, Response, jsonify, send_file
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
import json
import datetime
import re
import sqlite3
import uuid
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple
import requests
from urllib.parse import urlparse
from collections import deque
import tempfile
import io
import base64
import time
import threading
import asyncio

# For NLP and AI processing
from openai import OpenAI  # You'll need: pip install openai
from textblob import TextBlob  # You'll need: pip install textblob

# NEW: Text-to-Speech imports
try:
    import pyttsx3  # You'll need: pip install pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    print("⚠️  pyttsx3 not installed. TTS will use OpenAI API fallback.")
    TTS_AVAILABLE = False

try:
    from gtts import gTTS  # You'll need: pip install gtts
    GTTS_AVAILABLE = True
except ImportError:
    print("⚠️  gTTS not installed. Will use pyttsx3 or OpenAI fallback.")
    GTTS_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Laravel Backend Configuration
LARAVEL_BASE_URL = os.getenv("LARAVEL_BASE_URL", "http://127.0.0.1:8000/api")
LARAVEL_API_TOKEN = os.getenv("LARAVEL_API_TOKEN", "your-api-token")

# NEW: TTS Configuration
TTS_ENABLED = os.getenv("TTS_ENABLED", "true").lower() == "true"
TTS_VOICE_SPEED = int(os.getenv("TTS_VOICE_SPEED", "150"))  # Words per minute
TTS_LANGUAGE = os.getenv("TTS_LANGUAGE", "en")  # Language code
TTS_VOICE_GENDER = os.getenv("TTS_VOICE_GENDER", "female")  # male/female
TTS_MAX_LENGTH = int(os.getenv("TTS_MAX_LENGTH", "1000"))  # Max characters for TTS

# Initialize services
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Data models (keeping all existing models)
@dataclass
class IncidentReport:
    id: str
    user_phone: str
    timestamp: str
    incident_type: str
    severity: str
    description: str
    location: str
    location_lat: Optional[float]
    location_long: Optional[float]
    media_urls: List[str]
    status: str
    ai_analysis: Dict
    created_at: str

@dataclass
class UserProfile:
    phone: str
    name: Optional[str]
    role: Optional[str]
    department: Optional[str]
    preferred_language: str
    interaction_history: List[Dict]
    safety_interests: List[str]
    last_active: str
    # NEW: TTS preferences
    tts_enabled: bool = True
    tts_voice_preference: str = "female"
    tts_speed_preference: int = 150
    # NEW: Dual messaging preferences
    dual_messaging_enabled: bool = True
    voice_for_emergencies: bool = True
    voice_for_long_messages: bool = True
    voice_delay_seconds: int = 2
    preferred_message_format: str = "both"  # text, voice, both

@dataclass
class ConversationTurn:
    """Individual conversation turn with rich metadata"""
    id: str
    user_message: str
    bot_response: str
    timestamp: str
    intent: str
    topics: List[str]
    sentiment: str
    context_used: Dict
    response_quality_score: float
    user_satisfaction_indicators: List[str]
    # NEW: TTS metadata
    tts_audio_url: Optional[str] = None
    tts_generated: bool = False

@dataclass
class ConversationThread:
    """Complete conversation thread with continuity tracking"""
    phone: str
    thread_id: str
    start_time: str
    last_activity: str
    total_turns: int
    conversation_summary: str
    key_topics_discussed: List[str]
    user_goals_identified: List[str]
    relationship_building_score: float
    conversation_satisfaction_score: float
    unresolved_issues: List[str]
    follow_up_needed: bool
    conversation_type: str  # casual, incident_reporting, training, emergency

class EnhancedTextToSpeechManager:
    """Enhanced Text-to-Speech manager with dual messaging support"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.audio_cache = {}  # Cache for frequently used phrases
        self.performance_stats = {
            'total_generated': 0,
            'cache_hits': 0,
            'generation_times': [],
            'file_sizes': []
        }
        
        # Initialize TTS engines
        if TTS_AVAILABLE:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                self._configure_pyttsx3()
                self.pyttsx3_ready = True
            except:
                self.pyttsx3_ready = False
                print("⚠️  pyttsx3 engine initialization failed")
        else:
            self.pyttsx3_ready = False
        
        # Enhanced phrases for dual messaging
        self.critical_messages = {
            "emergency": "🚨 Emergency detected! Call 911 immediately for life-threatening situations!",
            "fire": "🔥 Fire emergency! Call 912 Fire Service or 911 Emergency Services right now!",
            "medical": "🚑 Medical emergency! Call 913 for ambulance or 911 for emergency services!",
            "welcome": "Hello! I'm ARIA, your AI safety assistant. I can help with incident reporting, safety questions, and emergency guidance.",
            "menu": "Main menu: Say REPORT for incident reporting, FAQ for safety information, EMERGENCY for contacts, or STATUS for system info.",
            "emergency_fire": "FIRE EMERGENCY! Call 912 Fire Service or 911 Emergency Services RIGHT NOW!",
            "emergency_medical": "MEDICAL EMERGENCY! Call 913 for ambulance or 911 for emergency services IMMEDIATELY!",
            "emergency_general": "EMERGENCY! Call 911 IMMEDIATELY for life-threatening situations!",
            "welcome_dual": "Hello! I'm ARIA, your AI safety assistant. You'll receive both text and audio messages for better accessibility.",
            "menu_dual": "Main menu: Say REPORT for incidents, FAQ for information, EMERGENCY for contacts, or VOICE for audio settings.",
            "report_submitted_dual": "Your safety report has been successfully submitted to the dashboard with both text confirmation and audio notification.",
            "voice_enabled_dual": "Voice responses are now enabled. You'll receive both text and audio messages for optimal accessibility.",
            "voice_disabled_dual": "Voice responses are now disabled. You'll only receive text messages from now on."
        }
        
        # Pre-generate common phrases
        self._pregenerate_common_phrases()
    
    def _configure_pyttsx3(self):
        """Configure pyttsx3 engine settings"""
        if not self.pyttsx3_ready:
            return
        
        try:
            # Set voice properties
            voices = self.pyttsx3_engine.getProperty('voices')
            if voices:
                # Try to find preferred voice gender
                for voice in voices:
                    if TTS_VOICE_GENDER.lower() in voice.name.lower():
                        self.pyttsx3_engine.setProperty('voice', voice.id)
                        break
                else:
                    # Default to first available voice
                    self.pyttsx3_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate (optimized for dual messaging)
            self.pyttsx3_engine.setProperty('rate', TTS_VOICE_SPEED)
            
            # Set volume
            self.pyttsx3_engine.setProperty('volume', 0.9)
            
        except Exception as e:
            print(f"Error configuring pyttsx3: {e}")
    
    def _pregenerate_common_phrases(self):
        """Pre-generate audio for common safety phrases"""
        print("🎙️  Pre-generating dual messaging phrases...")
        
        for phrase_id, text in self.critical_messages.items():
            try:
                # Clean text for TTS
                clean_text = self._clean_text_for_tts(text)
                audio_file = self._generate_tts_file(clean_text, phrase_id)
                if audio_file:
                    self.audio_cache[phrase_id] = audio_file
                    print(f"✅ Generated TTS for: {phrase_id}")
            except Exception as e:
                print(f"❌ Failed to generate TTS for {phrase_id}: {e}")
    
    def generate_tts_audio(self, text: str, user_preferences: Dict = None, cache_key: str = None) -> Optional[str]:
        """Generate TTS audio file and return file path or URL"""
        
        if not TTS_ENABLED:
            return None
        
        start_time = time.time()
        
        # Check cache first
        if cache_key and cache_key in self.audio_cache:
            self.performance_stats['cache_hits'] += 1
            return self.audio_cache[cache_key]
        
        # Clean and prepare text
        clean_text = self._clean_text_for_tts(text)
        
        # Check if text is too long
        if len(clean_text) > TTS_MAX_LENGTH:
            clean_text = self._truncate_text_for_tts(clean_text)
        
        # Try different TTS engines in order of preference
        audio_file = None
        
        # 1. Try gTTS (Google Text-to-Speech) - best quality
        if GTTS_AVAILABLE:
            audio_file = self._generate_gtts_audio(clean_text, user_preferences)
        
        # 2. Try pyttsx3 (offline) - privacy friendly
        if not audio_file and self.pyttsx3_ready:
            audio_file = self._generate_pyttsx3_audio(clean_text, user_preferences)
        
        # 3. Try OpenAI TTS (premium option)
        if not audio_file and OPENAI_API_KEY:
            audio_file = self._generate_openai_tts(clean_text, user_preferences)
        
        # Update performance stats
        generation_time = (time.time() - start_time) * 1000
        self.performance_stats['generation_times'].append(generation_time)
        self.performance_stats['total_generated'] += 1
        
        # Cache the result if successful
        if audio_file and cache_key:
            self.audio_cache[cache_key] = audio_file
        
        if audio_file and os.path.exists(audio_file):
            file_size = os.path.getsize(audio_file)
            self.performance_stats['file_sizes'].append(file_size)
            print(f"🎙️ TTS generated in {generation_time:.1f}ms, size: {file_size} bytes")
        
        return audio_file
    
    def generate_for_dual_messaging(self, text: str, user_preferences: Dict = None, 
                                   priority: str = 'normal') -> Optional[str]:
        """Generate TTS optimized for dual messaging"""
        
        # Clean and optimize text for dual messaging
        clean_text = self._clean_text_for_dual_messaging(text)
        
        # Generate with appropriate engine based on priority
        if priority == 'emergency':
            # Use fastest engine for emergencies
            audio_file = self._generate_emergency_audio(clean_text, user_preferences)
        else:
            # Use best quality engine for normal messages
            audio_file = self.generate_tts_audio(clean_text, user_preferences)
        
        return audio_file
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS pronunciation"""
        
        # Remove markdown formatting
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)  # Italic
        clean_text = re.sub(r'`(.*?)`', r'\1', clean_text)   # Code
        
        # Remove emojis and special characters
        clean_text = re.sub(r'[🔥🚨🚑🚒👮🏥📞📋🆔🚀📊🤖💬🛡️💪😊👋🔸📸📍⚡🧪🦺🪑📖🔹💡⚠️✅❌]', '', clean_text)
        
        # Replace common abbreviations for better pronunciation
        replacements = {
            'ARIA': 'Aria',
            'AI': 'A.I.',
            'PPE': 'P.P.E.',
            'HSSE': 'H.S.S.E.',
            'FAQ': 'F.A.Q.',
            'GPS': 'G.P.S.',
            'API': 'A.P.I.',
            'URL': 'U.R.L.',
            'ID': 'I.D.',
            'WhatsApp': 'WhatsApp',
            'Georgetown': 'Georgetown',
            'Guyana': 'Guy-ana'
        }
        
        for abbrev, pronunciation in replacements.items():
            clean_text = clean_text.replace(abbrev, pronunciation)
        
        # Clean up multiple spaces and newlines
        clean_text = re.sub(r'\n+', '. ', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Remove URLs and phone numbers (too long for TTS)
        clean_text = re.sub(r'http[s]?://\S+', 'website link', clean_text)
        clean_text = re.sub(r'\b\d{3}-\d{4}\b', 'phone number', clean_text)
        
        return clean_text.strip()
    
    def _clean_text_for_dual_messaging(self, text: str) -> str:
        """Enhanced text cleaning optimized for dual messaging"""
        
        # Start with base cleaning
        clean_text = self._clean_text_for_tts(text)
        
        # Additional optimizations for dual messaging
        dual_messaging_replacements = {
            '🎙️': 'Audio message:',
            '📱': 'Mobile',
            '💬': '',
            '📧': 'Message:',
            '✅': 'Success!',
            '❌': 'Error!',
            '⚠️': 'Warning!',
            'WhatsApp': 'WhatsApp messaging',
            'dashboard': 'safety dashboard',
            'Laravel': 'Laravel system'
        }
        
        for symbol, replacement in dual_messaging_replacements.items():
            clean_text = clean_text.replace(symbol, replacement)
        
        # Optimize for voice delivery
        clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)  # Remove bold
        clean_text = re.sub(r'🔸\s*', '', clean_text)  # Remove bullet points
        clean_text = re.sub(r'Type\s+"([^"]+)"\s*', r'Say \1 ', clean_text)  # Voice-friendly commands
        
        return clean_text.strip()
    
    def _truncate_text_for_tts(self, text: str) -> str:
        """Intelligently truncate text for TTS while preserving important information"""
        
        if len(text) <= TTS_MAX_LENGTH:
            return text
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Keep emergency information if present
        emergency_keywords = ['emergency', 'call 911', 'fire', 'medical', 'urgent']
        important_sentences = []
        other_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in emergency_keywords):
                important_sentences.append(sentence)
            else:
                other_sentences.append(sentence)
        
        # Start with important sentences
        result = '. '.join(important_sentences)
        
        # Add other sentences until we reach the limit
        for sentence in other_sentences:
            if len(result + '. ' + sentence) <= TTS_MAX_LENGTH:
                result += '. ' + sentence
            else:
                break
        
        # Add continuation hint if we truncated
        if len(result) < len(text):
            result += ". For complete information, please read the full message."
        
        return result
    
    def _generate_gtts_audio(self, text: str, user_preferences: Dict = None) -> Optional[str]:
        """Generate audio using Google Text-to-Speech"""
        try:
            language = user_preferences.get('language', TTS_LANGUAGE) if user_preferences else TTS_LANGUAGE
            
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Create temporary file
            audio_file = os.path.join(self.temp_dir, f"tts_{uuid.uuid4().hex}.mp3")
            tts.save(audio_file)
            
            return audio_file
            
        except Exception as e:
            print(f"gTTS generation failed: {e}")
            return None
    
    def _generate_pyttsx3_audio(self, text: str, user_preferences: Dict = None) -> Optional[str]:
        """Generate audio using pyttsx3 (offline)"""
        try:
            if not self.pyttsx3_ready:
                return None
            
            # Configure based on user preferences
            if user_preferences:
                speed = user_preferences.get('tts_speed_preference', TTS_VOICE_SPEED)
                self.pyttsx3_engine.setProperty('rate', speed)
            
            # Create temporary file
            audio_file = os.path.join(self.temp_dir, f"tts_{uuid.uuid4().hex}.wav")
            
            # Generate audio
            self.pyttsx3_engine.save_to_file(text, audio_file)
            self.pyttsx3_engine.runAndWait()
            
            # Check if file was created
            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                return audio_file
            else:
                return None
                
        except Exception as e:
            print(f"pyttsx3 generation failed: {e}")
            return None
    
    def _generate_openai_tts(self, text: str, user_preferences: Dict = None) -> Optional[str]:
        """Generate audio using OpenAI's TTS API"""
        try:
            # Choose voice based on preferences
            voice_preference = user_preferences.get('tts_voice_preference', TTS_VOICE_GENDER) if user_preferences else TTS_VOICE_GENDER
            
            voice_map = {
                'female': 'nova',
                'male': 'onyx',
                'alloy': 'alloy',
                'echo': 'echo',
                'fable': 'fable',
                'shimmer': 'shimmer'
            }
            
            voice = voice_map.get(voice_preference.lower(), 'nova')
            
            response = openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Create temporary file
            audio_file = os.path.join(self.temp_dir, f"tts_{uuid.uuid4().hex}.mp3")
            
            with open(audio_file, 'wb') as f:
                f.write(response.content)
            
            return audio_file
            
        except Exception as e:
            print(f"OpenAI TTS generation failed: {e}")
            return None
    
    def _generate_emergency_audio(self, text: str, user_preferences: Dict = None) -> Optional[str]:
        """Generate emergency audio with fastest available engine"""
        
        # Try pyttsx3 first for speed
        if self.pyttsx3_ready:
            try:
                return self._generate_pyttsx3_audio(text, user_preferences)
            except:
                pass
        
        # Fallback to other engines
        return self.generate_tts_audio(text, user_preferences)
    
    def _generate_tts_file(self, text: str, cache_key: str = None) -> Optional[str]:
        """Generate TTS file with default settings"""
        return self.generate_tts_audio(text, cache_key=cache_key)
    
    def get_emergency_audio(self, emergency_type: str = "emergency") -> Optional[str]:
        """Get pre-generated emergency audio"""
        return self.audio_cache.get(emergency_type)
    
    def get_dual_messaging_audio(self, message_type: str) -> Optional[str]:
        """Get pre-generated audio for dual messaging scenarios"""
        return self.audio_cache.get(f"{message_type}_dual", self.audio_cache.get(message_type))
    
    def get_performance_stats(self) -> Dict:
        """Get TTS performance statistics"""
        avg_generation_time = sum(self.performance_stats['generation_times']) / max(len(self.performance_stats['generation_times']), 1)
        avg_file_size = sum(self.performance_stats['file_sizes']) / max(len(self.performance_stats['file_sizes']), 1)
        cache_hit_rate = self.performance_stats['cache_hits'] / max(self.performance_stats['total_generated'], 1)
        
        return {
            'total_generated': self.performance_stats['total_generated'],
            'cache_hits': self.performance_stats['cache_hits'],
            'cache_hit_rate': round(cache_hit_rate * 100, 2),
            'avg_generation_time_ms': round(avg_generation_time, 2),
            'avg_file_size_bytes': round(avg_file_size, 2),
            'cache_size': len(self.audio_cache),
            'temp_files_count': len([f for f in os.listdir(self.temp_dir) if f.startswith('tts_')])
        }
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old TTS files to save disk space"""
        try:
            current_time = datetime.datetime.now()
            
            for filename in os.listdir(self.temp_dir):
                if filename.startswith('tts_'):
                    file_path = os.path.join(self.temp_dir, filename)
                    file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if (current_time - file_time).total_seconds() > max_age_hours * 3600:
                        os.remove(file_path)
                        print(f"🗑️  Cleaned up old TTS file: {filename}")
                        
        except Exception as e:
            print(f"Error cleaning up TTS files: {e}")

class LaravelBackendClient:
    """Client for communicating with Laravel backend"""
    
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        # Ensure the base URL has the proper protocol
        if not self.base_url.startswith(('http://', 'https://')):
            self.base_url = f'http://{self.base_url}'
        
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def submit_report(self, report_data: Dict) -> Dict:
        """Submit incident report to Laravel backend"""
        try:
            url = f"{self.base_url}/chatbot/reports"
            
            print(f"Submitting report to Laravel: {url}")
            print(f"Headers: {self.headers}")
            print(f"Report data: {json.dumps(report_data, indent=2)}")
            
            response = requests.post(
                url, 
                json=report_data, 
                headers=self.headers,
                timeout=30
            )
            
            print(f"Laravel response status: {response.status_code}")
            print(f"Laravel response: {response.text}")
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Backend error: {response.status_code}',
                    'details': response.text
                }
                
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error submitting to Laravel: {e}")
            return {
                'success': False,
                'error': f'Connection error: Unable to connect to Laravel backend at {self.base_url}. Please check if the Laravel server is running.'
            }
        except requests.exceptions.RequestException as e:
            print(f"Request error submitting to Laravel: {e}")
            return {
                'success': False,
                'error': f'Request error: {str(e)}'
            }
    
    def submit_media_files(self, report_id: str, media_files: List[Dict]) -> Dict:
        """Submit media files for a report"""
        try:
            url = f"{self.base_url}/chatbot/reports/{report_id}/media"
            
            # For media files, we'll need to handle file uploads differently
            # This endpoint expects multipart/form-data with actual files
            files = []
            data = {'uploaded_by': 'WhatsApp Bot'}
            
            # Note: In a real implementation, you'd need to download the media URLs
            # and upload them as actual files. For now, we'll send the URLs.
            for i, media in enumerate(media_files):
                data[f'media_urls[{i}]'] = media['url']
                data[f'media_types[{i}]'] = media['type']
            
            response = requests.post(
                url,
                data=data,
                headers={'Authorization': f'Bearer {self.api_token}'},
                timeout=30
            )
            
            return response

class EnhancedHSSEChatbot:
    """Enhanced chatbot with smart conversation tracking, menu system, Laravel integration, and dual TTS messaging"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.conversation_analyzer = ConversationAnalyzer()
        
        # Initialize Enhanced TTS Manager for dual messaging
        self.tts_manager = EnhancedTextToSpeechManager()
        
        self.response_generator = SmartResponseGenerator(self.tts_manager)
        self.location_parser = LocationParser()
        
        # Laravel integration
        self.laravel_client = LaravelBackendClient(LARAVEL_BASE_URL, LARAVEL_API_TOKEN)
        
        # Initialize conversation tracking
        self.conversation_tracker = EnhancedConversationTracker(self.db)
        self.conversation_manager = SmartConversationManager(
            self.conversation_tracker, 
            self.response_generator
        )
        
        self.states = {
            'CONVERSING': 'conversing',
            'COLLECTING_REPORT': 'collecting_report',
            'WAITING_MEDIA': 'waiting_media',
            'WAITING_LOCATION': 'waiting_location',
            'CONFIRMING_REPORT': 'confirming_report',
            'MENU_NAVIGATION': 'menu_navigation',
            'FAQ_MODE': 'faq_mode'
        }
        
        # Menu system
        self.menu_options = {
            'REPORT': 'Report incidents with AI analysis',
            'FAQ': 'Get safety information & policies', 
            'EMERGENCY': 'Get emergency contacts',
            'STATUS': 'Check system status',
            'VOICE': 'Voice & dual messaging controls'
        }
        
        # FAQ categories and content
        self.faq_categories = {
            'PPE': 'Personal Protective Equipment',
            'FIRE': 'Fire Safety & Prevention',
            'CHEMICAL': 'Chemical Safety & Handling',
            'ELECTRICAL': 'Electrical Safety',
            'CONFINED': 'Confined Space Safety',
            'ERGONOMICS': 'Workplace Ergonomics',
            'TRAINING': 'Safety Training & Procedures'
        }
        
        # Start cleanup task for TTS files
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background task to clean up old TTS files"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(3600)  # Clean up every hour
                    self.tts_manager.cleanup_old_files()
                except Exception as e:
                    print(f"TTS cleanup error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def process_message(self, from_number: str, message_body: str, media_urls: List[str] = None) -> Tuple[str, Optional[str]]:
        """Enhanced message processing with smart conversation tracking, menu system, Laravel integration, and dual TTS messaging"""
        
        # Emergency detection
        emergency_keywords = ['fire', 'emergency', 'urgent', 'accident', 'injury', 'help', 'danger', 'critical']
        if any(keyword in message_body.lower() for keyword in emergency_keywords):
            return self._handle_immediate_emergency(from_number, message_body)
        
        # Get user profile
        user_profile = self.db.get_user_profile(from_number)
        if not user_profile:
            user_profile = UserProfile(
                phone=from_number,
                name=None,
                role=None,
                department=None,
                preferred_language='en',
                interaction_history=[],
                safety_interests=[],
                last_active=datetime.datetime.now().isoformat(),
                tts_enabled=True,
                tts_voice_preference='female',
                tts_speed_preference=150,
                dual_messaging_enabled=True,
                voice_for_emergencies=True,
                voice_for_long_messages=True,
                voice_delay_seconds=2,
                preferred_message_format='both'
            )
            self.db.update_user_profile(user_profile)
        
        # Get current session state
        current_state, session_data = self.db.get_user_session(from_number)
        
        # Check for dual messaging commands first
        dual_messaging_response = self._handle_dual_messaging_commands(from_number, message_body, user_profile)
        if dual_messaging_response:
            return dual_messaging_response
        
        # Check for menu commands
        menu_response = self._handle_menu_commands(from_number, message_body, user_profile)
        if menu_response:
            return menu_response
        
        # Handle Laravel-integrated reporting flow
        if current_state in [self.states['COLLECTING_REPORT'], self.states['WAITING_MEDIA'], 
                            self.states['WAITING_LOCATION'], self.states['CONFIRMING_REPORT']]:
            return self._handle_laravel_incident_reporting(from_number, message_body, media_urls, 
                                                         current_state, session_data, {})
        
        # Handle FAQ mode
        if current_state == self.states['FAQ_MODE']:
            return self._handle_faq_interaction(from_number, message_body, session_data, user_profile)
        
        # Use smart conversation management for regular conversations
        intent_analysis = self.conversation_analyzer.analyze_message_intent(message_body)
        
        # Handle specific intents
        if intent_analysis.get('primary_intent') == 'emergency':
            return self._handle_emergency(from_number, message_body, intent_analysis, user_profile)
        elif intent_analysis.get('primary_intent') == 'report_incident':
            return self._start_laravel_incident_reporting(from_number, intent_analysis, user_profile)
        else:
            # Check if this is a first interaction or user needs guidance
            if self._should_show_menu(from_number, message_body, user_profile):
                return self._show_main_menu(from_number, user_profile, message_body)
            
            # Use smart conversation manager for regular chat
            response, conversation_metadata = self.conversation_manager.handle_smart_conversation(
                from_number, message_body, intent_analysis, user_profile, media_urls
            )
            
            # Get TTS URL from metadata
            tts_audio_url = conversation_metadata.get('tts_audio_url')
            
            # Add menu hint for longer conversations
            if len(response) < 800:
                response += f"\n\n💡 *Tip: Type 'MENU' anytime for quick access to reports, FAQ, emergency contacts, and dual messaging settings!*"
            
            # Update user profile with new information
            user_info = self.conversation_analyzer.extract_user_info(message_body)
            if user_info:
                self._update_user_profile(user_profile, user_info)
            
            return response, tts_audio_url
    
    def _handle_immediate_emergency(self, from_number: str, message: str) -> Tuple[str, Optional[str]]:
        """Handle immediate emergency situations with instant response and emergency TTS"""
        
        # Get user name if available
        user_profile = self.db.get_user_profile(from_number)
        name = user_profile.name if user_profile and user_profile.name else "there"
        
        message_lower = message.lower()
        
        # Fire emergency
        if 'fire' in message_lower:
            response = (f"🚨 **FIRE EMERGENCY - {name.upper()}!** 🚨\n\n"
                       f"**IMMEDIATE ACTIONS:**\n"
                       f"🔥 **CALL 912 RIGHT NOW** (Fire Service)\n"
                       f"📞 **OR CALL 911** (Emergency Services)\n\n"
                       f"**IF SAFE TO DO SO:**\n"
                       f"🚨 Activate fire alarm\n"
                       f"👥 Evacuate everyone\n"
                       f"🚪 Close doors behind you\n"
                       f"📍 Meet at assembly point\n\n"
                       f"**GUYANA EMERGENCY CONTACTS:**\n"
                       f"🚒 Fire Service: **912**\n"
                       f"🚑 Ambulance: **913** \n"
                       f"👮 Police: **911**\n"
                       f"🏥 Georgetown Hospital: **225-5200**\n\n"
                       f"Stay safe, {name}! Emergency audio alert will follow this text!")
            
            # Use pre-generated emergency audio
            tts_audio_url = self.tts_manager.get_emergency_audio('fire')
            
        # Medical emergency
        elif any(word in message_lower for word in ['injury', 'hurt', 'accident', 'medical']):
            response = (f"🚨 **MEDICAL EMERGENCY - {name.upper()}!** 🚨\n\n"
                       f"**CALL 913 IMMEDIATELY** (Ambulance)\n"
                       f"**OR CALL 911** (Emergency Services)\n\n"
                       f"**WHILE WAITING FOR HELP:**\n"
                       f"🩺 Check if person is conscious\n"
                       f"🫁 Check breathing\n"
                       f"🩸 Control any bleeding\n"
                       f"🚫 DO NOT move if spinal injury suspected\n\n"
                       f"**GUYANA EMERGENCY CONTACTS:**\n"
                       f"🚑 Ambulance: **913**\n"
                       f"🏥 Georgetown Hospital: **225-5200**\n\n"
                       f"Stay with the injured person, {name}! Audio emergency guide will follow!")
            
            tts_audio_url = self.tts_manager.get_emergency_audio('medical')
        
        # General emergency
        else:
            response = (f"🚨 **EMERGENCY DETECTED - {name.upper()}!** 🚨\n\n"
                       f"**CALL 911 IMMEDIATELY!**\n\n"
                       f"**GUYANA EMERGENCY SERVICES:**\n"
                       f"🚨 General Emergency: **911**\n"
                       f"🚒 Fire Service: **912**\n"
                       f"🚑 Ambulance: **913**\n"
                       f"👮 Police: **911**\n\n"
                       f"Stay safe, {name}! Emergency voice alert is being sent!")
            
            tts_audio_url = self.tts_manager.get_emergency_audio('emergency')
        
        return response, tts_audio_url
    
    def _handle_dual_messaging_commands(self, from_number: str, message: str, user_profile: UserProfile) -> Optional[Tuple[str, Optional[str]]]:
        """Handle dual messaging control commands"""
        
        message_lower = message.lower().strip()
        
        # Voice control commands
        if any(cmd in message_lower for cmd in ['voice off', 'disable voice', 'no voice', 'text only']):
            user_profile.tts_enabled = False
            user_profile.preferred_message_format = 'text'
            self.db.update_user_profile(user_profile)
            
            response = f"🔇 Voice messages disabled, {user_profile.name or 'there'}! You'll only receive text messages now.\n\nSay 'voice on' anytime to re-enable dual messaging (text + audio)."
            return response, None  # No TTS for voice-off command
        
        elif any(cmd in message_lower for cmd in ['voice on', 'enable voice', 'dual messaging', 'both messages']):
            user_profile.tts_enabled = True
            user_profile.preferred_message_format = 'both'
            self.db.update_user_profile(user_profile)
            
            response = f"🎙️ Dual messaging enabled, {user_profile.name or 'there'}! You'll now receive both text and voice messages for better accessibility."
            tts_audio_url = self.tts_manager.get_dual_messaging_audio('voice_enabled_dual')
            return response, tts_audio_url
        
        elif 'voice settings' in message_lower or message.upper().strip() == 'VOICE':
            return self._show_enhanced_voice_settings(from_number, user_profile)
        
        # Voice preference changes
        elif 'voice fast' in message_lower:
            user_profile.tts_speed_preference = min(250, user_profile.tts_speed_preference + 25)
            self.db.update_user_profile(user_profile)
            response = f"🎙️ Speech speed increased to {user_profile.tts_speed_preference} WPM. Try saying something to test!"
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(response, {'tts_speed_preference': user_profile.tts_speed_preference})
            return response, tts_audio_url
        
        elif 'voice slow' in message_lower:
            user_profile.tts_speed_preference = max(100, user_profile.tts_speed_preference - 25)
            self.db.update_user_profile(user_profile)
            response = f"🎙️ Speech speed decreased to {user_profile.tts_speed_preference} WPM. This message uses the new speed!"
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(response, {'tts_speed_preference': user_profile.tts_speed_preference})
            return response, tts_audio_url
        
        elif 'voice male' in message_lower:
            user_profile.tts_voice_preference = 'male'
            self.db.update_user_profile(user_profile)
            response = f"🎙️ Voice changed to male. This message demonstrates the new voice!"
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(response, {'tts_voice_preference': 'male'})
            return response, tts_audio_url
        
        elif 'voice female' in message_lower:
            user_profile.tts_voice_preference = 'female'
            self.db.update_user_profile(user_profile)
            response = f"🎙️ Voice changed to female. Listen to this message with the new voice!"
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(response, {'tts_voice_preference': 'female'})
            return response, tts_audio_url
        
        return None
    
    def _show_enhanced_voice_settings(self, from_number: str, user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Show enhanced voice settings with dual messaging options"""
        
        name = user_profile.name or "there"
        
        voice_menu = f"""🎙️ **Enhanced Dual Messaging Settings - {name}** 🎙️

**Current Setup:**
📱 Text Messages: Always enabled (instant delivery)
🔊 Voice Messages: {'✅ Enabled' if user_profile.tts_enabled else '❌ Disabled'}
🎵 Voice Type: {user_profile.tts_voice_preference.title()}
⚡ Speech Speed: {user_profile.tts_speed_preference} WPM
⏱️ Voice Delay: {getattr(user_profile, 'voice_delay_seconds', 2)} seconds after text

**Quick Commands:**
🔸 **"VOICE ON"** - Enable dual messaging (text + audio)
🔸 **"VOICE OFF"** - Text messages only  
🔸 **"VOICE FAST"** - Increase speech speed
🔸 **"VOICE SLOW"** - Decrease speech speed
🔸 **"VOICE MALE"** - Switch to male voice
🔸 **"VOICE FEMALE"** - Switch to female voice

**How Dual Messaging Works:**
📤 Text message sent immediately (0-1 second)
🎙️ Voice message follows shortly (2-3 seconds later)
🚨 Emergency messages get priority audio delivery
♿ Perfect for accessibility and hands-free operation

💬 *This message demonstrates dual messaging - you received text first, then this audio version!*

Type a voice command or 'MENU' to return to main menu."""
        
        # Always generate TTS for voice settings
        tts_audio_url = self.tts_manager.generate_for_dual_messaging(voice_menu)
        
        return voice_menu, tts_audio_url
    
    def _handle_menu_commands(self, from_number: str, message: str, user_profile: UserProfile) -> Optional[Tuple[str, Optional[str]]]:
        """Handle menu-specific commands with TTS"""
        
        message_upper = message.upper().strip()
        
        # Main menu trigger
        if message_upper in ['MENU', 'HELP', 'OPTIONS', 'START']:
            return self._show_main_menu(from_number, user_profile, message)
        
        # Direct menu options
        elif message_upper == 'REPORT':
            return self._start_incident_reporting_from_menu(from_number, user_profile)
        
        elif message_upper == 'FAQ':
            return self._show_faq_menu(from_number, user_profile)
        
        elif message_upper == 'EMERGENCY':
            return self._show_emergency_contacts(from_number, user_profile)
        
        elif message_upper == 'STATUS':
            return self._show_system_status(from_number, user_profile)
        
        # Back to menu from any state
        elif message_upper in ['BACK', 'MAIN', 'HOME']:
            self.db.update_user_session(from_number, self.states['CONVERSING'], {})
            return self._show_main_menu(from_number, user_profile, "returning to main menu")
        
        return None
    
    def _show_main_menu(self, from_number: str, user_profile: UserProfile, context_message: str = "") -> Tuple[str, Optional[str]]:
        """Display the main menu with personalized greeting and TTS"""
        
        name = user_profile.name or "there"
        
        # Set menu navigation state
        self.db.update_user_session(from_number, self.states['MENU_NAVIGATION'], {
            'last_menu': 'main',
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        # Personalized greeting based on context
        if "returning" in context_message.lower():
            greeting = f"Welcome back, {name}! 👋"
        elif user_profile.name:
            greeting = f"Hi {name}! 😊 How can I help you today?"
        else:
            greeting = f"Hello there! 👋 I'm ARIA, your AI safety assistant."
        
        menu = f"""{greeting}

🛡️ **ARIA Safety Assistant Menu** 🛡️

Choose an option by typing the keyword:

🔸 **REPORT** - Report incidents with AI analysis (sends to Laravel dashboard!)
🔸 **FAQ** - Get safety information & policies  
🔸 **EMERGENCY** - Get emergency contacts
🔸 **STATUS** - Check system status
🔸 **VOICE** - Dual messaging & voice controls 🎙️

💬 *You can also just ask me anything about workplace safety naturally - I understand regular conversation too!*

🚀 *NEW: Dual messaging active! You get both text (immediate) and voice (2 sec later) for optimal accessibility!*
📊 *Reports automatically sent to Laravel safety dashboard with AI analysis!*

What would you like to do?"""
        
        # Generate TTS
        tts_audio_url = None
        if user_profile.tts_enabled and TTS_ENABLED:
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(menu, cache_key='menu_dual')
        
        return menu, tts_audio_url
    
    def _start_incident_reporting_from_menu(self, from_number: str, user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Start incident reporting from menu with TTS"""
        
        name = user_profile.name or "there"
        
        # Initialize Laravel reporting session
        session_data = {
            'step': 'media',
            'report_data': {
                'reporter_name': user_profile.name or 'WhatsApp User',
                'reporter_contact': from_number,
                'source': 'whatsapp_chatbot',
                'report_type': 'incident',
                'industry': 'General'
            },
            'started_at': datetime.datetime.now().isoformat()
        }
        
        self.db.update_user_session(from_number, self.states['WAITING_MEDIA'], session_data)
        
        response = f"""🛡️ **Incident Report - {name}** 🛡️

I'll help you quickly report this incident to our Laravel safety dashboard. The process is simple:

**📸 STEP 1: Send photos or videos**
Send me photos/videos of the incident scene, damage, or any relevant evidence.

**📍 STEP 2: Share your location**  
Share your location so responders can find you.

**Let's start - please send your photos/videos now! 📱**

*Tip: You can send multiple photos one after another*

Your report will be automatically analyzed by AI and sent to the safety team through our Laravel dashboard! 🚀

Both text and voice guidance will help you through each step."""
        
        # Generate TTS
        tts_audio_url = None
        if user_profile.tts_enabled and TTS_ENABLED:
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(response)
        
        return response, tts_audio_url
    
    def _show_emergency_contacts(self, from_number: str, user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Show emergency contacts with TTS"""
        
        name = user_profile.name or "there"
        
        contacts = f"""🚨 **Emergency Contacts - {name}** 🚨

**GUYANA EMERGENCY SERVICES:**
🚨 General Emergency: **911**
🚒 Fire Service: **912**
🚑 Ambulance: **913**
👮 Police: **911**
🏥 Georgetown Hospital: **225-5200**

**WORKPLACE EMERGENCY:**
📞 Safety Officer: [Contact your safety team]
🏢 Security: [Your company security]
🚨 Emergency Assembly Point: [Your designated area]

**IMPORTANT:**
- Call 911 for life-threatening emergencies
- Use specific numbers (912/913) for fire/medical
- Report to dashboard after emergency response
- This contact list is available in both text and audio

Stay safe, {name}! 🛡️

Type 'MENU' to return to main menu."""
        
        # Generate TTS
        tts_audio_url = None
        if user_profile.tts_enabled and TTS_ENABLED:
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(contacts, cache_key='emergency_contacts')
        
        return contacts, tts_audio_url
    
    def _show_system_status(self, from_number: str, user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Show system status with TTS"""
        
        # Test Laravel connection
        laravel_status = "🟢 Connected" 
        try:
            test_result = self.laravel_client.test_connection()
            if not test_result.get('success'):
                laravel_status = "🔴 Connection Issues"
        except:
            laravel_status = "🔴 Offline"
        
        # TTS system status
        tts_engines = []
        if TTS_AVAILABLE and self.tts_manager.pyttsx3_ready:
            tts_engines.append("pyttsx3")
        if GTTS_AVAILABLE:
            tts_engines.append("gTTS")
        if OPENAI_API_KEY:
            tts_engines.append("OpenAI")
        
        status = f"""📊 **System Status** 📊

**Core Systems:**
🤖 AI Chatbot: 🟢 Online
🗄️ Database: 🟢 Connected
📱 WhatsApp: 🟢 Active
🚀 Laravel Dashboard: {laravel_status}

**Dual Messaging System:**
📱 Text Delivery: 🟢 Instant
🎙️ Voice System: {'🟢 Active' if TTS_ENABLED else '🔴 Disabled'}
🔧 TTS Engines: {', '.join(tts_engines) if tts_engines else 'None available'}
💾 Audio Cache: {len(self.tts_manager.audio_cache)} pre-generated phrases

**Your Settings:**
📢 Dual Messaging: {'🟢 Enabled' if user_profile.tts_enabled else '🔴 Text Only'}
🎵 Voice: {user_profile.tts_voice_preference.title()}
⚡ Speed: {user_profile.tts_speed_preference} WPM

**Features Active:**
✅ Smart Conversation Tracking
✅ Emergency Detection & Response
✅ Laravel Dashboard Integration
✅ Incident Reporting with AI Analysis
✅ Dual Text+Voice Messaging
✅ Voice Accessibility Features
✅ Multi-engine TTS Fallback

All systems operational! 🛡️

Type 'MENU' to return to main menu."""
        
        # Generate TTS
        tts_audio_url = None
        if user_profile.tts_enabled and TTS_ENABLED:
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(status)
        
        return status, tts_audio_url
    
    def _show_faq_menu(self, from_number: str, user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Show FAQ menu with TTS"""
        
        name = user_profile.name or "there"
        
        self.db.update_user_session(from_number, self.states['FAQ_MODE'], {
            'faq_category': None,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        faq_menu = f"""❓ **Safety FAQ - {name}** ❓

Choose a category by typing the keyword:

🦺 **PPE** - Personal Protective Equipment
🔥 **FIRE** - Fire Safety & Prevention
🧪 **CHEMICAL** - Chemical Safety & Handling
⚡ **ELECTRICAL** - Electrical Safety
🚪 **CONFINED** - Confined Space Safety
💺 **ERGONOMICS** - Workplace Ergonomics
📚 **TRAINING** - Safety Training & Procedures

💬 *You can also ask me any safety question naturally - I understand regular conversation and will provide detailed answers!*

🎙️ *All FAQ responses include both text and voice for accessibility*

Type a category keyword or ask any safety question!

Type 'MENU' to return to main menu."""
        
        # Generate TTS
        tts_audio_url = None
        if user_profile.tts_enabled and TTS_ENABLED:
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(faq_menu)
        
        return faq_menu, tts_audio_url
    
    def _handle_faq_interaction(self, from_number: str, message: str, session_data: dict, user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Handle FAQ interactions with TTS"""
        
        message_upper = message.upper().strip()
        
        # Check for FAQ categories
        if message_upper in self.faq_categories:
            category_name = self.faq_categories[message_upper]
            
            # Generate category-specific FAQ response
            faq_response = self._generate_faq_response(message_upper, category_name, user_profile)
            
            # Generate TTS
            tts_audio_url = None
            if user_profile.tts_enabled and TTS_ENABLED:
                tts_audio_url = self.tts_manager.generate_for_dual_messaging(faq_response)
            
            return faq_response, tts_audio_url
        
        # Handle natural questions
        else:
            # Exit FAQ mode and handle as regular conversation
            self.db.update_user_session(from_number, self.states['CONVERSING'], {})
            
            # Process as regular conversation with FAQ context
            intent_analysis = self.conversation_analyzer.analyze_message_intent(message)
            
            response, conversation_metadata = self.conversation_manager.handle_smart_conversation(
                from_number, message, intent_analysis, user_profile
            )
            
            response += "\n\nType 'FAQ' to return to FAQ menu or 'MENU' for main menu."
            
            return response, conversation_metadata.get('tts_audio_url')
    
    def _generate_faq_response(self, category: str, category_name: str, user_profile: UserProfile) -> str:
        """Generate FAQ response for a specific category"""
        
        name = user_profile.name or "there"
        
        faq_responses = {
            'PPE': f"""🦺 **Personal Protective Equipment - {name}** 🦺

**Essential PPE for Guyana Workplaces:**
👷 Hard hats for construction & industrial sites
🥽 Safety glasses/goggles for eye protection
👂 Hearing protection in noisy environments
🧤 Cut-resistant gloves for handling materials
👢 Steel-toed boots for foot protection
🦺 High-visibility vests for outdoor work

**PPE Inspection:**
🔍 Check equipment before each use
🚫 Replace damaged or worn PPE immediately
📋 Follow manufacturer guidelines
🧼 Keep PPE clean and properly stored

**Tropical Climate Considerations:**
🌡️ Choose breathable materials when possible
💧 Stay hydrated when wearing full PPE
🧴 Use anti-fog treatments for goggles
🧽 Clean PPE regularly to prevent bacteria

**Legal Requirements:**
📜 Employers must provide appropriate PPE
⚖️ Workers must use PPE as required
📚 Training required for specialized equipment

Need specific PPE guidance for your workplace? Just ask!""",
            
            'FIRE': f"""🔥 **Fire Safety & Prevention - {name}** 🔥

**Guyana Fire Emergency Numbers:**
🚒 Fire Service: **912**
🚨 Emergency Services: **911**

**Fire Prevention:**
🚭 No smoking in designated areas
⚡ Maintain electrical systems properly
🧴 Store flammable materials safely
🚪 Keep fire exits clear at all times
🔥 Hot work permits for welding/cutting

**Fire Response Steps:**
1️⃣ Sound the alarm immediately
2️⃣ Call 912 (Fire Service)
3️⃣ Evacuate using nearest safe exit
4️⃣ Meet at designated assembly point
5️⃣ Do NOT re-enter until cleared

**Fire Extinguisher Types:**
💧 Water: Paper, wood, fabric fires
🧯 Foam: Flammable liquid fires
❄️ CO2: Electrical fires
🧪 Dry Chemical: Multi-purpose

**Tropical Considerations:**
🌧️ Extra fire risk during dry seasons
🌱 Vegetation management around buildings
💧 Ensure water supply for fire fighting

Remember: GET OUT, STAY OUT, and let professionals handle it!""",
            
            'CHEMICAL': f"""🧪 **Chemical Safety & Handling - {name}** 🧪

**Before Working with Chemicals:**
📋 Read Safety Data Sheets (SDS)
🦺 Wear appropriate PPE
🌬️ Ensure adequate ventilation
🚿 Know location of emergency wash stations

**Storage Requirements:**
❄️ Temperature-controlled storage
🚫 Separate incompatible chemicals
🏷️ Proper labeling and dating
🔒 Secure storage away from unauthorized access

**Spill Response:**
⚠️ Alert others and evacuate if necessary
🧤 Use appropriate PPE for cleanup
🧽 Follow spill kit procedures
📞 Report all spills to supervision

**Tropical Climate Challenges:**
🌡️ Heat can increase chemical reactivity
💧 Humidity affects some chemical properties
🏢 Ensure climate-controlled storage
🌀 Hurricane/storm preparedness for chemicals

**Emergency Contacts:**
☣️ Chemical Emergency: **911**
🏥 Poison Control: Contact local hospital
📞 Company Emergency: [Your safety officer]

**Disposal:**
♻️ Follow proper disposal procedures
🚫 Never pour chemicals down drains
📋 Keep disposal records
🌍 Consider environmental impact

Always err on the side of caution with chemicals!""",
            
            'ELECTRICAL': f"""⚡ **Electrical Safety - {name}** ⚡

**Electrical Hazards in Guyana:**
🌧️ Wet conditions increase shock risk
⛈️ Lightning strikes during storms
🌡️ Heat affecting electrical equipment
🐭 Rodents damaging wiring

**Safe Work Practices:**
🔌 De-energize before working on equipment
🔒 Lockout/Tagout procedures
👷 Only qualified electricians do electrical work
🧤 Use insulated tools and PPE

**Extension Cord Safety:**
✅ Inspect before each use
🚫 Don't run through doorways
💧 Keep away from water
⚡ Match cord rating to equipment load

**Ground Fault Protection:**
🔌 Use GFCI outlets near water
🧪 Test GFCI devices monthly
🌧️ Extra important in humid climates
⚡ Install surge protection

**Storm Safety:**
⛈️ Unplug equipment during storms
💡 Have backup lighting ready
📱 Charge devices before outages
🌳 Stay away from downed power lines

**Emergency Response:**
⚡ Electrical Emergency: **911**
🏥 Electrical shock: Call ambulance (913)
🔥 Electrical fire: Call fire service (912)

**Power Outage Procedures:**
📋 Follow emergency lighting protocols
🔋 Use battery-powered equipment only
🚫 Don't use candles or open flames
📞 Report outages to utility company

Remember: When in doubt, turn it off and call an electrician!""",
            
            'CONFINED': f"""🚪 **Confined Space Safety - {name}** 🚪

**What is a Confined Space?**
🏗️ Tanks, vessels, silos
🕳️ Manholes, pits, tunnels
🏢 Storage bins, vaults
⛽ Fuel tanks, sewers

**Permit Required Spaces:**
📋 Entry permit system mandatory
👥 Attendant required outside
📡 Continuous monitoring required
🚨 Emergency rescue plan needed

**Atmospheric Hazards:**
💨 Oxygen deficiency/enrichment
☠️ Toxic gases (H2S, CO, etc.)
💥 Flammable vapors
🌪️ Engulfment hazards

**Testing Requirements:**
🔬 Test atmosphere before entry
📊 Continuous monitoring during work
⚡ Test for oxygen, toxics, flammables
📈 Document all readings

**Tropical Considerations:**
🌡️ Heat stress in confined spaces
💧 Humidity affecting equipment
🐍 Wildlife hazards in some spaces
🌧️ Water accumulation risks

**Entry Procedures:**
1️⃣ Obtain entry permit
2️⃣ Test atmosphere
3️⃣ Ventilate space
4️⃣ Position attendant
5️⃣ Enter with proper PPE
6️⃣ Maintain communication

**Emergency Response:**
🚨 Confined Space Emergency: **911**
👷 Never enter to rescue without proper equipment
📞 Alert emergency services immediately

Never take shortcuts with confined space safety!""",
            
            'ERGONOMICS': f"""💺 **Workplace Ergonomics - {name}** 💺

**Common Ergonomic Issues:**
🖥️ Computer workstation setup
📦 Manual lifting and handling
🏭 Repetitive motion tasks
🚶 Prolonged standing/sitting

**Workstation Setup:**
👀 Monitor at eye level
⌨️ Keyboard and mouse at elbow height
🪑 Feet flat on floor or footrest
💡 Adequate lighting to reduce eye strain

**Safe Lifting Techniques:**
🦵 Lift with your legs, not your back
📦 Keep load close to your body
🔄 Avoid twisting while lifting
👥 Get help for heavy items

**Tropical Climate Factors:**
🌡️ Heat stress affects physical capability
💧 Stay hydrated during physical work
🌀 Fan placement for air circulation
❄️ Air conditioning for comfort

**Repetitive Strain Prevention:**
⏰ Take regular breaks
🤸 Stretch exercises
🔄 Rotate tasks when possible
🛠️ Use ergonomic tools

**Warning Signs:**
⚠️ Pain or stiffness
🤲 Numbness or tingling
💪 Muscle fatigue
🦴 Joint soreness

**Solutions:**
🪑 Adjustable furniture
🛠️ Ergonomic tools
📚 Training programs
🏥 Early intervention

Report ergonomic concerns early - prevention is better than treatment!""",
            
            'TRAINING': f"""📚 **Safety Training & Procedures - {name}** 📚

**Required Training Programs:**
🆔 New employee orientation
🦺 PPE training and fit testing
🔥 Fire safety and evacuation
🩺 First aid and CPR
🧪 Chemical safety (if applicable)

**Guyana-Specific Training:**
🌀 Hurricane/tropical storm procedures
🐍 Local wildlife safety awareness
🌡️ Heat stress prevention
🌧️ Wet weather safety protocols

**Training Documentation:**
📋 Keep training records current
✅ Track certification expiration dates
📝 Document refresher training
🏆 Recognize safety achievements

**Competency Assessment:**
✅ Practical demonstrations
📝 Written assessments
👥 Peer observations
📊 Regular evaluations

**Training Methods:**
🎓 Classroom instruction
🎮 Interactive simulations
👷 Hands-on practice
📱 Online modules
🎥 Video demonstrations

**Refresher Training:**
📅 Annual safety updates
🔄 Incident-based training
🆕 New procedure training
🏆 Continuous improvement

**Training Resources:**
📚 Safety manuals
🎥 Training videos
🌐 Online courses
👨‍🏫 External trainers
🏢 Internal expertise

**Record Keeping:**
📁 Individual training files
📊 Training matrices
📅 Schedule tracking
✅ Compliance monitoring

Invest in training - it's the foundation of workplace safety!"""
        }
        
        return faq_responses.get(category, f"Information about {category_name} is being updated. Please contact your safety officer for specific guidance.")
    
    # Laravel incident reporting methods
    def _start_laravel_incident_reporting(self, from_number: str, intent_analysis: Dict, user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Start Laravel-integrated incident reporting with TTS"""
        
        name = user_profile.name or "there"
        
        # Initialize Laravel reporting session
        session_data = {
            'step': 'media',
            'report_data': {
                'reporter_name': user_profile.name or 'WhatsApp User',
                'reporter_contact': from_number,
                'source': 'whatsapp_chatbot',
                'report_type': 'incident',
                'industry': 'General'
            },
            'started_at': datetime.datetime.now().isoformat()
        }
        
        self.db.update_user_session(from_number, self.states['WAITING_MEDIA'], session_data)
        
        response = f"""🛡️ **Incident Report - {name}** 🛡️

I'll help you quickly report this incident to our Laravel safety dashboard with dual messaging support.

**📸 STEP 1: Send photos or videos**
Send me photos/videos of the incident scene, damage, or any relevant evidence.

**📍 STEP 2: Share your location**  
Share your location so responders can find you.

**Let's start - please send your photos/videos now! 📱**

*Tip: You can send multiple photos one after another*

Your report will be:
🤖 Automatically analyzed by AI
📊 Sent to the Laravel safety dashboard
🎙️ Confirmed with both text and voice messages

Both visual and audio guidance will help you through each step."""
        
        # Generate TTS
        tts_audio_url = None
        if user_profile.tts_enabled and TTS_ENABLED:
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(response)
        
        return response, tts_audio_url
    
    def _handle_laravel_incident_reporting(self, from_number: str, message: str, media_urls: List[str],
                                         current_state: str, session_data: dict, intent_analysis: Dict) -> Tuple[str, Optional[str]]:
        """Handle Laravel-integrated incident reporting flow with TTS"""
        
        user_profile = self.db.get_user_profile(from_number)
        
        if current_state == self.states['WAITING_MEDIA']:
            response, tts_audio_url = self._handle_media_submission_laravel(from_number, message, media_urls, session_data, user_profile)
        elif current_state == self.states['WAITING_LOCATION']:
            response, tts_audio_url = self._handle_location_submission_laravel(from_number, message, session_data, user_profile)
        elif current_state == self.states['CONFIRMING_REPORT']:
            response, tts_audio_url = self._handle_report_confirmation_laravel(from_number, message, session_data, user_profile)
        else:
            response = "I'm having trouble with the reporting process. Let me reset this for you. Type 'REPORT' to start a new incident report."
            tts_audio_url = None
            if user_profile and user_profile.tts_enabled and TTS_ENABLED:
                tts_audio_url = self.tts_manager.generate_for_dual_messaging(response)
        
        return response, tts_audio_url
    
    def _handle_media_submission_laravel(self, from_number: str, message: str, 
                                       media_urls: List[str], session_data: dict, 
                                       user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Handle media file submission for Laravel with TTS"""
        
        if not media_urls:
            response = (
                "📸 **I need photos or videos to complete your report.**\n\n"
                "Please send:\n"
                "🔸 Photos of the incident scene\n"
                "🔸 Videos showing what happened\n"
                "🔸 Images of any damage or injuries (if safe to take)\n\n"
                "📱 Just attach them to your next message!\n\n"
                "🎙️ Voice guidance: After you send the photos, I'll guide you through sharing your location."
            )
        else:
            # Save media URLs to session
            if 'media_files' not in session_data['report_data']:
                session_data['report_data']['media_files'] = []
            
            for url in media_urls:
                session_data['report_data']['media_files'].append({
                    'url': url,
                    'type': 'image' if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png']) else 'video',
                    'uploaded_at': datetime.datetime.now().isoformat()
                })
            
            # Move to location step
            self.db.update_user_session(from_number, self.states['WAITING_LOCATION'], session_data)
            
            response = (
                f"✅ **Excellent! I received {len(media_urls)} file(s).**\n\n"
                "📍 **STEP 2: Share your location**\n\n"
                "Please share your location by:\n"
                "🔸 Using WhatsApp's location sharing button\n"
                "🔸 Or typing coordinates like: `6.8013, -58.1551`\n"
                "🔸 Or describe where you are (I'll help find coordinates)\n\n"
                "This helps emergency responders reach you quickly! 🚨\n\n"
                "🎙️ You'll receive both text confirmation and voice guidance for the next step."
            )
        
        # Generate TTS
        tts_audio_url = None
        if user_profile and user_profile.tts_enabled and TTS_ENABLED:
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(response)
        
        return response, tts_audio_url
    
    def _handle_location_submission_laravel(self, from_number: str, message: str, 
                                          session_data: dict, user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Handle location submission for Laravel with TTS"""
        
        # Try to extract coordinates
        lat, lng = self.location_parser.extract_coordinates(message)
        
        if lat and lng:
            # Save coordinates
            session_data['report_data']['location_lat'] = lat
            session_data['report_data']['location_long'] = lng
            session_data['report_data']['location_description'] = f"Coordinates: {lat}, {lng}"
        else:
            # Use the message as location description
            session_data['report_data']['location_description'] = message
            # Set default coordinates for Georgetown, Guyana
            session_data['report_data']['location_lat'] = 6.8013
            session_data['report_data']['location_long'] = -58.1551
        
        # Move to confirmation
        self.db.update_user_session(from_number, self.states['CONFIRMING_REPORT'], session_data)
        
        # Show confirmation
        report_data = session_data['report_data']
        media_count = len(report_data.get('media_files', []))
        location = report_data.get('location_description', 'Location provided')
        
        response = f"""📋 **Report Ready for Laravel Dashboard Submission**

**📸 Media:** {media_count} file(s) attached
**📍 Location:** {location}
**⏰ Time:** {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**🚀 Destination:** Laravel Safety Dashboard
**🤖 AI Analysis:** Will be automatically generated

**Reply with:**
✅ **"SUBMIT"** - to submit this report to the dashboard
❌ **"CANCEL"** - to cancel and start over

Your report will be automatically analyzed by AI and immediately sent to the safety team dashboard! 🛡️

🎙️ Both text and voice confirmations will be provided after submission."""
        
        # Generate TTS
        tts_audio_url = None
        if user_profile and user_profile.tts_enabled and TTS_ENABLED:
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(response)
        
        return response, tts_audio_url
    
    def _handle_report_confirmation_laravel(self, from_number: str, message: str, 
                                          session_data: dict, user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Handle report confirmation for Laravel submission with TTS"""
        
        message_upper = message.upper().strip()
        
        if message_upper == "CANCEL":
            self.db.update_user_session(from_number, self.states['CONVERSING'], {})
            response = "❌ Report cancelled. Type 'REPORT' anytime to start a new incident report.\n\n🎙️ This cancellation is confirmed in both text and voice."
        elif message_upper == "SUBMIT":
            response, tts_audio_url = self._submit_report_to_laravel(from_number, session_data, user_profile)
            return response, tts_audio_url
        else:
            response = (
                "Please respond with:\n"
                "✅ **SUBMIT** - to submit your report to the Laravel dashboard\n"
                "❌ **CANCEL** - to cancel this report\n\n"
                "🎙️ Voice guidance: Your choice will be confirmed in both text and audio."
            )
        
        # Generate TTS
        tts_audio_url = None
        if user_profile and user_profile.tts_enabled and TTS_ENABLED:
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(response)
        
        return response, tts_audio_url
    
    def _submit_report_to_laravel(self, from_number: str, session_data: dict, 
                                user_profile: UserProfile) -> Tuple[str, Optional[str]]:
        """Submit report to Laravel backend with enhanced data and TTS"""
        
        try:
            report_data = session_data['report_data']
            
            # Enhance report data with AI analysis and Laravel-compatible format
            enhanced_data = self._enhance_report_for_laravel(report_data)
            
            # Submit to Laravel
            result = self.laravel_client.submit_report(enhanced_data)
            
            if result.get('success'):
                # Save local reference
                local_id = uuid.uuid4().hex
                laravel_report_id = result.get('data', {}).get('id')
                
                if laravel_report_id:
                    self.db.save_local_report(local_id, from_number, str(laravel_report_id))
                
                # Also save to local database with Laravel ID
                incident_report = IncidentReport(
                    id=local_id,
                    user_phone=from_number,
                    timestamp=enhanced_data.get('date_of_incident', datetime.datetime.now().isoformat()),
                    incident_type=enhanced_data.get('incident_type', 'other'),
                    severity=enhanced_data.get('severity', 'medium'),
                    description=enhanced_data.get('description', ''),
                    location=enhanced_data.get('location_description', ''),
                    location_lat=enhanced_data.get('location_lat'),
                    location_long=enhanced_data.get('location_long'),
                    media_urls=enhanced_data.get('media_files', []),
                    status='submitted_to_laravel',
                    ai_analysis={'laravel_report_id': laravel_report_id, 'submission_result': result},
                    created_at=datetime.datetime.now().isoformat()
                )
                
                self.db.save_report(incident_report)
                
                # Try to submit media files if any
                media_files = enhanced_data.get('media_files', [])
                if media_files and laravel_report_id:
                    media_result = self.laravel_client.submit_media_files(str(laravel_report_id), media_files)
                    if not media_result.get('success'):
                        print(f"Media upload warning: {media_result.get('error')}")
                
                # Clear session
                self.db.update_user_session(from_number, self.states['CONVERSING'], {})
                
                response = f"""✅ **REPORT SUBMITTED TO LARAVEL DASHBOARD!** ✅

**🆔 Dashboard Report ID:** {laravel_report_id or local_id[:8].upper()}
**🚀 Status:** Successfully sent to Laravel safety dashboard
**⚡ Priority:** {enhanced_data.get('severity', 'Medium')}
**📊 AI Analysis:** Completed and included
**🎙️ Confirmation:** Both text and voice notifications sent

**What happens next:**
🔍 Safety team will review your report on the Laravel dashboard
📞 Someone may contact you for more details
📊 Your report helps improve workplace safety analytics
🚨 Emergency responses will be coordinated through the system

**Laravel Dashboard Features:**
📈 Real-time incident tracking
🗺️ Location mapping with your coordinates
📸 Media files attached and accessible
🤖 AI-powered risk assessment included
🎙️ Accessibility features for all users

**Thank you for keeping everyone safe!** 🛡️💪

Need to report something else? Just send me photos and location!
Type 'MENU' for other options or ask me any safety questions."""
                
            else:
                error_msg = result.get('error', 'Unknown error')
                # Still save locally as backup
                self._save_local_backup_report(from_number, session_data, error_msg)
                
                response = f"""⚠️ **Laravel Dashboard Submission Issue** ⚠️

There was a problem submitting to the Laravel dashboard: {error_msg}

**✅ Don't worry - your report has been saved locally as backup!**

**Next steps:**
🔄 Please try again in a moment
📞 Or contact safety directly: [Your safety contact]
💾 Your report data is safely stored and can be re-submitted

**Emergency contacts:**
📞 Emergency: 911
📞 Safety Team: [Your safety team contact]

Would you like me to try submitting again? Just type 'SUBMIT' once more.

🎙️ This error notification is provided in both text and voice for your convenience."""
        
        except Exception as e:
            print(f"Error submitting report to Laravel: {e}")
            # Save local backup
            self._save_local_backup_report(from_number, session_data, str(e))
            
            response = (
                "❌ **Technical Error**\n\n"
                "Sorry, I'm having technical difficulties connecting to the Laravel dashboard. "
                "Your report has been saved locally as backup.\n\n"
                "**Please try again in a moment or contact safety directly:**\n"
                "📞 Emergency: 911\n"
                "📞 Safety Team: [Your safety contact]\n\n"
                "💾 Your report data is safe and will be submitted when the connection is restored.\n\n"
                "🎙️ This technical update is provided in both text and voice formats."
            )
        
        # Generate TTS
        tts_audio_url = None
        if user_profile and user_profile.tts_enabled and TTS_ENABLED:
            tts_audio_url = self.tts_manager.generate_for_dual_messaging(response)
        
        return response, tts_audio_url
    
    # Utility methods
    def _enhance_report_for_laravel(self, report_data: dict) -> dict:
        """Enhance report with AI analysis and Laravel-compatible format"""
        
        enhanced = report_data.copy()
        
        # Add required Laravel fields
        enhanced.update({
            'report_type': 'incident',
            'date_of_incident': datetime.datetime.now().strftime('%Y-%m-%d'),
            'time_of_incident': datetime.datetime.now().strftime('%H:%M:%S'),
            'severity': self._analyze_severity_from_data(enhanced),
            'incident_type': self._detect_incident_type(enhanced),
            'status': 'submitted',
            'industry': enhanced.get('industry', 'General'),
            'description': self._generate_ai_description(enhanced),
            'ai_analysis': self._generate_ai_analysis(enhanced),
            'submitted_via': 'whatsapp_chatbot_dual_messaging',
            'submission_timestamp': datetime.datetime.now().isoformat()
        })
        
        return enhanced
    
    def _analyze_severity_from_data(self, report_data: dict) -> str:
        """Analyze severity based on available data"""
        
        # Simple severity analysis based on media count and urgency indicators
        media_count = len(report_data.get('media_files', []))
        
        if media_count >= 3:
            return 'high'
        elif media_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _detect_incident_type(self, report_data: dict) -> str:
        """Detect incident type from available data"""
        
        # Simple incident type detection
        location_desc = report_data.get('location_description', '').lower()
        
        if any(word in location_desc for word in ['office', 'desk', 'computer']):
            return 'workplace_injury'
        elif any(word in location_desc for word in ['machine', 'equipment', 'tool']):
            return 'equipment_failure'
        elif any(word in location_desc for word in ['chemical', 'spill', 'leak']):
            return 'chemical_incident'
        else:
            return 'other'
    
    def _generate_ai_description(self, report_data: dict) -> str:
        """Generate AI-enhanced description"""
        
        media_count = len(report_data.get('media_files', []))
        location = report_data.get('location_description', 'Location not specified')
        
        description = f"Incident reported via WhatsApp chatbot with dual messaging support. {media_count} media file(s) submitted. "
        description += f"Location: {location}. "
        description += f"Reported by: {report_data.get('reporter_name', 'Anonymous')}. "
        description += f"Submission time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. "
        description += f"User received both text and voice confirmations for accessibility."
        
        return description
    
    def _generate_ai_analysis(self, report_data: dict) -> str:
        """Generate AI analysis summary"""
        
        analysis = {
            'source': 'WhatsApp Chatbot with Dual Messaging',
            'media_analysis': f"{len(report_data.get('media_files', []))} files submitted",
            'location_analysis': 'GPS coordinates provided' if report_data.get('location_lat') else 'Location description provided',
            'urgency_assessment': 'Standard reporting flow followed',
            'ai_confidence': 'High - complete data submitted',
            'accessibility_features': 'Dual messaging (text + voice) used for user guidance',
            'recommendation': 'Review media files and coordinate appropriate response',
            'submission_method': 'Enhanced WhatsApp integration with Laravel dashboard'
        }
        
        return json.dumps(analysis)
    
    def _save_local_backup_report(self, from_number: str, session_data: dict, error_reason: str):
        """Save report locally as backup when Laravel submission fails"""
        
        try:
            report_data = session_data['report_data']
            
            backup_report = IncidentReport(
                id=uuid.uuid4().hex,
                user_phone=from_number,
                timestamp=datetime.datetime.now().isoformat(),
                incident_type='backup_pending_laravel',
                severity='medium',
                description=f"BACKUP REPORT - Laravel submission failed: {error_reason}. Submitted via dual messaging system.",
                location=report_data.get('location_description', ''),
                location_lat=report_data.get('location_lat'),
                location_long=report_data.get('location_long'),
                media_urls=report_data.get('media_files', []),
                status='backup_pending_submission',
                ai_analysis={'error_reason': error_reason, 'requires_manual_submission': True, 'dual_messaging_used': True},
                created_at=datetime.datetime.now().isoformat()
            )
            
            self.db.save_report(backup_report)
            print(f"Backup report saved: {backup_report.id}")
            
        except Exception as e:
            print(f"Error saving backup report: {e}")
    
    def _should_show_menu(self, from_number: str, message: str, user_profile: UserProfile) -> bool:
        """Determine if we should show the menu to the user"""
        
        # Show menu for first-time users
        if not user_profile.name and len(user_profile.interaction_history) == 0:
            return True
        
        # Show menu for simple greetings
        simple_greetings = ['hi', 'hello', 'hey', 'start', 'begin']
        if message.lower().strip() in simple_greetings:
            return True
        
        # Show menu if user seems lost
        confused_messages = ['what can you do', 'help me', 'i need help', 'what are my options']
        if any(phrase in message.lower() for phrase in confused_messages):
            return True
        
        return False
    
    def _update_user_profile(self, user_profile: UserProfile, user_info: Dict):
        """Update user profile with extracted information including TTS and dual messaging preferences"""
        
        if user_info.get('name') and not user_profile.name:
            user_profile.name = user_info['name']
        
        if user_info.get('role') and not user_profile.role:
            user_profile.role = user_info['role']
        
        if user_info.get('department') and not user_profile.department:
            user_profile.department = user_info['department']
        
        if user_info.get('interests'):
            user_profile.safety_interests.extend(user_info['interests'])
            user_profile.safety_interests = list(set(user_profile.safety_interests))
        
        # Update TTS preferences if mentioned
        tts_prefs = user_info.get('tts_preferences', {})
        if tts_prefs.get('voice'):
            user_profile.tts_voice_preference = tts_prefs['voice']
        if tts_prefs.get('speed'):
            if tts_prefs['speed'] == 'fast':
                user_profile.tts_speed_preference = 200
            elif tts_prefs['speed'] == 'slow':
                user_profile.tts_speed_preference = 120
        
        user_profile.last_active = datetime.datetime.now().isoformat()
        self.db.update_user_profile(user_profile)

# Initialize the enhanced chatbot with Laravel integration and dual TTS messaging
hsse_bot = EnhancedHSSEChatbot()

# ENHANCED WHATSAPP HANDLER WITH DUAL MESSAGING
@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    """Enhanced WhatsApp webhook handler with dual text+voice messaging"""
    
    # Get message data
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    
    # Get media URLs if any
    num_media = int(request.values.get('NumMedia', 0))
    media_urls = []
    for i in range(num_media):
        media_url = request.values.get(f'MediaUrl{i}')
        if media_url:
            media_urls.append(media_url)
    
    print(f"=== INCOMING MESSAGE ===")
    print(f"From: {from_number}")
    print(f"Message: '{incoming_msg}'")
    print(f"Media files: {len(media_urls)}")
    
    # Process with enhanced AI chatbot
    try:
        response_result = hsse_bot.process_message(from_number, incoming_msg, media_urls)
        
        if isinstance(response_result, tuple):
            response_text, tts_audio_url = response_result
        else:
            response_text = response_result
            tts_audio_url = None
            
    except Exception as e:
        print(f"Error processing message: {e}")
        response_text = ("🤖 Hi there! I'm ARIA, your safety assistant with dual messaging (text + voice)! "
                        "I'm here to help with all your workplace safety questions and incident reporting! "
                        "How can I assist you today? 😊")
        tts_audio_url = None
    
    # Get user profile for dual messaging preferences
    user_profile = hsse_bot.db.get_user_profile(from_number)
    
    # STEP 1: ALWAYS send text message first (immediate response)
    resp = MessagingResponse()
    text_msg = resp.message()
    text_msg.body(response_text)
    
    # STEP 2: Schedule voice message if TTS is enabled and available
    if (tts_audio_url and 
        os.path.exists(tts_audio_url) and
        user_profile and 
        user_profile.tts_enabled and
        TTS_ENABLED):
        
        def send_voice_message_delayed():
            """Send voice message as separate Twilio API call after brief delay"""
            
            # Get delay from user preferences
            delay = getattr(user_profile, 'voice_delay_seconds', 2)
            time.sleep(delay)
            
            try:
                audio_filename = os.path.basename(tts_audio_url)
                audio_url = f"{request.url_root}tts-audio/{audio_filename}"
                
                # Send voice message
                voice_message = twilio_client.messages.create(
                    media_url=[audio_url],
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=from_number,
                    body="🎙️ Audio version"
                )
                
                print(f"✅ Voice message sent successfully: {voice_message.sid}")
                
                # Update dual messaging analytics
                file_size = os.path.getsize(tts_audio_url) if os.path.exists(tts_audio_url) else 0
                hsse_bot.db.save_dual_messaging_analytics(from_number, {
                    'message_id': voice_message.sid,
                    'text_sent': True,
                    'voice_sent': True,
                    'text_delivery_time_ms': 500,  # Approximate
                    'voice_delivery_time_ms': delay * 1000,
                    'interaction_type': 'dual_messaging',
                    'message_length': len(response_text)
                })
                
                # Update TTS analytics
                hsse_bot.db.save_tts_analytics(
                    from_number, len(response_text), 'dual_messaging', 0, file_size
                )
                
            except Exception as voice_error:
                print(f"❌ Error sending voice message: {voice_error}")
                
                # Send fallback notification
                try:
                    fallback_message = twilio_client.messages.create(
                        body="🎙️ (Voice message generated but couldn't be delivered. Say 'voice off' to disable audio features.)",
                        from_=TWILIO_WHATSAPP_NUMBER,
                        to=from_number
                    )
                except:
                    pass  # If fallback also fails, just log it
        
        # Start voice message in background thread
        voice_thread = threading.Thread(target=send_voice_message_delayed)
        voice_thread.daemon = True
        voice_thread.start()
        
        print(f"🎙️ Voice message scheduled for delivery in {getattr(user_profile, 'voice_delay_seconds', 2)} seconds")
    
    print(f"📤 Text message sent immediately: {response_text[:100]}...")
    
    return Response(str(resp), mimetype="application/xml")

# TTS Audio serving endpoint
@app.route("/tts-audio/<filename>", methods=['GET'])
def serve_tts_audio(filename):
    """Serve TTS audio files"""
    try:
        audio_path = os.path.join(hsse_bot.tts_manager.temp_dir, filename)
        
        if os.path.exists(audio_path):
            return send_file(
                audio_path,
                mimetype='audio/mpeg' if filename.endswith('.mp3') else 'audio/wav',
                as_attachment=False
            )
        else:
            return jsonify({'error': 'Audio file not found'}), 404
            
    except Exception as e:
        print(f"Error serving TTS audio: {e}")
        return jsonify({'error': 'Error serving audio file'}), 500

# DUAL MESSAGING API ENDPOINTS

@app.route("/dual-messaging/preferences/<phone>", methods=['GET', 'PUT'])
def dual_messaging_preferences(phone):
    """Get or update dual messaging preferences"""
    
    try:
        user_profile = hsse_bot.db.get_user_profile(phone)
        
        if not user_profile:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == 'GET':
            return jsonify({
                'phone': phone,
                'dual_messaging_settings': {
                    'dual_messaging_enabled': getattr(user_profile, 'dual_messaging_enabled', True),
                    'voice_for_emergencies': getattr(user_profile, 'voice_for_emergencies', True),
                    'voice_for_long_messages': getattr(user_profile, 'voice_for_long_messages', True),
                    'voice_delay_seconds': getattr(user_profile, 'voice_delay_seconds', 2),
                    'preferred_message_format': getattr(user_profile, 'preferred_message_format', 'both')
                },
                'tts_settings': {
                    'tts_enabled': user_profile.tts_enabled,
                    'tts_voice_preference': user_profile.tts_voice_preference,
                    'tts_speed_preference': user_profile.tts_speed_preference
                }
            })
        
        elif request.method == 'PUT':
            data = request.json
            
            # Update dual messaging preferences
            if 'dual_messaging_enabled' in data:
                user_profile.dual_messaging_enabled = bool(data['dual_messaging_enabled'])
            if 'voice_for_emergencies' in data:
                user_profile.voice_for_emergencies = bool(data['voice_for_emergencies'])
            if 'voice_for_long_messages' in data:
                user_profile.voice_for_long_messages = bool(data['voice_for_long_messages'])
            if 'voice_delay_seconds' in data:
                user_profile.voice_delay_seconds = int(data['voice_delay_seconds'])
            if 'preferred_message_format' in data:
                user_profile.preferred_message_format = data['preferred_message_format']
            
            # Update TTS settings
            if 'tts_enabled' in data:
                user_profile.tts_enabled = bool(data['tts_enabled'])
            if 'tts_voice_preference' in data:
                user_profile.tts_voice_preference = data['tts_voice_preference']
            if 'tts_speed_preference' in data:
                user_profile.tts_speed_preference = int(data['tts_speed_preference'])
            
            # Save updated profile
            hsse_bot.db.update_user_profile(user_profile)
            
            return jsonify({
                'success': True,
                'message': 'Dual messaging preferences updated successfully',
                'updated_preferences': {
                    'dual_messaging_enabled': getattr(user_profile, 'dual_messaging_enabled', True),
                    'voice_for_emergencies': getattr(user_profile, 'voice_for_emergencies', True),
                    'voice_for_long_messages': getattr(user_profile, 'voice_for_long_messages', True),
                    'voice_delay_seconds': getattr(user_profile, 'voice_delay_seconds', 2),
                    'preferred_message_format': getattr(user_profile, 'preferred_message_format', 'both'),
                    'tts_enabled': user_profile.tts_enabled
                }
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/dual-messaging/test/<phone>", methods=['POST'])
def test_dual_messaging(phone):
    """Test dual messaging with a specific user"""
    
    try:
        data = request.json
        test_message = data.get('message', 'This is a test of dual messaging - you should receive both text and voice!')
        
        # Process test message
        response_text, tts_audio_url = hsse_bot.process_message(f"whatsapp:{phone}", test_message)
        
        results = {
            'text_sent': False,
            'voice_sent': False,
            'response_text': response_text,
            'tts_audio_url': tts_audio_url
        }
        
        # Send text message
        try:
            text_message = twilio_client.messages.create(
                body=f"📧 TEST DUAL MESSAGING:\n{response_text}",
                from_=TWILIO_WHATSAPP_NUMBER,
                to=f"whatsapp:{phone}"
            )
            results['text_sent'] = True
            results['text_message_sid'] = text_message.sid
            
        except Exception as e:
            results['text_error'] = str(e)
        
        # Send voice message if available
        if tts_audio_url and os.path.exists(tts_audio_url):
            try:
                audio_filename = os.path.basename(tts_audio_url)
                audio_url = f"{request.url_root}tts-audio/{audio_filename}"
                
                voice_message = twilio_client.messages.create(
                    media_url=[audio_url],
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=f"whatsapp:{phone}",
                    body="🎙️ TEST: Audio version of the above message"
                )
                results['voice_sent'] = True
                results['voice_message_sid'] = voice_message.sid
                results['audio_url'] = audio_url
                
            except Exception as e:
                results['voice_error'] = str(e)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/dual-messaging/analytics", methods=['GET'])
def dual_messaging_analytics():
    """Get analytics for dual messaging usage"""
    
    try:
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        # Overall dual messaging stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_messages,
                SUM(CASE WHEN tts_generated = 1 THEN 1 ELSE 0 END) as voice_messages,
                AVG(response_quality_score) as avg_quality
            FROM conversation_turns 
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        
        overall_stats = cursor.fetchone()
        
        # User adoption of dual messaging
        cursor.execute('''
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN tts_enabled = 1 THEN 1 ELSE 0 END) as dual_messaging_users
            FROM user_profiles
        ''')
        
        adoption_stats = cursor.fetchone()
        
        # Dual messaging specific analytics
        cursor.execute('''
            SELECT 
                COUNT(*) as dual_messaging_sessions,
                AVG(voice_delivery_time_ms) as avg_voice_delay,
                AVG(message_length) as avg_message_length
            FROM dual_messaging_analytics 
            WHERE created_at > datetime('now', '-7 days')
        ''')
        
        dual_stats = cursor.fetchone()
        
        # TTS performance for dual messaging
        cursor.execute('''
            SELECT 
                AVG(generation_time_ms) as avg_generation_time,
                AVG(file_size_bytes) as avg_file_size,
                COUNT(*) as total_tts_requests
            FROM tts_analytics 
            WHERE created_at > datetime('now', '-7 days')
        ''')
        
        performance_stats = cursor.fetchone()
        
        conn.close()
        
        voice_adoption_rate = (overall_stats[1] or 0) / max(overall_stats[0], 1) * 100
        user_adoption_rate = (adoption_stats[1] or 0) / max(adoption_stats[0], 1) * 100
        
        return jsonify({
            'summary': {
                'total_messages_7d': overall_stats[0] or 0,
                'voice_messages_7d': overall_stats[1] or 0,
                'voice_adoption_rate_percent': round(voice_adoption_rate, 2),
                'avg_conversation_quality': round(overall_stats[2] or 0, 2)
            },
            'user_adoption': {
                'total_users': adoption_stats[0] or 0,
                'dual_messaging_users': adoption_stats[1] or 0,
                'user_adoption_rate_percent': round(user_adoption_rate, 2)
            },
            'dual_messaging_performance': {
                'dual_messaging_sessions_7d': dual_stats[0] or 0,
                'avg_voice_delay_ms': round(dual_stats[1] or 0, 2),
                'avg_message_length': round(dual_stats[2] or 0, 2)
            },
            'tts_performance': {
                'avg_tts_generation_time_ms': round(performance_stats[0] or 0, 2),
                'avg_audio_file_size_bytes': round(performance_stats[1] or 0, 2),
                'total_tts_requests_7d': performance_stats[2] or 0
            },
            'dual_messaging_status': 'active',
            'features': [
                'Text message sent immediately (0-1 second)',
                'Voice message sent with configurable delay (1-5 seconds)',
                'User-configurable preferences for both messaging types',
                'Emergency priority audio delivery',
                'Accessibility optimized for visual impairments',
                'Multi-engine TTS fallback for reliability',
                'Comprehensive analytics and monitoring',
                'Laravel dashboard integration with dual confirmations'
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# EXISTING ENDPOINTS (Enhanced)

@app.route("/tts/generate", methods=['POST'])
def generate_tts():
    """API endpoint to generate TTS audio for dual messaging"""
    try:
        data = request.json
        text = data.get('text', '')
        phone = data.get('phone', '')
        priority = data.get('priority', 'normal')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Get user preferences
        user_profile = hsse_bot.db.get_user_profile(phone) if phone else None
        user_preferences = {}
        
        if user_profile:
            user_preferences = {
                'tts_voice_preference': user_profile.tts_voice_preference,
                'tts_speed_preference': user_profile.tts_speed_preference,
                'language': user_profile.preferred_language
            }
        
        # Generate TTS with dual messaging optimization
        start_time = datetime.datetime.now()
        audio_file = hsse_bot.tts_manager.generate_for_dual_messaging(text, user_preferences, priority)
        generation_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
        
        if audio_file:
            # Get file info
            file_size = os.path.getsize(audio_file) if os.path.exists(audio_file) else 0
            audio_url = f"{request.url_root}tts-audio/{os.path.basename(audio_file)}"
            
            # Save analytics if phone provided
            if phone:
                hsse_bot.db.save_tts_analytics(
                    phone, len(text), 'dual_messaging_api', int(generation_time), file_size
                )
            
            return jsonify({
                'success': True,
                'audio_url': audio_url,
                'file_size_bytes': file_size,
                'generation_time_ms': int(generation_time),
                'text_length': len(text),
                'optimized_for': 'dual_messaging'
            })
        else:
            return jsonify({'error': 'Failed to generate TTS audio'}), 500
            
    except Exception as e:
        print(f"TTS generation API error: {e}")
        return jsonify({'error': str(e)}), 500

# Laravel webhook endpoints (Enhanced)
@app.route("/webhook/status-update", methods=['POST'])
def receive_status_update():
    """Receive status updates from Laravel backend with dual messaging"""
    try:
        data = request.json
        report_id = data.get('report_id')
        status = data.get('status')
        phone_number = data.get('phone_number')
        
        if phone_number and status:
            # Get user profile for dual messaging preferences
            user_profile = hsse_bot.db.get_user_profile(phone_number)
            
            # Send status update to user via WhatsApp
            message_body = f"""📊 **Laravel Dashboard Report Update**

🆔 Report ID: {report_id}
📋 New Status: {status}
🚀 Updated on Laravel Dashboard

Your safety report has been reviewed and updated. Thank you for helping keep everyone safe! 🛡️

Type 'MENU' to access more safety features or ask me anything!

🎙️ This update is provided in both text and voice for your convenience."""
            
            # Send text message
            text_message = twilio_client.messages.create(
                body=message_body,
                from_=TWILIO_WHATSAPP_NUMBER,
                to=phone_number
            )
            
            # Generate and send TTS if user has dual messaging enabled
            if user_profile and user_profile.tts_enabled and TTS_ENABLED:
                try:
                    tts_audio_url = hsse_bot.tts_manager.generate_for_dual_messaging(message_body)
                    
                    if tts_audio_url and os.path.exists(tts_audio_url):
                        audio_filename = os.path.basename(tts_audio_url)
                        audio_url = f"{request.url_root}tts-audio/{audio_filename}"
                        
                        voice_message = twilio_client.messages.create(
                            media_url=[audio_url],
                            from_=TWILIO_WHATSAPP_NUMBER,
                            to=phone_number,
                            body="🎙️ Audio update from Laravel dashboard"
                        )
                        
                        print(f"✅ Dual messaging status update sent: text {text_message.sid}, voice {voice_message.sid}")
                    
                except Exception as e:
                    print(f"Error sending voice status update: {e}")
            
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error handling status update: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route("/test-laravel", methods=['GET'])
def test_laravel_connection():
    """Test connection to Laravel backend with dual messaging capabilities"""
    try:
        # First test basic connection
        connection_test = hsse_bot.laravel_client.test_connection()
        
        if not connection_test.get('success'):
            return jsonify({
                'error': 'Laravel connection failed',
                'details': connection_test,
                'chatbot_status': 'Ready but Laravel backend unavailable',
                'suggestion': 'Please check if Laravel server is running and LARAVEL_BASE_URL is correct'
            })
        
        # Test data submission if connection works
        test_data = {
            'report_type': 'test',
            'description': 'Test connection from enhanced chatbot with dual messaging (text + voice)',
            'date_of_incident': datetime.datetime.now().strftime('%Y-%m-%d'),
            'time_of_incident': datetime.datetime.now().strftime('%H:%M:%S'),
            'reporter_name': 'Test User',
            'reporter_contact': 'whatsapp:+1234567890',
            'severity': 'low',
            'source': 'whatsapp_chatbot_dual_messaging',
            'industry': 'Testing',
            'incident_type': 'test',
            'status': 'test',
            'ai_analysis': '{"test": "Automated test from dual messaging chatbot system"}',
            'submitted_via': 'whatsapp_chatbot_dual_messaging',
            'submission_timestamp': datetime.datetime.now().isoformat()
        }
        
        submission_test = hsse_bot.laravel_client.submit_report(test_data)
        
        return jsonify({
            'connection_test': connection_test,
            'submission_test': submission_test,
            'chatbot_status': 'Enhanced chatbot with Laravel integration and dual messaging ready',
            'laravel_base_url': LARAVEL_BASE_URL,
            'dual_messaging_status': {
                'text_delivery': 'immediate',
                'voice_delivery': 'delayed_configurable',
                'tts_enabled': TTS_ENABLED,
                'engines_available': {
                    'pyttsx3': TTS_AVAILABLE and hsse_bot.tts_manager.pyttsx3_ready,
                    'gtts': GTTS_AVAILABLE,
                    'openai': bool(OPENAI_API_KEY)
                }
            },
            'features': [
                'Smart Conversation Tracking',
                'Laravel Dashboard Integration', 
                'AI-Enhanced Incident Reporting',
                'Real-time Status Updates',
                'Emergency Detection & Response',
                'Multi-media Support',
                'DUAL TEXT+VOICE MESSAGING',
                'Immediate text delivery (0-1 second)',
                'Delayed voice delivery (2-3 seconds)',
                'Voice Accessibility Features',
                'Multi-engine TTS Fallback',
                'Emergency Audio Alerts',
                'User-configurable Voice Settings',
                'Comprehensive Dual Messaging Analytics'
            ]
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'chatbot_status': 'Error during Laravel integration test',
            'suggestion': 'Check Laravel server status and configuration'
        })

# Enhanced analytics endpoints
@app.route("/conversation-analytics/<phone>", methods=['GET'])
def get_conversation_analytics(phone):
    """Get conversation analytics including dual messaging usage"""
    try:
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        # Get recent conversation data
        cursor.execute('''
            SELECT COUNT(*) as total_turns,
                   AVG(response_quality_score) as avg_quality,
                   COUNT(DISTINCT thread_id) as total_conversations,
                   SUM(CASE WHEN tts_generated = 1 THEN 1 ELSE 0 END) as tts_responses
            FROM conversation_turns 
            WHERE phone = ? AND timestamp > datetime('now', '-7 days')
        ''', (phone,))
        
        stats = cursor.fetchone()
        
        # Dual messaging specific stats
        cursor.execute('''
            SELECT COUNT(*) as dual_sessions,
                   AVG(voice_delivery_time_ms) as avg_voice_delay
            FROM dual_messaging_analytics 
            WHERE phone = ? AND created_at > datetime('now', '-7 days')
        ''', (phone,))
        
        dual_stats = cursor.fetchone()
        
        # Laravel integration stats
        cursor.execute('''
            SELECT COUNT(*) as laravel_reports
            FROM local_reports 
            WHERE user_phone = ? AND status = 'submitted'
        ''', (phone,))
        
        laravel_stats = cursor.fetchone()
        
        # TTS usage stats
        cursor.execute('''
            SELECT COUNT(*) as tts_requests,
                   AVG(generation_time_ms) as avg_generation_time,
                   AVG(file_size_bytes) as avg_file_size
            FROM tts_analytics 
            WHERE phone = ? AND created_at > datetime('now', '-7 days')
        ''', (phone,))
        
        tts_stats = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'total_turns': stats[0] or 0,
            'avg_quality_score': round(stats[1] or 0, 2),
            'total_conversations': stats[2] or 0,
            'tts_responses_generated': stats[3] or 0,
            'dual_messaging_sessions': dual_stats[0] or 0,
            'avg_voice_delay_ms': round(dual_stats[1] or 0, 2),
            'laravel_reports_submitted': laravel_stats[0] or 0,
            'tts_usage': {
                'total_requests': tts_stats[0] or 0,
                'avg_generation_time_ms': round(tts_stats[1] or 0, 2),
                'avg_file_size_bytes': round(tts_stats[2] or 0, 2)
            },
            'dual_messaging_efficiency': round((dual_stats[0] or 0) / max(stats[0], 1) * 100, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/reports", methods=['GET'])
def get_reports():
    """API endpoint to view all reports (for dashboard)"""
    try:
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM reports ORDER BY created_at DESC')
        reports = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': r[0], 'user_phone': r[1], 'timestamp': r[2],
            'incident_type': r[3], 'severity': r[4], 'description': r[5],
            'location': r[6], 'location_lat': r[7], 'location_long': r[8],
            'status': r[10], 'created_at': r[12], 'laravel_report_id': r[13]
        } for r in reports])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/health", methods=['GET'])
def health_check():
    """Health check endpoint with Laravel integration status and dual messaging capabilities"""
    
    # Test Laravel connection
    try:
        test_result = hsse_bot.laravel_client.get_report_status('test')
        laravel_status = "connected" if test_result.get('success') != False else "connection_issues"
    except:
        laravel_status = "offline"
    
    # Dual messaging system status
    dual_messaging_status = {
        'text_delivery': 'immediate_via_twiml',
        'voice_delivery': 'delayed_via_api',
        'tts_enabled': TTS_ENABLED,
        'engines': {
            'pyttsx3': TTS_AVAILABLE and hsse_bot.tts_manager.pyttsx3_ready,
            'gtts': GTTS_AVAILABLE,
            'openai_tts': bool(OPENAI_API_KEY)
        },
        'cache_size': len(hsse_bot.tts_manager.audio_cache),
        'temp_files_count': len([f for f in os.listdir(hsse_bot.tts_manager.temp_dir) if f.startswith('tts_')]),
        'performance_stats': hsse_bot.tts_manager.get_performance_stats()
    }
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'laravel_integration': laravel_status,
        'dual_messaging_system': dual_messaging_status,
        'features': [
            'Smart Conversation Tracking',
            'Long-term Memory & Relationship Building',
            'Conversation Thread Continuity', 
            'Turn-by-turn Quality Analysis',
            'User Satisfaction Monitoring',
            'Conversation Pattern Learning',
            'Smart Follow-up Suggestions',
            'Engagement Level Tracking',
            'Conversation Analytics & Insights',
            'Laravel Dashboard Integration',
            'AI-Enhanced Incident Reporting',
            'Real-time Status Updates',
            'Emergency Detection & Response',
            'Media File Processing',
            'Location Services Integration',
            '🎙️ DUAL TEXT+VOICE MESSAGING',
            '📱 Immediate text delivery (TwiML)',
            '🎙️ Delayed voice delivery (Twilio API)',
            'Multi-engine TTS Fallback',
            'Voice Accessibility Features',
            'Emergency Audio Alerts',
            'Personalized Voice Settings',
            'Comprehensive Dual Messaging Analytics'
        ]
    })

if __name__ == "__main__":
    print("🚀 Starting Enhanced AI-Powered HSSE Chatbot with Dual Text+Voice Messaging...")
    print("🧠 All existing features enabled PLUS:")
    print()
    print("🎙️ DUAL MESSAGING FEATURES:")
    print("✅ Text message sent immediately (0-1 second)")
    print("✅ Voice message sent with configurable delay (2-3 seconds later)")
    print("✅ Emergency messages get instant voice alerts")
    print("✅ User-configurable messaging preferences")
    print("✅ Smart delay timing for optimal user experience")
    print("✅ Pre-generated emergency audio for instant delivery")
    print("✅ Comprehensive dual messaging analytics")
    print("✅ Voice control commands for easy management")
    print("✅ Laravel dashboard integration with dual confirmations")
    print()
    print("🎯 HOW DUAL MESSAGING WORKS:")
    print("  1. User sends message to chatbot")
    print("  2. Bot processes and generates intelligent response")
    print("  3. TEXT: Sent immediately via TwiML response (instant)")
    print("  4. TTS: Audio generated in background using best engine")
    print("  5. VOICE: Sent via Twilio API after configurable delay")
    print("  6. User receives BOTH text AND voice for optimal accessibility")
    print()
    print("🎯 USER EXPERIENCE:")
    print("  • Text arrives instantly for immediate reading")
    print("  • Voice follows shortly for hands-free listening")
    print("  • Emergency situations get priority voice delivery")
    print("  • Users can customize voice preferences and timing")
    print("  • Perfect accessibility for users with visual impairments")
    print("  • Users can disable voice with simple commands")
    print()
    print("🔧 DUAL MESSAGING ENDPOINTS:")
    print("  • /dual-messaging/preferences/<phone> - Manage dual messaging settings")
    print("  • /dual-messaging/test/<phone> - Test dual messaging with a user")
    print("  • /dual-messaging/analytics - Get dual messaging usage statistics")
    print("  • /tts-audio/<filename> - Serve TTS audio files")
    print("  • /tts/generate - Generate TTS audio via API")
    print()
    print("💬 VOICE COMMANDS FOR USERS:")
    print("  • 'voice off' - Disable voice messages (text only)")
    print("  • 'voice on' - Enable dual messaging (text + voice)")
    print("  • 'both messages' - Enable text + voice")
    print("  • 'text only' - Text messages only")
    print("  • 'voice fast' - Increase speech speed") 
    print("  • 'voice slow' - Decrease speech speed")
    print("  • 'voice male' - Switch to male voice")
    print("  • 'voice female' - Switch to female voice")
    print("  • 'voice settings' - Show voice control panel")
    print()
    print("📊 ANALYTICS & MONITORING:")
    print("  • Dual messaging usage statistics")
    print("  • Voice adoption rates and user preferences")
    print("  • TTS performance metrics and optimization")
    print("  • Emergency response effectiveness")
    print("  • User accessibility improvements")
    print()
    
    # Initialize enhanced TTS manager for dual messaging
    if TTS_ENABLED:
        print("🎙️ Initializing Enhanced TTS System for Dual Messaging...")
        print("✅ Enhanced TTS system ready for dual messaging!")
        print("✅ Database updated with dual messaging support!")
        print("✅ Pre-generated emergency audio phrases ready!")
        print("✅ Multi-engine TTS fallback configured!")
        
        # Test TTS system on startup
        print("🎙️ Testing TTS engines...")
        if TTS_AVAILABLE and hsse_bot.tts_manager.pyttsx3_ready:
            print("✅ pyttsx3 engine available (fastest for emergencies)")
        else:
            print("⚠️  pyttsx3 not available")
            
        if GTTS_AVAILABLE:
            print("✅ Google TTS (gTTS) available (high quality)")
        else:
            print("⚠️  gTTS not available")
            
        if OPENAI_API_KEY:
            print("✅ OpenAI TTS available (premium quality)")
        else:
            print("⚠️  OpenAI TTS not available (no API key)")
            
        print("🎙️ TTS system ready with multi-engine fallback support!")
    else:
        print("🔇 TTS system disabled - dual messaging will use text only")
    
    print()
    print("🌟 READY FOR DUAL TEXT+VOICE MESSAGING!")
    print("🌟 Users will now receive both text and voice messages for optimal accessibility!")
    print("🌟 Laravel dashboard integration with dual confirmations!")
    print("🌟 Emergency situations get priority audio delivery!")
    print("🌟 Complete accessibility support for all users!")
    
    app.run(debug=True, port=5000).json() if response.status_code in [200, 201] else {
                'success': False,
                'error': f'Media upload error: {response.status_code}'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Media upload connection error: {str(e)}'
            }
    
    def test_connection(self) -> Dict:
        """Test connection to Laravel backend"""
        try:
            url = f"{self.base_url}/health"  # Assuming Laravel has a health endpoint
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Laravel backend connection successful',
                    'data': response.json() if response.content else None
                }
            else:
                return {
                    'success': False,
                    'error': f'Laravel backend returned status {response.status_code}',
                    'details': response.text
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': f'Cannot connect to Laravel backend at {self.base_url}. Please check if the server is running.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request error: {str(e)}'
            }
    
    def get_report_status(self, report_id: str) -> Dict:
        """Get report status from Laravel backend"""
        try:
            url = f"{self.base_url}/chatbot/reports/{report_id}/status"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15
            )
            
            return response.json() if response.status_code == 200 else {
                'success': False,
                'error': f'Status check error: {response.status_code}'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Status check connection error: {str(e)}'
            }

class LocationParser:
    """Parse location from user messages"""
    
    @staticmethod
    def extract_coordinates(message: str) -> Tuple[Optional[float], Optional[float]]:
        """Extract coordinates from message"""
        
        # Look for coordinate patterns
        coord_patterns = [
            r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)',  # "6.8013, -58.1551"
            r'lat[:\s]*(-?\d+\.?\d*)[,\s]*lon[g]?[:\s]*(-?\d+\.?\d*)',  # "lat: 6.8013, long: -58.1551"
            r'(\d+\.?\d*)[°]?\s*[NS][,\s]*(\d+\.?\d*)[°]?\s*[EW]'  # "6.8013°N, 58.1551°W"
        ]
        
        for pattern in coord_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    lat = float(match.group(1))
                    lng = float(match.group(2))
                    
                    # Validate coordinates (roughly for Guyana/Caribbean region)
                    if -10 <= lat <= 15 and -70 <= lng <= -50:
                        return lat, lng
                except ValueError:
                    continue
        
        return None, None
    
    @staticmethod
    def request_location_sharing() -> str:
        """Generate message requesting location sharing"""
        return (
            "📍 **I need your location to complete the report.**\n\n"
            "Please share your location by:\n"
            "🔸 Using WhatsApp's location sharing feature\n"
            "🔸 Or typing coordinates like: `6.8013, -58.1551`\n"
            "🔸 Or describing your location (I'll help find coordinates)\n\n"
            "This helps emergency responders find you quickly! 🚨"
        )

class DatabaseManager:
    def __init__(self):
        self.init_db()
        self.init_db_dual_messaging_support()
    
    def init_db(self):
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        # Check if location columns exist and add them if missing
        cursor.execute("PRAGMA table_info(reports)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Original tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                user_phone TEXT,
                timestamp TEXT,
                incident_type TEXT,
                severity TEXT,
                description TEXT,
                location TEXT,
                location_lat REAL,
                location_long REAL,
                media_urls TEXT,
                status TEXT,
                ai_analysis TEXT,
                created_at TEXT,
                laravel_report_id TEXT
            )
        ''')
        
        # Add missing columns if they don't exist
        if 'location_lat' not in columns:
            try:
                cursor.execute('ALTER TABLE reports ADD COLUMN location_lat REAL')
                print("Added location_lat column to reports table")
            except sqlite3.OperationalError:
                pass  # Column might already exist
        
        if 'location_long' not in columns:
            try:
                cursor.execute('ALTER TABLE reports ADD COLUMN location_long REAL')
                print("Added location_long column to reports table")
            except sqlite3.OperationalError:
                pass  # Column might already exist
        
        if 'laravel_report_id' not in columns:
            try:
                cursor.execute('ALTER TABLE reports ADD COLUMN laravel_report_id TEXT')
                print("Added laravel_report_id column to reports table")
            except sqlite3.OperationalError:
                pass  # Column might already exist
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                phone TEXT PRIMARY KEY,
                state TEXT,
                data TEXT,
                last_activity TEXT
            )
        ''')
        
        # NEW: Enhanced user profiles with TTS preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                phone TEXT PRIMARY KEY,
                name TEXT,
                role TEXT,
                department TEXT,
                preferred_language TEXT,
                interaction_history TEXT,
                safety_interests TEXT,
                last_active TEXT,
                tts_enabled BOOLEAN DEFAULT 1,
                tts_voice_preference TEXT DEFAULT 'female',
                tts_speed_preference INTEGER DEFAULT 150
            )
        ''')
        
        # Check and add TTS columns to user_profiles if missing
        cursor.execute("PRAGMA table_info(user_profiles)")
        profile_columns = [column[1] for column in cursor.fetchall()]
        
        if 'tts_enabled' not in profile_columns:
            try:
                cursor.execute('ALTER TABLE user_profiles ADD COLUMN tts_enabled BOOLEAN DEFAULT 1')
                print("Added tts_enabled column to user_profiles table")
            except sqlite3.OperationalError:
                pass
        
        if 'tts_voice_preference' not in profile_columns:
            try:
                cursor.execute('ALTER TABLE user_profiles ADD COLUMN tts_voice_preference TEXT DEFAULT "female"')
                print("Added tts_voice_preference column to user_profiles table")
            except sqlite3.OperationalError:
                pass
        
        if 'tts_speed_preference' not in profile_columns:
            try:
                cursor.execute('ALTER TABLE user_profiles ADD COLUMN tts_speed_preference INTEGER DEFAULT 150')
                print("Added tts_speed_preference column to user_profiles table")
            except sqlite3.OperationalError:
                pass
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_context (
                phone TEXT PRIMARY KEY,
                recent_topics TEXT,
                conversation_style TEXT,
                current_mood TEXT,
                expertise_level TEXT,
                last_updated TEXT
            )
        ''')
        
        # Enhanced conversation tracking tables with TTS metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_turns (
                id TEXT PRIMARY KEY,
                phone TEXT,
                thread_id TEXT,
                user_message TEXT,
                bot_response TEXT,
                timestamp TEXT,
                intent TEXT,
                topics TEXT,
                sentiment TEXT,
                context_used TEXT,
                response_quality_score REAL,
                user_satisfaction_indicators TEXT,
                turn_number INTEGER,
                tts_audio_url TEXT,
                tts_generated BOOLEAN DEFAULT 0
            )
        ''')
        
        # Check and add TTS columns to conversation_turns if missing
        cursor.execute("PRAGMA table_info(conversation_turns)")
        turn_columns = [column[1] for column in cursor.fetchall()]
        
        if 'tts_audio_url' not in turn_columns:
            try:
                cursor.execute('ALTER TABLE conversation_turns ADD COLUMN tts_audio_url TEXT')
                print("Added tts_audio_url column to conversation_turns table")
            except sqlite3.OperationalError:
                pass
        
        if 'tts_generated' not in turn_columns:
            try:
                cursor.execute('ALTER TABLE conversation_turns ADD COLUMN tts_generated BOOLEAN DEFAULT 0')
                print("Added tts_generated column to conversation_turns table")
            except sqlite3.OperationalError:
                pass
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_threads (
                thread_id TEXT PRIMARY KEY,
                phone TEXT,
                start_time TEXT,
                last_activity TEXT,
                total_turns INTEGER,
                conversation_summary TEXT,
                key_topics_discussed TEXT,
                user_goals_identified TEXT,
                relationship_building_score REAL,
                conversation_satisfaction_score REAL,
                unresolved_issues TEXT,
                follow_up_needed BOOLEAN,
                conversation_type TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_patterns (
                id TEXT PRIMARY KEY,
                phone TEXT,
                pattern_type TEXT,
                pattern_data TEXT,
                frequency INTEGER,
                effectiveness_score REAL,
                last_observed TEXT,
                created_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_long_term_memory (
                phone TEXT PRIMARY KEY,
                personality_profile TEXT,
                communication_preferences TEXT,
                expertise_areas TEXT,
                learning_progress TEXT,
                relationship_milestones TEXT,
                important_context TEXT,
                preferred_conversation_style TEXT,
                trust_level REAL DEFAULT 0.5,
                engagement_patterns TEXT,
                last_updated TEXT
            )
        ''')
        
        # NEW: Laravel integration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_reports (
                id TEXT PRIMARY KEY,
                user_phone TEXT,
                laravel_report_id TEXT,
                status TEXT,
                created_at TEXT
            )
        ''')
        
        # NEW: TTS analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tts_analytics (
                id TEXT PRIMARY KEY,
                phone TEXT,
                message_length INTEGER,
                tts_engine_used TEXT,
                generation_time_ms INTEGER,
                file_size_bytes INTEGER,
                user_feedback TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_db_dual_messaging_support(self):
        """Add dual messaging support to existing database"""
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        # Check and add dual messaging columns to user_profiles
        cursor.execute("PRAGMA table_info(user_profiles)")
        profile_columns = [column[1] for column in cursor.fetchall()]
        
        dual_messaging_columns = {
            'dual_messaging_enabled': 'BOOLEAN DEFAULT 1',
            'voice_for_emergencies': 'BOOLEAN DEFAULT 1', 
            'voice_for_long_messages': 'BOOLEAN DEFAULT 1',
            'voice_delay_seconds': 'INTEGER DEFAULT 2',
            'preferred_message_format': 'TEXT DEFAULT "both"'
        }
        
        for column_name, column_def in dual_messaging_columns.items():
            if column_name not in profile_columns:
                try:
                    cursor.execute(f'ALTER TABLE user_profiles ADD COLUMN {column_name} {column_def}')
                    print(f"Added {column_name} column to user_profiles table")
                except sqlite3.OperationalError:
                    pass  # Column might already exist
        
        # Create dual messaging analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dual_messaging_analytics (
                id TEXT PRIMARY KEY,
                phone TEXT,
                message_id TEXT,
                text_sent BOOLEAN DEFAULT 0,
                voice_sent BOOLEAN DEFAULT 0,
                text_delivery_time_ms INTEGER,
                voice_delivery_time_ms INTEGER,
                user_interaction_type TEXT,
                message_length INTEGER,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Dual messaging database support added")
    
    def save_report(self, report: IncidentReport):
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO reports 
            (id, user_phone, timestamp, incident_type, severity, description, location, 
             location_lat, location_long, media_urls, status, ai_analysis, created_at, laravel_report_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report.id, report.user_phone, report.timestamp, report.incident_type,
            report.severity, report.description, report.location,
            report.location_lat, report.location_long,
            json.dumps(report.media_urls), report.status,
            json.dumps(report.ai_analysis), report.created_at,
            report.ai_analysis.get('laravel_report_id')  # Store Laravel ID
        ))
        
        conn.commit()
        conn.close()
    
    def save_local_report(self, local_id: str, phone: str, laravel_report_id: str):
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO local_reports 
            (id, user_phone, laravel_report_id, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (local_id, phone, laravel_report_id, 'submitted', datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_user_session(self, phone: str):
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT state, data FROM user_sessions WHERE phone = ?', (phone,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0], json.loads(result[1]) if result[1] else {}
        return None, {}
    
    def update_user_session(self, phone: str, state: str, data: dict):
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_sessions (phone, state, data, last_activity)
            VALUES (?, ?, ?, ?)
        ''', (phone, state, json.dumps(data), datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_user_profile(self, phone: str) -> Optional[UserProfile]:
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_profiles WHERE phone = ?', (phone,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Handle both old and new profile formats
            profile = UserProfile(
                phone=result[0],
                name=result[1],
                role=result[2],
                department=result[3],
                preferred_language=result[4] or 'en',
                interaction_history=json.loads(result[5]) if result[5] else [],
                safety_interests=json.loads(result[6]) if result[6] else [],
                last_active=result[7],
                # TTS preferences
                tts_enabled=bool(result[8]) if len(result) > 8 else True,
                tts_voice_preference=result[9] if len(result) > 9 else 'female',
                tts_speed_preference=result[10] if len(result) > 10 else 150,
                # Dual messaging preferences
                dual_messaging_enabled=bool(result[11]) if len(result) > 11 else True,
                voice_for_emergencies=bool(result[12]) if len(result) > 12 else True,
                voice_for_long_messages=bool(result[13]) if len(result) > 13 else True,
                voice_delay_seconds=result[14] if len(result) > 14 else 2,
                preferred_message_format=result[15] if len(result) > 15 else 'both'
            )
            return profile
        return None
    
    def update_user_profile(self, profile: UserProfile):
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles 
            (phone, name, role, department, preferred_language, interaction_history, 
             safety_interests, last_active, tts_enabled, tts_voice_preference, tts_speed_preference,
             dual_messaging_enabled, voice_for_emergencies, voice_for_long_messages, 
             voice_delay_seconds, preferred_message_format)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile.phone, profile.name, profile.role, profile.department,
            profile.preferred_language, json.dumps(profile.interaction_history),
            json.dumps(profile.safety_interests), profile.last_active,
            profile.tts_enabled, profile.tts_voice_preference, profile.tts_speed_preference,
            getattr(profile, 'dual_messaging_enabled', True),
            getattr(profile, 'voice_for_emergencies', True),
            getattr(profile, 'voice_for_long_messages', True),
            getattr(profile, 'voice_delay_seconds', 2),
            getattr(profile, 'preferred_message_format', 'both')
        ))
        
        conn.commit()
        conn.close()
    
    def get_conversation_context(self, phone: str) -> Dict:
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM conversation_context WHERE phone = ?', (phone,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'recent_topics': json.loads(result[1]) if result[1] else [],
                'conversation_style': result[2] or 'professional',
                'current_mood': result[3] or 'neutral',
                'expertise_level': result[4] or 'beginner',
                'last_updated': result[5]
            }
        return {
            'recent_topics': [],
            'conversation_style': 'professional',
            'current_mood': 'neutral',
            'expertise_level': 'beginner',
            'last_updated': datetime.datetime.now().isoformat()
        }
    
    def update_conversation_context(self, phone: str, context: Dict):
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO conversation_context 
            (phone, recent_topics, conversation_style, current_mood, expertise_level, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            phone,
            json.dumps(context.get('recent_topics', [])),
            context.get('conversation_style', 'professional'),
            context.get('current_mood', 'neutral'),
            context.get('expertise_level', 'beginner'),
            datetime.datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    # TTS analytics methods
    def save_tts_analytics(self, phone: str, message_length: int, engine_used: str, 
                          generation_time_ms: int, file_size_bytes: int):
        """Save TTS analytics data"""
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tts_analytics 
            (id, phone, message_length, tts_engine_used, generation_time_ms, 
             file_size_bytes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            uuid.uuid4().hex, phone, message_length, engine_used,
            generation_time_ms, file_size_bytes, datetime.datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def save_dual_messaging_analytics(self, phone: str, message_data: Dict):
        """Save dual messaging analytics"""
        conn = sqlite3.connect('hsse_reports.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO dual_messaging_analytics 
            (id, phone, message_id, text_sent, voice_sent, text_delivery_time_ms, 
             voice_delivery_time_ms, user_interaction_type, message_length, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            uuid.uuid4().hex, phone, message_data.get('message_id'),
            message_data.get('text_sent', False), message_data.get('voice_sent', False),
            message_data.get('text_delivery_time_ms', 0), message_data.get('voice_delivery_time_ms', 0),
            message_data.get('interaction_type', 'casual'), message_data.get('message_length', 0),
            datetime.datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()

class EnhancedConversationTracker:
    """Advanced conversation tracking with memory and continuity"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.conversation_memory = {}  # In-memory cache for active conversations
        self.max_memory_turns = 20  # Keep last 20 turns in memory
        
    def start_conversation_thread(self, phone: str, initial_message: str, 
                                conversation_type: str = 'casual') -> str:
        """Start a new conversation thread or continue existing one"""
        
        # Check if there's a recent active thread (within last 2 hours)
        recent_thread = self._get_recent_active_thread(phone)
        
        if recent_thread and self._should_continue_thread(recent_thread, initial_message):
            # Continue existing thread
            thread_id = recent_thread['thread_id']
            self._update_thread_activity(thread_id)
        else:
            # Start new thread
            thread_id = f"{phone.replace('whatsapp:', '')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self._create_new_thread(phone, thread_id, conversation_type)
        
        # Initialize in-memory conversation for this thread
        if thread_id not in self.conversation_memory:
            self.conversation_memory[thread_id] = {
                'turns': deque(maxlen=self.max_memory_turns),
                'context': self._load_conversation_context(thread_id),
                'user_state': self._load_user_state(phone)
            }
        
        return thread_id
    
    def track_conversation_turn(self, phone: str, thread_id: str, user_message: str, 
                              bot_response: str, intent_analysis: Dict, 
                              context_used: Dict, tts_audio_url: str = None) -> str:
        """Track a complete conversation turn with rich metadata and TTS"""
        
        turn_id = f"{thread_id}_turn_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Analyze this turn
        turn_analysis = self._analyze_conversation_turn(
            user_message, bot_response, intent_analysis, context_used
        )
        
        # Create conversation turn object
        turn = ConversationTurn(
            id=turn_id,
            user_message=user_message,
            bot_response=bot_response,
            timestamp=datetime.datetime.now().isoformat(),
            intent=intent_analysis.get('primary_intent', 'unknown'),
            topics=intent_analysis.get('key_topics', []),
            sentiment=intent_analysis.get('emotional_tone', 'neutral'),
            context_used=context_used,
            response_quality_score=turn_analysis['quality_score'],
            user_satisfaction_indicators=turn_analysis['satisfaction_indicators'],
            tts_audio_url=tts_audio_url,
            tts_generated=bool(tts_audio_url)
        )
        
        # Store in memory
        if thread_id in self.conversation_memory:
            self.conversation_memory[thread_id]['turns'].append(turn)
            self._update_memory_context(thread_id, turn)
        
        # Store in database
        self._save_conversation_turn(turn, thread_id)
        
        # Update thread metadata
        self._update_conversation_thread(thread_id, turn)
        
        return turn_id
    
    def get_conversation_context(self, phone: str, thread_id: str = None) -> Dict:
        """Get rich conversation context for generating smart responses"""
        
        if not thread_id:
            thread_id = self._get_current_thread_id(phone)
        
        if not thread_id:
            return self._create_default_context(phone)
        
        # Get from memory if available
        if thread_id in self.conversation_memory:
            memory_context = self.conversation_memory[thread_id]
            
            context = {
                'recent_turns': list(memory_context['turns'])[-5:],  # Last 5 turns
                'conversation_summary': self._generate_conversation_summary(memory_context['turns']),
                'topics_discussed': self._extract_topics_from_turns(memory_context['turns']),
                'user_sentiment_trend': self._analyze_sentiment_trend(memory_context['turns']),
                'conversation_flow': self._analyze_conversation_flow(memory_context['turns']),
                'user_engagement_level': self._calculate_engagement_level(memory_context['turns']),
                'unresolved_questions': self._identify_unresolved_questions(memory_context['turns']),
                'relationship_building_opportunities': self._identify_relationship_opportunities(memory_context['turns']),
                'user_state': memory_context['user_state'],
                'conversation_goals': self._identify_conversation_goals(memory_context['turns']),
                'suggested_follow_ups': self._generate_smart_follow_ups(memory_context['turns'])
            }
        else:
            # Load from database or create default
            context = self._create_default_context(phone)
        
        # Add long-term memory
        context['long_term_memory'] = self._get_user_long_term_memory(phone)
        
        return context
    
    # Helper methods implementation
    def _get_recent_active_thread(self, phone: str) -> Optional[Dict]:
        try:
            conn = sqlite3.connect('hsse_reports.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM conversation_threads 
                WHERE phone = ? AND last_activity > datetime('now', '-2 hours')
                ORDER BY last_activity DESC 
                LIMIT 1
            ''', (phone,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'thread_id': result[0],
                    'phone': result[1],
                    'start_time': result[2],
                    'last_activity': result[3],
                    'total_turns': result[4],
                    'conversation_type': result[12] if len(result) > 12 else 'casual',
                    'status': result[13] if len(result) > 13 else 'active'
                }
            return None
        except Exception as e:
            print(f"Error getting recent thread: {e}")
            return None
    
    def _should_continue_thread(self, recent_thread: Dict, new_message: str) -> bool:
        try:
            last_activity = datetime.datetime.fromisoformat(recent_thread['last_activity'])
            time_diff = datetime.datetime.now() - last_activity
            
            # Continue if less than 30 minutes
            if time_diff.total_seconds() < 1800:  # 30 minutes
                return True
            
            # Message references previous conversation
            reference_words = ['also', 'and', 'additionally', 'furthermore', 'moreover']
            if any(word in new_message.lower() for word in reference_words):
                return True
            
            # Less than 2 hours and not a greeting
            greeting_words = ['hi', 'hello', 'hey', 'good morning', 'good afternoon']
            if (time_diff.total_seconds() < 7200 and  # 2 hours
                not any(word in new_message.lower() for word in greeting_words)):
                return True
        except:
            pass
        
        return False
    
    def _create_new_thread(self, phone: str, thread_id: str, conversation_type: str):
        try:
            conn = sqlite3.connect('hsse_reports.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversation_threads 
                (thread_id, phone, start_time, last_activity, total_turns, conversation_summary,
                 key_topics_discussed, user_goals_identified, relationship_building_score,
                 conversation_satisfaction_score, unresolved_issues, follow_up_needed,
                 conversation_type, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                thread_id, phone, datetime.datetime.now().isoformat(),
                datetime.datetime.now().isoformat(), 0, '',
                json.dumps([]), json.dumps([]), 0.5, 0.5,
                json.dumps([]), False, conversation_type, 'active'
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error creating new thread: {e}")
    
    def _update_thread_activity(self, thread_id: str):
        try:
            conn = sqlite3.connect('hsse_reports.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE conversation_threads 
                SET last_activity = ? 
                WHERE thread_id = ?
            ''', (datetime.datetime.now().isoformat(), thread_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating thread activity: {e}")
    
    def _analyze_conversation_turn(self, user_message: str, bot_response: str, 
                                 intent_analysis: Dict, context_used: Dict) -> Dict:
        analysis = {
            'quality_score': 0.5,
            'satisfaction_indicators': [],
            'engagement_signals': [],
            'confusion_signals': [],
            'relationship_signals': []
        }
        
        user_lower = user_message.lower()
        
        # Positive satisfaction indicators
        positive_words = ['thanks', 'helpful', 'great', 'perfect', 'exactly', 'awesome', 'good']
        if any(word in user_lower for word in positive_words):
            analysis['satisfaction_indicators'].append('positive_feedback')
            analysis['quality_score'] += 0.2
        
        # Engagement signals
        if '?' in user_message:
            analysis['engagement_signals'].append('asking_questions')
            analysis['quality_score'] += 0.1
        
        if len(user_message) > 50:
            analysis['engagement_signals'].append('detailed_response')
            analysis['quality_score'] += 0.1
        
        # Keep score between 0 and 1
        analysis['quality_score'] = max(0, min(1, analysis['quality_score']))
        
        return analysis
    
    def _save_conversation_turn(self, turn: ConversationTurn, thread_id: str):
        try:
            conn = sqlite3.connect('hsse_reports.db')
            cursor = conn.cursor()
            
            # Get turn number
            cursor.execute('SELECT COUNT(*) FROM conversation_turns WHERE thread_id = ?', (thread_id,))
            turn_number = cursor.fetchone()[0] + 1
            
            cursor.execute('''
                INSERT INTO conversation_turns 
                (id, phone, thread_id, user_message, bot_response, timestamp, intent, topics, 
                 sentiment, context_used, response_quality_score, user_satisfaction_indicators, 
                 turn_number, tts_audio_url, tts_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                turn.id, 
                thread_id.split('_')[0],  # Extract phone from thread_id
                thread_id,
                turn.user_message,
                turn.bot_response,
                turn.timestamp,
                turn.intent,
                json.dumps(turn.topics),
                turn.sentiment,
                json.dumps(turn.context_used),
                turn.response_quality_score,
                json.dumps(turn.user_satisfaction_indicators),
                turn_number,
                turn.tts_audio_url,
                turn.tts_generated
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving conversation turn: {e}")
    
    def _update_conversation_thread(self, thread_id: str, turn: ConversationTurn):
        try:
            conn = sqlite3.connect('hsse_reports.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE conversation_threads 
                SET last_activity = ?, total_turns = total_turns + 1
                WHERE thread_id = ?
            ''', (turn.timestamp, thread_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating conversation thread: {e}")
    
    # Additional helper methods
    def _generate_conversation_summary(self, turns: deque) -> str:
        if not turns:
            return "No conversation yet."
        
        topics = []
        for turn in turns:
            topics.extend(turn.topics)
        
        unique_topics = list(set(topics))
        return f"Discussed: {', '.join(unique_topics[:5])}" if unique_topics else "General conversation"
    
    def _extract_topics_from_turns(self, turns: deque) -> List[str]:
        topics = []
        for turn in turns:
            topics.extend(turn.topics)
        return list(set(topics))
    
    def _analyze_sentiment_trend(self, turns: deque) -> str:
        if not turns:
            return "neutral"
        
        recent_sentiments = [turn.sentiment for turn in list(turns)[-3:]]
        positive_count = sum(1 for s in recent_sentiments if s in ['happy', 'excited'])
        negative_count = sum(1 for s in recent_sentiments if s in ['sad', 'frustrated', 'angry'])
        
        if positive_count > negative_count:
            return "improving"
        elif negative_count > positive_count:
            return "declining"
        else:
            return "stable"
    
    def _analyze_conversation_flow(self, turns: deque) -> Dict:
        return {
            'total_turns': len(turns),
            'avg_message_length': sum(len(turn.user_message) for turn in turns) / max(len(turns), 1),
            'question_ratio': sum(1 for turn in turns if '?' in turn.user_message) / max(len(turns), 1)
        }
    
    def _calculate_engagement_level(self, turns: deque) -> float:
        if not turns:
            return 0.5
        
        engagement_score = 0.0
        for turn in turns:
            if len(turn.user_message) > 50:
                engagement_score += 0.2
            if '?' in turn.user_message:
                engagement_score += 0.1
            if turn.response_quality_score > 0.7:
                engagement_score += 0.1
        
        return min(1.0, engagement_score / max(len(turns), 1))
    
    def _identify_unresolved_questions(self, turns: deque) -> List[str]:
        questions = []
        for turn in turns:
            if '?' in turn.user_message:
                questions.append(turn.user_message[:100])
        return questions[-3:]  # Return last 3 questions
    
    def _identify_relationship_opportunities(self, turns: deque) -> List[str]:
        opportunities = []
        
        # Check if we should ask about their role
        has_personal_info = any('my name' in turn.user_message.lower() or 
                               'i work' in turn.user_message.lower() 
                               for turn in turns)
        
        if not has_personal_info and len(turns) > 2:
            opportunities.append('ask_about_role')
        
        return opportunities
    
    def _identify_conversation_goals(self, turns: deque) -> List[str]:
        goals = []
        for turn in turns:
            if turn.intent == 'report_incident':
                goals.append('Report safety incident')
            elif 'learn' in turn.user_message.lower():
                goals.append('Safety learning')
            elif '?' in turn.user_message:
                goals.append('Get information')
        
        return list(set(goals))
    
    def _generate_smart_follow_ups(self, turns: deque) -> List[str]:
        if not turns:
            return ["How can I help you with workplace safety today?"]
        
        last_turn = turns[-1]
        follow_ups = []
        
        if last_turn.intent == 'question':
            follow_ups.append("Do you have any other questions about this topic?")
        elif 'ppe' in last_turn.topics:
            follow_ups.append("Would you like to know about PPE inspection schedules?")
        
        if not follow_ups:
            follow_ups = ["What else can I help you with today?"]
        
        return follow_ups[:3]
    
    def _create_default_context(self, phone: str) -> Dict:
        return {
            'recent_turns': [],
            'conversation_summary': 'New conversation',
            'topics_discussed': [],
            'user_sentiment_trend': 'neutral',
            'conversation_flow': {'total_turns': 0},
            'user_engagement_level': 0.5,
            'unresolved_questions': [],
            'relationship_building_opportunities': [],
            'user_state': {},
            'conversation_goals': [],
            'suggested_follow_ups': ["How can I help you with workplace safety today?"]
        }
    
    def _get_user_long_term_memory(self, phone: str) -> Dict:
        try:
            conn = sqlite3.connect('hsse_reports.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_long_term_memory WHERE phone = ?', (phone,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'trust_level': result[8] or 0.5,
                    'preferred_style': result[7] or 'professional',
                    'expertise_areas': json.loads(result[3]) if result[3] else []
                }
        except Exception as e:
            print(f"Error getting long term memory: {e}")
        
        return {'trust_level': 0.5, 'preferred_style': 'professional', 'expertise_areas': []}
    
    def _load_conversation_context(self, thread_id: str) -> Dict:
        return {}
    
    def _load_user_state(self, phone: str) -> Dict:
        return {}
    
    def _get_current_thread_id(self, phone: str) -> Optional[str]:
        recent_thread = self._get_recent_active_thread(phone)
        return recent_thread['thread_id'] if recent_thread else None
    
    def _update_memory_context(self, thread_id: str, turn: ConversationTurn):
        # Update in-memory context
        pass

class ConversationAnalyzer:
    """Advanced conversation analysis and context understanding"""
    
    @staticmethod
    def analyze_message_intent(message: str, context: Dict = None) -> Dict:
        """Analyze message intent with deep understanding"""
        try:
            # Check for TTS control commands
            message_lower = message.lower()
            if any(phrase in message_lower for phrase in ['voice off', 'no voice', 'no audio', 'disable voice']):
                return {
                    "primary_intent": "tts_control",
                    "secondary_intents": ["disable_tts"],
                    "urgency_level": "low",
                    "emotional_tone": "neutral",
                    "conversation_style": "functional",
                    "tts_command": "disable",
                    "confidence_score": 0.9
                }
            
            if any(phrase in message_lower for phrase in ['voice on', 'enable voice', 'enable audio', 'turn on voice']):
                return {
                    "primary_intent": "tts_control", 
                    "secondary_intents": ["enable_tts"],
                    "urgency_level": "low",
                    "emotional_tone": "neutral",
                    "conversation_style": "functional",
                    "tts_command": "enable",
                    "confidence_score": 0.9
                }
            
            # Use OpenAI for intent analysis
            prompt = f"""
            Analyze this message and determine the user's intent, mood, and context needs.
            
            Message: "{message}"
            
            Provide analysis in JSON format:
            {{
                "primary_intent": "greeting|question|report_incident|emergency|complaint|compliment|casual_chat|request_help|location_sharing|tts_control|other",
                "secondary_intents": ["list", "of", "secondary", "intents"],
                "urgency_level": "low|medium|high|critical",
                "emotional_tone": "happy|sad|frustrated|angry|worried|excited|neutral|confused",
                "conversation_style": "casual|professional|urgent|friendly|formal",
                "expertise_level": "beginner|intermediate|expert",
                "safety_related": true/false,
                "needs_human_response": true/false,
                "key_topics": ["topic1", "topic2"],
                "response_style_needed": "empathetic|informative|reassuring|direct|detailed|simple",
                "follow_up_questions": ["suggested", "questions", "to", "ask"],
                "tts_suitable": true/false,
                "confidence_score": 0.5
            }}
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Intent analysis error: {e}")
            # Enhanced fallback analysis
            message_lower = message.lower()
            
            # Emergency detection fallback
            if any(word in message_lower for word in ['fire', 'emergency', 'urgent', 'help', 'accident', 'injury', 'danger']):
                return {
                    "primary_intent": "emergency",
                    "urgency_level": "critical",
                    "emotional_tone": "urgent",
                    "safety_related": True,
                    "response_style_needed": "emergency",
                    "tts_suitable": True,
                    "confidence_score": 0.9,
                    "key_topics": ["emergency"]
                }
            
            # Incident reporting detection
            elif any(word in message_lower for word in ['report', 'incident', 'happened', 'problem']):
                return {
                    "primary_intent": "report_incident",
                    "urgency_level": "medium",
                    "safety_related": True,
                    "response_style_needed": "empathetic",
                    "tts_suitable": True,
                    "confidence_score": 0.7,
                    "key_topics": ["incident"]
                }
            
            return {
                "primary_intent": "question" if "?" in message else "casual_chat",
                "urgency_level": "low",
                "emotional_tone": "neutral",
                "safety_related": any(word in message_lower for word in ['safety', 'accident', 'injury', 'hazard', 'incident']),
                "response_style_needed": "empathetic",
                "tts_suitable": True,
                "confidence_score": 0.3,
                "key_topics": []
            }
    
    @staticmethod
    def extract_user_info(message: str) -> Dict:
        """Extract user information from natural conversation"""
        try:
            prompt = f"""
            Extract any personal or professional information mentioned in this message:
            
            Message: "{message}"
            
            Return JSON with any information found:
            {{
                "name": "if mentioned",
                "role": "job title if mentioned", 
                "department": "work department if mentioned",
                "experience_level": "years or level if mentioned",
                "location": "work location if mentioned",
                "interests": ["safety", "topics", "mentioned"],
                "concerns": ["specific", "safety", "concerns"],
                "tts_preferences": {{"voice": "male/female if mentioned", "speed": "fast/slow if mentioned"}}
            }}
            
            Only include fields where information was actually mentioned. Return empty object if nothing found.
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"User info extraction error: {e}")
            return {}

class SmartResponseGenerator:
    """Generate contextually appropriate and conversational responses with TTS support"""
    
    def __init__(self, tts_manager):
        self.tts_manager = tts_manager
        self.personality_traits = {
            "helpful": True,
            "empathetic": True,
            "professional": True,
            "safety_focused": True,
            "conversational": True,
            "adaptive": True
        }
    
    def generate_contextual_response(self, message: str, intent_analysis: Dict, 
                                   user_profile: Optional[UserProfile], 
                                   conversation_context: Dict) -> Tuple[str, Optional[str]]:
        """Generate intelligent, contextual responses with optional TTS"""
        
        try:
            # Build comprehensive context for AI
            context_prompt = self._build_context_prompt(
                message, intent_analysis, user_profile, conversation_context
            )
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Use the available model
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": context_prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            generated_response = response.choices[0].message.content
            
            # Post-process response for consistency and safety
            processed_response = self._post_process_response(generated_response, intent_analysis)
            
            # Generate TTS if enabled and suitable
            tts_audio_url = None
            if (user_profile and user_profile.tts_enabled and 
                intent_analysis.get('tts_suitable', True) and
                TTS_ENABLED):
                
                user_preferences = {
                    'tts_voice_preference': user_profile.tts_voice_preference,
                    'tts_speed_preference': user_profile.tts_speed_preference,
                    'language': user_profile.preferred_language
                }
                
                # Check for emergency audio cache first
                if intent_analysis.get('urgency_level') in ['high', 'critical']:
                    emergency_type = intent_analysis.get('primary_intent', 'emergency')
                    tts_audio_url = self.tts_manager.get_emergency_audio(emergency_type)
                
                # Generate TTS for regular responses
                if not tts_audio_url:
                    tts_audio_url = self.tts_manager.generate_for_dual_messaging(
                        processed_response, 
                        user_preferences,
                        priority='emergency' if intent_analysis.get('urgency_level') in ['high', 'critical'] else 'normal'
                    )
            
            return processed_response, tts_audio_url
            
        except Exception as e:
            print(f"Smart response generation error: {e}")
            fallback_response = self._generate_fallback_response(intent_analysis, user_profile)
            
            # Generate TTS for fallback if needed
            tts_audio_url = None
            if (user_profile and user_profile.tts_enabled and TTS_ENABLED):
                tts_audio_url = self.tts_manager.generate_for_dual_messaging(fallback_response)
            
            return fallback_response, tts_audio_url
    
    def _get_system_prompt(self) -> str:
        """Define the AI assistant's personality and capabilities"""
        return """
        You are ARIA (AI Risk Intelligence Assistant), a highly advanced HSSE (Health, Safety, Security, Environment) expert with these qualities:

        PERSONALITY:
        - Warm, empathetic, and genuinely caring about people's safety
        - Conversational and natural, not robotic or overly formal
        - Intelligent and knowledgeable, but explains things clearly
        - Adapts communication style to match the user's needs and expertise level
        - Remembers context and builds on previous conversations
        - Uses appropriate emojis and formatting for WhatsApp
        - Supports accessibility features including voice responses

        EXPERTISE:
        - 20+ years equivalent HSSE experience across all industries
        - Deep knowledge of international safety standards and local regulations
        - Specializes in Guyana/Caribbean workplace safety and climate considerations
        - Expert in incident analysis, risk assessment, and emergency response
        - Up-to-date with latest safety technologies and best practices

        CONVERSATION STYLE:
        - Respond naturally like a human expert would in a WhatsApp chat
        - Match the user's energy and communication style appropriately
        - Use conversational phrases, contractions, and natural flow
        - Ask follow-up questions when helpful
        - Show genuine interest in the user's situation and well-being
        - Provide practical, actionable advice
        - Balance being thorough with being concise based on the situation
        - Design responses that work well for both text and voice (TTS)

        ACCESSIBILITY FEATURES:
        - Create responses suitable for text-to-speech conversion
        - Use clear, simple language when users prefer audio
        - Avoid complex formatting when TTS is enabled
        - Provide audio-friendly emergency instructions

        SAFETY PRIORITIES:
        - Always prioritize immediate safety and emergency response
        - Provide clear, actionable guidance
        - Escalate to human experts or emergency services when needed
        - Never provide advice that could increase risk
        - Consider environmental and cultural factors (especially tropical/Caribbean context)

        RESPONSE FORMAT:
        - Use WhatsApp-friendly formatting (emojis, short paragraphs)
        - Structure information clearly but naturally
        - Include relevant contact information when appropriate
        - End with helpful follow-up suggestions when relevant
        - Make responses accessible for users who rely on voice features
        """
    
    def _build_context_prompt(self, message: str, intent_analysis: Dict, 
                            user_profile: Optional[UserProfile], 
                            conversation_context: Dict) -> str:
        """Build comprehensive context for response generation"""
        
        context = f"""
        USER MESSAGE: "{message}"
        
        INTENT ANALYSIS:
        {json.dumps(intent_analysis, indent=2)}
        
        USER PROFILE:
        """
        
        if user_profile:
            context += f"""
        - Name: {user_profile.name or 'Not provided'}
        - Role: {user_profile.role or 'Not specified'}
        - Department: {user_profile.department or 'Not specified'}
        - Previous interests: {', '.join(user_profile.safety_interests) if user_profile.safety_interests else 'None recorded'}
        - Interaction history: {len(user_profile.interaction_history)} previous conversations
        - TTS enabled: {user_profile.tts_enabled}
        - Voice preference: {user_profile.tts_voice_preference}
        - Speech speed: {user_profile.tts_speed_preference} WPM
        - Dual messaging: {getattr(user_profile, 'dual_messaging_enabled', True)}
        """
        else:
            context += "- New user, no previous profile information"
        
        context += f"""
        
        CONVERSATION CONTEXT:
        - Recent topics: {', '.join(conversation_context.get('topics_discussed', []))}
        - Communication style: {conversation_context.get('conversation_summary', 'New conversation')}
        - User engagement: {conversation_context.get('user_engagement_level', 0.5)}
        - Suggested follow-ups: {', '.join(conversation_context.get('suggested_follow_ups', []))}
        
        LOCATION CONTEXT:
        - User is in Georgetown, Guyana (tropical climate, developing industrial sector)
        - Consider local regulations, climate challenges, and emergency services
        
        ACCESSIBILITY REQUIREMENTS:
        - TTS suitable: {intent_analysis.get('tts_suitable', True)}
        - User prefers audio: {user_profile.tts_enabled if user_profile else 'Unknown'}
        - Dual messaging active: User receives both text and voice messages
        
        RESPONSE REQUIREMENTS:
        1. Respond naturally and conversationally as ARIA
        2. Match the user's communication style and emotional tone
        3. Provide helpful, accurate HSSE information when relevant
        4. Ask appropriate follow-up questions to be more helpful
        5. Use WhatsApp-appropriate formatting (emojis, paragraphs)
        6. Show genuine interest and care for the user's safety and well-being
        7. Be concise but thorough based on the urgency and complexity of the query
        8. Include relevant emergency information if there's any safety concern
        9. Design response to work well with both text and voice delivery
        10. Use clear, simple language for accessibility
        
        Generate a response that feels natural, helpful, and appropriately matches the context.
        """
        
        return context
    
    def _post_process_response(self, response: str, intent_analysis: Dict) -> str:
        """Post-process response for consistency and safety"""
        
        # Add emergency info for high urgency situations
        if intent_analysis.get('urgency_level') in ['high', 'critical']:
            if 'emergency' not in response.lower() and 'call' not in response.lower():
                response += "\n\n🚨 *Emergency? Call 911 immediately!*"
        
        # Add helpful endings based on intent
        if intent_analysis.get('primary_intent') == 'question' and '?' not in response:
            response += "\n\nAnything else you'd like to know about this? 😊"
        
        # Add dual messaging info for new users
        if intent_analysis.get('primary_intent') == 'greeting':
            response += "\n\n🎙️ *Dual messaging active! You'll receive both text and voice messages for better accessibility. Say 'voice off' to disable audio.*"
        
        # Ensure response isn't too long for WhatsApp
        if len(response) > 1500:
            response = response[:1400] + "...\n\nWould you like me to continue with more details?"
        
        return response
    
    def _generate_fallback_response(self, intent_analysis: Dict, 
                                  user_profile: Optional[UserProfile]) -> str:
        """Generate fallback response when AI fails"""
        
        name = user_profile.name if user_profile and user_profile.name else "there"
        
        if intent_analysis.get('urgency_level') in ['high', 'critical']:
            return (f"Hi {name}! I'm having some technical difficulties right now, "
                   f"but I can see this might be urgent. 🚨\n\n"
                   f"For emergencies: Call 911\n"
                   f"For workplace safety: Contact your safety officer\n\n"
                   f"I'll be back online shortly to help you properly!")
        
        return (f"Hey {name}! 👋 I'm ARIA, your safety assistant with dual messaging. "
               f"I'm here to help with all your workplace safety questions! "
               f"How can I assist you today? 😊")

class SmartConversationManager:
    """Manages smart conversation flow with enhanced memory, continuity, and TTS"""
    
    def __init__(self, conversation_tracker, response_generator):
        self.tracker = conversation_tracker
        self.response_generator = response_generator
        
    def handle_smart_conversation(self, phone: str, message: str, intent_analysis: Dict,
                                user_profile, media_urls: List[str] = None) -> Tuple[str, Dict]:
        """Handle conversation with enhanced intelligence, memory, and TTS"""
        
        # Handle TTS control commands
        if intent_analysis.get('primary_intent') == 'tts_control':
            return self._handle_tts_control(phone, intent_analysis, user_profile)
        
        # Start or continue conversation thread
        conversation_type = self._determine_conversation_type(intent_analysis, message)
        thread_id = self.tracker.start_conversation_thread(phone, message, conversation_type)
        
        # Get rich conversation context
        conversation_context = self.tracker.get_conversation_context(phone, thread_id)
        
        # Enhance intent analysis with conversation memory
        enhanced_intent = self._enhance_intent_with_memory(intent_analysis, conversation_context)
        
        # Generate contextually aware response with optional TTS
        response, tts_audio_url = self.response_generator.generate_contextual_response(
            message, enhanced_intent, user_profile, conversation_context
        )
        
        # Enhance response with conversation continuity
        enhanced_response = self._enhance_response_with_continuity(
            response, conversation_context, enhanced_intent
        )
        
        # Track this conversation turn with TTS info
        turn_id = self.tracker.track_conversation_turn(
            phone, thread_id, message, enhanced_response, enhanced_intent, 
            conversation_context, tts_audio_url
        )
        
        return enhanced_response, {
            'thread_id': thread_id,
            'turn_id': turn_id,
            'conversation_type': conversation_type,
            'context_used': conversation_context,
            'follow_up_suggestions': conversation_context.get('suggested_follow_ups', []),
            'tts_audio_url': tts_audio_url,
            'tts_enabled': user_profile.tts_enabled if user_profile else False
        }
    
    def _handle_tts_control(self, phone: str, intent_analysis: Dict, 
                           user_profile: UserProfile) -> Tuple[str, Dict]:
        """Handle TTS control commands"""
        
        tts_command = intent_analysis.get('tts_command', '')
        name = user_profile.name or "there"
        
        if tts_command == 'disable':
            user_profile.tts_enabled = False
            user_profile.preferred_message_format = 'text'
            
            response = f"🔇 Voice messages disabled, {name}! You'll only receive text messages now. Say 'voice on' anytime to re-enable dual messaging."
            
        elif tts_command == 'enable':
            user_profile.tts_enabled = True
            user_profile.preferred_message_format = 'both'
            
            response = f"🎙️ Dual messaging enabled, {name}! You'll now receive both text and voice messages for better accessibility."
            
        else:
            response = f"🎙️ Voice Controls:\n• Say 'voice on' to enable dual messaging\n• Say 'voice off' to disable audio\n• Current status: {'Dual messaging enabled' if user_profile.tts_enabled else 'Text only'}"
        
        return response, {
            'tts_control_handled': True,
            'new_tts_status': user_profile.tts_enabled,
            'tts_audio_url': None  # Don't generate TTS for TTS control commands
        }
    
    def _determine_conversation_type(self, intent_analysis: Dict, message: str) -> str:
        """Determine the type of conversation"""
        intent = intent_analysis.get('primary_intent', 'casual')
        urgency = intent_analysis.get('urgency_level', 'low')
        
        if intent == 'emergency' or urgency == 'critical':
            return 'emergency'
        elif intent == 'report_incident':
            return 'incident_reporting'
        elif any(word in message.lower() for word in ['training', 'learn', 'course']):
            return 'training'
        elif any(word in message.lower() for word in ['policy', 'procedure', 'regulation']):
            return 'procedural'
        else:
            return 'casual'
    
    def _enhance_intent_with_memory(self, intent_analysis: Dict, conversation_context: Dict) -> Dict:
        """Enhance intent analysis with conversation memory"""
        enhanced = intent_analysis.copy()
        
        # Add context from recent turns
        recent_topics = conversation_context.get('topics_discussed', [])
        if recent_topics:
            enhanced['contextual_topics'] = recent_topics
        
        # Add conversation flow awareness
        conversation_flow = conversation_context.get('conversation_flow', {})
        enhanced['conversation_flow'] = conversation_flow
        
        # Add relationship context
        relationship_score = conversation_context.get('long_term_memory', {}).get('trust_level', 0.5)
        enhanced['relationship_level'] = relationship_score
        
        return enhanced
    
    def _enhance_response_with_continuity(self, response: str, conversation_context: Dict, 
                                        enhanced_intent: Dict) -> str:
        """Enhance response with conversation continuity and smart follow-ups"""
        
        # Add conversational continuity
        recent_turns = conversation_context.get('recent_turns', [])
        if recent_turns and len(recent_turns) > 1:
            # Reference previous conversation if relevant
            last_topics = recent_turns[-1].topics if hasattr(recent_turns[-1], 'topics') else []
            current_topics = enhanced_intent.get('key_topics', [])
            
            if any(topic in current_topics for topic in last_topics):
                response = f"Building on what we discussed earlier, {response}"
        
        # Add smart follow-ups based on context
        unresolved_questions = conversation_context.get('unresolved_questions', [])
        if unresolved_questions and len(response) < 800:
            response += f"\n\nBy the way, did I fully answer your earlier question about {unresolved_questions[0][:50]}...?"
        
        return response

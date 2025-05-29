import re
import os
import logging
from datetime import datetime
from src.notes_extractor import NotesExtractor
from src.vector_store import VectorStore
from src.llm_service import LLMService
from src.study_planner import StudyPlanner
from src.roadmap_generator import RoadmapGenerator
from src.content_explainer import ContentExplainer
from src.progress_tracker import ProgressTracker
from src.assignment_manager import AssignmentManager
from langchain_community.chat_message_histories import ChatMessageHistory

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TeachingAgent:
    def __init__(self, user_data, uploaded_files=None):
        self.user_data = user_data
        self.notes_extractor = NotesExtractor()
        self.vector_store = VectorStore()
        self.llm_service = LLMService(model="gemini-1.5-flash-8b-latest", host="https://generativelanguage.googleapis.com/v1beta")
        self.study_planner = StudyPlanner()
        self.roadmap_generator = RoadmapGenerator()
        self.content_explainer = ContentExplainer(self.vector_store)
        self.progress_tracker = ProgressTracker()
        self.assignment_manager = AssignmentManager()

        # LangChain conversational memory
        self.memory = ChatMessageHistory()

        # State to track roadmap progress and conversation
        self.current_roadmap = None
        self.current_phase = None
        self.follow_up_active = False
        self.last_interaction_date = None
        self.conversation_id = None

        # Process uploaded files
        if uploaded_files:
            for file_path in uploaded_files:
                text = self.notes_extractor.extract_text_from_pdf(file_path)
                self.vector_store.store_document(text, self.user_data['email'])
            logging.debug(f"Vector store initialized for user: {self.user_data['email']}")

        # Load chat history from Qdrant and populate LangChain memory
        self._load_chat_history()

    def _load_chat_history(self):
        """Load chat history from Qdrant and populate LangChain memory."""
        try:
            logging.debug(f"Loading chat history for user: {self.user_data['email']}")
            # Get the latest conversation ID
            self.conversation_id = self.vector_store.get_latest_conversation_id(self.user_data['email'])
            if not self.conversation_id:
                logging.info(f"No conversation history found for user: {self.user_data['email']}")
                return

            # Retrieve messages for the latest conversation
            chat_history = self.vector_store.retrieve_chat_history(self.user_data['email'], conversation_id=self.conversation_id)
            if chat_history:
                for message in chat_history:
                    if message['sender'] == 'user':
                        self.memory.add_user_message(message['message'])
                    else:
                        self.memory.add_ai_message(message['message'])
                last_message = chat_history[-1]
                self.last_interaction_date = datetime.fromisoformat(last_message['timestamp']).date()
                for msg in reversed(chat_history):
                    if 'roadmap' in msg['message'].lower() and msg['sender'] == 'assistant':
                        phase_match = re.search(r'Phase\s*\d+:\s*[^()]+?\s*\(Weeks\s*\d+\s*[-+]\s*\d*\)', msg['message'], re.IGNORECASE)
                        roadmap_match = re.search(r'(\w+)\s+roadmap', msg['message'].lower())
                        if phase_match and roadmap_match:
                            self.current_phase = phase_match.group(0).strip()
                            self.current_roadmap = roadmap_match.group(1).capitalize()
                            logging.debug(f"Detected roadmap: {self.current_roadmap}, phase: {self.current_phase}")
                            break
                logging.info(f"Loaded {len(chat_history)} messages for user: {self.user_data['email']}, conversation_id: {self.conversation_id}")
            else:
                logging.info(f"No messages found for conversation_id: {self.conversation_id}")
        except Exception as e:
            logging.error(f"Error loading chat history: {str(e)}")
            raise Exception(f"Failed to load chat history: {str(e)}")

    def _store_message(self, message, sender):
        """Store a message in Qdrant."""
        try:
            timestamp = datetime.utcnow()
            # Use existing conversation_id or start a new one
            self.conversation_id = self.vector_store.store_chat_message(
                message=message,
                user_email=self.user_data['email'],
                sender=sender,
                timestamp=timestamp,
                conversation_id=self.conversation_id
            )
            self.last_interaction_date = timestamp.date()
            logging.debug(f"Stored message from {sender} for user: {self.user_data['email']}, conversation_id: {self.conversation_id}")
        except Exception as e:
            logging.error(f"Error storing message: {str(e)}")
            raise Exception(f"Failed to store message: {str(e)}")

    def handle_message(self, message):
        # Store user message
        self._store_message(message, "user")
        self.memory.add_user_message(message)

        message_lower = message.lower().strip()

        # Check for quick reply or follow-up
        if self.follow_up_active:
            response = self._handle_follow_up_response(message_lower)
        else:
            # Intent detection
            if 'study plan' in message_lower:
                response = self._generate_study_plan(message)
            elif 'roadmap' in message_lower:
                response = self._generate_roadmap(message)
            elif 'explain' in message_lower or 'what is' in message_lower:
                response = self._explain_topic(message_lower)
            elif 'progress' in message_lower:
                response = self._show_progress()
            elif 'assignment' in message_lower:
                response = self._handle_assignment(message_lower)
            elif 'welcome' in message_lower or 'hi' in message_lower or 'hello' in message_lower:
                response = self._welcome_message()
            else:
                response = self._llm_response(message_lower)

        # Store assistant response
        self._store_message(response["message"], "assistant")
        self.memory.add_ai_message(response["message"])

        return response

    def _welcome_message(self):
        welcome_msg = f"Hi {self.user_data['name']}! I'm your teaching assistant. How can I assist you today? You can ask for a study plan, roadmap, topic explanation, progress update, or manage assignments."
        
        today = datetime.utcnow().date()
        if self.last_interaction_date and self.current_roadmap and self.current_phase:
            welcome_msg += f"\n\nWelcome back! Last time, we were working on your {self.current_roadmap} roadmap, specifically {self.current_phase}. Did you complete the tasks where you left off?"
            logging.debug(f"Generated follow-up welcome message for user: {self.user_data['email']}")
            return {
                "message": welcome_msg,
                "quick_replies": ["Yes, I completed them", "No, I need help"]
            }
        
        return {
            "message": welcome_msg,
            "quick_replies": []
        }

    def _handle_follow_up_response(self, message):
        self.follow_up_active = False
        if 'yes' in message:
            return {
                "message": f"Awesome, {self.user_data['name']}! Since you're in {self.current_phase}, have you completed the practice tasks? For example, solving problems like calculating a factorial or checking if a number is prime. Let me know how it’s going!",
                "quick_replies": ["Yes, I’ve completed them", "No, I need help"]
            }
        elif 'no' in message:
            return {
                "message": f"No worries, {self.user_data['name']}! Let’s get you started. In {self.current_phase}, you should begin with setting up Python and an IDE. Have you installed Python and an IDE like VS Code or PyCharm yet?",
                "quick_replies": ["Yes, I’ve set it up", "No, I need help"]
            }
        else:
            return {
                "message": f"I didn’t quite understand that. Let’s make sure you’re on track with your roadmap. Have you started working on the tasks in {self.current_phase}?",
                "quick_replies": ["Yes", "No"]
            }

    def _generate_study_plan(self, message):
        try:
            hours = int(re.search(r'(\d+)\s*hours?', message).group(1)) if re.search(r'(\d+)\s*hours?', message) else 2
            exam_date = re.search(r'(\d{4}-\d{2}-\d{2})', message).group(1) if re.search(r'(\d{4}-\d{2}-\d{2})', message) else "2025-06-01"
            subjects = re.findall(r'subjects\s+([\w\s,]+)', message)
            subjects = subjects[0].split(',') if subjects else ["Python", "DSA"]
            subjects = [s.strip() for s in subjects]

            plan = self.study_planner.generate_study_plan(hours, exam_date, subjects, user_request=message)
            return {
                "message": plan,
                "quick_replies": []
            }
        except Exception as e:
            logging.error(f"Error generating study plan: {str(e)}")
            return {
                "message": f"Error generating study plan: {str(e)}",
                "quick_replies": []
            }

    def _generate_roadmap(self, message):
        try:
            subject = re.search(r'roadmap\s+for\s+([\w\s]+)', message)
            subject = subject.group(1).strip() if subject else "Python"

            roadmap = self.roadmap_generator.generate_roadmap(subject, self.user_data['year'], self.user_data['department'], user_request=message)

            self.current_roadmap = subject.capitalize()
            self.current_phase = "Phase 1: Getting Started (Weeks 1-2)"
            self.follow_up_active = True

            return {
                "message": roadmap + f"\nLet’s make sure you’re on track, {self.user_data['name']}! Have you started working on {self.current_phase} of your {subject} roadmap?",
                "quick_replies": ["Yes", "No"]
            }
        except Exception as e:
            logging.error(f"Error generating roadmap: {str(e)}")
            return {
                "message": f"Error generating roadmap: {str(e)}",
                "quick_replies": []
            }

    def _explain_topic(self, message):
        try:
            topic = re.search(r'(explain|what is)\s+([\w\s]+)', message)
            topic = topic.group(2).strip() if topic else "unknown topic"
            
            history = "\n".join([msg.content for msg in self.memory.messages])
            prompt = "You are a teaching assistant. Below is the conversation history:\n"
            prompt += history
            prompt += f"\n\nUser: {self.user_data['name']} (Year {self.user_data['year']}, {self.user_data['department']})\nQuestion: Explain {topic}\nAnswer as a helpful teaching assistant with detailed examples."

            explanation = self.llm_service.generate_response(prompt)
            
            return {
                "message": explanation,
                "quick_replies": ["Yes, explain more", "No, I’m good"]
            }
        except Exception as e:
            logging.error(f"Error explaining topic: {str(e)}")
            return {
                "message": f"Error explaining topic: {str(e)}",
                "quick_replies": []
            }

    def _show_progress(self):
        try:
            progress = self.progress_tracker.get_progress()
            return {
                "message": progress,
                "quick_replies": []
            }
        except Exception as e:
            logging.error(f"Error retrieving progress: {str(e)}")
            return {
                "message": f"Error retrieving progress: {str(e)}",
                "quick_replies": []
            }

    def _handle_assignment(self, message):
        try:
            if 'add assignment' in message:
                title = re.search(r'add assignment\s+([\w\s]+)', message)
                title = title.group(1).strip() if title else "Untitled"
                due_date = re.search(r'due\s+(\d{4}-\d{2}-\d{2})', message)
                due_date = due_date.group(1) if due_date else "2025-06-01"
                self.assignment_manager.add_assignment(title, due_date)
                return {
                    "message": f"Assignment '{title}' added with due date {due_date}.",
                    "quick_replies": []
                }
            else:
                assignments = self.assignment_manager.view_assignments()
                return {
                    "message": assignments,
                    "quick_replies": []
                }
        except Exception as e:
            logging.error(f"Error handling assignment: {str(e)}")
            return {
                "message": f"Error handling assignment: {str(e)}",
                "quick_replies": []
            }

    def _llm_response(self, message):
        try:
            history = "\n".join([msg.content for msg in self.memory.messages])
            prompt = "You are a teaching assistant. Below is the conversation history:\n"
            prompt += history
            prompt += f"\n\nUser: {self.user_data['name']} (Year {self.user_data['year']}, {self.user_data['department']})\nQuestion: {message}\nAnswer as a helpful teaching assistant with detailed examples."

            response = self.llm_service.generate_response(prompt)

            return {
                "message": response,
                "quick_replies": ["Yes, show examples", "No, I’ll try on my own"]
            }
        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            return {
                "message": f"Error generating response: {str(e)}",
                "quick_replies": []
            }
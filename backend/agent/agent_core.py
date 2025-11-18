import google.generativeai as genai
import json
import re
from .memory import ChatMemory
from .tools import AgentTools

class ElevateUAgent:
    def __init__(self, mongo_db, api_key):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.memory = ChatMemory(mongo_db)
        self.tools = AgentTools(mongo_db)
        self.is_initialized = True
        print(" * ElevateU Agent initialized with Gemini model")

    def clean_json_response(self, text):
        """Clean JSON response from markdown code blocks"""
        if not text:
            return text
        # Remove ```json and ``` markers
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        return text.strip()

    def build_prompt(self, user_message, user_context, conversation_history):
        return f"""
You are ElevateU Agent — a friendly learning assistant for an online learning platform.

USER CONTEXT:
{json.dumps(user_context, indent=2) if user_context else "No user context available"}

CONVERSATION HISTORY (last 5 messages):
{conversation_history}

USER MESSAGE: "{user_message}"

RESPONSE REQUIREMENTS:
- Be conversational and helpful
- If user asks about progress, courses, learning, or recommendations, provide specific answers
- For progress-related questions, use action: "get_progress"
- For course recommendations, use action: "recommend_courses"  
- For general questions, just answer conversationally with action: "none"

CRITICAL: You MUST respond with VALID JSON only in this exact format:
{{
  "reply": "Your helpful response here",
  "action": "none|get_progress|recommend_courses",
  "parameters": {{}}
}}

EXAMPLES:
- User: "What is Python?" → {{"reply": "Python is a popular programming language known for being beginner-friendly!", "action": "none", "parameters": {{}}}}
- User: "Show my progress" → {{"reply": "Let me check your learning progress!", "action": "get_progress", "parameters": {{}}}}
- User: "What courses should I take?" → {{"reply": "I'll find some great courses for you!", "action": "recommend_courses", "parameters": {{}}}}
""".strip()

    def process_message(self, message, user_id):
        if not hasattr(self, 'is_initialized') or not self.is_initialized:
            return {
                "reply": "I'm still getting ready. Please try again in a moment.",
                "action": "none"
            }

        try:
            print(f" * Processing message from user {user_id}: '{message}'")
            
            # Load context + memory
            user_context = self.tools.get_user_context(user_id)
            history = self.memory.get_recent_history(user_id)

            print(f" * User context: {user_context}")
            print(f" * Conversation history: {history}")

            # Build structured prompt
            prompt = self.build_prompt(message, user_context, history)
            print(f" * Prompt built, length: {len(prompt)}")

            # Model response
            ai_response = self.model.generate_content(prompt)
            raw_text = ai_response.text
            print(f" * Raw AI response: {raw_text}")

            # Clean and parse JSON response
            cleaned_response = self.clean_json_response(raw_text)
            print(f" * Cleaned response: {cleaned_response}")

            # Parse JSON response
            try:
                parsed_response = json.loads(cleaned_response)
                clean_reply = parsed_response.get("reply", "I'm here to help! Could you please rephrase that?")
                action = parsed_response.get("action", "none")
                parameters = parsed_response.get("parameters", {})
                
                print(f" * Parsed - Reply: '{clean_reply}', Action: '{action}'")
                
            except json.JSONDecodeError as e:
                print(f" * JSON parsing failed: {e}")
                # If JSON parsing fails, use the raw text as reply
                clean_reply = raw_text if raw_text else "I'm here to help! Could you please rephrase your question?"
                action = "none"
                parameters = {}

            # Save memory
            self.memory.save_message(user_id, "user", message)
            self.memory.save_message(user_id, "agent", clean_reply)

            # Handle agent response with the parsed data
            result = self.tools.handle_agent_response({
                "reply": clean_reply,
                "action": action,
                "parameters": parameters
            }, user_id)
            
            print(f" * Final result: {result}")
            return result
            
        except Exception as e:
            print(f" * Error in process_message: {e}")
            import traceback
            traceback.print_exc()
            return {
                "reply": "I encountered an error while processing your message. Please try again.",
                "action": "none"
            }
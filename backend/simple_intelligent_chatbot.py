# ======================================================================
#  ElevateU Agentic Chatbot (Gemini 2.5 Flash)
#  ONLY Tracks Progress, Suggests Next Steps, Motivates
#  NO teaching, NO external tools, NO topic explanation
# ======================================================================

import os
import google.generativeai as genai
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

class SimpleIntelligentChatbot:
    """
    ElevateU Agent:
    - Tracks user progress
    - Reads course enrollments & completed topics
    - Gives intelligent analysis + motivation
    - Suggests next steps (but NEVER teaches topics)
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.conversation_history = {}

        if not self.api_key:
            print("⚠️ GEMINI_API_KEY missing → running in fallback mode")
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            print("✨ ElevateU Agent initialized with Gemini 2.5 Flash")
        except Exception as e:
            print(f"⚠️ Failed to init Gemini: {e}")
            self.model = None

    # ------------------------------------------------------------------
    # Build proper structured context from backend /api/chatbot/message
    # ------------------------------------------------------------------
    def _extract_learning_context(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        From backend user_context → convert to a standardized format.
        """
        try:
            if not user_data or not isinstance(user_data, dict):
                return {"status": "new_user"}

            # Safely extract data with defaults
            user_info = user_data.get("user", {})
            learning_info = user_data.get("learning", {})
            enrollments = user_data.get("enrollments", [])
            course_progress = learning_info.get("courseProgress", [])
            
            # Ensure course_progress is a list
            if not isinstance(course_progress, list):
                course_progress = []

            # Calculate learning statistics safely
            total_courses = len(course_progress)
            completed_courses = 0
            active_courses = 0
            total_progress = 0

            for course in course_progress:
                if isinstance(course, dict):
                    progress_val = course.get("progress", 0)
                    if isinstance(progress_val, (int, float)):
                        total_progress += progress_val
                        if progress_val >= 100:
                            completed_courses += 1
                        elif progress_val > 0:
                            active_courses += 1

            avg_progress = total_progress / total_courses if total_courses > 0 else 0

            return {
                "status": "active_user",
                "name": user_info.get("name", "Learner"),
                "total_courses": total_courses,
                "completed_courses": completed_courses,
                "active_courses": active_courses,
                "avg_progress": round(avg_progress, 2),
                "course_progress": course_progress,
                "recommendations": user_data.get("recommendations", []),
                "enrollments": enrollments
            }
        except Exception as e:
            print(f"Error in _extract_learning_context: {e}")
            return {"status": "error"}

    # ------------------------------------------------------------------
    # Gemini Response Logic (Agent Mode)
    # ------------------------------------------------------------------
    def _build_prompt(self, message: str, ctx: Dict[str, Any]) -> str:
        """
        Strict instruction: DO NOT teach topics. ONLY track progress.
        """
        try:
            lines = []
            lines.append("You are ElevateU's AI Progress Tracker - a specialized assistant that ONLY tracks learning progress and motivates users.")
            lines.append("")
            lines.append("STRICT RULES:")
            lines.append("1. You DO NOT teach, explain, or provide educational content about any topics")
            lines.append("2. You ONLY analyze progress, completed topics, and learning trends")
            lines.append("3. If user asks to explain/teach → politely redirect to external resources")
            lines.append("4. You suggest next logical topics to complete based on progress")
            lines.append("5. You provide motivation and keep users accountable")
            lines.append("6. Keep responses concise, friendly, and focused on progress tracking")
            lines.append("")

            # Add user data
            lines.append("USER LEARNING CONTEXT:")
            lines.append(f"- Name: {ctx.get('name', 'Learner')}")
            lines.append(f"- Total Courses: {ctx.get('total_courses', 0)}")
            lines.append(f"- Active Courses: {ctx.get('active_courses', 0)}")
            lines.append(f"- Completed Courses: {ctx.get('completed_courses', 0)}")
            lines.append(f"- Average Progress: {ctx.get('avg_progress', 0)}%")
            lines.append("")

            # Add detailed course progress
            course_progress = ctx.get("course_progress", [])
            if course_progress:
                lines.append("COURSE PROGRESS DETAILS:")
                for course in course_progress:
                    if not isinstance(course, dict):
                        continue
                        
                    lines.append(f"📚 {course.get('courseTitle', 'Unknown Course')}")
                    lines.append(f"   Progress: {course.get('progress', 0)}% ({len(course.get('completedTopics', []))}/{course.get('totalTopics', 0)} topics)")
                    
                    # Show completed topics
                    completed = course.get('completedTopics', [])
                    topics = course.get('topics', [])
                    if completed and topics and isinstance(completed, list) and isinstance(topics, list):
                        completed_titles = []
                        for i in completed[:3]:  # Show only first 3
                            if i < len(topics) and isinstance(topics[i], dict):
                                completed_titles.append(topics[i].get('title', f'Topic {i+1}'))
                        if completed_titles:
                            lines.append(f"   ✅ Completed: {', '.join(completed_titles)}")
                    
                    # Suggest next topics
                    if isinstance(topics, list):
                        remaining = []
                        for i in range(len(topics)):
                            if i not in completed:
                                if i < len(topics) and isinstance(topics[i], dict):
                                    remaining.append(topics[i].get('title', f'Topic {i+1}'))
                        if remaining:
                            lines.append(f"   ➡️ Next: {remaining[0]}")
                    lines.append("")
            else:
                lines.append("No active course enrollments.")
                lines.append("")

            lines.append(f"USER QUESTION: {message}")
            lines.append("")
            lines.append("RESPONSE GUIDELINES:")
            lines.append("- Focus on progress analysis and motivation")
            lines.append("- Suggest next logical steps, not explanations")
            lines.append("- Be encouraging and accountability-focused")
            lines.append("- Never provide educational content")

            return "\n".join(lines)
        except Exception as e:
            print(f"Error in _build_prompt: {e}")
            return f"User asked: {message}. Respond as a progress tracker focusing only on learning progress and motivation."

    # ------------------------------------------------------------------
    # Response Generator
    # ------------------------------------------------------------------
    def generate_response(self, message: str, user_data: Dict[str, Any], user_id: Optional[str]):
        try:
            ctx = self._extract_learning_context(user_data)

            # Handle different user states
            if ctx.get("status") == "new_user":
                return {
                    "response": "Hi! 👋 I'm your ElevateU Progress Tracker. I help monitor your learning journey. Once you enroll in courses, I'll track your progress, suggest next steps, and keep you motivated!",
                    "response_type": "welcome",
                    "context_used": False,
                    "suggested_actions": ["Browse Courses", "Enroll in a Course"],
                    "user_context_summary": "New user - no enrollments yet"
                }

            if ctx.get("status") == "error":
                return {
                    "response": "Hello! I'm here to help track your learning progress. Let me know what courses you're working on and I'll help you stay on track!",
                    "response_type": "greeting",
                    "context_used": False,
                    "suggested_actions": ["Browse Courses", "Check Progress"],
                    "user_context_summary": "Error loading user data"
                }

            # Fallback if Gemini is offline
            if not self.model:
                if ctx['total_courses'] == 0:
                    response_text = "Welcome to ElevateU! Start by browsing available courses and enrolling in ones that interest you. I'll track your progress once you begin learning!"
                    actions = ["Browse Courses", "Find Recommendations"]
                else:
                    response_text = f"Great work on your learning journey! You're enrolled in {ctx['total_courses']} course(s) with {ctx['completed_courses']} completed and an average progress of {ctx['avg_progress']}%. Keep updating your completed topics to stay on track! 🚀"
                    actions = ["View Progress", "Update Topics", "See Recommendations"]

                return {
                    "response": response_text,
                    "response_type": "progress_update",
                    "context_used": True,
                    "suggested_actions": actions,
                    "user_context_summary": f"{ctx['total_courses']} courses, {ctx['avg_progress']}% avg progress"
                }

            # If Gemini is available
            prompt = self._build_prompt(message, ctx)

            result = self.model.generate_content(prompt)
            text = result.text.strip()

            # Determine response type
            response_type = "progress_analysis"
            message_lower = message.lower()
            if any(word in message_lower for word in ['hi', 'hello', 'hey']):
                response_type = "greeting"
            elif any(word in message_lower for word in ['progress', 'status', 'how am i']):
                response_type = "progress_update"
            elif any(word in message_lower for word in ['next', 'what should', 'recommend']):
                response_type = "next_steps"

            return {
                "response": text,
                "response_type": response_type,
                "context_used": True,
                "suggested_actions": ["View Progress", "Mark Topic Complete", "Browse Courses"],
                "user_context_summary": f"{ctx['total_courses']} courses, {ctx['avg_progress']}% avg, {ctx['completed_courses']} completed"
            }

        except Exception as e:
            print(f"Error in generate_response: {e}")
            return {
                "response": "I'm here to track your learning progress! Let me know what courses you're working on and I'll help you stay motivated and on track. 📚",
                "response_type": "fallback",
                "context_used": False,
                "suggested_actions": ["Browse Courses", "Check Progress"],
                "user_context_summary": "Error in response generation"
            }

    # ------------------------------------------------------------------
    # Entry point used by app.py
    # ------------------------------------------------------------------
    def process_message(self, message, user_data=None, user_id=None, **kwargs):
        try:
            response = self.generate_response(message, user_data or {}, user_id)

            # Log conversation
            if user_id:
                self.conversation_history.setdefault(user_id, []).append({
                    "user": message,
                    "bot": response["response"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "context_used": response.get("context_used", False)
                })

            return response
        except Exception as e:
            print(f"Error in process_message: {e}")
            return {
                "response": "I'm here to help with your learning journey! I can track your progress and suggest next steps. What would you like to know?",
                "response_type": "error_fallback",
                "context_used": False,
                "suggested_actions": ["Browse Courses", "Check Progress"]
            }
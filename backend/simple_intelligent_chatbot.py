import os
import google.generativeai as genai
from datetime import datetime
from typing import Dict, List, Any, Optional
import random

class SimpleIntelligentChatbot:
    """Simple but truly intelligent chatbot that understands user context"""

    def __init__(self):
        """Initialize the intelligent chatbot"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.conversation_history = {}

        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found. Running in intelligent fallback mode.")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("+ Simple Intelligent Chatbot initialized with Gemini 2.0 Flash")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini: {e}")
                print("Chatbot will run in intelligent fallback mode.")

    def analyze_user_context(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's learning context from their data"""
        if not user_data:
            return {
                'status': 'new_user',
                'total_courses': 0,
                'completed_courses': 0,
                'in_progress': 0,
                'average_progress': 0,
                'last_active': None
            }

        user_info = user_data.get('user', {})
        learning_info = user_data.get('learning', {})
        enrollments = user_data.get('enrollments', [])

        # Calculate real metrics from actual data
        total_courses = len(enrollments)
        completed_courses = sum(1 for e in enrollments if e.get('progress', 0) >= 100)
        in_progress = sum(1 for e in enrollments if 0 < e.get('progress', 0) < 100)
        average_progress = sum(e.get('progress', 0) for e in enrollments) / max(len(enrollments), 1)

        # Find last activity
        last_active = None
        for enrollment in enrollments:
            if enrollment.get('lastAccessed'):
                last_active = enrollment['lastAccessed']
                break

        return {
            'status': 'active_user',
            'user_name': user_info.get('name', 'there'),
            'total_courses': total_courses,
            'completed_courses': completed_courses,
            'in_progress': in_progress,
            'average_progress': round(average_progress, 1),
            'last_active': last_active,
            'completion_rate': round((completed_courses / max(total_courses, 1)) * 100, 1),
            'enrolled_courses': [e.get('course', {}) for e in enrollments],
            'recommendations': user_data.get('recommendations', [])
        }

    def generate_intelligent_response(self, message: str, context: Dict[str, Any], user_name: str) -> Dict[str, Any]:
        """Generate intelligent response based on user context"""
        message_lower = message.lower().strip()

        # Always use the user context to generate responses
        if not context:
            return self.get_new_user_response(message, user_name)

        status = context['status']
        user_name = context.get('user_name', user_name)
        total_courses = context['total_courses']
        completed_courses = context['completed_courses']
        in_progress = context['in_progress']
        avg_progress = context['average_progress']
        completion_rate = context['completion_rate']

        # Generate responses based on actual user data
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return self.get_intelligent_greeting(user_name, context)

        elif any(word in message_lower for word in ['progress', 'how am i', 'doing', 'status']):
            return self.get_progress_analysis(context)

        elif any(word in message_lower for word in ['recommend', 'suggest', 'what should', 'next']):
            return self.get_smart_recommendations(context)

        elif any(word in message_lower for word in ['help', 'stuck', 'can\'t', 'difficult']):
            return self.get_help_response(context, message)

        elif any(word in message_lower for word in ['motivat', 'encourage', 'can\'t focus']):
            return self.get_motivation_response(context)

        elif any(word in message_lower for word in ['courses', 'enrolled', 'taking']):
            return self.get_courses_response(context)

        else:
            return self.get_contextual_response(message, context)

    def get_intelligent_greeting(self, user_name: str, context: Dict) -> Dict[str, Any]:
        """Generate intelligent greeting based on user data"""
        status = context['status']
        total_courses = context['total_courses']
        avg_progress = context['average_progress']

        if status == 'new_user' or total_courses == 0:
            response = f"Hi {user_name}! 👋 I see you're just getting started with ElevateU. I'm here to help you succeed! What kind of topics interest you? We have Python, GenAI, and JavaScript courses available."
        elif avg_progress >= 70:
            response = f"Welcome back {user_name}! You're doing exceptionally well with {avg_progress}% average progress! Your consistency is really paying off. How can I help you continue your learning journey?"
        elif avg_progress >= 30:
            response = f"Hi {user_name}! 👋 Great to see you again! You're making solid progress with {avg_progress}% completion. You're building real momentum! What can I help you with today?"
        else:
            response = f"Hi {user_name}! 👋 Welcome back! I can see you have {in_progress} course(s) in progress and have completed {completed_courses} courses. Let's get you back on track! What would you like to work on?"

        return {
            'response': response,
            'response_type': 'intelligent_greeting',
            'suggested_actions': [
                "View my learning analytics",
                "Get course recommendations",
                "Ask about study tips"
            ],
            'context_used': True,
            'agent_used': True
        }

    def get_progress_analysis(self, context: Dict) -> Dict[str, Any]:
        """Generate detailed progress analysis"""
        user_name = context.get('user_name', 'there')
        total_courses = context['total_courses']
        completed_courses = context['completed_courses']
        in_progress = context['in_progress']
        avg_progress = context['average_progress']
        completion_rate = context['completion_rate']

        response_parts = []

        if total_courses > 0:
            response_parts.append(f"You're enrolled in {total_courses} courses")

        if completed_courses > 0:
            response_parts.append(f"and have completed {completed_courses} of them")

        if avg_progress > 0:
            response_parts.append(f"with an average progress of {avg_progress}%")

        response = " ".join(response_parts) + "."

        # Add intelligent insights
        if completion_rate >= 75:
            response += f" Your completion rate of {completion_rate}% is excellent! You're in the top 20% of learners!"
        elif completion_rate >= 50:
            response += f" With a {completion_rate}% completion rate, you're doing well above average."
        elif completion_rate < 25 and total_courses > 2:
            response += f" Your completion rate is {completion_rate}% - let's work on finishing what you start!"

        if in_progress > 2:
            response += f" You have {in_progress} courses in progress - consider focusing on 1-2 at a time for better results."

        return {
            'response': response,
            'response_type': 'progress_analysis',
            'suggested_actions': [
                "Set learning goals",
                "Get personalized study plan",
                "View course details"
            ],
            'context_used': True,
            'agent_used': True
        }

    def get_smart_recommendations(self, context: Dict) -> Dict[str, Any]:
        """Generate smart course recommendations based on user data"""
        completed_courses = context['completed_courses']
        in_progress = context['in_progress']
        avg_progress = context['average_progress']
        recommendations = context.get('recommendations', [])

        response_parts = []

        if completed_courses > 0:
            response_parts.append(f"Great job completing {completed_courses} course(s)!")

        if in_progress > 0:
            response_parts.append(f"You have {in_progress} course(s) in progress")

        if avg_progress > 60:
            response_parts.append("and you're progressing well")
            if len(recommendations) > 0:
                response_parts.append("so you're ready for advanced topics.")
        elif avg_progress < 30:
            response_parts.append("but let's focus on building consistency")
        else:
            response_parts.append("with good momentum")

        response = " ".join(response_parts) + "." if response_parts else "Here are some options for you."

        if len(recommendations) > 0:
            top_courses = recommendations[:2]
            course_titles = [c.get('title', 'Course') for c in top_courses]
            response += f" Based on your progress, I recommend trying: {', '.join(course_titles)}."
        else:
            response += " Check out our Python and GenAI courses - they're very popular and well-structured!"

        return {
            'response': response,
            'response_type': 'smart_recommendation',
            'suggested_actions': [
                "Browse all courses",
                "Enroll in recommended course",
                "Get study schedule"
            ],
            'context_used': True,
            'agent_used': True
        }

    def get_help_response(self, context: Dict, user_message: str) -> Dict[str, Any]:
        """Provide specific help based on user's situation"""
        user_name = context.get('user_name', 'there')
        in_progress = context['in_progress']
        enrolled_courses = context.get('enrolled_courses', [])
        course_titles = [c.get('title', 'your course') for c in enrolled_courses if c.get('title')]

        if in_progress > 0 and course_titles:
            response = f"I can see you're working on {course_titles[0]}. "
            response += "What specific topic or concept are you struggling with? "
            response += "I can provide explanations, suggest resources, or break down complex topics. Remember, asking for help is smart!"
        else:
            response = f"I'm here to help you succeed, {user_name}! "
            response += "Whether you need course recommendations, study strategies, or motivation - I've got your back. "
            response += "What specific challenge are you facing with?"

        return {
            'response': response,
            'response_type': 'intelligent_help',
            'suggested_actions': [
                "Get study resources",
                "Book help session",
                "Join study group"
            ],
            'context_used': True,
            'agent_used': True
        }

    def get_motivation_response(self, context: Dict) -> Dict[str, Any]:
        """Provide personalized motivation"""
        user_name = context.get('user_name', 'there')
        avg_progress = context['average_progress']
        completion_rate = context['completion_rate']

        motivations = [
            f"Every expert was once a beginner, {user_name}! Your progress of {avg_progress}% shows real commitment.",
            f"You're building real skills that will serve you well! Keep up the excellent work.",
            f"Remember that progress isn't always linear, but your dedication will lead to success!",
            f"Your consistency is creating opportunities you can't even see yet!",
            f"Learning is a journey, not a race. You're exactly where you need to be right now!"
        ]

        if avg_progress > 70:
            motivation = f"You're crushing it with {avg_progress}% progress! {random.choice(motivations)}"
        elif avg_progress > 40:
            motivation = f"You're making solid progress at {avg_progress}%. {random.choice(motivations)}"
        else:
            motivation = f"Every small step counts. {random.choice(motivations)}"

        return {
            'response': motivation,
            'response_type': 'personalized_motivation',
            'suggested_actions': [
                "Set daily goals",
                "Track progress",
                "Get study buddy"
            ],
            'context_used': True,
            'agent_used': True
        }

    def get_courses_response(self, context: Dict) -> Dict[str, Any]:
        """Respond to questions about courses"""
        user_name = context.get('user_name', 'there')
        enrolled_courses = context.get('enrolled_courses', [])

        if enrolled_courses:
            course_list = [c.get('title', 'your courses') for c in enrolled_courses]
            response = f"You're enrolled in: {', '.join(course_list)}. "
            response += "Which one would you like to focus on today? I can help you with specific topics or study plans!"
        else:
            response = f"You haven't enrolled in any courses yet, {user_name}! "
            response += "Check out our course catalog - we have excellent options in Python, GenAI, and JavaScript. Which area interests you most?"

        return {
            'response': response,
            'response_type': 'courses_info',
            'suggested_actions': [
                "Browse course catalog",
                "Enroll in course",
                "Get learning plan"
            ],
            'context_used': True,
            'agent_used': True
        }

    def get_contextual_response(self, message: str, context: Dict) -> Dict[str, Any]:
        """Generate contextual response using available data"""
        user_name = context.get('user_name', 'there')

        # Try Gemini if available
        if self.model:
            try:
                prompt = f"""You are an intelligent learning assistant for ElevateU with full user context.

User Context:
- User: {user_name}
- Total Courses: {context.get('total_courses', 0)}
- Completed: {context.get('completed_courses', 0)}
- In Progress: {context['in_progress']}
- Average Progress: {context['average_progress']}%
- Completion Rate: {context['completion_rate']}%

User Question: {message}

Provide a helpful, personalized response that shows you understand their learning journey. Keep it conversational and actionable."""

                response = self.model.generate_content(prompt)
                response_text = response.text.strip()

                if len(response_text) > 300:
                    sentences = response_text.split('.')[:3]
                    response_text = '.'.join(sentences).strip() + '.'

                return {
                    'response': response_text,
                    'response_type': 'contextual_intelligent',
                    'suggested_actions': ["View progress", "Get recommendations", "Study tips"],
                    'context_used': True,
                    'agent_used': True
                }
            except Exception as e:
                print(f"Gemini error: {e}")
                pass

        # Fallback to intelligent rule-based
        return {
            'response': f"I understand you're asking about '{message}'. Based on your learning journey with ElevateU, I can provide personalized guidance. What specific aspect would you like help with?",
            'response_type': 'intelligent_fallback',
            'suggested_actions': ["Tell me more", "View my progress", "Get recommendations"],
            'context_used': True,
            'agent_used': True
        }

    def get_new_user_response(self, message: str, user_name: str) -> Dict[str, Any]:
        """Response for new users"""
        if any(word in message.lower() for word in ['hello', 'hi', 'hey']):
            return {
                'response': f"Hi {user_name}! 👋 Welcome to ElevateU! I'm your AI learning assistant. I'm excited to help you discover and succeed in your learning journey!",
                'response_type': 'new_user_greeting',
                'suggested_actions': ["Browse courses", "Get started guide", "Learn about platform"],
                'context_used': True,
                'agent_used': True
            }

        return {
            'response': f"Hi {user_name}! I'm here to help you on your ElevateU learning journey! Whether you need course recommendations, study tips, or motivation - I'm your personal learning assistant!",
            'response_type': 'new_user_info',
            'suggested_actions': ["Browse courses", "Get study tips", "Start learning"],
            'context_used': True,
            'agent_used': True
        }

    def process_message(self, message: str, user_data: Optional[Dict[str, Any]] = None,
                       user_id: Optional[str] = None, user_name: Optional[str] = None,
                       user_email: Optional[str] = None) -> Dict[str, Any]:
        """Process message with intelligent context awareness"""
        try:
            user_name = user_name or "there"

            # Analyze user context
            context = self.analyze_user_context(user_data or {})

            # Generate intelligent response
            response_data = self.generate_intelligent_response(message, context, user_name)

            # Store conversation
            if user_id:
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []

                self.conversation_history[user_id].append({
                    'user': message,
                    'bot': response_data['response'],
                    'timestamp': datetime.now().isoformat(),
                    'context': context
                })

                # Keep only last 10 exchanges
                if len(self.conversation_history[user_id]) > 10:
                    self.conversation_history[user_id] = self.conversation_history[user_id][-10:]

            # Add metadata
            response_data.update({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'user_email': user_email,
                'session_id': f"session_{datetime.now().timestamp()}",
                'agent_version': 'simple_intelligent_v1.0'
            })

            return response_data

        except Exception as e:
            print(f"Error in intelligent chatbot processing: {e}")
            return {
                'response': f"Hi there! I'm your intelligent ElevateU learning assistant. I can analyze your progress, recommend courses, and provide personalized guidance. How can I help you today?",
                'response_type': 'error',
                'suggested_actions': ["Browse courses", "Get started", "Help topics"],
                'error': str(e),
                'agent_used': False,
                'context_used': False
            }

# Create fallback function
def create_intelligent_response(message: str, user_name: str = "there", user_data: Dict = None) -> Dict[str, Any]:
    """Create intelligent fallback responses"""
    message_lower = message.lower()

    # Analyze basic user data if available
    if user_data:
        enrollments = user_data.get('enrollments', [])
        total_enrollments = len(enrollments)

        if total_enrollments > 0:
            if any(word in message_lower for word in ['hello', 'hi']):
                return {
                    'response': f"Hi {user_name}! 👋 I can see you're enrolled in {total_enrollments} courses. How's your learning journey going?",
                    'response_type': 'intelligent_greeting',
                    'suggested_actions': ["View progress", "Get recommendations", "Study tips"]
                }

    # Default intelligent responses
    if any(word in message_lower for word in ['progress', 'doing']):
        return {
            'response': f"I'd love to analyze your progress! With access to your learning data, I can provide insights about completion rates, learning patterns, and personalized recommendations.",
            'response_type': 'progress_check',
            'suggested_actions': ["Detailed analysis", "Set goals", "Compare with average"]
        }

    return {
        'response': f"I'm your intelligent learning assistant! I can analyze your progress, recommend courses based on your patterns, and provide personalized guidance. What would you like to explore?",
        'response_type': 'intelligent_introduction',
        'suggested_actions': ["Analyze progress", "Get recommendations", "Learning insights"]
    }
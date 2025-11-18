import re
import json
from bson import ObjectId
from datetime import datetime

class AgentTools:
    def __init__(self, db):
        self.db = db

    def get_user_context(self, user_id):
        try:
            user = self.db["users"].find_one({"clerkId": user_id})
            if not user:
                return {"error": "User not found"}

            enrollments = list(self.db["enrollments"].find({"userId": user_id}))
            progress_list = list(self.db["progress"].find({"userId": user_id}))

            # Build course progress
            course_progress = []
            for progress in progress_list:
                course_id = progress.get("courseId")
                course = self.db["courses"].find_one({"_id": ObjectId(course_id)})
                if course:
                    completed = len(progress.get("completedTopics", []))
                    total = len(course.get("topics", []))
                    progress_percent = (completed / total * 100) if total > 0 else 0
                    
                    course_progress.append({
                        "courseTitle": course.get("title", "Unknown Course"),
                        "progress": progress_percent,
                        "completedTopics": completed,
                        "totalTopics": total
                    })

            return {
                "name": user.get("name"),
                "email": user.get("email"),
                "totalEnrollments": len(enrollments),
                "courseProgress": course_progress,
                "hasProgress": len(course_progress) > 0
            }
        except Exception as e:
            print(f"Error in get_user_context: {e}")
            return {"error": str(e)}

    def handle_agent_response(self, parsed_response, user_id):
        """Handle agent response with parsed data"""
        action = parsed_response.get("action", "none")
        reply = parsed_response.get("reply", "I'm here to help!")
        parameters = parsed_response.get("parameters", {})
        
        print(f" * Tools handling - Action: {action}, Reply: {reply}")

        # For most cases, just return the clean reply
        if action == "none":
            return {"reply": reply, "action": "none"}

        if action == "get_progress":
            return self._handle_get_progress(user_id, reply)
            
        if action == "recommend_courses":
            return self._handle_recommend_courses(user_id, reply)
            
        if action == "update_progress":
            return self._handle_update_progress(user_id, parameters, reply)

        # Default fallback
        return {"reply": reply, "action": "none"}

    def _handle_get_progress(self, user_id, base_reply):
        """Handle get progress action"""
        try:
            progress_list = list(self.db["progress"].find({"userId": user_id}))
            if not progress_list:
                return {
                    "reply": "You haven't started any courses yet. Would you like me to recommend some?",
                    "action": "get_progress"
                }

            progress_details = []
            for progress in progress_list:
                course_id = progress.get("courseId")
                course = self.db["courses"].find_one({"_id": ObjectId(course_id)})
                if course:
                    completed = len(progress.get("completedTopics", []))
                    total = len(course.get("topics", []))
                    progress_percent = (completed / total * 100) if total > 0 else 0
                    
                    progress_details.append({
                        "courseTitle": course.get("title", "Unknown Course"),
                        "progress": progress_percent,
                        "completedTopics": completed,
                        "totalTopics": total
                    })

            # Create a friendly progress summary
            if progress_details:
                summary = "Here's your learning progress:\n\n"
                for detail in progress_details:
                    emoji = "✅" if detail["progress"] >= 80 else "📚" if detail["progress"] >= 50 else "🎯"
                    summary += f"{emoji} **{detail['courseTitle']}**: {detail['progress']:.1f}% complete ({detail['completedTopics']}/{detail['totalTopics']} topics)\n"
                
                reply = f"{base_reply}\n\n{summary}"
            else:
                reply = "I couldn't find your progress details. You may need to enroll in courses first."

            return {
                "reply": reply,
                "action": "get_progress",
                "data": progress_details
            }
            
        except Exception as e:
            print(f"Error in _handle_get_progress: {e}")
            return {
                "reply": "Sorry, I had trouble fetching your progress. Please try again.",
                "action": "get_progress"
            }

    def _handle_recommend_courses(self, user_id, base_reply):
        """Handle course recommendations"""
        try:
            # Get user's enrolled courses
            enrollments = list(self.db["enrollments"].find({"userId": user_id}))
            enrolled_ids = [e["courseId"] for e in enrollments]

            # Find courses not enrolled in
            all_courses = list(self.db["courses"].find())
            recommendations = []
            
            for course in all_courses:
                if str(course["_id"]) not in enrolled_ids:
                    recommendations.append({
                        "title": course.get("title", "Untitled Course"),
                        "description": course.get("description", "No description"),
                        "instructor": course.get("instructor", "Staff"),
                        "topics": len(course.get("topics", [])),
                        "duration": course.get("duration", "Self-paced")
                    })

            # Create recommendation text
            if recommendations:
                rec_text = "Here are some courses you might like:\n\n"
                for rec in recommendations[:3]:  # Limit to 3
                    rec_text += f"🎓 **{rec['title']}**\n"
                    rec_text += f"   👨‍🏫 {rec['instructor']} | ⏱️ {rec['duration']}\n"
                    rec_text += f"   {rec['description'][:100]}...\n\n"
                
                reply = f"{base_reply}\n\n{rec_text}"
            else:
                reply = "You're already enrolled in all available courses! Great job! 🎉"

            return {
                "reply": reply,
                "action": "recommend_courses",
                "recommended": recommendations[:3]
            }
            
        except Exception as e:
            print(f"Error in _handle_recommend_courses: {e}")
            return {
                "reply": "Sorry, I had trouble finding course recommendations.",
                "action": "recommend_courses"
            }

    def _handle_update_progress(self, user_id, parameters, base_reply):
        """Handle progress updates"""
        # Implementation for updating progress
        return {"reply": base_reply, "action": "update_progress"}
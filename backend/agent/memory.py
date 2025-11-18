from datetime import datetime
from bson import ObjectId

class ChatMemory:
    def __init__(self, db):
        self.collection = db["agent_memory"]

    def save_message(self, user_id, role, content):
        self.collection.insert_one({
            "userId": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        })

    def get_recent_history(self, user_id, limit=5):
        messages = list(self.collection.find({"userId": user_id})
                          .sort("timestamp", -1)
                          .limit(limit))
        history = []
        for m in messages:
            history.append(f"{m['role']}: {m['content']}")
        return "\n".join(history[::-1])  # Reverse to show oldest first
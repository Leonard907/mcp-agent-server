class ConversationServer:
    def __init__(self):
        self.question = ""
        self.conversation_history = None
        
    def set_conversation_history(self, history: str):
        self.conversation_history = history
        return {"status": "success", "message": "Conversation history stored successfully"}
    
    def set_question(self, question: str):
        self.question = question
        return {"status": "success", "message": "Question stored successfully"}
        
    def get_conversation_history(self):
        if self.conversation_history is None:
            return {"status": "error", "message": "No conversation history available"}
        return {"conversation": self.conversation_history}
    
    def get_question(self):
        return {"question": self.question}

# Create a singleton instance
conversation_server = ConversationServer() 
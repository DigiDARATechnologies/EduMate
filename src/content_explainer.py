class ContentExplainer:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def explain_topic(self, topic, user_email):
        try:
            # Search for relevant context in the vector store
            context = self.vector_store.search(topic, user_email, top_k=1)
            context_text = context[0] if context else "No relevant context found."

            # Placeholder explanation (replace with LLM call once fixed)
            explanation = (
                f"Here's an explanation of {topic}:\n\n"
                f"This is a placeholder explanation. In a real implementation, I’d use an LLM or knowledge base to explain the topic.\n"
                f"Context from your notes: {context_text}\n\n"
                f"Would you like more details?"
            )
            return explanation
        except Exception as e:
            raise Exception(f"Error explaining topic: {str(e)}")
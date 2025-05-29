from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            url="https://bb433c34-ebbf-4efb-ac53-6299a6e83718.us-east4-0.gcp.cloud.qdrant.io",
            api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.tUOyyQ1XJ31AV9Dlv2DU-Vb4VnNJzEIrrC-rSjDgsGc",
            https=True
        )
        self.collection_name = "edu_mate_documents"
        self.chat_collection_name = "edu_mate_chats"
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

        # Create document collection if it doesn't exist
        try:
            self.client.get_collection(self.collection_name)
            logging.debug(f"Document collection {self.collection_name} exists")
        except Exception as e:
            logging.warning(f"Document collection {self.collection_name} not found, creating it: {str(e)}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "size": 384,
                    "distance": "Cosine"
                }
            )
            logging.debug(f"Created document collection {self.collection_name}")

        # Create chat collection if it doesn't exist
        try:
            self.client.get_collection(self.chat_collection_name)
            logging.debug(f"Chat collection {self.chat_collection_name} exists")
        except Exception as e:
            logging.warning(f"Chat collection {self.chat_collection_name} not found, creating it: {str(e)}")
            self.client.create_collection(
                collection_name=self.chat_collection_name,
                vectors_config={
                    "size": 384,
                    "distance": "Cosine"
                }
            )
            logging.debug(f"Created chat collection {self.chat_collection_name}")

    def store_document(self, text, user_email):
        try:
            embedding = self.encoder.encode(text).tolist()
            doc_id = str(uuid.uuid4())
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    {
                        "id": doc_id,
                        "vector": embedding,
                        "payload": {"text": text, "user_email": user_email}
                    }
                ]
            )
            logging.debug(f"Stored document for user: {user_email}, doc_id: {doc_id}")
        except Exception as e:
            logging.error(f"Error storing document: {str(e)}")
            raise Exception(f"Error storing document: {str(e)}")

    def store_chat_message(self, message, user_email, sender, timestamp, conversation_id=None):
        """Store a chat message in Qdrant with a conversation ID."""
        try:
            message_id = str(uuid.uuid4())
            if conversation_id is None:
                conversation_id = str(uuid.uuid4())  # Generate new conversation ID if not provided
            self.client.upsert(
                collection_name=self.chat_collection_name,
                points=[
                    {
                        "id": message_id,
                        "vector": [0.0] * 384,  # Dummy vector since retrieval uses email filter
                        "payload": {
                            "message": message,
                            "user_email": user_email,
                            "sender": sender,
                            "timestamp": timestamp.isoformat(),
                            "conversation_id": conversation_id
                        }
                    }
                ]
            )
            logging.debug(f"Stored chat message for user: {user_email}, sender: {sender}, message_id: {message_id}, conversation_id: {conversation_id}")
            return conversation_id  # Return conversation_id for session tracking
        except Exception as e:
            logging.error(f"Error storing chat message: {str(e)}")
            raise Exception(f"Error storing chat message: {str(e)}")

    def retrieve_chat_history(self, user_email, conversation_id=None, limit=50):
        """Retrieve chat history for a user, optionally by conversation ID, sorted by timestamp."""
        try:
            logging.debug(f"Retrieving chat history for user: {user_email}, conversation_id: {conversation_id}")
            filter_conditions = [{"key": "user_email", "match": {"value": user_email}}]
            if conversation_id:
                filter_conditions.append({"key": "conversation_id", "match": {"value": conversation_id}})
            
            search_result = self.client.scroll(
                collection_name=self.chat_collection_name,
                scroll_filter={"must": filter_conditions},
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            messages = sorted(
                [hit.payload for hit in search_result[0]],
                key=lambda x: x["timestamp"]
            )
            logging.debug(f"Retrieved {len(messages)} chat messages for user: {user_email}, conversation_id: {conversation_id}")
            return messages
        except Exception as e:
            logging.error(f"Error retrieving chat history: {str(e)}")
            raise Exception(f"Error retrieving chat history: {str(e)}")

    def get_latest_conversation_id(self, user_email):
        """Get the latest conversation ID for a user."""
        try:
            search_result = self.client.scroll(
                collection_name=self.chat_collection_name,
                scroll_filter={"must": [{"key": "user_email", "match": {"value": user_email}}]},
                limit=1,
                with_payload=True,
                with_vectors=False,
                order_by={"key": "timestamp", "direction": "desc"}
            )
            if search_result[0]:
                return search_result[0][0].payload.get("conversation_id")
            return None
        except Exception as e:
            logging.error(f"Error retrieving latest conversation ID: {str(e)}")
            return None

    def search(self, query, user_email, top_k=3):
        try:
            query_embedding = self.encoder.encode(query).tolist()
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,
                query_filter={"must": [{"key": "user_email", "match": {"value": user_email}}]}
            )
            logging.debug(f"Search returned {len(search_result)} results for user: {user_email}")
            return [hit.payload['text'] for hit in search_result]
        except Exception as e:
            logging.error(f"Error searching vector store: {str(e)}")
            raise Exception(f"Error searching vector store: {str(e)}")
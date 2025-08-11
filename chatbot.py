from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

# Check if API key is loaded
if not api_key:
    print("WARNING: API key not found")
else:
    print("API key loaded successfully")

# Configure Google Generative AI with the API key
genai.configure(api_key=api_key)

# Set project folder for FAISS index
project_folder = os.path.join(os.getcwd(), "faiss_index")

# Custom embeddings class to wrap Google's generative AI
class GoogleGenerativeAIEmbeddingsWrapper(Embeddings):
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Using the embedding model
        self.model = "models/embedding-001"
    
    def embed_documents(self, texts):
        """Generate embeddings for a list of documents."""
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result["embedding"])
        return embeddings
    
    def embed_query(self, text):
        """Generate embeddings for a query."""
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return result["embedding"]

# Function to handle user input and generate responses
def process_user_input(user_question, conversation_history=""):
    try:
        # Create custom embeddings object
        embeddings = GoogleGenerativeAIEmbeddingsWrapper(api_key)
        
        # Load FAISS index
        try:
            new_db = FAISS.load_local(project_folder, embeddings, allow_dangerous_deserialization=True)
            docs = new_db.similarity_search(user_question)
        except Exception as e:
            # If FAISS load fails, return error message
            return f"Error loading knowledge base: {str(e)}"
        
        # Create context from relevant documents
        context = "\n".join([doc.page_content for doc in docs])
        
        # Include conversation history in the question if provided
        full_question = f"{conversation_history}\nuser: {user_question}" if conversation_history else user_question
        
        # Create prompt
        prompt = f"""
        Answer the question as detailed as possible from the provided context, make sure to provide all the details. If the answer is not in
        the provided context, just say, "answer is not available in the context"; don't provide a wrong answer.

        Context:
        {context}?

        Question: 
        {full_question}

        Answer:
        """
        
        # Use Gemini 2.0 flash (the latest model)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        return f"Error processing your request: {str(e)}"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_question = data.get('message', '')
    conversation_history = data.get('history', '')
    
    if not user_question:
        return jsonify({"error": "No message provided"}), 400
    
    response = process_user_input(user_question, conversation_history)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
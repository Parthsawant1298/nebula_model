from flask import Flask, request, jsonify
import pandas as pd
import os
import io
import google.generativeai as genai
from flask_cors import CORS
from db_file_system import DBFileSystem
from db_system_integration import apply_patches
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the database file system
db_fs = DBFileSystem()
fs_adapter = apply_patches()

# Virtual storage directory for uploaded files
DATASETS_DIR = 'datasets'
uploaded_files = {}

# Configure Gemini API with key from environment variables
api_key = os.getenv("GEMINI_API_KEY")
print("API Key:", api_key)  # This will help you verify if the key is being read correctly

genai.configure(api_key=api_key)

def chat_with_csv(df, query):
    """
    Chat with CSV data using Gemini
    
    Args:
        df (pd.DataFrame): Input DataFrame
        query (str): User's query about the data
    
    Returns:
        str: Gemini's response to the query
    """
    try:
        # Get DataFrame info
        df_info = df.describe().to_string()
        df_head = df.head(5).to_string()
        df_columns = ', '.join(df.columns.tolist())
        
        # Create prompt for Gemini
        prompt = f"""
        I have a CSV dataset with the following columns: {df_columns}
        
        Here's a sample of the data:
        {df_head}
        
        Here's a statistical summary:
        {df_info}
        
        Based on this data, please answer the following question:
        {query}
        
        Provide a direct and concise answer. If calculations are needed, explain your approach.
        """
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Get response from Gemini
        response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({"success": False, "error": "No file part"})
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        return jsonify({"success": False, "error": "No files selected"})
    
    file_info = []
    
    for file in files:
        if file and file.filename.endswith('.csv'):
            filename = file.filename
            
            # Save to database storage
            db_fs.save_file(file, DATASETS_DIR)
            
            # Store filename for later use
            uploaded_files[filename] = filename
            
            # Read preview data
            try:
                # Get the file content from database
                file_content = db_fs.get_file(filename, DATASETS_DIR)
                
                # Create DataFrame from content
                df = pd.read_csv(io.BytesIO(file_content))
                
                preview = df.head(3).to_dict('records')
                columns = df.columns.tolist()
                file_info.append({
                    "filename": filename,
                    "preview": preview,
                    "columns": columns
                })
            except Exception as e:
                return jsonify({"success": False, "error": f"Error reading CSV: {str(e)}"})
    
    return jsonify({"success": True, "files": file_info})

@app.route('/query', methods=['POST'])
def query_csv():
    data = request.json
    
    if not data or 'filename' not in data or 'query' not in data:
        return jsonify({"success": False, "error": "Missing filename or query"})
    
    filename = data['filename']
    query = data['query']
    
    # Check if file exists in the database
    if not db_fs.file_exists(filename, DATASETS_DIR):
        return jsonify({"success": False, "error": "File not found in database"})
    
    try:
        # Get file content from database
        file_content = db_fs.get_file(filename, DATASETS_DIR)
        
        # Read the content into a DataFrame
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Use the chat_with_csv function with Gemini
        result = chat_with_csv(df, query)
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"})

# Add a route to list all available CSV files in the database
@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        # Get all files from database
        all_files = db_fs.list_files(DATASETS_DIR)
        
        # Filter for CSV files
        csv_files = [f for f in all_files if f.endswith('.csv')]
        
        files = []
        for filename in csv_files:
            # Get file content from database
            try:
                file_content = db_fs.get_file(filename, DATASETS_DIR)
                
                # Read the content into a DataFrame
                df = pd.read_csv(io.BytesIO(file_content))
                
                preview = df.head(3).to_dict('records')
                columns = df.columns.tolist()
                files.append({
                    "filename": filename,
                    "preview": preview,
                    "columns": columns
                })
            except Exception as e:
                # Skip files that can't be read
                print(f"Error reading file {filename}: {str(e)}")
                continue
        
        return jsonify({"success": True, "files": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # Initialize by loading existing CSV files from the database
    try:
        all_files = db_fs.list_files(DATASETS_DIR)
        csv_files = [f for f in all_files if f.endswith('.csv')]
        for filename in csv_files:
            uploaded_files[filename] = filename
    except Exception as e:
        print(f"Error loading existing files: {str(e)}")
    
    app.run(debug=False, port=5002, host='0.0.0.0')
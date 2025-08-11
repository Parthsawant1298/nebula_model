from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import random
import json
import time
import re
import pandas as pd
import io
import csv
import base64
import traceback
import tempfile
from datetime import datetime, timedelta
from db_file_system import DBFileSystem
from db_system_integration import apply_patches

from dotenv import load_dotenv

load_dotenv()

# Optional import - will try to use Gemini but can fallback if unavailable
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google.generativeai package not found. Will use synthetic data generation only.")

app = Flask(__name__)
# Configure CORS to allow requests from frontend
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize the database file system
db_fs = DBFileSystem()
fs_adapter = apply_patches()

# Set dataset directory name in the database
DATASET_DIR = "datasets"
EXPORTS_DIR = "exports"  # This will be a subdirectory in the database

# Global variables
API_AVAILABLE = False

# Try to configure Gemini API if available
if GEMINI_AVAILABLE:
    try:
        # Get API key from environment variables
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        # Set configuration for Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Test the connection
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        response = model.generate_content("Test connection")
        if response and response.text:
            API_AVAILABLE = True
            print("✅ Successfully connected to Gemini API")
        else:
            print("⚠️ Gemini API connection test failed - will use synthetic data")
    except Exception as e:
        print(f"⚠️ Error configuring Gemini API: {str(e)}")
        print("⚠️ Will use synthetic data generation as fallback")
else:
    print("⚠️ Gemini API not available - will use synthetic data generation only")
    
def generate_synthetic_dataset(prompt, rows=100):
    """Generate a synthetic dataset when the API is unavailable"""
    print(f"🔄 Generating synthetic dataset for prompt: {prompt}")
    
    # Create basic column structure based on common patterns in the prompt
    columns = ["id", "name", "category", "value", "date", "status", "description"]
    
    # Check prompt for specific keywords to customize columns
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["customer", "client", "user"]):
        columns = ["customer_id", "customer_name", "location", "purchase_amount", "purchase_date", "is_member", "category"]
    elif any(word in prompt_lower for word in ["product", "item", "inventory"]):
        columns = ["product_id", "product_name", "category", "price", "manufacture_date", "in_stock", "description"]
    elif any(word in prompt_lower for word in ["employee", "staff", "worker"]):
        columns = ["employee_id", "name", "department", "salary", "hire_date", "is_active", "position"]
    elif any(word in prompt_lower for word in ["student", "education", "school"]):
        columns = ["student_id", "student_name", "grade", "score", "enrollment_date", "is_active", "course"]
    elif any(word in prompt_lower for word in ["movie", "film", "entertainment"]):
        columns = ["movie_id", "title", "genre", "rating", "release_date", "is_available", "director"]
    elif any(word in prompt_lower for word in ["hospital", "patient", "medical"]):
        columns = ["patient_id", "patient_name", "diagnosis", "bill_amount", "admission_date", "is_discharged", "doctor"]
    
    # Create a pandas DataFrame with synthetic data
    data = []
    for i in range(rows):
        row = {}
        # ID field
        row[columns[0]] = f"{columns[0][0:3]}_{i+1000}"
        
        # Name field
        if "movie" in columns[0] or "title" in columns[1]:
            titles = ["The Adventure", "Mystery of the Night", "Journey to Tomorrow", "Lost in Time", 
                     "Hidden Secrets", "Beyond the Stars", "The Last Chapter", "Endless Summer",
                     "Forgotten Memories", "Echoes of the Past", "New Beginnings", "The Final Countdown"]
            row[columns[1]] = random.choice(titles)
        else:
            first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
                          "William", "Elizabeth", "David", "Susan", "Richard", "Jessica", "Joseph", "Sarah",
                          "Thomas", "Karen", "Charles", "Nancy", "Christopher", "Lisa", "Daniel", "Margaret"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
                         "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", 
                         "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]
            row[columns[1]] = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Category field
        if "genre" in columns[2]:
            categories = ["Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Romance", "Thriller", "Documentary"]
        elif "diagnosis" in columns[2]:
            categories = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Oncology", "Dermatology"]
        elif "department" in columns[2]:
            categories = ["HR", "Finance", "Marketing", "Engineering", "Sales", "Customer Support", "R&D"]
        elif "course" in columns[2]:
            categories = ["Mathematics", "Science", "History", "English", "Computer Science", "Art", "Music"]
        elif "location" in columns[2]:
            categories = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio"]
        else:
            categories = ["Category A", "Category B", "Category C", "Category D", "Category E"]
        row[columns[2]] = random.choice(categories)
        
        # Numeric value field
        if "price" in columns[3] or "amount" in columns[3]:
            row[columns[3]] = round(random.uniform(10, 1000), 2)
        elif "score" in columns[3]:
            row[columns[3]] = round(random.uniform(50, 100), 1)
        elif "rating" in columns[3]:
            row[columns[3]] = round(random.uniform(1, 10), 1)
        elif "salary" in columns[3]:
            row[columns[3]] = random.randint(30000, 150000)
        else:
            row[columns[3]] = round(random.uniform(10, 1000), 2)
        
        # Date field
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2023, 12, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_days)
        row[columns[4]] = random_date.strftime("%Y-%m-%d")
        
        # Boolean/status field
        row[columns[5]] = random.choice([True, False])
        
        # Description/text field
        if "director" in columns[6]:
            directors = ["Steven Spielberg", "Christopher Nolan", "Martin Scorsese", "Quentin Tarantino", 
                        "James Cameron", "Ridley Scott", "Greta Gerwig", "Kathryn Bigelow", "Ava DuVernay"]
            row[columns[6]] = random.choice(directors)
        elif "doctor" in columns[6]:
            doctors = ["Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Jones", "Dr. Brown", "Dr. Davis", 
                      "Dr. Miller", "Dr. Wilson", "Dr. Moore", "Dr. Taylor", "Dr. Anderson", "Dr. Thomas"]
            row[columns[6]] = random.choice(doctors)
        elif "position" in columns[6]:
            positions = ["Manager", "Director", "Supervisor", "Coordinator", "Specialist", "Analyst", 
                        "Assistant", "Associate", "Senior Associate", "Vice President", "Consultant"]
            row[columns[6]] = random.choice(positions)
        else:
            descriptions = [
                "This is a sample description for testing purposes.",
                "Another example of synthetic data generation.",
                "Created as a fallback when API is unavailable.",
                "Random text content for the description field.",
                "This data is synthetic and for demonstration only.",
                "Generated by the fallback mechanism.",
                "This is an example description.",
                "Placeholder text for demonstration.",
                "Synthetic content for testing.",
                "Sample data to illustrate functionality."
            ]
            row[columns[6]] = random.choice(descriptions)
        
        data.append(row)
    
    return pd.DataFrame(data)

def generate_dataset_with_gemini(prompt, rows=100, temperature=0.7, max_retries=3):
    """Generate tabular dataset using Gemini API"""
    if not API_AVAILABLE:
        print("⚠️ Gemini API not available, returning None")
        return None
        
    # Handle retries with progressively more conservative settings
    retries = 0
    while retries < max_retries:
        try:
            # Adjust parameters based on retry count
            current_temp = temperature * (1 - 0.2 * retries)  # Reduce temperature on retries
            
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={"temperature": current_temp}
            )
            
            # Create a single combined prompt without using system role
            combined_prompt = f"""You are an expert data scientist who creates realistic CSV datasets. You always produce valid, well-structured CSV data that follows requirements exactly.

Generate a CSV dataset based on the following description: {prompt}
    
Requirements:
1. Generate exactly {rows} rows of data
2. Format as CSV with appropriate headers
3. Do not include any explanations, just the CSV data
4. Data should be realistic and consistent
5. Ensure numeric columns have appropriate ranges
6. Include realistic variance in the data
7. Each row must have at least 6 columns including:
   - At least one ID column
   - At least one text column
   - At least one numeric column
   - At least one date column in YYYY-MM-DD format
   - At least one categorical column
   - At least one boolean column

Return ONLY the raw CSV data, no markdown formatting or explanations.
"""
            
            response = model.generate_content(combined_prompt)
            
            csv_data = response.text
            
            # Validate column count
            try:
                reader = csv.reader(io.StringIO(csv_data))
                header = next(reader)
                
                # If fewer than 6 columns, try again with a more specific prompt
                if len(header) < 6:
                    print(f"First attempt had only {len(header)} columns, retrying...")
                    
                    # More specific second attempt with a fresh model instance
                    second_model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        generation_config={"temperature": current_temp}
                    )
                    
                    enhanced_prompt = f"""I need a CSV dataset with at least 6 columns about: {prompt}

IMPORTANT: Your CSV must have AT LEAST these 6 required columns:
- id (unique identifier)
- name (text name field)
- category (categorical data)
- value (numeric data - price, amount, etc.)
- date (in YYYY-MM-DD format)
- status (boolean true/false or text status)

Plus any additional columns that make sense for the data.
Generate exactly {rows} rows. 
First row must be the column headers.
Return ONLY the raw CSV data with no explanation."""
                    
                    response = second_model.generate_content(enhanced_prompt)
                    
                    csv_data = response.text
                    
                    # Final validation
                    reader = csv.reader(io.StringIO(csv_data))
                    header = next(reader)
                    
                    if len(header) < 6:
                        print(f"Second attempt still has only {len(header)} columns, trying final approach...")
                        
                        # Explicit fixed format for third attempt with a fresh model instance
                        third_model = genai.GenerativeModel(
                            model_name="gemini-1.5-flash",
                            generation_config={"temperature": 0.5}  # Lower temperature for more predictable output
                        )
                        
                        final_prompt = f"""Generate a CSV dataset with EXACTLY these 7 columns:
id,name,category,price,date,status,description

The dataset should be about: {prompt}

Generate exactly {rows} rows of realistic data.
First row must be the column headers exactly as shown above.
All data must be properly formatted, with dates as YYYY-MM-DD.
Ensure all prices are realistic numbers and categories are consistent.

ONLY output the raw CSV data with no explanations or markdown."""
                        
                        response = third_model.generate_content(final_prompt)
                        
                        csv_data = response.text
            except Exception as parse_error:
                print(f"Error parsing CSV response: {parse_error}")
                # Continue with what we have
            
            # Clean up the response to extract just the CSV data
            if "```" in csv_data:
                # Extract from markdown code block
                csv_match = re.search(r'```(?:csv)?\s*(.*?)\s*```', csv_data, re.DOTALL)
                if csv_match:
                    return csv_match.group(1).strip()
            
            # If no markdown, return as is
            return csv_data
            
        except Exception as e:
            retries += 1
            print(f"Error during generation (attempt {retries}/{max_retries}): {str(e)}")
            if retries >= max_retries:
                print("Failed to generate dataset after multiple attempts.")
                return None
            
            # Wait before retry
            time.sleep(2)
    
    return None

def clean_and_format_csv(csv_data, include_header=True):
    """Clean and format CSV data for better presentation"""
    try:
        # If csv_data is None, return an empty DataFrame
        if csv_data is None:
            return pd.DataFrame()
            
        # Read the CSV data into a DataFrame
        df = pd.read_csv(io.StringIO(csv_data), skipinitialspace=True, header=0 if include_header else None)
        
        if not include_header:
            # Create default column names if no header
            df.columns = [f'Column_{i+1}' for i in range(df.shape[1])]
        else:
            # Clean column names
            df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
        
        # Remove any completely empty rows or columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Ensure we have at least 6 columns - add columns if necessary
        if len(df.columns) < 6:
            current_len = len(df.columns)
            for i in range(current_len, 6):
                if i == current_len:
                    df[f'category_{i+1}'] = f'Category {i+1}'
                elif i == current_len + 1:
                    df[f'value_{i+1}'] = random.randint(10, 100)
                elif i == current_len + 2:
                    df[f'date_{i+1}'] = pd.Timestamp('today').strftime('%Y-%m-%d')
                elif i == current_len + 3:
                    df[f'status_{i+1}'] = random.choice([True, False])
                else:
                    df[f'extra_{i+1}'] = f'Extra column {i+1}'
        
        # Convert appropriate columns to numeric
        for col in df.columns:
            try:
                # Check if more than 50% of values can be converted to numeric
                numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                if numeric_count > 0.5 * len(df):
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                continue
        
        # Handle date columns
        for col in df.columns:
            if df[col].dtype == object:
                try:
                    # Check if this might be a date column
                    date_sample = df[col].dropna().sample(min(10, len(df[col].dropna()))).tolist()
                    date_match_count = 0
                    
                    for val in date_sample:
                        if isinstance(val, str):
                            # Check for common date patterns
                            if re.search(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}', val) or \
                               re.search(r'\d{1,2}[-/]\w{3}[-/]\d{2,4}', val) or \
                               re.search(r'\w{3,9}\s+\d{1,2},?\s+\d{2,4}', val):
                                date_match_count += 1
                    
                    # If at least 70% of samples look like dates, convert column
                    if date_match_count >= 0.7 * len(date_sample):
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    continue
                    
        # Identify and convert boolean columns
        for col in df.columns:
            if df[col].dtype == object:
                # Check if column contains primarily boolean-like values
                lower_values = df[col].astype(str).str.lower()
                bool_matches = lower_values.isin(['true', 'false', 'yes', 'no', 'y', 'n', '1', '0', 't', 'f'])
                
                if bool_matches.mean() > 0.9:  # If >90% of values are boolean-like
                    # Map to proper boolean values
                    bool_map = {'true': True, 'yes': True, 'y': True, '1': True, 't': True,
                               'false': False, 'no': False, 'n': False, '0': False, 'f': False}
                    
                    df[col] = lower_values.map(lambda x: bool_map.get(x, None))
        
        return df
    except Exception as e:
        print(f"Error formatting data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error

def export_clean_csv(df):
    """Export DataFrame as clean CSV string"""
    output = io.StringIO()
    df.to_csv(output, index=False, quoting=csv.QUOTE_NONNUMERIC)
    return output.getvalue()

def generate_data_insights(df):
    """Generate insights about the dataset without using AI"""
    insights = []
    
    try:
        # Get general dataset info
        num_rows = len(df)
        num_cols = len(df.columns)
        insights.append(f"Dataset contains {num_rows} rows and {num_cols} columns, providing a comprehensive view of the data.")
        
        # Check for completeness
        null_counts = df.isnull().sum()
        columns_with_nulls = [col for col, count in null_counts.items() if count > 0]
        if columns_with_nulls:
            insights.append(f"Data quality check: {len(columns_with_nulls)} column(s) contain missing values which may require attention.")
        else:
            insights.append("Data quality check: All columns are complete with no missing values.")
        
        # Check for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            # Find the column with the highest standard deviation (most variance)
            std_devs = df[numeric_cols].std()
            highest_std_col = std_devs.idxmax()
            highest_std_val = std_devs.max()
            
            insights.append(f"The '{highest_std_col}' column shows the highest variability with a standard deviation of {highest_std_val:.2f}.")
            
            # Check for correlations between numeric columns
            if len(numeric_cols) > 1:
                corr = df[numeric_cols].corr()
                # Get the highest correlation (excluding self-correlations)
                high_corrs = []
                for i in range(len(numeric_cols)):
                    for j in range(i+1, len(numeric_cols)):
                        corr_val = corr.iloc[i, j]
                        if abs(corr_val) > 0.5:  # Moderate to strong correlation
                            high_corrs.append((numeric_cols[i], numeric_cols[j], corr_val))
                
                if high_corrs:
                    # Sort by absolute correlation value
                    high_corrs.sort(key=lambda x: abs(x[2]), reverse=True)
                    col1, col2, val = high_corrs[0]
                    insights.append(f"Strong {'positive' if val > 0 else 'negative'} relationship (correlation: {val:.2f}) detected between '{col1}' and '{col2}'.")
        
        # Check for categorical columns
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            # Find the column with the most diverse values
            unique_counts = {col: df[col].nunique() for col in cat_cols}
            most_diverse_col = max(unique_counts.items(), key=lambda x: x[1])
            
            if most_diverse_col[1] > 1:
                insights.append(f"The '{most_diverse_col[0]}' column has the most diversity with {most_diverse_col[1]} unique values.")
            
            # Check distribution of a categorical column
            if cat_cols:
                sample_col = cat_cols[0]
                value_counts = df[sample_col].value_counts()
                top_value = value_counts.index[0]
                top_percentage = (value_counts.iloc[0] / num_rows) * 100
                
                insights.append(f"'{top_value}' is the most common value in the '{sample_col}' column, representing {top_percentage:.1f}% of all records.")
        
        # Check for date columns
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        if date_cols:
            # Find the date range
            sample_col = date_cols[0]
            min_date = df[sample_col].min()
            max_date = df[sample_col].max()
            
            if pd.notna(min_date) and pd.notna(max_date):
                date_range = (max_date - min_date).days
                insights.append(f"The data spans {date_range} days, from {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}.")
    
    except Exception as e:
        print(f"Error generating insights: {str(e)}")
        insights.append("Basic dataset analysis completed. Further exploration recommended.")
    
    # Ensure we have at least 3 insights
    while len(insights) < 3:
        insights.append("This synthetic dataset is ready for analysis and can be used for testing and development purposes.")
    
    return insights[:5]  # Return at most 5 insights

# API Routes for Tabular Dataset Generation
@app.route('/api/generate-tabular', methods=['POST'])
def generate_tabular():
    """Generate tabular dataset using Gemini API or fallback to synthetic data"""
    data = request.json
    tabular_prompt = data.get('prompt', '')
    num_rows = min(500, max(10, data.get('numRows', 100)))  # Limit to 10-500 rows
    include_header = data.get('includeHeader', True)
    temperature = data.get('temperature', 0.7)
    
    if not tabular_prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    try:
        print(f"🚀 Generating dataset for prompt: {tabular_prompt}")
        
        # Try to generate with Gemini API first
        csv_data = None
        df = None
        generation_method = "synthetic"
        
        if API_AVAILABLE:
            csv_data = generate_dataset_with_gemini(
                tabular_prompt, 
                num_rows,
                temperature
            )
            
            if csv_data is not None:
                # Successfully generated with API
                df = clean_and_format_csv(csv_data, include_header)
                if not df.empty and len(df.columns) >= 6:
                    generation_method = "ai"
                    print("✅ Successfully generated dataset using Gemini API")
                else:
                    print("⚠️ API returned data but it's empty or has too few columns")
        
        # If API failed or returned inadequate data, use synthetic data
        if df is None or df.empty or len(df.columns) < 6:
            print("🔄 Using synthetic data generation")
            df = generate_synthetic_dataset(tabular_prompt, num_rows)
            generation_method = "synthetic"
        
        # Generate clean CSV for download
        clean_csv = export_clean_csv(df)
        
        # Save the dataset to the database
        current_time = time.strftime("%Y%m%d_%H%M%S")
        dataset_name = re.sub(r'[^a-zA-Z0-9]', '_', tabular_prompt.lower())[:20]
        dataset_filename = f"{dataset_name}_{current_time}.csv"
        
        # Create a temporary file to save the CSV
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv', encoding='utf-8') as temp_file:
            df.to_csv(temp_file, index=False)
            temp_file_path = temp_file.name
        
        try:
            # Save the file to the database
            db_fs.save_file(temp_file_path, DATASET_DIR)
            print(f"Saved dataset to database: {dataset_filename}")
            # Clean up the temporary file
            os.unlink(temp_file_path)
        except Exception as save_error:
            print(f"Error saving to database: {str(save_error)}")
        
        # Convert DataFrame to JSON for preview
        preview_data = df.head(10).to_dict(orient='records')
        
        # Get column info with data types
        columns_with_types = []
        for col in df.columns:
            data_type = str(df[col].dtype)
            try:
                sample_values = df[col].dropna().sample(min(3, len(df[col].dropna()))).tolist()
            except:
                sample_values = df[col].head(3).tolist()
                
            columns_with_types.append({
                "name": col,
                "type": data_type,
                "samples": sample_values
            })
        
        # Get basic statistics
        stats = {}
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if numeric_cols:
                stats['numeric'] = df[numeric_cols].describe().to_dict()
            
            # Add categorical stats
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if cat_cols:
                stats['categorical'] = {}
                for col in cat_cols:
                    value_counts = df[col].value_counts().head(5).to_dict()
                    stats['categorical'][col] = {
                        'unique_values': df[col].nunique(),
                        'top_values': value_counts
                    }
            
            # Add date stats
            date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
            if date_cols:
                stats['dates'] = {}
                for col in date_cols:
                    stats['dates'][col] = {
                        'min': df[col].min().strftime('%Y-%m-%d') if not pd.isna(df[col].min()) else None,
                        'max': df[col].max().strftime('%Y-%m-%d') if not pd.isna(df[col].max()) else None,
                        'range_days': (df[col].max() - df[col].min()).days if not pd.isna(df[col].min()) and not pd.isna(df[col].max()) else None
                    }
        except Exception as stats_error:
            print(f"Error calculating statistics: {stats_error}")
        
        # Generate insights
        insights = generate_data_insights(df)
        
        return jsonify({
            "success": True,
            "message": f"Dataset generated and saved as {dataset_filename}! ({generation_method} generation)",
            "previewData": preview_data,
            "columns": columns_with_types,
            "rowCount": len(df),
            "columnCount": len(df.columns),
            "statistics": stats,
            "insights": insights,
            "csvData": base64.b64encode(clean_csv.encode('utf-8')).decode('utf-8'),
            "generationMethod": generation_method
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error generating dataset: {str(e)}")
        print(error_traceback)
        return jsonify({"error": f"Failed to generate dataset: {str(e)}"}), 500

# Routes for Dataset Management
# Routes for Dataset Management (continued)
@app.route('/api/datasets', methods=['GET'])
def list_datasets():
    """List all available datasets from the database"""
    try:
        datasets = []
        
        # Get CSV datasets from database
        db_files = db_fs.list_files(DATASET_DIR)
        
        for filename in db_files:
            if filename.endswith('.csv'):
                # Get file metadata from database
                # Note: In a real implementation, you might need to track metadata
                # separately as DBFileSystem might not provide all file metadata
                datasets.append({
                    "name": filename,
                    "size": 0,  # We don't have easy access to file size in database
                    "modified": time.strftime('%Y-%m-%d %H:%M:%S'),  # Current time as we can't easily get modification time
                    "type": "tabular"
                })
        
        return jsonify({
            "tabular_datasets": datasets
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/preview', methods=['POST'])
def preview_dataset():
    """Preview dataset content from the database"""
    data = request.json
    file_name = data.get('file_name', '')
    
    if not file_name:
        return jsonify({"error": "No file name provided"}), 400
    
    try:
        # Check if file exists in database
        if not db_fs.file_exists(file_name, DATASET_DIR):
            return jsonify({"error": f"File {file_name} not found in database"}), 404
        
        # Get file content from database
        file_content = db_fs.get_file(file_name, DATASET_DIR)
        
        # Read the CSV content into a DataFrame
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Get data types for each column
        column_types = {col: str(df[col].dtype) for col in df.columns}
        
        # Get basic statistics for numeric columns
        numeric_stats = {}
        for col in df.select_dtypes(include=['number']).columns:
            numeric_stats[col] = {
                'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                'median': float(df[col].median()) if not pd.isna(df[col].median()) else None
            }
        
        # Return enhanced preview data
        return jsonify({
            "preview": df.head(10).to_dict(orient='records'),
            "columns": df.columns.tolist(),
            "column_types": column_types,
            "rows": len(df),
            "numeric_stats": numeric_stats,
            "memory_usage": df.memory_usage(deep=True).sum()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload dataset file to the database"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not file.filename.endswith(('.csv', '.xlsx', '.json')):
        return jsonify({"error": "Only CSV, XLSX and JSON files are allowed"}), 400
    
    try:
        # Save the file directly to the database
        db_fs.save_file(file, DATASET_DIR)
        
        # If it's an Excel file, also convert to CSV for easier processing
        if file.filename.endswith('.xlsx'):
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:
                    file.seek(0)
                    file.save(temp_excel.name)
                    temp_excel_path = temp_excel.name
                
                # Read the Excel file
                excel_df = pd.read_excel(temp_excel_path)
                
                # Create CSV filename
                csv_filename = file.filename.replace('.xlsx', '.csv')
                
                # Save as CSV to a temporary file
                with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv', encoding='utf-8') as temp_csv:
                    excel_df.to_csv(temp_csv, index=False)
                    temp_csv_path = temp_csv.name
                
                # Save CSV to database
                db_fs.save_file(temp_csv_path, DATASET_DIR)
                
                # Clean up temporary files
                os.unlink(temp_excel_path)
                os.unlink(temp_csv_path)
                
                return jsonify({
                    "message": f"File {file.filename} uploaded successfully and converted to CSV ({csv_filename})",
                    "csv_file": csv_filename
                })
            except Exception as excel_error:
                return jsonify({
                    "message": f"File {file.filename} uploaded but could not convert to CSV: {str(excel_error)}",
                    "warning": True
                })
        
        return jsonify({"message": f"File {file.filename} uploaded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """Download generated dataset file from the database"""
    try:
        # Check if file exists in database
        if not db_fs.file_exists(filename, DATASET_DIR):
            return jsonify({"error": "File not found in database"}), 404
        
        # Get file content from database
        file_content = db_fs.get_file(filename, DATASET_DIR)
        
        # Create a temporary file to serve
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(file_content)
        temp_file.close()
        
        # Send the file
        response = send_file(temp_file.name, as_attachment=True, download_name=filename)
        
        # Delete the temporary file after sending
        # Note: This won't actually delete until the next request due to how Flask works
        @response.call_on_close
        def cleanup():
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
        
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """Analyze dataset without using AI API"""
    data = request.json
    file_name = data.get('file_name', '')
    query = data.get('query', '')
    
    if not file_name or not query:
        return jsonify({"error": "File name and query are required"}), 400
    
    try:
        # Check if file exists in database
        if not db_fs.file_exists(file_name, DATASET_DIR):
            return jsonify({"error": f"File {file_name} not found in database"}), 404
        
        # Get file content from database
        file_content = db_fs.get_file(file_name, DATASET_DIR)
        
        # Read the CSV content into a DataFrame
        df = pd.read_csv(io.BytesIO(file_content))
        
        # Get basic analysis results
        results = {}
        
        # Get basic dataset info
        results["dataset_info"] = {
            "rows": len(df),
            "columns": len(df.columns),
            "columns_list": df.columns.tolist(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
        
        # Get column types
        column_types = {}
        for col in df.columns:
            column_types[col] = str(df[col].dtype)
        results["column_types"] = column_types
        
        # Get basic statistics for numeric columns
        numeric_stats = {}
        for col in df.select_dtypes(include=['number']).columns:
            numeric_stats[col] = {
                'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                'std': float(df[col].std()) if not pd.isna(df[col].std()) else None
            }
        results["numeric_stats"] = numeric_stats
        
        # Get categorical column stats
        categorical_stats = {}
        for col in df.select_dtypes(include=['object', 'category']).columns:
            value_counts = df[col].value_counts().head(5).to_dict()
            categorical_stats[col] = {
                'unique_values': df[col].nunique(),
                'top_values': value_counts
            }
        results["categorical_stats"] = categorical_stats
        
        # Check for missing values
        missing_values = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_values[col] = missing_count
        results["missing_values"] = missing_values
        
        # Generate a response based on the query and analysis
        query_lower = query.lower()
        response_text = ""
        
        if "missing" in query_lower or "null" in query_lower:
            # Query about missing values
            if missing_values:
                response_text = f"I found missing values in {len(missing_values)} columns. "
                for col, count in missing_values.items():
                    percentage = (count / len(df)) * 100
                    response_text += f"Column '{col}' has {count} missing values ({percentage:.1f}%). "
            else:
                response_text = "Good news! There are no missing values in this dataset."
                
        elif "summary" in query_lower or "overview" in query_lower or "describe" in query_lower:
            # General dataset summary
            response_text = f"This dataset contains {len(df)} rows and {len(df.columns)} columns. "
            response_text += f"Column types include: {', '.join(set(column_types.values()))}. "
            
            if numeric_stats:
                sample_col = list(numeric_stats.keys())[0]
                response_text += f"For example, the '{sample_col}' column ranges from {numeric_stats[sample_col]['min']} to {numeric_stats[sample_col]['max']} with an average of {numeric_stats[sample_col]['mean']:.2f}. "
                
            if categorical_stats:
                sample_col = list(categorical_stats.keys())[0]
                top_value = list(categorical_stats[sample_col]['top_values'].keys())[0]
                response_text += f"The most common value in '{sample_col}' is '{top_value}'. "
        
        elif any(word in query_lower for word in ["maximum", "max", "highest", "largest"]):
            # Query about maximum values
            if numeric_stats:
                for col, stats in numeric_stats.items():
                    response_text += f"The maximum value in '{col}' is {stats['max']}. "
            else:
                response_text = "I didn't find any numeric columns to analyze for maximum values."
                
        elif any(word in query_lower for word in ["minimum", "min", "lowest", "smallest"]):
            # Query about minimum values
            if numeric_stats:
                for col, stats in numeric_stats.items():
                    response_text += f"The minimum value in '{col}' is {stats['min']}. "
            else:
                response_text = "I didn't find any numeric columns to analyze for minimum values."
                
        elif "average" in query_lower or "mean" in query_lower:
            # Query about averages
            if numeric_stats:
                for col, stats in numeric_stats.items():
                    response_text += f"The average value in '{col}' is {stats['mean']:.2f}. "
            else:
                response_text = "I didn't find any numeric columns to analyze for averages."
                
        elif "categories" in query_lower or "unique" in query_lower:
            # Query about categorical data
            if categorical_stats:
                for col, stats in categorical_stats.items():
                    response_text += f"Column '{col}' has {stats['unique_values']} unique values. "
                    if stats['top_values']:
                        top_items = list(stats['top_values'].items())
                        response_text += f"Top values: "
                        for value, count in top_items[:3]:
                            percentage = (count / len(df)) * 100
                            response_text += f"'{value}' ({percentage:.1f}%), "
                        response_text = response_text.rstrip(", ") + ". "
            else:
                response_text = "I didn't find any categorical columns to analyze."
        
        else:
            # Generic response
            response_text = f"I analyzed the dataset '{file_name}' which contains {len(df)} rows and {len(df.columns)} columns. "
            
            if missing_values:
                response_text += f"There are missing values in {len(missing_values)} columns. "
            else:
                response_text += "The dataset is complete with no missing values. "
                
            if numeric_stats:
                response_text += f"There are {len(numeric_stats)} numeric columns and {len(categorical_stats)} categorical columns. "
                
            response_text += "For more specific insights, please ask about particular aspects of the data such as 'missing values', 'column summaries', or 'maximum/minimum values'."
        
        # Generate insights
        insights = generate_data_insights(df)
        
        return jsonify({
            "result": {
                "type": "success", 
                "value": response_text
            },
            "additional_insights": insights,
            "dataset_summary": results
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error analyzing dataset: {str(e)}")
        print(error_traceback)
        return jsonify({
            "result": {
                "type": "error",
                "value": str(e)
            }
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check server health and API status"""
    status = {
        "status": "ok",
        "server": "running",
        "apis": {
            "gemini": "available" if API_AVAILABLE else "unavailable (using fallback)"
        },
        "storage": {
            "database": "connected", 
            "total_datasets": 0
        },
        "version": "1.0.0"
    }
    
    # Count datasets
    try:
        csv_count = len([f for f in db_fs.list_files(DATASET_DIR) if f.endswith('.csv')])
        status["storage"]["total_datasets"] = csv_count
    except Exception as e:
        status["storage"]["error"] = str(e)
    
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=False)
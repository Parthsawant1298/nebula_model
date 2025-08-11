import os
import zipfile
import uuid
import pickle
import tempfile
from db_file_system import DBFileSystem

# Initialize database file system
db_fs = DBFileSystem()

def generate_loading_code(filename, feature_names, downloads_dir, is_image_model=False, dataset_folder=None, is_object_detection=False):
    """Generate Python code for loading a model and creating predictions"""
    code_template = ""
    
    if is_object_detection:
        code_template = """
import streamlit as st
from ultralytics import YOLO
import cv2
from PIL import Image
import numpy as np
import os

def main():
  st.title('Object Detection with YOLOv8')
  st.write('Upload an image to detect objects')
  
  # File uploader
  uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
  
  if uploaded_file is not None:
      # Read the image
      image = Image.open(uploaded_file)
      st.image(image, caption='Uploaded Image', use_container_width=True)
      
      # Save the uploaded image temporarily
      with open("temp_image.jpg", "wb") as f:
          f.write(uploaded_file.getbuffer())
      
      # Perform object detection
      if st.button('Detect Objects'):
          with st.spinner('Detecting...'):
              # Load the model
              model = YOLO("best_model.pt")
              
              # Run inference
              results = model.predict(source="temp_image.jpg", conf=0.25)
              
              # Get the first result (we only have one image)
              result = results[0]
              
              # Display result
              result_img = result.plot()
              result_img_rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
              st.image(result_img_rgb, caption='Detection Result', use_container_width=True)
              
              # Display detection details
              st.subheader('Detection Results:')
              
              # Get class names dictionary
              names = model.names
              
              # Display each detection
              for box in result.boxes:
                  cls_id = int(box.cls[0].item())
                  class_name = names[cls_id]
                  confidence = box.conf[0].item()
                  coordinates = box.xyxy[0].tolist()  # get box coordinates in (top, left, bottom, right) format
                  
                  st.write(f"**Class:** {class_name}, **Confidence:** {confidence:.2f}")
                  st.write(f"**Coordinates:** [x1={coordinates[0]:.1f}, y1={coordinates[1]:.1f}, x2={coordinates[2]:.1f}, y2={coordinates[3]:.1f}]")
                  st.write("---")
              
              # Clean up
              try:
                  os.remove("temp_image.jpg")
              except:
                  pass

if __name__ == "__main__":
  main()
"""
    elif is_image_model:
        code_template = """
import streamlit as st
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os

# Load the model
model_path = 'best_model.keras'
try:
  model = tf.keras.models.load_model(model_path)
  print(f"Model loaded successfully from {model_path}")
  print(f"Model output shape: {model.output_shape}")
  num_classes = model.output_shape[1]
except Exception as e:
  st.error(f"Error loading model: {e}")
  st.stop()

# Define class labels based on the class indices
# You may need to update these class labels based on your specific dataset
class_labels = {i: f'Class {i}' for i in range(num_classes)}

def predict_image(img_path):
  # Load and preprocess the image
  img = Image.open(img_path).convert('RGB')  # Ensure the image is in RGB format
  img = img.resize((64, 64))  # Resize to match training images
  img_array = image.img_to_array(img)
  img_array = np.expand_dims(img_array, axis=0)
  img_array /= 255.0  # Ensure scaling matches training preprocessing
  
  # Predict the class
  result = model.predict(img_array)
  predicted_class_index = np.argmax(result[0])
  
  # Get the class name
  if predicted_class_index in class_labels:
      prediction = class_labels[predicted_class_index]
  else:
      prediction = f"Unknown class {predicted_class_index}"
  
  return prediction, result[0]

st.title("Image Classification")
st.write("Upload an image to classify.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
  st.image(uploaded_file, caption='Uploaded Image', use_container_width=True)
  st.write("")
  st.write("Classifying...")
  
  try:
      prediction, probabilities = predict_image(uploaded_file)
      
      st.write(f"Prediction: {prediction}")
      
      # Display probabilities
      st.write("Prediction probabilities:")
      for i, prob in enumerate(probabilities):
          class_name = class_labels.get(i, f"Class {i}")
          st.write(f"{class_name}: {prob:.4f}")
  except Exception as e:
      st.error(f"Error during prediction: {e}")
"""
    else:
        # Code for regular ML models (regression/classification)
        feature_list = ""
        if feature_names:
            for feature in feature_names:
                feature_list += f"    '{feature}': st.number_input('Enter {feature}', value=0.0),\n"
        
        code_template = f"""
import pickle
import streamlit as st
import pandas as pd
import numpy as np

# Load the model from file
def load_model():
  try:
      with open('best_model.pkl', 'rb') as f:
          model = pickle.load(f)
      return model
  except Exception as e:
      st.error(f"Error loading model: {{e}}")
      return None

# Streamlit UI for predictions
def main():
  st.title("Model Prediction App")
  
  model = load_model()
  if not model:
      st.stop()
  
  # Display information about the model
  st.write("## Model Information")
  model_type = type(model).__name__
  st.write(f"Model type: {{model_type}}")
  
  # Create input fields for each feature
  st.write("## Enter Feature Values")
  
  # Get user inputs
  user_inputs = {{
{feature_list}
  }}
  
  # Predict the output
  if st.button("Predict"):
      try:
          # Create a DataFrame with the input values
          input_df = pd.DataFrame([user_inputs])
          
          # Make prediction
          prediction = model.predict(input_df)
          
          # Display the prediction
          st.write("## Prediction Result")
          
          # Check if it's a classification or regression model
          if hasattr(model, 'classes_'):
              # Classification model
              st.write(f"Predicted class: {{prediction[0]}}")
              
              # If model has predict_proba method, show probabilities
              if hasattr(model, 'predict_proba'):
                  try:
                      proba = model.predict_proba(input_df)
                      st.write("### Class Probabilities")
                      for i, class_name in enumerate(model.classes_):
                          st.write(f"{{class_name}}: {{proba[0][i]:.4f}}")
                  except:
                      pass
          else:
              # Regression model
              st.write(f"Predicted value: {{prediction[0]:.4f}}")
              
      except Exception as e:
          st.error(f"Error making prediction: {{e}}")

if __name__ == "__main__":
  main()
"""
    
    # For database storage, save to a temporary file first
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "load_model.py")
    
    # Write the code to the temporary file
    with open(temp_path, "w") as f:
        f.write(code_template.strip())
    
    # Determine if we need to save to database
    if 'ml_system' in downloads_dir:
        # Extract directory name for database storage
        parts = downloads_dir.replace('\\', '/').strip('/').split('/')
        idx = parts.index('ml_system')
        if idx + 1 < len(parts):
            dir_name = parts[idx + 1]
        else:
            dir_name = 'downloads'  # Default to downloads directory
        
        # Save to database
        db_fs.save_file(temp_path, dir_name)
        print(f"Loading code saved to database in {dir_name} directory")
        
        # Return the logical path that would be used in the app
        load_model_path = os.path.join(downloads_dir, "load_model.py")
    else:
        # For filesystem storage, use the direct path
        load_model_path = os.path.join(downloads_dir, "load_model.py")
        # Copy from temp to actual location
        os.makedirs(os.path.dirname(load_model_path), exist_ok=True)
        import shutil
        shutil.copy2(temp_path, load_model_path)
    
    # Clean up temporary file
    os.remove(temp_path)
    
    return load_model_path

def write_requirements_file(downloads_dir, is_tensorflow=False, is_yolo=False):
    """Write the requirements.txt file with the necessary dependencies"""
    base_requirements = """
streamlit
pandas
matplotlib
seaborn
scikit-learn
numpy
"""
    
    # Add TensorFlow dependencies if needed
    if is_tensorflow:
        tensorflow_requirements = """
tensorflow
pillow
"""
        requirements = base_requirements + tensorflow_requirements
    elif is_yolo:
        # Add YOLO dependencies if needed
        yolo_requirements = """
ultralytics>=8.0.0
torch>=1.10.0
torchvision>=0.11.0
opencv-python>=4.5.0
pillow
"""
        requirements = base_requirements + yolo_requirements
    else:
        requirements = base_requirements
    
    # Create a temporary file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "requirements.txt")
    
    # Write to the temporary file
    with open(temp_path, "w") as f:
        f.write(requirements.strip())
    
    # Determine if we need to save to database
    if 'ml_system' in downloads_dir:
        # Extract directory name for database storage
        parts = downloads_dir.replace('\\', '/').strip('/').split('/')
        idx = parts.index('ml_system')
        if idx + 1 < len(parts):
            dir_name = parts[idx + 1]
        else:
            dir_name = 'downloads'  # Default to downloads directory
        
        # Save to database
        db_fs.save_file(temp_path, dir_name)
        print(f"Requirements file saved to database in {dir_name} directory")
        
        # Return the logical path that would be used in the app
        requirements_path = os.path.join(downloads_dir, "requirements.txt")
    else:
        # For filesystem storage, use the direct path
        requirements_path = os.path.join(downloads_dir, "requirements.txt")
        # Copy from temp to actual location
        os.makedirs(os.path.dirname(requirements_path), exist_ok=True)
        import shutil
        shutil.copy2(temp_path, requirements_path)
    
    # Clean up temporary file
    os.remove(temp_path)
    
    return requirements_path

def create_project_zip(model_file, models_dir, downloads_dir, is_image_model=False, is_object_detection=False):
    """Create a ZIP file with the model and necessary files, replacing any existing ones"""
    # Create a temporary directory for building the zip
    temp_dir = tempfile.mkdtemp()
    
    # Determine if we're using database storage
    is_database_models = 'ml_system' in models_dir
    is_database_downloads = 'ml_system' in downloads_dir
    
    try:
        # Clear old zip files from the downloads directory
        if is_database_downloads:
            # Extract directory name
            parts = downloads_dir.replace('\\', '/').strip('/').split('/')
            idx = parts.index('ml_system')
            if idx + 1 < len(parts):
                downloads_dir_name = parts[idx + 1]
            else:
                downloads_dir_name = 'downloads'
            
            # Get list of existing zip files
            existing_files = db_fs.list_files(downloads_dir_name)
            for filename in existing_files:
                if filename.endswith('.zip'):
                    db_fs.delete_file(filename, downloads_dir_name)
                    print(f"Removed old zip file from database: {filename}")
        else:
            # Standard filesystem cleanup
            for item in os.listdir(downloads_dir):
                if item.endswith('.zip'):
                    try:
                        os.remove(os.path.join(downloads_dir, item))
                        print(f"Removed old zip file: {item}")
                    except Exception as e:
                        print(f"Error removing old zip file {item}: {e}")
        
        # Generate unique ID for the download
        download_id = str(uuid.uuid4())
        temp_zip_path = os.path.join(temp_dir, f"project_{download_id}.zip")
        
        # Create the ZIP file
        with zipfile.ZipFile(temp_zip_path, 'w') as zipf:
            # Add the model file
            if is_database_models:
                # Extract directory name
                parts = models_dir.replace('\\', '/').strip('/').split('/')
                idx = parts.index('ml_system')
                if idx + 1 < len(parts):
                    models_dir_name = parts[idx + 1]
                else:
                    models_dir_name = 'models'
                
                # Get the model from database
                try:
                    model_content = db_fs.get_file(model_file, models_dir_name)
                    # Save to a temporary file
                    temp_model_path = os.path.join(temp_dir, model_file)
                    with open(temp_model_path, 'wb') as f:
                        f.write(model_content)
                    # Add to zip
                    zipf.write(temp_model_path, arcname=model_file)
                except Exception as e:
                    print(f"Error getting model file from database: {e}")
            else:
                # Standard filesystem
                model_path = os.path.join(models_dir, model_file)
                if os.path.exists(model_path):
                    zipf.write(model_path, arcname=model_file)
            
            # Add the load_model.py file
            if is_database_downloads:
                # Extract directory name
                parts = downloads_dir.replace('\\', '/').strip('/').split('/')
                idx = parts.index('ml_system')
                if idx + 1 < len(parts):
                    downloads_dir_name = parts[idx + 1]
                else:
                    downloads_dir_name = 'downloads'
                
                # Get the file from database
                try:
                    content = db_fs.get_file("load_model.py", downloads_dir_name)
                    # Save to a temporary file
                    temp_file_path = os.path.join(temp_dir, "load_model.py")
                    with open(temp_file_path, 'wb') as f:
                        f.write(content)
                    # Add to zip
                    zipf.write(temp_file_path, arcname="load_model.py")
                except Exception as e:
                    print(f"Error getting load_model.py from database: {e}")
            else:
                # Standard filesystem
                load_model_path = os.path.join(downloads_dir, "load_model.py")
                if os.path.exists(load_model_path):
                    zipf.write(load_model_path, arcname="load_model.py")
            
            # Add the requirements.txt file
            if is_database_downloads:
                # Get the file from database
                try:
                    content = db_fs.get_file("requirements.txt", downloads_dir_name)
                    # Save to a temporary file
                    temp_file_path = os.path.join(temp_dir, "requirements.txt")
                    with open(temp_file_path, 'wb') as f:
                        f.write(content)
                    # Add to zip
                    zipf.write(temp_file_path, arcname="requirements.txt")
                except Exception as e:
                    print(f"Error getting requirements.txt from database: {e}")
            else:
                # Standard filesystem
                requirements_path = os.path.join(downloads_dir, "requirements.txt")
                if os.path.exists(requirements_path):
                    zipf.write(requirements_path, arcname="requirements.txt")
            
            # Add a README file
            readme_content = "# Machine Learning Project\n\n"
            readme_content += "This project contains a trained machine learning model and code to use it.\n\n"
            readme_content += "## Files\n\n"
            readme_content += f"- {model_file}: The trained model\n"
            readme_content += "- load_model.py: Code to load and use the model\n"
            readme_content += "- requirements.txt: Required Python packages\n\n"
            readme_content += "## Usage\n\n"
            readme_content += "1. Install the required packages: `pip install -r requirements.txt`\n"
            readme_content += "2. Run the app: `streamlit run load_model.py`\n"
            
            zipf.writestr("README.md", readme_content)
            
            # Add a setup script
            setup_script = """import subprocess
import os
import sys

def setup_venv():
    print("Setting up virtual environment...")
    # Create virtual environment
    subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Get the pip path based on OS
    pip_path = os.path.join("venv", "Scripts", "pip") if os.name == "nt" else os.path.join("venv", "bin", "pip")
    
    # Install packages
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    print("Virtual environment setup complete!")

if __name__ == "__main__":
    setup_venv()
"""
            zipf.writestr("setup_env.py", setup_script)
        
        # Now save the zip file to the database or filesystem
        if is_database_downloads:
            # Save to database
            zip_filename = f"project_{download_id}.zip"
            db_fs.save_file(temp_zip_path, downloads_dir_name)
            print(f"Created new zip file in database: {zip_filename}")
            # Return logical path
            zip_path = os.path.join(downloads_dir, zip_filename)
        else:
            # Save to filesystem
            zip_path = os.path.join(downloads_dir, f"project_{download_id}.zip")
            os.makedirs(os.path.dirname(zip_path), exist_ok=True)
            import shutil
            shutil.copy2(temp_zip_path, zip_path)
            print(f"Created new zip file: {os.path.basename(zip_path)}")
        
        return zip_path
    
    finally:
        # Clean up temporary directory
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error cleaning up temporary directory: {e}")

def generate_comprehensive_report(model_file, models_dir, downloads_dir, task_type, model_info, dataset_info, visualizations, is_image_model=False, is_object_detection=False):
    """Generate a comprehensive PDF report for the ML project with actual data and visualizations"""
    try:
        import tempfile
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        import base64
        import io
        import json
        import os
        import pandas as pd
        
        # Create a temporary directory for the report
        temp_dir = tempfile.mkdtemp()
        temp_report_path = os.path.join(temp_dir, f"ML_Comprehensive_Report.pdf")
        
        # Create the PDF document
        doc = SimpleDocTemplate(temp_report_path, pagesize=A4)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.purple
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.purple
        )
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.darkblue
        )
        normal_style = styles['Normal']
        highlight_style = ParagraphStyle(
            'Highlight',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.darkgreen,
            spaceAfter=10
        )
        
        # Title
        story.append(Paragraph("Machine Learning Project Comprehensive Report", title_style))
        story.append(Spacer(1, 20))
        
        # Project Overview
        story.append(Paragraph("Project Overview", heading_style))
        story.append(Paragraph(f"This comprehensive report details the machine learning project generated from your dataset. The project includes a trained model, detailed visualizations, performance metrics, and complete implementation code.", normal_style))
        story.append(Spacer(1, 20))
        
        # Task Type Information
        story.append(Paragraph("Task Type Analysis", heading_style))
        task_description = {
            'classification': 'Categorize data into predefined classes',
            'regression': 'Predict continuous numerical values',
            'nlp': 'Process and analyze natural language text',
            'image_classification': 'Classify images into categories',
            'object_detection': 'Detect and locate objects in images'
        }
        story.append(Paragraph(f"Task Type: {task_type.replace('_', ' ').title()}", subheading_style))
        story.append(Paragraph(f"Description: {task_description.get(task_type, 'Advanced machine learning task')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Model Information Section
        story.append(Paragraph("Model Information", heading_style))
        
        if model_info:
            story.append(Paragraph("Model Performance Metrics:", subheading_style))
            
            # Create a table for model metrics
            metrics_data = []
            if 'model_name' in model_info:
                metrics_data.append(['Model Name', model_info['model_name']])
            if 'score' in model_info:
                metrics_data.append(['Performance Score', f"{model_info['score']:.4f}"])
            if 'task_type' in model_info:
                metrics_data.append(['Task Type', model_info['task_type'].replace('_', ' ').title()])
            
            # Add specific metrics for different model types
            if is_object_detection and 'mAP' in model_info:
                metrics_data.append(['mAP (Mean Average Precision)', f"{model_info['mAP']:.4f}"])
            if 'precision' in model_info:
                metrics_data.append(['Precision', f"{model_info['precision']:.4f}"])
            if 'recall' in model_info:
                metrics_data.append(['Recall', f"{model_info['recall']:.4f}"])
            
            if metrics_data:
                metrics_table = Table(metrics_data, colWidths=[2*inch, 3*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(metrics_table)
                story.append(Spacer(1, 20))
        
        # Dataset Information
        story.append(Paragraph("Dataset Information", heading_style))
        if dataset_info:
            story.append(Paragraph("Dataset Details:", subheading_style))
            if 'shape' in dataset_info:
                story.append(Paragraph(f"Dataset Shape: {dataset_info['shape']}", normal_style))
            if 'columns' in dataset_info:
                story.append(Paragraph(f"Number of Features: {len(dataset_info['columns'])}", normal_style))
            if 'target_column' in dataset_info:
                story.append(Paragraph(f"Target Column: {dataset_info['target_column']}", normal_style))
            story.append(Spacer(1, 15))
        
        # Try to get actual file information from database
        try:
            if db_fs is not None:
                # Get model file info
                model_files = db_fs.list_files('models')
                if model_files:
                    story.append(Paragraph("Generated Model Files:", subheading_style))
                    for model_file_name in model_files:
                        story.append(Paragraph(f"• {model_file_name}", normal_style))
                    story.append(Spacer(1, 15))
                
                # Get dataset file info
                dataset_files = db_fs.list_files('datasets')
                if dataset_files:
                    story.append(Paragraph("Input Dataset Files:", subheading_style))
                    for dataset_file_name in dataset_files:
                        story.append(Paragraph(f"• {dataset_file_name}", normal_style))
                    story.append(Spacer(1, 15))
        except Exception as e:
            print(f"Error getting file info: {e}")
        
        # Project Files
        story.append(Paragraph("Project Files", heading_style))
        story.append(Paragraph("The generated project includes the following files:", normal_style))
        story.append(Paragraph("• Trained model file (best_model.pkl/.keras/.pt)", normal_style))
        story.append(Paragraph("• Interactive Streamlit application (load_model.py)", normal_style))
        story.append(Paragraph("• Requirements file (requirements.txt)", normal_style))
        story.append(Paragraph("• Setup script (setup_env.py)", normal_style))
        story.append(Paragraph("• README documentation", normal_style))
        story.append(Spacer(1, 20))
        
        # Visualization Section with Actual Images
        if visualizations and 'plots' in visualizations:
            story.append(Paragraph("Data Visualizations & Analysis", heading_style))
            story.append(Paragraph("The following visualizations were generated from your dataset to help understand data patterns and model performance:", normal_style))
            story.append(Spacer(1, 20))
            
            for i, plot in enumerate(visualizations['plots']):
                story.append(Paragraph(f"Visualization {i+1}: {plot.get('title', f'Plot {i+1}')}", subheading_style))
                
                # Add plot explanation if available
                if 'explanation' in plot:
                    story.append(Paragraph("AI Explanation:", normal_style))
                    story.append(Paragraph(plot['explanation'], highlight_style))
                    story.append(Spacer(1, 15))
                
                # Add the actual plot image if available
                if 'image' in plot and plot['image']:
                    try:
                        # Convert base64 image to temporary file
                        img_data = base64.b64decode(plot['image'])
                        temp_img_path = os.path.join(temp_dir, f"plot_{i}.png")
                        with open(temp_img_path, 'wb') as f:
                            f.write(img_data)
                        
                        # Add image to PDF
                        img = Image(temp_img_path, width=5*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 15))
                        
                        # Clean up temp image
                        os.remove(temp_img_path)
                    except Exception as e:
                        print(f"Error adding plot image {i}: {e}")
                        story.append(Paragraph("[Visualization image could not be included]", normal_style))
                
                story.append(Spacer(1, 20))
        
        # Usage Instructions
        story.append(PageBreak())
        story.append(Paragraph("Usage Instructions", heading_style))
        story.append(Paragraph("To use this machine learning project:", normal_style))
        story.append(Paragraph("1. Extract the project ZIP file", normal_style))
        story.append(Paragraph("2. Install Python dependencies: pip install -r requirements.txt", normal_style))
        story.append(Paragraph("3. Run the application: streamlit run load_model.py", normal_style))
        story.append(Paragraph("4. Upload new data for predictions", normal_style))
        story.append(Spacer(1, 20))
        
        # Technical Details
        story.append(Paragraph("Technical Implementation Details", heading_style))
        story.append(Paragraph("The project was generated using advanced machine learning techniques including:", normal_style))
        story.append(Paragraph("• Automated model selection and hyperparameter tuning", normal_style))
        story.append(Paragraph("• Cross-validation for robust performance evaluation", normal_style))
        story.append(Paragraph("• Data preprocessing and feature engineering", normal_style))
        story.append(Paragraph("• Model performance visualization and analysis", normal_style))
        story.append(Paragraph("• Comprehensive error handling and validation", normal_style))
        story.append(Spacer(1, 20))
        
        # Model Performance Details
        story.append(Paragraph("Model Performance Analysis", heading_style))
        story.append(Paragraph("The trained model has been evaluated using industry-standard metrics and cross-validation techniques to ensure reliable performance. The evaluation includes:", normal_style))
        story.append(Paragraph("• Training and validation accuracy/precision", normal_style))
        story.append(Paragraph("• Cross-validation scores", normal_style))
        story.append(Paragraph("• Feature importance analysis", normal_style))
        story.append(Paragraph("• Performance comparison across different algorithms", normal_style))
        story.append(Spacer(1, 20))
        
        # Best Practices
        story.append(Paragraph("Best Practices Implemented", heading_style))
        story.append(Paragraph("• Data validation and preprocessing", normal_style))
        story.append(Paragraph("• Model selection based on performance metrics", normal_style))
        story.append(Paragraph("• Hyperparameter optimization", normal_style))
        story.append(Paragraph("• Cross-validation for robust evaluation", normal_style))
        story.append(Paragraph("• Comprehensive error handling", normal_style))
        story.append(Paragraph("• Model interpretability and explainability", normal_style))
        story.append(Spacer(1, 20))
        
        # Future Improvements
        story.append(Paragraph("Future Improvements & Recommendations", heading_style))
        story.append(Paragraph("Consider the following enhancements for production use:", normal_style))
        story.append(Paragraph("• Collect more training data for better performance", normal_style))
        story.append(Paragraph("• Implement model versioning and monitoring", normal_style))
        story.append(Paragraph("• Add automated retraining pipelines", normal_style))
        story.append(Paragraph("• Implement A/B testing for model comparison", normal_style))
        story.append(Paragraph("• Add model explainability tools", normal_style))
        story.append(Paragraph("• Implement data drift detection", normal_style))
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("Generated by Nebula AI - Advanced Machine Learning Platform", normal_style))
        story.append(Paragraph(f"Report generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Paragraph("This report contains comprehensive information about your ML project including visualizations, performance metrics, and implementation details.", normal_style))
        
        # Build the PDF
        doc.build(story)
        
        # Save the report to database if needed
        if 'ml_system' in downloads_dir:
            # Extract directory name
            parts = downloads_dir.replace('\\', '/').strip('/').split('/')
            idx = parts.index('ml_system')
            if idx + 1 < len(parts):
                dir_name = parts[idx + 1]
            else:
                dir_name = 'downloads'
            
            # Save to database
            db_fs.save_file(temp_report_path, dir_name)
            print(f"Comprehensive report saved to database: ML_Comprehensive_Report.pdf")
        
        return temp_report_path
        
    except Exception as e:
        print(f"Error generating comprehensive report: {e}")
        import traceback
        traceback.print_exc()
        return None
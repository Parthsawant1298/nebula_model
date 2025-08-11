#!/usr/bin/env python3
"""
Test script for the comprehensive report generation functionality
"""

import os
import sys
import tempfile

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_comprehensive_report():
    """Test the comprehensive report generation function"""
    try:
        from utils import generate_comprehensive_report
        
        print("Testing comprehensive report generation...")
        
        # Test parameters
        model_file = "test_model.pkl"
        models_dir = "ml_system/models"
        downloads_dir = "ml_system/downloads"
        task_type = "classification"
        model_info = {
            'model_name': 'Random Forest',
            'score': 0.85,
            'task_type': 'classification',
            'precision': 0.87,
            'recall': 0.83
        }
        dataset_info = {
            'shape': '(1000, 20)',
            'columns': ['feature1', 'feature2', 'feature3'],
            'target_column': 'target'
        }
        visualizations = {
            'plots': [
                {
                    'title': 'Feature Importance',
                    'explanation': 'This plot shows the relative importance of different features in the model.',
                    'image': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='  # 1x1 pixel PNG
                }
            ]
        }
        
        # Generate report
        report_path = generate_comprehensive_report(
            model_file=model_file,
            models_dir=models_dir,
            downloads_dir=downloads_dir,
            task_type=task_type,
            model_info=model_info,
            dataset_info=dataset_info,
            visualizations=visualizations,
            is_image_model=False,
            is_object_detection=False
        )
        
        if report_path and os.path.exists(report_path):
            print(f"✅ Report generated successfully: {report_path}")
            print(f"   File size: {os.path.getsize(report_path)} bytes")
            
            # Clean up test file
            try:
                os.remove(report_path)
                print("   Test file cleaned up")
            except:
                pass
                
            return True
        else:
            print("❌ Report generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing ML Project Report Generation")
    print("=" * 50)
    
    success = test_comprehensive_report()
    
    print("=" * 50)
    if success:
        print("✅ All tests passed! Report generation is working.")
    else:
        print("❌ Tests failed. Please check the error messages above.")
    print("=" * 50)

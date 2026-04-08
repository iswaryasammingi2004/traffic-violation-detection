
# Quick Download Script for Common Datasets
# Run these commands in your terminal

# 1. Install Kaggle API
pip install kaggle

# 2. Download Helmet Detection Dataset
kaggle datasets download -d andrewmvd/helmet-detection
unzip helmet-detection.zip -d dataset/helmet/

# 3. Download License Plate Dataset  
kaggle datasets download -d andrewmvd/license-plate-recognition
unzip license-plate-recognition.zip -d dataset/anpr/

# 4. Alternative: Use wget/curl for direct downloads
# wget https://example.com/dataset.zip

# 5. After downloading, run the demo
python demo_with_dataset.py

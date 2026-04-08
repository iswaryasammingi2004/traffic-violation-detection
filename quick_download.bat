
@echo off
REM Quick Download Script for Windows

REM 1. Install Kaggle API
pip install kaggle

REM 2. Download Helmet Detection Dataset
kaggle datasets download -d andrewmvd/helmet-detection
powershell -Command "Expand-Archive -Path 'helmet-detection.zip' -DestinationPath 'dataset/helmet/' -Force"

REM 3. Download License Plate Dataset
kaggle datasets download -d andrewmvd/license-plate-recognition  
powershell -Command "Expand-Archive -Path 'license-plate-recognition.zip' -DestinationPath 'dataset/anpr/' -Force"

REM 4. Run demo
python demo_with_dataset.py

pause

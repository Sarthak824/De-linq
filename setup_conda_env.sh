#!/bin/bash
# Load Conda into the bash session
source /opt/anaconda3/etc/profile.d/conda.sh

echo "Creating isolated Conda virtual environment: delinq_venv (Python 3.12)"
conda create --name delinq_venv python=3.12 -y

echo "Activating virtual environment..."
conda activate delinq_venv

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing all dependencies into virtual environment..."
pip install -r requirements.txt

echo "=================================="
echo "✅ Virtual Environment Setup Complete!"
echo "To use this environment, type:"
echo "conda activate delinq_venv"
echo "=================================="

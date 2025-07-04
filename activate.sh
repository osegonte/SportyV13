#!/bin/bash
# Convenience script to activate the virtual environment
source venv/bin/activate
echo "Virtual environment activated!"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

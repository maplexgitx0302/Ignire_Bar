#!/bin/zsh

# Ensure conda is initialized before trying to activate the environment
source ~/miniconda3/etc/profile.d/conda.sh

# Activate the conda environment
conda activate calendar-app

# Run the calendar script
streamlit run calendar_app.py

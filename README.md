# SFT Collector Project

A Python web application for dataset collection using Flask, SQLite, and Gunicorn. This project was created largely thanks to ChatGPT 4. See https://chat.openai.com/share/1d54fad4-a65d-4442-85b6-0e4e98cd9f4f for the conversation that led to this project.

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone or download the project files.

2. Create a virtual environment to isolate your project dependencies:

   python -m venv venv

3. Activate the virtual environment:

   - On Windows:
     venv\Scripts\activate
   - On macOS/Linux:
     source venv/bin/activate

4. Install the required packages:

   pip install -r requirements.txt

## Usage

### Database Setup

If your application uses tables that need to be set up, ensure the database is created before running.

### Run the Application

Start the application server using Gunicorn:

   gunicorn -w 4 -b 0.0.0.0:8000 sft_collector:app

- sft_collector is the name of your Python script (without the .py extension).
- app is the name of the Flask app instance inside sft_collector.py.

## Using the collected dataset

### Convert it to .json file

This repository comes with a script that returns a json file.

    python produce_json.py --dataset_name YOUR_DATASET_NAME --sqlie_file datasets.db --json_file YOUR_DATASET_NAME.json

### Use it with LitGPT

Install litgpt as an example:

    pip install litgpt

Finetune your favourite model with the collected dataset:

    litgpt finetune lora --checkpoint_dir ./checkpoints/microsoft/phi-1_5 --data JSON --data.json_path ./YOUR_DATASET_NAME.json --data.val_split_fraction 0.1 --out_dir out/my_model/
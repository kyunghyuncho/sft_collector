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

5. Download a small language model of your choice for "Ask a language model":

   litgpt download --repo_id "microsoft/phi-1_5"

## Usage

### Run the Application

Start the application server using Flask local server:

   python sft_collector:app

- sft_collector is the name of your Python script (without the .py extension).
- app is the name of the Flask app instance inside sft_collector.py.
- Somehow I cannot get lit-gpt work with gunicorn.
- Put `PYTORCH_ENABLE_MPS_FALLBACK=1` in front, if you are running it on Mac with Apple silicon.

## Using the collected dataset

### Convert it to .json file

This repository comes with a script that returns a json file.

    python produce_json.py --dataset_name YOUR_DATASET_NAME --sqlie_file datasets.db --json_file YOUR_DATASET_NAME.json

### Use it with LitGPT

Finetune your favourite model with the collected dataset:

    litgpt finetune lora --checkpoint_dir ./checkpoints/microsoft/phi-1_5 --data JSON --data.json_path ./YOUR_DATASET_NAME.json --data.val_split_fraction 0.1 --out_dir out/my_model/
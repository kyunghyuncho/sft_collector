# SFT Collector Project

A Python web application for dataset collection using Flask, SQLite, and Gunicorn.

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

### Troubleshooting

- **ModuleNotFoundError**: Ensure the virtual environment is activated and packages are correctly installed.
- **Address Already in Use**: Try changing the port to a different number (e.g., 8001) if the default port is taken.
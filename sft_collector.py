from litgpt_wrapper import load_model, generate_candidate, promptify
from pathlib import Path

from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# create the upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database configuration
DATABASE = 'datasets.db'

# load the model
fabric, model, tokenizer = load_model(Path('./checkpoints/microsoft/phi-1_5'), 1024)

def get_connection():
    """Helper function to connect to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows dictionary-style access to row data
    return conn

def init_db():
    """Initialize the database and create the necessary tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                input_data TEXT NOT NULL,
                output_data TEXT NOT NULL,
                image_path TEXT
            );
        ''')
        conn.commit()

# Initialize the database when the server starts
init_db()

@app.route('/')
@app.route('/<string:success_message>/<string:selected_dataset>')
def home(success_message=None, selected_dataset=None):
    """Display the main dataset input form."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT dataset_name FROM datasets')
    dataset_names = cursor.fetchall()
    conn.close()
    return render_template(
        'collector_template.html',
        dataset_names=[row[0] for row in dataset_names],
        success_message=success_message,
        selected_dataset=selected_dataset
    )

@app.route('/submit', methods=['POST'])
def submit():
    """Process the form submission to add a new dataset instance."""
    dataset_name_select = request.form.get('dataset_name_select')
    new_dataset_name = request.form.get('new_dataset_name')
    input_data = request.form.get('input_data')
    output_data = request.form.get('output_data')
    file = request.files['image_upload']

    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

    # Determine the final dataset name
    dataset_name = new_dataset_name if dataset_name_select == 'new' else dataset_name_select

    if not dataset_name:  # Handle empty dataset names
        return redirect(url_for('home', success_message='Error: Dataset name cannot be empty.'))

    # Insert data into the SQLite database
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO datasets (dataset_name, input_data, output_data, image_path) VALUES (?, ?, ?, ?)',
                       (dataset_name, input_data, output_data, filename))
        conn.commit()

    # Redirect back to the form page with the selected dataset name
    success_message = f'Successfully added dataset "{dataset_name}".'
    return redirect(url_for('home', success_message=success_message, selected_dataset=dataset_name))

@app.route('/examples/<string:dataset_name>')
def view_examples(dataset_name):
    """Display paginated examples for a particular dataset, optionally filtered by a search query."""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    offset = (page - 1) * per_page
    search_query = request.args.get('search', '').strip()

    # Create SQL query condition for search
    search_condition = '%' + search_query + '%' if search_query else '%'

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch examples with filtering and pagination
    cursor.execute('''
        SELECT id, input_data, output_data, image_path
        FROM datasets
        WHERE dataset_name = ? AND (input_data LIKE ? OR output_data LIKE ?)
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    ''', (dataset_name, search_condition, search_condition, per_page, offset))
    examples = cursor.fetchall()

    # Calculate total pages needed for the current search condition
    cursor.execute('''
        SELECT COUNT(*) AS total
        FROM datasets
        WHERE dataset_name = ? AND (input_data LIKE ? OR output_data LIKE ?)
    ''', (dataset_name, search_condition, search_condition))
    total_examples = cursor.fetchone()['total']
    total_pages = (total_examples + per_page - 1) // per_page

    conn.close()

    return render_template(
        'examples.html',
        dataset_name=dataset_name,
        examples=examples,
        current_page=page,
        total_pages=total_pages,
        search_query=search_query
    )

@app.route('/delete_example', methods=['POST'])
def delete_example():
    """Delete a specific example by its ID."""
    example_id = request.form.get('id')
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM datasets WHERE id = ?', (example_id,))
        conn.commit()
    return jsonify({'success': True})

@app.route('/ask_language_model', methods=['POST'])
def ask_language_model():
    """Generate an answer using lit-gpt given input_data."""
    data = request.get_json()
    if 'input_data' not in data:
        return jsonify({'error': 'Missing input_data field in the request.'})

    # Initialize or load your lit-gpt model here and generate a response
    # For simplicity, assume `generate_answer` is a custom function that processes the input
    answer = generate_answer(data['input_data'])

    return jsonify({'answer': answer})

def generate_answer(question):
    response = generate_candidate(fabric, model, tokenizer, 
                                  "Answer this question as concisely as possible. "
                                  + "Terminate after answering this question immediately.", 
                                  question)
    return response

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


if __name__ == '__main__':
    app.run(debug=False, port=8000)


from flask import Flask, request, render_template, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

# Database configuration
DATABASE = 'datasets.db'

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
                dataset_name TEXT,
                input_data TEXT,
                output_data TEXT
            )
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

    # Determine the final dataset name
    dataset_name = new_dataset_name if dataset_name_select == 'new' else dataset_name_select

    if not dataset_name:  # Handle empty dataset names
        return redirect(url_for('home', success_message='Error: Dataset name cannot be empty.'))

    # Insert data into the SQLite database
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO datasets (dataset_name, input_data, output_data)
            VALUES (?, ?, ?)
        ''', (dataset_name, input_data, output_data))
        conn.commit()

    # Redirect back to the form page with the selected dataset name
    success_message = f'Successfully added dataset "{dataset_name}".'
    return redirect(url_for('home', success_message=success_message, selected_dataset=dataset_name))

@app.route('/examples/<dataset_name>')
def view_examples(dataset_name):
    """Display paginated examples for a particular dataset."""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch the required page of examples
    cursor.execute('''
        SELECT id, input_data, output_data
        FROM datasets
        WHERE dataset_name = ?
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    ''', (dataset_name, per_page, offset))
    examples = cursor.fetchall()

    # Calculate the total number of examples for this dataset
    cursor.execute('''
        SELECT COUNT(*) AS total FROM datasets WHERE dataset_name = ?
    ''', (dataset_name,))
    total_examples = cursor.fetchone()['total']
    total_pages = (total_examples + per_page - 1) // per_page  # Calculate total pages needed

    conn.close()

    return render_template(
        'examples.html',
        dataset_name=dataset_name,
        examples=examples,
        current_page=page,
        total_pages=total_pages
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

if __name__ == '__main__':
    app.run(debug=True)

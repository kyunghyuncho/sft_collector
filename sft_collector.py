from flask import Flask, request, redirect, url_for, render_template, jsonify
import sqlite3
import math

app = Flask(__name__)

# Database setup
DATABASE = 'datasets.db'

def init_db():
    """Initialize the SQLite database and create the necessary table."""
    with sqlite3.connect(DATABASE) as conn:
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

def get_unique_dataset_names():
    """Retrieve all unique dataset names from the database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT dataset_name FROM datasets')
        return [row[0] for row in cursor.fetchall()]

def get_paginated_samples(dataset_name, page, per_page):
    """Retrieve paginated samples for a given dataset name."""
    offset = (page - 1) * per_page
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT input_data, output_data FROM datasets
            WHERE dataset_name = ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        ''', (dataset_name, per_page, offset))
        samples = cursor.fetchall()

        cursor.execute('''
            SELECT COUNT(*) FROM datasets WHERE dataset_name = ?
        ''', (dataset_name,))
        total = cursor.fetchone()[0]

    return samples, total

@app.route('/')
@app.route('/<string:success_message>/<string:selected_dataset>')
def home(success_message=None, selected_dataset=None):
    dataset_names = get_unique_dataset_names()
    return render_template('collector_template.html', 
                           dataset_names=dataset_names, 
                           success_message=success_message,
                           selected_dataset=selected_dataset)

@app.route('/samples', methods=['GET'])
def samples():
    dataset_name = request.args.get('dataset_name')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))

    samples, total = get_paginated_samples(dataset_name, page, per_page)
    total_pages = math.ceil(total / per_page)

    return jsonify({
        'samples': [{'input_data': s[0], 'output_data': s[1]} for s in samples],
        'total_pages': total_pages,
        'current_page': page
    })

@app.route('/submit', methods=['POST'])
def submit():
    dataset_name_select = request.form.get('dataset_name_select')
    new_dataset_name = request.form.get('new_dataset_name')
    input_data = request.form.get('input_data')
    output_data = request.form.get('output_data')

    # Determine the final dataset name
    dataset_name = new_dataset_name if dataset_name_select == 'new' else dataset_name_select

    # Insert data into the SQLite database
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO datasets (dataset_name, input_data, output_data)
            VALUES (?, ?, ?)
        ''', (dataset_name, input_data, output_data))
        conn.commit()

    # Redirect back to the form page with the selected dataset name
    success_message = f'Successfully added dataset "{dataset_name}".'
    return redirect(url_for('home', 
                            success_message=success_message, 
                            selected_dataset=dataset_name))

if __name__ == '__main__':
    app.run(debug=True)
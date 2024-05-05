import sqlite3
import json
import argparse

def select_data(dataset_name, table_name, sqlite_file, json_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    # Select input-output pairs for the given dataset name
    cursor.execute(f"SELECT input_data, output_data FROM {table_name} WHERE dataset_name=?", (dataset_name,))
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the data to a list of dictionaries
    input_output_pairs = [{'input': row[0], 'output': row[1]} for row in data]

    # Write the data to a JSON file
    with open(json_file, 'w') as f:
        json.dump(input_output_pairs, f, indent=4)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Select input-output pairs from SQLite database and write to JSON file.")
    parser.add_argument("--sqlite_file", default="datasets.db", nargs='?', help="SQLite file name")
    parser.add_argument("--table_name", default="datasets", nargs='?', help="Name of the table")
    parser.add_argument("--json_file", default="output.json", nargs='?', help="Output JSON file name")
    parser.add_argument("--dataset_name", default="Antibody", nargs='?', help="Name of the dataset")
    args = parser.parse_args()

    # Call the function with provided arguments
    select_data(args.dataset_name, args.table_name, args.sqlite_file, args.json_file)

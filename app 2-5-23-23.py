from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3

app = Flask(__name__, static_folder='/Users/potat/Desktop/comic/static')

def toggle_sort_order(column):
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    if sort_by == column:
        sort_order = 'desc' if sort_order == 'asc' else 'asc'
    return f"&sort_by={column}&sort_order={sort_order}"

def get_sorted_rows_from_database(sort_by, sort_order):
    conn = sqlite3.connect('Comics.sqlite')
    c = conn.cursor()
    c.execute('SELECT * FROM comics ORDER BY ' + sort_by + ' ' + sort_order)
    rows = c.fetchall()
    conn.close()
    return rows

@app.route('/')
def index():
    # Connect to the database
    conn = sqlite3.connect('Comics.sqlite')
    c = conn.cursor()

    # Retrieve limit and sort query parameters
    limit = request.args.get('limit', 50)
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    # Retrieve all the records from the 'comics' table, limited to the specified number
    if limit == 'all':
        c.execute("SELECT * FROM comics")
    else:
        c.execute(f"SELECT * FROM comics LIMIT {limit}")
    rows = c.fetchall()

    # Sort the rows if sorting parameters are present in the query string
    if sort_by != 'id' or sort_order != 'asc':
        rows = get_sorted_rows_from_database(sort_by, sort_order)

    # Render the template with the data
    return render_template('index.html', rows=rows, sort_by=sort_by, sort_order=sort_order)


@app.route('/static/<path:path>')
def send_css(path):
    return send_from_directory('static', path)

@app.route('/sort')
def sort():
    # Retrieve the sort query parameters
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    # Sort the rows and render the template with the data
    rows = get_sorted_rows_from_database(sort_by, sort_order)
    return render_template('index.html', rows=rows, sort_by=sort_by, sort_order=sort_order)

@app.context_processor
def inject_toggle_sort_order():
    return dict(toggle_sort_order=toggle_sort_order)

if __name__ == '__main__':
    app.run(debug=True)


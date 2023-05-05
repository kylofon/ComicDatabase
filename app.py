from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import math  # Import the math module

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
    limit = request.args.get('limit', 50, type=int)
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    # Retrieve total number of records in the 'comics' table
    c.execute("SELECT COUNT(*) FROM comics")
    total_records = c.fetchone()[0]

    # Calculate the total number of pages
    total_pages = math.ceil(total_records / limit)

    # Determine the current page based on the 'limit' parameter in the URL
    current_page = int(request.args.get('page', 1))

    # Calculate the offset for the SQL query
    offset = (current_page - 1) * limit

    # Get the search query and selected column from the URL parameters
    search_query = request.args.get('query', '').strip()
    search_column = request.args.get('column', 'all')

    # Modify the SQL query based on the search query and selected column
    if search_query:
        if search_column == 'all':
            sql_query = f"SELECT * FROM comics WHERE title LIKE ? OR publisher LIKE ? OR category LIKE ? OR writer LIKE ? OR artist LIKE ? OR editor LIKE ? OR comment LIKE ? ORDER BY {sort_by} {sort_order}"
            params = (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%")
        else:
            sql_query = f"SELECT * FROM comics WHERE {search_column} LIKE ? ORDER BY {sort_by} {sort_order}"
            params = (f"%{search_query}%",)
            print("sql_query:", sql_query)
            print("params:", params)
        c.execute(sql_query, params)
        rows = c.fetchall()

        # Retrieve total number of matching records
        count_query = sql_query.replace('SELECT *', 'SELECT COUNT(*)').split('ORDER BY')[0]
        count_params = params
        c.execute(count_query, count_params)
        total_records = c.fetchone()[0]

        # Calculate the total number of pages
        total_pages = math.ceil(total_records / limit)

    else:
        # Modify the SQL query to include LIMIT and OFFSET clauses
        sql_query = f"SELECT * FROM comics ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
        params = (limit, offset)
        c.execute(sql_query, params)
        rows = c.fetchall()

        print("rows:", rows)
        print("sort_by:", sort_by)
        print("sort_order:", sort_order)
        print("limit:", limit)
        print("current_page:", current_page)
        print("search_query:", search_query)
        print("search_column:", search_column)

    # Render the template with the data
    return render_template('index.html', rows=rows, sort_by=sort_by, sort_order=sort_order, limit=limit,
                           current_page=current_page, total_pages=total_pages, search_query=search_query,
                           search_column=search_column)

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

@app.route('/add', methods=['GET', 'POST'])
def add_new():
    if request.method == 'POST':
        title = request.form['title']
        publication_date = request.form['publication_date']
        publisher = request.form['publisher']
        category = request.form['category']
        score = request.form['score']
        last_read = request.form['last_read']
        writer = request.form['writer']
        artist = request.form['artist']
        editor = request.form['editor']
        comment = request.form['comment']

        conn = sqlite3.connect('Comics.sqlite')
        c = conn.cursor()

        c.execute('INSERT INTO comics (title, publication_date, publisher, category, score, last_read, writer, artist, editor, comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (title, publication_date, publisher, category, score, last_read, writer, artist, editor, comment))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_new.html')

@app.context_processor
def inject_toggle_sort_order():
    return dict(toggle_sort_order=toggle_sort_order)

if __name__ == '__main__':
    app.run(debug=True)



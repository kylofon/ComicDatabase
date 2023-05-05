import sqlite3
import csv

# Connect to the database
conn = sqlite3.connect('Comics.sqlite')

# Create a new table called 'comics'
conn.execute('''CREATE TABLE comics
             (id INTEGER PRIMARY KEY,
              title TEXT,
              publication_date DATE,
              publisher TEXT,
              category TEXT,
              score REAL,
              last_read DATE,
              writer TEXT,
              artist TEXT,
              editor TEXT,
              comment TEXT)''')

# Read the CSV file and insert its contents into the 'comics' table
with open('comics_source.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # Skip the header row
    for row in reader:
        conn.execute('''INSERT INTO comics
                    (id, title, publication_date, publisher, category, score, last_read, writer, artist, editor, comment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', row)

# Commit the changes and close the connection
conn.commit()
conn.close()

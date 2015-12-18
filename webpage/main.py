import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

DATABASE = ""
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    # I've heard it's faster this way..
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    db.row_factory = sqlite3.Row
    return db

def query_db(query, args=()):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        search_term = request.form['search_input']
        return redirect(url_for('search', q=search_term))

    tags = query_db("SELECT DISTINCT tag FROM tags WHERE tag_probability > 0.5")
    return render_template('index.html', tags=tags, amount=len(tags))

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_input']
        return redirect(url_for('search', q=search_term))

    search_term = request.args.get('q', '')
    rows = query_db("SELECT * FROM tags WHERE tag == :search_term AND tag_probability>0.5", [search_term.strip()])
    return render_template('images.html', rows=rows[:10], amount=len(rows), search_term=search_term)

if __name__ == '__main__':
    app.run()
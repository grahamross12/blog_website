import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from newsapi import NewsApiClient
from helpers import login_required


# Initialise NewsAPI
newsapi = NewsApiClient(api_key=os.getenv('API_KEY'))
domains = 'bbc.co.uk,theguardian.com,telegraph.co.uk,channel4.com,sky.com'

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config.from_object(__name__)
Session(app)

db = 'info.db'


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=['GET'])
def index():
    
    # Obtain a list of all the user's saved articles
    # If user is not logged in, return None
    if 'user_id' not in session:
        saved_titles = None
    else:
        saved_titles = find_saved_titles(session['user_id'])

    categories = ['Politics', 'Finance', 'Technology', 'Sport', 'World']
    top_headlines = find_headlines()
    if top_headlines == None:
        return render_template('empty.html', title='Error', message="Error retrieving NewsAPI data")

    article_dicts = []
    for category in categories:
        articles = find_articles(category, page_size=3)

        if articles == None:
            return render_template('empty.html', title='Error', message="Error retrieving NewsAPI data")
        
        article_dict = {'category': category, 'articles': articles}
        article_dicts.append(article_dict)

    return render_template('index.html', headlines=top_headlines, all_articles=article_dicts, saved_titles=saved_titles)


@app.route("/saving", methods=['POST'])
def saving():
    """Add an article to a user's save list."""
    title = request.form['title']

    conn = sqlite3.connect(db)
    c = conn.cursor()
    with conn:
        # Check if the article is in the articles table
        c.execute("SELECT * FROM articles WHERE title = :title", {'title': title})
        if len(c.fetchall()) == 0:
            url = request.form['url']
            image_url = request.form['image_url']
            description = request.form['description']
            print(description)
            c.execute("INSERT INTO articles (title, url, image_url, description) VALUES (:title, :url, :image_url, :description)", 
                     {'title': title, 'url': url, 'image_url': image_url, 'description': description})

        # Obtain the id of the article from the articles table
        c.execute("SELECT id FROM articles WHERE title = :title", {'title': title})
        article_id = c.fetchone()[0]

        # Check if the article is already in the user_articles table
        c.execute("SELECT user_id, article_id FROM user_articles WHERE user_id = :user_id AND article_id = :article_id", {'user_id': session['user_id'], 'article_id': article_id})
        if len(c.fetchall()) == 0:
            # Add the article to the user_articles table
            c.execute("INSERT INTO user_articles (user_id, article_id) VALUES (:user_id, :article_id)", {'user_id': session['user_id'], 'article_id': article_id})
        else:
            # Remove the article from the user_articles table
            c.execute("DELETE FROM user_articles WHERE user_id = :user_id AND article_id = :article_id", {'user_id': session['user_id'], 'article_id': article_id})
    return redirect('/')


@app.route("/saved", methods=['GET', 'POST'])
@login_required
def saved():
    """List a user's saved articles from the user_articles table"""
    saved_articles, saved_titles = find_saved_articles(session['user_id'])
    if saved_articles == None:
        return render_template('empty.html', title='Saved Articles', message="You have no saved articles")

    # Transfer the article info into a dictionary
        
    return render_template('results.html', title='Saved Articles', articles=saved_articles, saved_titles=saved_titles, page=1)

@app.route("/results")
def results():
    """Display more results."""
    return redirect('/saved')

@app.route("/sport")
def sport():
    """Display a list of sport articles"""

    # Obtain a list of all the user's saved articles
    # If user is not logged in, return None
    if 'user_id' not in session:
        saved_titles = None
    else:
        saved_titles = find_saved_titles(session['user_id'])

    # Obtain a list of article dictionaries for the sport query
    articles = find_articles('sport', page_size=10, page=1)
    if articles == None:
        return render_template('empty.html', title='Error', message="Error retrieving NewsAPI data")

    return render_template('results.html', title='Sport', articles=articles, saved_titles=saved_titles)


@app.route("/technology")
def technology():
    """Display a list of technology articles"""
    
    # Obtain a list of all the user's saved articles
    # If user is not logged in, return None
    if 'user_id' not in session:
        saved_titles = None
    else:
        saved_titles = find_saved_titles(session['user_id'])

    # Obtain a list of article dictionaries for the sport query
    articles = find_articles('technology', page_size=10, page=1)
    if articles == None:
        return render_template('empty.html', title='Error', message="Error retrieving NewsAPI data")

    return render_template('results.html', title='Technology', articles=articles, saved_titles=saved_titles)


@app.route("/politics")
def politics():
    """Display a list of politics articles"""
    
    # Obtain a list of all the user's saved articles
    # If user is not logged in, return None
    if 'user_id' not in session:
        saved_titles = None
    else:
        saved_titles = find_saved_titles(session['user_id'])

    # Obtain a list of article dictionaries for the sport query
    articles = find_articles('politics', page_size=10, page=1)
    if articles == None:
        return render_template('empty.html', title='Error', message="Error retrieving NewsAPI data")

    return render_template('results.html', title='Politics', articles=articles, saved_titles=saved_titles)


@app.route("/finance")
def finance():
    """Display a list of finance articles"""
    
    # Obtain a list of all the user's saved articles
    # If user is not logged in, return None
    if 'user_id' not in session:
        saved_titles = None
    else:
        saved_titles = find_saved_titles(session['user_id'])

    # Obtain a list of article dictionaries for the sport query
    articles = find_articles('finance', page_size=10, page=1)
    if articles == None:
        return render_template('empty.html', title='Error', message="Error retrieving NewsAPI data")

    return render_template('results.html', title='Finance', articles=articles, saved_titles=saved_titles)


@app.route("/world")
def world():
    """Display a list of world articles"""
    
    # Obtain a list of all the user's saved articles
    # If user is not logged in, return None
    if 'user_id' not in session:
        saved_titles = None
    else:
        saved_titles = find_saved_titles(session['user_id'])

    # Obtain a list of article dictionaries for the sport query
    articles = find_articles('world', page_size=10, page=1)
    if articles == None:
        return render_template('empty.html', title='Error', message="Error retrieving NewsAPI data")

    return render_template('results.html', title='World', articles=articles, saved_titles=saved_titles)


@app.route("/search")
def search():
    """Search for any category"""
    query = request.args.get('q')

    if 'user_id' not in session:
        saved_titles = None
    else:
        saved_titles = find_saved_titles(session['user_id'])

    # Obtain a list of article dictionaries for the sport query
    articles = find_articles(query, page_size=10, page=1)
    if articles == None:
        return render_template('empty.html', title='Error', message="Error retrieving NewsAPI data")

    return render_template('results.html', title='Search', articles=articles, saved_titles=saved_titles)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", error=1)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('login.html', error=2)

        # Query database for username
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        with conn:
        	c.execute("SELECT * FROM users WHERE username = :username", {'username': request.form.get("username")})
        	rows = c.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template('login.html', error=3)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash('You were successfully logged in')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    if request.method == "POST":
    	# Connect to the database

        # Check if a username and password has been entered
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or len(username) < 4 or len(username) > 20:
            return render_template("register.html", error=1)

        if not password or len(password) < 4 or len(password) > 20:
            return render_template("register.html", error=2)

        # Check if the passwords match
        if password != request.form.get("confirmation"):
            return render_template("register.html", error=3)

        # Check if the username has been taken
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        with conn:
        	c.execute("SELECT * FROM users WHERE username = :username", {'username': username})
        	rows = c.fetchall()

        if len(rows) != 0:
            return render_template("register.html", error=4)

        # Hash the password before storing it in the database
        hash_password = generate_password_hash(password)

        # Add the new user information to the database
        with conn:
        	c.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", {'username': username, 'hash': hash_password})
        	conn.commit()

        # Log the user in using the details they provided
        with conn:
        	c.execute("SELECT * FROM users WHERE username = :username", {'username': request.form.get("username")})
        	rows = c.fetchall()

        session["user_id"] = rows[0]["id"]

        flash('Account created!')
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    """Display account information and password change option"""
    if request.method == 'POST':
        conn = sqlite3.connect(db)
        c = conn.cursor()
        with conn:
            c.execute("SELECT username FROM users WHERE id = :id", {'id': session['user_id']})
            username = c.fetchone()[0]

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if new password is valid
        if not password or len(password) < 4 or len(password) > 20:
            return render_template("account.html", username=username, error=1)

        # Check if passwords match
        if password != confirmation:
            return render_template("account.html", username=username, error=2)

        # Update the password information
        hash_password = generate_password_hash(password)
        conn = sqlite3.connect(db)
        c = conn.cursor()
        with conn:
            c.execute("UPDATE users SET hash = :hash WHERE id = :id", {'hash': hash_password, 'id': session['user_id']})
            rows = c.fetchone()

        flash("Your password has been changed")
        return render_template("account.html", username=username)

    else:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        with conn:
            c.execute("SELECT username FROM users WHERE id = :id", {'id': session['user_id']})
            rows = c.fetchone()

        return render_template("account.html", username=rows[0])


def find_articles(query, page_size=10, page=1):
    """Return the articles dictionary from NewsAPI given a query"""
    try:
        articles = newsapi.get_everything(language='en',
                                       q=query,
                                       domains = domains,
                                       sort_by='publishedAt',
                                       page=page,
                                       page_size=page_size)
        if articles['status'] != 'ok':
            return None

        articles_reduct = []
        for article in articles['articles']:
            article_dict = {'title': article['title'],
                            'url': article['url'],
                            'urlToImage': article['urlToImage'],
                            'description': article['description']}
            articles_reduct.append(article_dict)

        return articles_reduct

    # Return None if there is a problem
    except Exception as e:
        print(e)
        return None


def find_saved_titles(user_id):
    """Find the titles of the saved articles for a given user by querying the user_articles table"""
    conn = sqlite3.connect(db)
    c = conn.cursor()

    with conn:
        # Find the articles that the user has saved
        c.execute("""SELECT * FROM articles WHERE id IN (
                     SELECT article_id FROM user_articles WHERE user_id = :user_id)""", 
                     {'user_id': user_id})
        rows = c.fetchall()
        saved_titles = []
        for row in rows:
            saved_titles.append(row[1])

        # If user has no saved articles, return None
        if saved_titles == []:
            return None

        return saved_titles


def find_saved_articles(user_id):
    """Find the saved titles and the article info for a given user"""
    conn = sqlite3.connect(db)
    c = conn.cursor()

    with conn:
        # Find the articles that the user has saved
        c.execute("""SELECT title, url, image_url, description FROM articles WHERE id IN (
                     SELECT article_id FROM user_articles WHERE user_id = :user_id)""", 
                     {'user_id': user_id})
        rows = c.fetchall()
        rows.reverse()
        saved_articles = []
        saved_titles = []
        for row in rows:
            article_dict = {'title': row[0],
                            'url': row[1],
                            'urlToImage': row[2],
                            'description': row[3]}
            saved_titles.append(row[0])
            saved_articles.append(article_dict)

        # If user has no saved articles, return None
        if saved_articles == [] or saved_titles == []:
            return None, None

        return saved_articles, saved_titles


def find_headlines(page_size=3, page=1):
    """Return the articles dictionary from NewsAPI given a query"""
    try:
        top_headlines = newsapi.get_top_headlines(language='en',
                                                  # domains = domains,
                                                  # sort_by='publishedAt',
                                                  country='gb',
                                                  page=page,
                                                  page_size=page_size)
        if top_headlines['status'] != 'ok':
            return None

        return top_headlines['articles']

    # Return None if there is a problem
    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':
    app.run(debug=True)
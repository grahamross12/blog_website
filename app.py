import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from newsapi import NewsApiClient
from helpers import login_required

# Initialise NewsAPI
newsapi = NewsApiClient(api_key='f29c5ca7a2d544889ceaf1396eb0cc75')


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


@app.route("/", methods=['GET', 'POST'])
def index():
	top_headlines = newsapi.get_top_headlines(language='en')

	sport = newsapi.get_everything(language='en',
									  q='sport',
									  domains = 'cnn.com',
                                      sort_by='publishedAt',
                                      page=1)
	return render_template('index.html', headlines=top_headlines, sport=sport)


@app.route("/save", methods=['POST'])
def save():
    """Add an article to a user's save list."""
    title = request.form['title']
    conn = sqlite3.connect(db)
    c = conn.cursor()
    with conn:
        # Check if the article is in the articles table
        c.execute("SELECT * FROM articles WHERE title = :title", {'title': title})
        if len(c.fetchall()) == 0:
        	c.execute("INSERT INTO articles (title) VALUES (:title)", {'title': title})

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
    return redirect("/")



@app.route("/sport")
def sport():
	"""Display a list of sport articles"""
	sport = newsapi.get_everything(language='en',
								  q='sport',
								  domains = 'cnn.com',
                                  sort_by='publishedAt',
                                  page=1)
	return render_template('results.html', sport=sport)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return redirect('login')

        # Ensure password was submitted
        elif not request.form.get("password"):
            return redirect('login')

        # Query database for username
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        with conn:
        	c.execute("SELECT * FROM users WHERE username = :username", {'username': request.form.get("username")})
        	rows = c.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return redirect('login')

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
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    if request.method == "POST":
    	# Connect to the database

        # Check if a username and password has been entered
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        print(email)

        if not username:
            return redirect("/register")

        if not password:
            return redirect("/register")

        # Check if the passwords match
        if password != request.form.get("confirmation"):
            return redirect("/register")

        # Check if the username has been taken
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        with conn:
        	c.execute("SELECT * FROM users WHERE username = :username", {'username': username})
        	rows = c.fetchall()

        if len(rows) != 0:
            return redirect("/register")

        # Hash the password before storing it in the database
        hash_password = generate_password_hash(password)

        # Add the new user information to the database
        with conn:
        	c.execute("INSERT INTO users (username, email, hash) VALUES (:username, :email, :hash)", {'username': username, 'email': email, 'hash': hash_password})
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





if __name__ == '__main__':
	news = newsapi.get_everything(language='en',
								  q="Turn your living room couch into the best seats at every game with Samsung's 2021 TVs",
								  domains = 'cnn.com',
                                  sort_by='publishedAt',
                                  page=1)
	print(news)
	app.run(debug=True)
# News Website
For my final project in CS50 I have created a news website with Flask. This website uses NewsAPI to find information about news articles from a number of different websites and display them in a user friendly format using HTML, CSS and Bootstrap elements. I made the project outside the CS50 IDE using Sublime Text and a Python virtual environment, and I have hosted it on Heroku. While developing the project, I found it useful to use Git and Github save working versions of the code while working on new features.
<br>
The main backend part of the website is written in app.py and contains the Flask routes for the different pages in the website. Here, the article information is retrieved from NewsAPI and loaded into the frontend programatically using Jinja.
<br>
In the backend, requests are also made to an SQLite database to hold information about user accounts and articles. While articles are loaded using NewsAPI, users have an option to save articles to their profile. Information about the article title, description, URL and image URL are saved into this database from the API in an articles table. Another users table holds the user ID, username and password hash of every user. In a separate table, the user ID and article ID are given to show which articles each user has saved. A user's saved articles can therefore be shown in the website using appropriate SQLite queries. This schema of database tables was used to avoid storing redundant information, as each article is only stored once in the database.

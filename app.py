import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
Session(app)


@app.route("/", methods=['GET', 'POST'])
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True)
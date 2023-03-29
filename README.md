# ShareBnB

ShareBnB is a full stack web application of a peer-to-peer marketplace where users can connect about potential rental spaces. 
Users can create an account, login, browse through the list of rental spaces or post a rental space, and can either remove their personal
rental space or book a rental space. Personal pages of the user show their personal rental spaces and the rental spaces they liked.

# Table of Contents
1. [Features](#Features)
2. [Tech Stack](#Tech-Stack)
3. [Database Hierarchy](#DB-Hierarchy)
4. [Install](#Install)
5. [Deployment](#Deployment)
6. [Getting Started](#Boilerplate)
7. [Testing](#Testing)

## Features<a name="Features"></a>:
* Logged out users have the option to sign up for an account. Authentication is managed by the backend. 
* Logged in users have access to view rental spaces, book for spaces, and the option to update their profile.
* Logged in users have ability to post their own rental spaces.
* Users can book and unbook for rental spaces to keep track of bookings they have made.
* Search fields are available for users to filter through. 
* Token stored on localStorage so that a user is not automatically logged out upon page refresh.
* Alerts are displayed to the user when signing up for an account and editing the user profile if minimum requirements are not met or user already exists.

## Tech stack<a name="Tech-stack"></a>: 
### Backend
<p>
  <a href="https://www.python.org" target="_blank" rel="noreferrer"> 
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> 
  </a> &nbsp;
  <a href="https://flask.palletsprojects.com/" target="_blank" rel="noreferrer"> 
    <img src="https://www.vectorlogo.zone/logos/pocoo_flask/pocoo_flask-icon.svg" alt="flask" width="40" height="40"/> 
  </a> &nbsp;
 </p>

### Frontend
<p>
  <a href="https://developer.mozilla.org/en-US/docs/Glossary/HTML" target="_blank" rel="noreferrer"> 
    <img src="https://www.vectorlogo.zone/logos/w3_html5/w3_html5-icon.svg" alt="dart" width="40" height="40"/> 
  </a> &nbsp;
  <a href="https://developer.mozilla.org/en-US/docs/Web/CSS" target="_blank" rel="noreferrer"> 
    <img src="https://www.vectorlogo.zone/logos/w3_css/w3_css-official.svg" alt="dart" width="40" height="40"/> 
  </a> &nbsp;
 </p>
  
 ### Database Management
 <p>
    <a href="https://www.postgresql.org/" target="_blank" rel="noreferrer"> 
      <img src="https://www.vectorlogo.zone/logos/postgresql/postgresql-icon.svg" alt="postgres" width="40" height="40"/> 
    </a> &nbsp;
 </p>

## Database Hierarchy<a name="DB-Hierarchy"></a>


## Install<a name="Install"></a>:
To install backend requirements from the requirements.txt file:
  pip3 freeze > requirements.txt
  pip3 install -r requirements.txt

## Deployment<a name="Deployment"></a>
To deploy, make sure server (PostgreSql) is running and enter venv environment:
  flask run
  

## Getting Started<a name="Boilerplate"></a>
Create virtual environment:
  1. python3 -m venv venv
  2. source venv/bin/activate
  3. pip3 install flask
  4. 
To help you get started with your very own: We use Flask SQLAlchemy to interact with PostgreSQL
  ```python (models.py)
  from flask_sqlalchemy import SQLAlchemy

  db = SQLAlchemy()

  def connect_db(app):
  """Connect to database."""
    app.app_context().push()
    db.app = app
    db.init_app(app)
  ```
  ```python (app.py)
  from flask import Flask, request, redirect, render_template
  from models import db, connect_db, Pet

  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sqla_intro'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SQLALCHEMY_ECHO'] = True

  connect_db(app)
  %%If there is no seed, to create tables%%
  db.create_all()
  ```
  
## Testing<a name="Testing"></a>
To test: 
  python3 -m unittest

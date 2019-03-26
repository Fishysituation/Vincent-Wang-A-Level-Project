"""
initialises the database
helps solve problem with circular imports
"""


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
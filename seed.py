"""Seed file to make sample data for users db."""

from models import connect_db, db, User
from app import app

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
User.query.delete()
from main import db, User  # Import your db instance and User model

# Drop existing tables
# db.drop_all()

# Recreate the tables with the updated schema
db.create_all()
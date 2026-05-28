"""
Run this script ONCE after setting up the database.
It creates the pre-existing admin user.
Usage: python create_admin.py
"""
from app import create_app
from models.models import db, User, Student, Company
from werkzeug.security import generate_password_hash

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        existing = User.query.filter_by(role="admin").first()
        if existing:
            print("Admin already exists!")
            return

        admin = User(
            username      = "admin",
            email         = "admin@placement.com",
            password_hash = generate_password_hash("Admin@123"),
            role          = "admin",
            is_active     = True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created successfully!")
        print("  Username : admin")
        print("  Password : Admin@123")
        print("  Email    : admin@placement.com")

if __name__ == "__main__":
    create_admin()
    
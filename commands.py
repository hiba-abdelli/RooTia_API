
#create an admin 

import click
from flask import current_app
from models import db, User, Role
from extensions import bcrypt

def register_commands(app):
    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("email")
    @click.argument("password")
    @click.argument("name")
    def create_admin(username, email, password, name):
        """
        Create an admin user.
        Usage: flask create-admin <username> <email> <password> <name>
        """
        with app.app_context():
            # Fetch the admin role (role_id = 3)
            role = Role.query.get(3)
            if not role:
                print("Admin role (role_id = 3) not found. Please ensure it exists in the database.")
                return

            # Check if the admin user already exists
            admin = User.query.filter_by(email=email).first()
            if admin:
                print(f"Admin user with email '{email}' already exists.")
                return

            # Create the admin user
            admin = User(
                username=username,
                email=email,
                name=name,
                role_id=role.id  # Set role_id to 3 (admin)
            )
            admin.set_password(password)

            db.session.add(admin)
            db.session.commit()
            print(f"Admin user '{username}' created successfully.")
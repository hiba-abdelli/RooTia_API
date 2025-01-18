from app import create_app
from models import Role
from extensions import db

def init_roles():
    app = create_app()
    
    with app.app_context():
        # Drop existing tables and create new ones
        db.drop_all()
        db.create_all()
        
        print("Creating roles...")
        
        # Create roles
        user_role = Role(name='user')
        business_role = Role(name='business')
        
        # Add roles to session
        db.session.add(user_role)
        db.session.add(business_role)
        
        try:
            # Commit the changes
            db.session.commit()
            
            # Verify roles were created
            all_roles = Role.query.all()
            print("Created roles:", [role.name for role in all_roles])
            print("Roles initialized successfully")
        except Exception as e:
            print(f"Error initializing roles: {e}")
            db.session.rollback()

if __name__ == "__main__":
    init_roles()

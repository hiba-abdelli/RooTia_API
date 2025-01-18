from flask import Flask
from config import Config
from extensions import db
from models import User, Role, Business, Herb, Use, Risk, Disease, HerbDisease ,Review
import sqlite3

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def migrate_data():
    app = create_app()
    
    # Source SQLite database
    sqlite_conn = sqlite3.connect('your_database.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Create all tables in MySQL
    with app.app_context():
        db.create_all()
        
        # Migrate Roles
        sqlite_cursor.execute('SELECT * FROM role')
        roles = sqlite_cursor.fetchall()
        for role in roles:
            new_role = Role(id=role[0], name=role[1])
            db.session.add(new_role)
        db.session.commit()

        # Migrate Users
        sqlite_cursor.execute('SELECT * FROM user')
        users = sqlite_cursor.fetchall()
        for user in users:
            new_user = User(
                id=user[0],
                username=user[1],
                email=user[2],
                password=user[3],
                role_id=user[4],
                name=user[5],
                age=user[6],
                chronic_disease=user[7],
                since_when=user[8],
                consulting_doctor=bool(user[9]),
                taking_medication=bool(user[10]),
                reason_for_herbal_medicine=user[11]
            )
            db.session.add(new_user)
        db.session.commit()

        # Migrate Businesses
        sqlite_cursor.execute('SELECT * FROM business')
        businesses = sqlite_cursor.fetchall()
        for business in businesses:
            new_business = Business(
                id=business[0],
                email=business[1],
                password=business[2],
                business_name=business[3],
                business_description=business[4],
                business_address=business[5],
                business_website=business[6],
                role_id=business[7]
            )
            db.session.add(new_business)
        db.session.commit()

        # Migrate Herbs
        sqlite_cursor.execute('SELECT * FROM herbs')
        herbs = sqlite_cursor.fetchall()
        for herb in herbs:
            new_herb = Herb(
                id=herb[0],
                name=herb[1]
            )
            db.session.add(new_herb)
        db.session.commit()

        # Migrate Uses
        sqlite_cursor.execute('SELECT * FROM uses')
        uses = sqlite_cursor.fetchall()
        for use in uses:
            new_use = Use(
                id=use[0],
                herb_id=use[1],
                use_description=use[2],
                disease_treated=use[3],
                dosage=use[4]
            )
            db.session.add(new_use)
        db.session.commit()

        # Migrate Risks
        sqlite_cursor.execute('SELECT * FROM risks')
        risks = sqlite_cursor.fetchall()
        for risk in risks:
            new_risk = Risk(
                id=risk[0],
                herb_id=risk[1],
                risk_description=risk[2],
                affected_groups=risk[3]
            )
            db.session.add(new_risk)
        db.session.commit()

        # Migrate Diseases
        sqlite_cursor.execute('SELECT * FROM diseases')
        diseases = sqlite_cursor.fetchall()
        for disease in diseases:
            new_disease = Disease(
                id=disease[0],
                name=disease[1],
                description=disease[2],
                common_treatments=disease[3]
            )
            db.session.add(new_disease)
        db.session.commit()

        # Migrate Herb-Disease relationships
        sqlite_cursor.execute('SELECT * FROM herb_disease')
        herb_diseases = sqlite_cursor.fetchall()
        for hd in herb_diseases:
            new_hd = HerbDisease(
                herb_id=hd[0],
                disease_id=hd[1]
            )
            db.session.add(new_hd)
        db.session.commit()

        # Migrate Reviews
        sqlite_cursor.execute('SELECT * FROM reviews')
        reviews = sqlite_cursor.fetchall()
        for review in reviews:
        # Ensure the herb_id exists in the MySQL database
           herb = Herb.query.get(review[1])
    
           if herb:  # If the herb exists, migrate the review
              new_review = Review(
                 herb_id=review[1],
                rating=review[2],
                review=review[3]
              )
              db.session.add(new_review)
        db.session.commit()


        # Migrate Reviews
        sqlite_cursor.execute('SELECT * FROM reviews')
        reviews = sqlite_cursor.fetchall()
        for review in reviews:
           herb = Herb.query.get(review[1])
           user = User.query.get(review[0])
           if herb and user:  
              new_review = Review(
                 user_id=review[0],
                 herb_id=review[1],
                 rating=review[2],
                 review=review[3]
              
              ) 
              db.session.add(new_review)
        db.session.commit()

 

    sqlite_conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    migrate_data()


    


       

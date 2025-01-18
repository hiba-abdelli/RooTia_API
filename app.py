from models import User, Role, Business, Herb, Use, Risk, Disease, HerbDisease , Review , Ad , ResearchArticle
from flask import Flask
from config import Config
from extensions import db, bcrypt, jwt , socketio , oauth
from commands import register_commands  # Import the register_commands function from commands.py
from routes.herbal import herbal_bp
from routes.ads import ads_bp
from routes.messages import messages_bp
from routes.external import external
from routes.auth import auth_bp
from dotenv import load_dotenv
from flask_migrate import Migrate  # Import Migrate
from routes.socketio import socketio_bp,init_socketio
import os
from routes.auth import oauth 



# Load environment variables from .env file

load_dotenv()  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)
    socketio.init_app(app)
    oauth.init_app(app)
    # Register CLI commands
    register_commands(app)

    

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(herbal_bp, url_prefix='/herbal')
    app.register_blueprint(ads_bp, url_prefix='/ads')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(socketio_bp) 
    app.register_blueprint(external, url_prefix='/external')

    # Initialize SocketIO event handlers
    init_socketio(socketio)

    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

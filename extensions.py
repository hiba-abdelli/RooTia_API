from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import datetime
from flask_socketio import SocketIO
from authlib.integrations.flask_client import OAuth



# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Bcrypt
bcrypt = Bcrypt()

# Initialize JWTManager
jwt = JWTManager()

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*") 


oauth = OAuth()






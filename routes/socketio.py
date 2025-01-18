from flask import Blueprint
from flask_socketio import emit
from flask_jwt_extended import jwt_required, get_jwt_identity

# Blueprint for SocketIO (optional, for better structure)
socketio_bp = Blueprint('socketio', __name__)

# Function to initialize SocketIO event handlers
def init_socketio(socketio):
    """
    This function registers SocketIO event handlers.
    It must be called with the socketio object from the main app.
    """
    @socketio.on('connect')
    @jwt_required()
    def handle_connect():
        """
        Handles the 'connect' event.
        When a client connects, it joins a room named after the user's ID.
        """
        identity = get_jwt_identity()
        if identity and isinstance(identity, dict):
            user_id = identity.get("id")
            if user_id:
                socketio.join_room(str(user_id))  # Join a room named after the user's ID
                print(f"User {user_id} connected and joined room {user_id}")

    @socketio.on('disconnect')
    @jwt_required()
    def handle_disconnect():
        """
        Handles the 'disconnect' event.
        When a client disconnects, it leaves the room named after the user's ID.
        """
        identity = get_jwt_identity()
        if identity and isinstance(identity, dict):
            user_id = identity.get("id")
            if user_id:
                socketio.leave_room(str(user_id))  # Leave the room upon disconnection
                print(f"User {user_id} disconnected and left room {user_id}")

    @socketio.on('join_conversation')
    @jwt_required()
    def handle_join_conversation(data):
        """
        Handles joining a room for a specific conversation.
        """
        conversation_id = data.get("conversation_id")
        if conversation_id:
            socketio.join_room(f"conversation_{conversation_id}")
            print(f"User {get_jwt_identity()} joined conversation room {conversation_id}")

    @socketio.on('leave_conversation')
    @jwt_required()
    def handle_leave_conversation(data):
        """
        Handles leaving a room for a specific conversation.
        """
        conversation_id = data.get("conversation_id")
        if conversation_id:
            socketio.leave_room(f"conversation_{conversation_id}")
            print(f"User {get_jwt_identity()} left conversation room {conversation_id}")
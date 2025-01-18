from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Business, Role

def role_required(allowed_role_ids):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapped(*args, **kwargs):
            # Get the identity from the JWT token
            identity = get_jwt_identity()

            # Debugging: Print the identity to verify its type and value
            print(f"Identity: {identity}, Type: {type(identity)}")

            # Ensure identity is a string (user ID or business ID)
            if not isinstance(identity, str):
                return jsonify({'message': 'Invalid token format'}), 401

            # Fetch the user or business from the database
            user = User.query.get(identity)
            business = Business.query.get(identity)

            # Determine if the identity corresponds to a user or business
            if user:
                entity = user
                entity_type = "user"
            elif business:
                entity = business
                entity_type = "business"
            else:
                return jsonify({'message': 'User or Business not found'}), 404

            # Debugging: Print the entity and its role_id
            print(f"Entity: {entity}, Role ID: {entity.role_id}")

            # Allow access if the entity is an admin (role_id == 3)
            if entity.role_id == 3:
                return f(*args, **kwargs)

            # Check if the entity's role ID is in the allowed role IDs
            if entity.role_id not in allowed_role_ids:
                return jsonify({'message': 'Unauthorized access'}), 403

            # Proceed to the route if authorized
            return f(*args, **kwargs)
        return wrapped
    return decorator
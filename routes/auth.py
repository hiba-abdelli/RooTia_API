from flask import Blueprint, request, jsonify ,redirect, url_for, session
from models import User, Business, Role
from extensions import db , bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import jwt 
from flask import current_app as app
from flask import current_app
import base64
import uuid
from config import Config  
import json
from authlib.integrations.flask_client import OAuth
import logging

auth_bp = Blueprint('auth', __name__)

oauth = OAuth()

    
# Configure Google OAuth
google = oauth.register(
    name='google',
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs' 
)


# Google OAuth Login
@auth_bp.route('/login/google')
def login_google():
    # Get the actor_type from query parameters
    actor_type = request.args.get('actor_type')
    print(f"Actor Type: {actor_type}")  # Debugging

    # Validate the actor_type
    if actor_type not in ['user', 'business']:
        return jsonify({"msg": "Invalid actor type. Must be 'user' or 'business'."}), 400

    # Store the actor_type in the session for use in the callback
    session['actor_type'] = actor_type

    # Generate the redirect_uri
    redirect_uri ="http://127.0.0.1:5001/auth/oauth-callback"
    print(f"Redirect URI: {redirect_uri}")  # Debugging

    # Redirect to Google for authorization
    return google.authorize_redirect(redirect_uri)

# Google OAuth Callback
@auth_bp.route('/oauth-callback')
def google_callback():
    try:
        # Retrieve the actor_type from the session
        actor_type = session.get('actor_type')
        print(f"Callback Actor Type: {actor_type}")  # Debugging

        # Validate the actor_type
        if actor_type not in ['user', 'business']:
            return jsonify({"msg": "Invalid actor type. Must be 'user' or 'business'."}), 400

        # Get the OAuth token and user info
        token = google.authorize_access_token()
        user_info = google.get('userinfo').json()
        print(f"User Info: {user_info}")  # Debugging

        # Extract user info
        email = user_info.get('email')
        name = user_info.get('name')
        google_id = user_info.get('id')

        if actor_type == 'user':
            # Handle user login/registration
            user = User.query.filter_by(email=email).first()
            if not user:
                role = Role.query.filter_by(name='user').first()
                if not role:
                    return jsonify({"msg": "Role not found"}), 400

                user = User(
                    username=email,  # Use email as username
                    email=email,
                    name=name,
                    google_id=google_id,
                    role_id=role.id
                )
                db.session.add(user)
                db.session.commit()

            # Create access token for user
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    "username": user.username,
                    "role": "user"
                }
            )
            return jsonify({
                "msg": "Login successful",
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": user.name
                }
            }), 200

        elif actor_type == 'business':
            # Handle business login/registration
            business = Business.query.filter_by(email=email).first()
            if not business:
                role = Role.query.filter_by(name='business').first()
                if not role:
                    return jsonify({"msg": "Role not found"}), 400

                business = Business(
                    email=email,
                    business_name=name,  # Use name as business name
                    google_id=google_id,
                    role_id=role.id
                )
                db.session.add(business)
                db.session.commit()

            # Create access token for business
            access_token = create_access_token(
                identity=str(business.id),
                additional_claims={
                    "email": business.email,
                    "business_name": business.business_name,
                    "role": "business"
                }
            )
            return jsonify({
                "msg": "Login successful",
                "access_token": access_token,
                "business": {
                    "id": business.id,
                    "email": business.email,
                    "business_name": business.business_name
                }
            }), 200

    except Exception as e:
        logging.error(f"Error during Google OAuth: {str(e)}")
        return jsonify({"msg": f"Error during Google OAuth: {str(e)}"}), 500







@auth_bp.route('/register/user', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    # Check if the email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email is already registered"}), 400
        
    password = data.get('password')
    name = data.get('name')
    age = data.get('age')
    chronic_disease = data.get('chronic_disease')
    since_when = data.get('since_when')
    consulting_doctor = data.get('consulting_doctor')
    taking_medication = data.get('taking_medication')
    reason_for_herbal_medicine = data.get('reason_for_herbal_medicine')

    if not username or not email or not password or not name or not age or not chronic_disease or not since_when or consulting_doctor is None or taking_medication is None or not reason_for_herbal_medicine:
        return jsonify({"msg": "Missing required fields"}), 400

    role = Role.query.filter_by(name='user').first()
    if not role:
        return jsonify({"msg": "Role not found"}), 400

    new_user = User(
        username=username,
        email=email,
        name=name,
        age=age,
        chronic_disease=chronic_disease,
        since_when=since_when,
        consulting_doctor=consulting_doctor,
        taking_medication=taking_medication,
        reason_for_herbal_medicine=reason_for_herbal_medicine,
        role_id=role.id
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route('/register/business', methods=['POST'])
def register_business():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    business_name = data.get('business_name')
    business_description = data.get('business_description')
    business_address = data.get('business_address')
    business_website = data.get('business_website')

    if not email or not password or not business_name or not business_description or not business_address or not business_website:
        return jsonify({"msg": "Missing required fields"}), 400

    # Debug: Print all roles
    all_roles = Role.query.all()
    print("Available roles:", [role.name for role in all_roles])

    role = Role.query.filter_by(name='business').first()
    if not role:
        return jsonify({"msg": "Role not found"}), 400

    # Check if email already exists
    if Business.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 400

    new_business = Business(
        email=email,
        business_name=business_name,
        business_description=business_description,
        business_address=business_address,
        business_website=business_website,
        role_id=role.id
    )
    new_business.set_password(password)

    db.session.add(new_business)
    db.session.commit()

    return jsonify({"msg": "Business registered successfully"}), 201

@auth_bp.route('/login/user', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid username or password"}), 401

    # Create access token with user info
    access_token = create_access_token (
        identity=str(user.id),
        additional_claims={
            "username": user.username,
            "role": "user"
        }
        )
    return jsonify({
        "msg": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.name
        }
    }), 200

@auth_bp.route('/login/business', methods=['POST'])
def login_business():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    business = Business.query.filter_by(email=email).first()
    if not business or not business.check_password(password):
        return jsonify({"msg": "Invalid email or password"}), 401

    # Create access token with business info (identity as a dictionary)
    access_token = create_access_token(
        identity=str(business.id),
        additional_claims={
            "email": business.email,
            "business_name": business.business_name,
            "role": "business"
        }
    )
    
    return jsonify({
        "msg": "Login successful",
        "access_token": access_token,
        "business": {
            "id": business.id,
            "email": business.email,
            "business_name": business.business_name,
            "business_description": business.business_description,
            "business_address": business.business_address,
            "business_website": business.business_website
        }
    }), 200



#update business profile 
@auth_bp.route('/business/profile', methods=['PUT'])
@jwt_required()
def update_business_profile():
    try:
        # Parse the JWT identity as a dictionary
        identity = json.loads(get_jwt_identity())
        business_id = identity.get('id')

        # Fetch the business from the database
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"msg": "Business not found"}), 404

        # Update business fields from the request body
        data = request.get_json()
        business.business_name = data.get('business_name', business.business_name)
        business.business_description = data.get('business_description', business.business_description)
        business.phone_number = data.get('phone_number', business.phone_number)
        business.social_media_links = data.get('social_media_links', business.social_media_links)

        # Save changes to the database
        db.session.commit()

        return jsonify({
            "msg": "Business profile updated successfully",
            "business": {
                "id": business.id,
                "email": business.email,
                "business_name": business.business_name,
                "business_description": business.business_description,
                "business_address": business.business_address,
                "business_website": business.business_website,
                "phone_number": business.phone_number,
                "social_media_links": business.social_media_links
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


#delete a busines

@auth_bp.route('/business/profile', methods=['DELETE'])
@jwt_required()
def delete_business_profile():
    try:
        import json
        # Parse the JWT identity to get the business ID
        identity = json.loads(get_jwt_identity())
        business_id = identity.get('id')

        # Fetch the business from the database
        business = Business.query.get(business_id)
        if not business:
            return jsonify({"msg": "Business not found"}), 404

        # Delete the business profile
        db.session.delete(business)
        db.session.commit()

        return jsonify({"msg": "Business profile deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500

#reset password

@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')
    entity_type = data.get('entity_type')  # Either 'user' or 'business'

    if entity_type not in ['user', 'business']:
        return jsonify({'message': 'Invalid entity type. Must be "user" or "business".'}), 400

    entity = User.query.filter_by(email=email).first() if entity_type == 'user' else Business.query.filter_by(email=email).first()
    if not entity:
        return jsonify({'message': f'{entity_type.capitalize()} with this email not found.'}), 404

    reset_token = jwt.encode(
        {'id': entity.id, 'entity_type': entity_type, 'exp': datetime.utcnow() + timedelta(minutes=15)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )
    # Here, i'd send the token via email (but i omitted it for simplicity as i plan to implement it in the future)
    return jsonify({'message': 'Password reset token sent', 'reset_token': reset_token}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    reset_token = data.get('reset_token')
    new_password = data.get('new_password')

    try:
        decoded_token = jwt.decode(reset_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        entity_type = decoded_token['entity_type']
        entity_id = decoded_token['id']

        entity = User.query.get(entity_id) if entity_type == 'user' else Business.query.get(entity_id)
        if not entity:
            return jsonify({'message': f'{entity_type.capitalize()} not found'}), 404

        # Update the password
        entity.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        return jsonify({'message': 'Password updated successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Reset token has expired'}), 400
    except Exception as e:
        return jsonify({'message': f'Error resetting password: {str(e)}'}), 400

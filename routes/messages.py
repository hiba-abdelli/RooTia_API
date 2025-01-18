from flask import Blueprint, request, jsonify
from models import Message, User, Business
from extensions import db, socketio
import logging
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

messages_bp = Blueprint('messages', __name__)

# Send a message
@messages_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    try:
        # Get sender ID
        sender_id = get_jwt_identity()
        
        # Get claims for role
        jwt_claims = get_jwt()
        sender_role = jwt_claims.get("role")

        if not sender_id or not sender_role:
            return jsonify({"msg": "Missing sender ID or role in JWT"}), 400

        # Get request data
        data = request.get_json()
        receiver_id = int(data.get("receiver_id"))
        receiver_type = data.get("receiver_type")
        conversation_id = data.get("conversation_id")  # Use conversation_id instead of ad_id
        content = data.get("content")
        attachment_url = data.get("attachment_url")

        # Create message object based on sender_id instead of identity
        if sender_role == "user":
            message = Message(
                user_id=sender_id,
                business_id=receiver_id if receiver_type == "business" else None,
                conversation_id=conversation_id,  # Use conversation_id
                content=content,
                attachment_url=attachment_url
            )
        else:  # sender is business
            message = Message(
                user_id=receiver_id if receiver_type == "user" else None,
                business_id=sender_id,
                conversation_id=conversation_id,  # Use conversation_id
                content=content,
                attachment_url=attachment_url
            )

        db.session.add(message)
        db.session.commit()

        # Emit a Socket.IO event to notify the recipient
        socketio.emit('new_message', {
            "message_id": message.id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }, room=f"conversation_{conversation_id}")  # Send to the conversation room

        return jsonify({"msg": "Message sent successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

# Fetch messages for a specific conversation with pagination
@messages_bp.route('/fetch/<int:conversation_id>', methods=['GET'])
@jwt_required()
def fetch_messages(conversation_id):
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Fetch messages for the given conversation_id, ordered by timestamp
        messages = (
            Message.query
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.timestamp)
            .paginate(page=page, per_page=per_page)
        )

        # Format the messages for the response
        messages_data = [
            {
                "id": msg.id,
                "user_id": msg.user_id,
                "business_id": msg.business_id,
                "content": msg.content,
                "attachment_url": msg.attachment_url,
                "timestamp": msg.timestamp.isoformat(),
                "is_read": msg.is_read
            }
            for msg in messages.items
        ]

        return jsonify({
            "messages": messages_data,
            "page": messages.page,
            "per_page": messages.per_page,
            "total_pages": messages.pages,
            "total_messages": messages.total
        }), 200

    except Exception as e:
        logging.error(f"Error in fetch_messages: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

# Mark a message as read
@messages_bp.route('/mark_as_read/<int:message_id>', methods=['POST'])
@jwt_required()
def mark_as_read(message_id):
    try:
        # Fetch the message
        message = Message.query.get(message_id)
        if not message:
            return jsonify({"msg": "Message not found"}), 404

        # Mark the message as read
        message.is_read = True
        db.session.commit()

        # Emit a Socket.IO event to notify the sender
        socketio.emit('message_read', {
            "message_id": message.id,
            "reader_id": get_jwt_identity()
        }, room=f"conversation_{message.conversation_id}")  # Send to the conversation room

        return jsonify({"msg": "Message marked as read"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in mark_as_read: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

# Fetch conversations for the current user or business
@messages_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    try:
        # Get JWT identity and claims
        identity = get_jwt_identity()
        jwt_claims = get_jwt()

        sender_id = identity  # Identity is the user ID
        sender_role = jwt_claims.get("role")

        if not sender_id or not sender_role:
            return jsonify({"msg": "Missing sender ID or role in JWT claims"}), 400

        # Fetch unique conversations (grouped by conversation_id)
        conversations = (
            db.session.query(Message.conversation_id, db.func.count(Message.id))
            .filter((Message.user_id == int(sender_id)) | (Message.business_id == int(sender_id)))
            .group_by(Message.conversation_id)
            .all()
        )

        conversations_data = [
            {"conversation_id": conv[0], "message_count": conv[1]} for conv in conversations
        ]

        return jsonify(conversations_data), 200

    except Exception as e:
        logging.error(f"Error in get_conversations: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

# Fetch unread message notifications
@messages_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        # Get JWT identity and claims
        identity = get_jwt_identity()
        jwt_claims = get_jwt()

        sender_id = int(identity)  # Identity is the user ID as a string
        sender_role = jwt_claims.get("role")

        # Validate required fields
        if not sender_id or not sender_role:
            return jsonify({"msg": "Missing sender ID or role in JWT claims"}), 400

        # Fetch unread messages
        unread_messages = Message.query.filter(
            ((Message.user_id == sender_id) | (Message.business_id == sender_id)) &
            (Message.is_read == False)
        ).all()

        # Format the unread messages for the response
        notifications_data = [
            {
                "message_id": msg.id,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in unread_messages
        ]

        return jsonify(notifications_data), 200

    except Exception as e:
        logging.error(f"Error in get_notifications: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
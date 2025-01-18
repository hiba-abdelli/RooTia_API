from flask import Blueprint, request, jsonify
from models import db, Ad , Business
from flask import current_app as app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json


ads_bp = Blueprint('ads', __name__)

#post an ad 

@ads_bp.route('/create', methods=['POST'])
def create_ad():
    data = request.get_json()
    business_id = data.get('business_id')
    title = data.get('title')
    description = data.get('description')
    media_type = data.get('media_type')  # 'text', 'image', 'video'
    media_url = data.get('media_url')  # URL of the media file (image or video)

    if not business_id or not title or not media_type or not media_url:
        return jsonify({"msg": "Missing required fields"}), 400

    new_ad = Ad(
        business_id=business_id,
        title=title,
        description=description,
        media_type=media_type,
        media_url=media_url
    )

    try:
        db.session.add(new_ad)
        db.session.commit()
        return jsonify({"msg": "Ad created successfully", "ad": new_ad.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


# Fetching Ads for Users (view all ads or ads filtered by business name)

# 1: Get the list of businesses
@ads_bp.route('/businesses', methods=['GET'])
def get_businesses():
    businesses = Business.query.all()
    return jsonify([{'id': business.id, 'business_name': business.business_name} for business in businesses])

# 2: Filtering ads by business_name
@ads_bp.route('/ads', methods=['GET'])
def get_ads():
    business_name = request.args.get('business_name')
    
    query = Ad.query

    # Filtering by business name with strict matching
    if business_name:
        query = query.join(Business).filter(Business.business_name == business_name)

    # Execute query and get ads
    ads = query.all()

    # Return a message if no ads are found
    if not ads:
        return jsonify({'message': 'No ads found for the specified filter'}), 404

    # Manually serialize Ad objects to dictionaries
    ads_data = []
    for ad in ads:
        ads_data.append({
            'id': ad.id,
            'business_id': ad.business_id,
            'title': ad.title,
            'description': ad.description,
            'media_type': ad.media_type,
            'media_url': ad.media_url,
            'created_at': ad.created_at.isoformat() if ad.created_at else None
        })

    # Return ads as JSON
    return jsonify(ads_data)


# Delete an ad
@ads_bp.route('/ads/<int:ad_id>', methods=['DELETE'])
@jwt_required()
def delete_ad(ad_id):
    # Extract the JWT identity to get the business ID
    identity = get_jwt_identity()
    
    # Check if the identity is a string (it should be a dictionary)
    if isinstance(identity, str):
        # Parse the identity (this assumes the JWT payload is a stringified dictionary)
        import json
        try:
            identity = json.loads(identity)
        except json.JSONDecodeError:
            return jsonify({"msg": "Invalid JWT token format"}), 400
    
    # Check if identity is now a dictionary and contains 'id'
    if not isinstance(identity, dict) or 'id' not in identity:
        return jsonify({"msg": "Invalid JWT token, 'id' not found"}), 400
    
    business_id = identity.get('id')
    
    # Fetch the ad from the database
    ad = Ad.query.get(ad_id)
    
    # Check if the ad exists
    if not ad:
        return jsonify({"msg": "Ad not found"}), 404
    
    # Check if the ad belongs to the authenticated business
    if ad.business_id != business_id:
        return jsonify({"msg": "Unauthorized to delete this ad"}), 403
    
    # Delete the ad from the database
    db.session.delete(ad)
    db.session.commit()
    
    # Return a success message
    return jsonify({"msg": "Ad deleted successfully"}), 200

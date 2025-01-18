from flask import Blueprint, request, jsonify
from models import db, Herb, Use, Risk, Disease , Review , User , HerbDisease
from decorators_herbal import role_required 


#  a Blueprint for the herbal routes
herbal_bp = Blueprint('herbal', __name__)



#  add a new herb
@herbal_bp.route('/herbs', methods=['POST'])
@role_required ([3])
def add_herb():
    try:
        # Get data from request
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'scientific_name', 'family', 'region_found', 'description', 'traditional_use']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'message': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        # Create a new herb object
        new_herb = Herb(
            name=data.get('name'),
            scientific_name=data.get('scientific_name'),
            family=data.get('family'),
            region_found=data.get('region_found'),
            description=data.get('description'),
            traditional_use=data.get('traditional_use'),
            image_url=data.get('image_url') # Optional
        )

        # Add to session and commit
        db.session.add(new_herb)
        db.session.commit()

        return jsonify({'message': 'Herb added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error adding herb: {str(e)}'}), 400



#  fetch all herbs
@herbal_bp.route('/herbs', methods=['GET'])
@role_required([1,2,3])
def get_all_herbs():
    try:
        herbs = Herb.query.all()
        herbs_list = [{
            'id': herb.id,
            'name': herb.name,
            'scientific_name': herb.scientific_name,
            'family': herb.family,
            'region_found': herb.region_found,
            'description': herb.description,
            'traditional_use': herb.traditional_use,
            'image_url': herb.image_url
        } for herb in herbs]

        return jsonify(herbs_list), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching herbs: {str(e)}'}), 400


# get a specific herb by name 
@herbal_bp.route('/herbs/<string:name>', methods=['GET'])
@role_required([1,2,3])
def get_herb(name):
    try:
        # Query the herb by name
        herb = Herb.query.filter_by(name=name).first()

        if not herb:
            return jsonify({'message': 'Herb not found'}), 404

        herb_data = {
            'id': herb.id,
            'name': herb.name,
            'scientific_name': herb.scientific_name,
            'family': herb.family,
            'region_found': herb.region_found,
            'description': herb.description,
            'traditional_use': herb.traditional_use,
            'image_url': herb.image_url,
            'uses': [{'use_description': use.use_description, 'disease_treated': use.disease_treated} for use in herb.uses],
            'risks': [{'risk_description': risk.risk_description, 'affected_groups': risk.affected_groups} for risk in herb.risks],
            'diseases': [{'name': disease.name, 'description': disease.description} for disease in herb.diseases]
        }

        return jsonify(herb_data), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching herb: {str(e)}'}), 400



#add multiple herbs once 

@herbal_bp.route('/herbs/bulk', methods=['POST'])
@role_required ([3])
def add_bulk_herbs():
    try:
        data = request.get_json()

        # Validate the structure of the data
        if not isinstance(data, list):
            return jsonify({'message': 'Data should be a list of herbs'}), 400

        # Initialize an empty list to store the herb objects
        herbs_to_add = []

        for herb_data in data:
            required_fields = ['name', 'scientific_name', 'family', 'region_found', 'description', 'traditional_use']
            missing_fields = [field for field in required_fields if not herb_data.get(field)]
            
            if missing_fields:
                return jsonify({
                    'message': 'Missing required fields in one or more herbs',
                    'missing_fields': missing_fields
                }), 400

            new_herb = Herb(
                name=herb_data.get('name'),
                scientific_name=herb_data.get('scientific_name'),
                family=herb_data.get('family'),
                region_found=herb_data.get('region_found'),
                description=herb_data.get('description'),
                traditional_use=herb_data.get('traditional_use'),
                image_url=herb_data.get('image_url')
            )
            herbs_to_add.append(new_herb)

        # Bulk insert into the database
        db.session.add_all(herbs_to_add)
        db.session.commit()

        return jsonify({'message': f'{len(herbs_to_add)} herbs added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error adding herbs: {str(e)}'}), 400


# delete multiple herbs by their names 

@herbal_bp.route('/herbs', methods=['DELETE'])
@role_required ([3])
def delete_multiple_herbs():
    try:
        # Get the list of herb names from the request body
        data = request.get_json()
        herb_names = data.get('names', [])

        # Validate if names are provided
        if not herb_names:
            return jsonify({'message': 'No herb names provided'}), 400

        # Find the herbs by their names
        herbs_to_delete = Herb.query.filter(Herb.name.in_(herb_names)).all()

        if not herbs_to_delete:
            return jsonify({'message': 'No matching herbs found to delete'}), 404

        # Delete each herb from the database
        for herb in herbs_to_delete:
            db.session.delete(herb)

        db.session.commit()

        return jsonify({'message': f'{len(herbs_to_delete)} herb(s) deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting herbs: {str(e)}'}), 400


# search herbs by criteria (family , region , traditional use)

@herbal_bp.route('/herbs/search', methods=['GET'])
@role_required([1,2,3])
def search_herbs():
    try:
        # Extract query parameters
        family = request.args.get('family')
        region = request.args.get('region')
        traditional_use = request.args.get('traditional_use')

        # Build the query dynamically based on the parameters provided
        query = Herb.query
        if family:
            query = query.filter(Herb.family.ilike(f'%{family}%'))  # Case-insensitive match
        if region:
            query = query.filter(Herb.region_found.ilike(f'%{region}%'))  # Case-insensitive match
        if traditional_use:
            query = query.filter(Herb.traditional_use.ilike(f'%{traditional_use}%'))  # Case-insensitive match

        # Execute the query
        herbs = query.all()

        if not herbs:
            return jsonify({'message': 'No herbs found matching the criteria'}), 404

        # Format the response
        herbs_list = [{
            'id': herb.id,
            'name': herb.name,
            'scientific_name': herb.scientific_name,
            'family': herb.family,
            'region_found': herb.region_found,
            'description': herb.description,
            'traditional_use': herb.traditional_use,
            'image_url': herb.image_url
        } for herb in herbs]

        return jsonify(herbs_list), 200

    except Exception as e:
        return jsonify({'message': f'Error searching herbs: {str(e)}'}), 500


# update a herb 
@herbal_bp.route('/herbs/<string:herb_name>', methods=['PUT'])
@role_required ([3])
def update_herb(herb_name):
    try:
        # Get the request data
        data = request.get_json()

        # Find the herb by name
        herb = Herb.query.filter_by(name=herb_name).first()

        if not herb:
            return jsonify({'message': f'Herb with name "{herb_name}" not found'}), 404

        # Update herb attributes if provided in the request
        herb.scientific_name = data.get('scientific_name', herb.scientific_name)
        herb.family = data.get('family', herb.family)
        herb.region_found = data.get('region_found', herb.region_found)
        herb.description = data.get('description', herb.description)
        herb.traditional_use = data.get('traditional_use', herb.traditional_use)
        herb.image_url = data.get('image_url', herb.image_url)

        # Commit the changes
        db.session.commit()

        return jsonify({'message': f'Herb "{herb_name}" updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating herb: {str(e)}'}), 400


# add a review 
@herbal_bp.route('/reviews', methods=['POST'])
@role_required ([1,3])
def add_review():
    try:
        # Get the request JSON data
        data = request.get_json()

        # Extract the necessary fields from the request
        user_id = data['user_id']
        herb_id = data['herb_id']
        rating = data['rating']
        review_text = data.get('review', '')  # Optional review text

        # Ensure that the user and herb exist
        user = User.query.get(user_id)
        herb = Herb.query.get(herb_id)

        if not user or not herb:
            return jsonify({'message': 'User or Herb not found'}), 404

        # Create a new review
        new_review = Review(user_id=user_id, herb_id=herb_id, rating=rating, review=review_text)

        # Add the new review to the session and commit
        db.session.add(new_review)
        db.session.commit()

        # Return the success message with the review data
        return jsonify({'message': 'Review added successfully', 'review': new_review.to_dict()}), 201

    except Exception as e:
        # In case of any errors, return a generic error message
        return jsonify({'message': str(e)}), 500


# enable a user to delete a review he/she posted 
@herbal_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@role_required ([1,3])
def delete_review(review_id):
    try:
        # Get the user_id from the request headers
        user_id = request.headers.get('user_id')
        if not user_id:
            return jsonify({'message': 'User ID is required in headers'}), 400
        
        # Fetch the review by ID
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'message': 'Review not found'}), 404

        # Check if the user requesting is the owner of the review
        if review.user_id != int(user_id):
            return jsonify({'message': 'You are not authorized to delete this review'}), 403

        # Delete the review
        db.session.delete(review)
        db.session.commit()

        return jsonify({'message': 'Review deleted successfully'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500



# get all reviews for a specefic herb by name 
@herbal_bp.route('/herbs/<string:herb_name>/reviews', methods=['GET'])
@role_required ([1,2,3])
def get_reviews_by_herb_name(herb_name):
    try:
        # Find the herb by name
        herb = Herb.query.filter_by(name=herb_name).first()
        if not herb:
            return jsonify({'message': 'Herb not found'}), 404

        # Fetch all reviews for the herb
        reviews = Review.query.filter_by(herb_id=herb.id).all()

        # Convert reviews to a list of dictionaries
        reviews_list = [review.to_dict() for review in reviews]

        return jsonify({'herb': herb.name, 'reviews': reviews_list}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500






# add uses 
@herbal_bp.route('/uses', methods=['POST'])
@role_required ([3])
def add_use():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # If data is a single object, convert it to a list for uniform processing
        if not isinstance(data, list):
            data = [data]

        uses_added = []
        for item in data:
            # Check for required fields in each item
            if 'herb_id' not in item or 'use_description' not in item:
                return jsonify({"error": "Missing required fields in one or more items"}), 400

            new_use = Use(
                herb_id=item['herb_id'],
                use_description=item['use_description'],
                dosage=item.get('dosage')  # Optional field
            )
            db.session.add(new_use)
            uses_added.append(new_use.id)

        db.session.commit()
        return jsonify({"message": "Uses added successfully", "ids": uses_added}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@herbal_bp.route('/risks', methods=['POST'])
@role_required ([3])
def add_risk():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # If data is a single object, convert it to a list for uniform processing
        if not isinstance(data, list):
            data = [data]

        risks_added = []
        for item in data:
            # Check if item is a dictionary
            if not isinstance(item, dict):
                return jsonify({"error": "Expected a JSON object or array of objects"}), 400

            # Check for required fields in each item
            if 'herb_id' not in item or 'risk_description' not in item:
                return jsonify({"error": "Missing required fields in one or more items"}), 400

            new_risk = Risk(
                herb_id=item['herb_id'],
                risk_description=item['risk_description'],
                affected_groups=item.get('affected_groups')  # Optional field
            )
            db.session.add(new_risk)
            risks_added.append(new_risk.id)

        db.session.commit()
        return jsonify({"message": "Risks added successfully", "ids": risks_added}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@herbal_bp.route('/diseases', methods=['POST'])
@role_required ([3])
def add_disease():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # If data is a single object, convert it to a list for uniform processing
        if not isinstance(data, list):
            data = [data]

        diseases_added = []
        for item in data:
            # Check if item is a dictionary
            if not isinstance(item, dict):
                return jsonify({"error": "Expected a JSON object or array of objects"}), 400

            # Check for required fields in each item
            if 'name' not in item:
                return jsonify({"error": "Missing required fields in one or more items"}), 400

            new_disease = Disease(
                name=item['name'],
                description=item.get('description'),  # Optional field
                common_treatments=item.get('common_treatments')  # Optional field
            )
            db.session.add(new_disease)
            diseases_added.append(new_disease.id)

        db.session.commit()
        return jsonify({"message": "Diseases added successfully", "ids": diseases_added}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# link a herb to a disease 
@herbal_bp.route('/herb_disease', methods=['POST'])
@role_required ([3])
def link_herb_disease():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # If data is a single object, convert it to a list for uniform processing
        if not isinstance(data, list):
            data = [data]

        links_added = []
        for item in data:
            # Check if item is a dictionary
            if not isinstance(item, dict):
                return jsonify({"error": "Expected a JSON object or array of objects"}), 400

            # Check for required fields in each item
            if 'herb_id' not in item or 'disease_id' not in item:
                return jsonify({"error": "Missing required fields in one or more items"}), 400

            herb_disease = HerbDisease(
                herb_id=item['herb_id'],
                disease_id=item['disease_id']
            )
            db.session.add(herb_disease)
            links_added.append({"herb_id": item['herb_id'], "disease_id": item['disease_id']})

        db.session.commit()
        return jsonify({"message": "Herbs linked to diseases successfully", "links": links_added}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



#users would choose the herb they want from the list of herbs available to get its uses , risks and diseases associated with it after 

#search herbs by name 
@herbal_bp.route('/herbs/search', methods=['GET'])
@role_required ([1,2,3])
def search_for_herbs():
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400

        # Fetch herbs that match the query (case-insensitive, partial match)
        herbs = Herb.query.filter(Herb.name.ilike(f"%{query}%")).limit(10).all()
        if not herbs:
            return jsonify({"message": "No herbs found", "data": []}), 200

        # Return matching herbs
        return jsonify({
            "message": "Herbs retrieved successfully",
            "data": [{"id": herb.id, "name": herb.name} for herb in herbs]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get uses for a herb
@herbal_bp.route('/herbs/<int:herb_id>/uses', methods=['GET'])
@role_required ([1,2,3])
def get_uses_for_herb(herb_id):
    try:
        # Fetch uses for the herb
        uses = Use.query.filter_by(herb_id=herb_id).all()
        if not uses:
            return jsonify({"message": "No uses found for this herb", "data": []}), 200

        # Return uses in a consistent format
        return jsonify({
            "message": "Uses retrieved successfully",
            "data": [{"id": use.id, "use_description": use.use_description, "dosage": use.dosage} for use in uses]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get risks for a herb
@herbal_bp.route('/herbs/<int:herb_id>/risks', methods=['GET'])
@role_required ([1,2,3])
def get_risks_for_herb(herb_id):
    try:
        # Fetch risks for the herb
        risks = Risk.query.filter_by(herb_id=herb_id).all()
        if not risks:
            return jsonify({"message": "No risks found for this herb", "data": []}), 200

        # Return risks in a consistent format
        return jsonify({
            "message": "Risks retrieved successfully",
            "data": [{"id": risk.id, "risk_description": risk.risk_description, "affected_groups": risk.affected_groups} for risk in risks]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get diseases treated by a herb
@herbal_bp.route('/herbs/<int:herb_id>/diseases', methods=['GET'])
@role_required ([1,2,3])
def get_diseases_for_herb(herb_id):
    try:
        # Fetch the herb
        herb = Herb.query.get(herb_id)
        if not herb:
            return jsonify({"error": "Herb not found"}), 404

        # Fetch diseases treated by the herb
        diseases = herb.diseases
        if not diseases:
            return jsonify({"message": "No diseases found for this herb", "data": []}), 200

        # Return diseases in a consistent format
        return jsonify({
            "message": "Diseases retrieved successfully",
            "data": [{"id": disease.id, "name": disease.name, "description": disease.description, "common_treatments": disease.common_treatments} for disease in diseases]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500





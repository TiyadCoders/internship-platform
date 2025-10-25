from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from App.controllers import (open_position, get_positions_by_employer, get_all_positions_json, get_positions_by_employer_json)

position_views = Blueprint('position_views', __name__)

#get all positions
@position_views.route('/api/positions/all', methods = ['GET'])
def get_all_positions():
    position_list = get_all_positions_json()
    return jsonify(position_list), 200

# for opening a position 
@position_views.route('/api/positions/create', methods = ['POST'])
@jwt_required()
def create_position():
     if current_user.role != 'employer':
        return jsonify({"message": "Unauthorized user"}), 403
    
     data = request.json
     position = open_position(title=data['title'], user_id=current_user.id, number_of_positions=data['number'])
     
     if position:
        return jsonify(position.toJSON()), 201
     else:
      return jsonify({"error": "Failed to create position"}), 400
  
  
# get positions for a given employer
@position_views.route('/api/employer/positions', methods=['GET'])
@jwt_required()
def get_employer_positions():
    
    if current_user.role != 'employer':
        return jsonify({"message": "Unauthorized user"}), 403
    
    return jsonify(get_positions_by_employer_json(current_user.id)), 200


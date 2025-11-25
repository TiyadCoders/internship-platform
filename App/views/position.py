from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user
from App.controllers import (
    open_position,
    get_all_positions_json,
    get_positions_by_employer_json,
    require_role
)

position_views = Blueprint('position_views', __name__)


@position_views.route('/api/positions/all', methods=['GET'])
def get_all_positions():
    position_list = get_all_positions_json()
    return jsonify(position_list), 200


@position_views.route('/api/positions/create', methods=['POST'])
@require_role('employer')
def create_position():
    data = request.json
    position = open_position(title=data['title'], user_id=current_user.id, number_of_positions=data['number'])

    if position:
        return jsonify(position.toJSON()), 201
    else:
        return jsonify({"error": "Failed to create position"}), 400


@position_views.route('/api/employer/positions', methods=['GET'])
@require_role('employer')
def get_employer_positions():
    return jsonify(get_positions_by_employer_json(current_user.id)), 200


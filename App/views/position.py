from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user
from App.models.position import PositionStatus
from App.controllers import (
    open_position,
    get_all_positions_json,
    get_positions_by_employer_json,
    get_open_positions_json,
    get_position,
    get_position_json,
    update_position_status,
    update_position,
    require_role,
    apply_for_position,
    get_positions_by_company_json,
)

position_views = Blueprint('position_views', __name__)


@position_views.route('/api/positions/all', methods=['GET'])
def get_all_positions():
    position_list = get_all_positions_json()
    return jsonify(position_list), 200

@position_views.route('/api/employer/positions', methods=['GET'])
@require_role('employer')
def get_employer_positions():
    return jsonify(get_positions_by_employer_json(current_user.id)), 200

@position_views.route('/api/positions', methods=['GET'])
def get_open_positions_route():
    position_list = get_open_positions_json()
    return jsonify(position_list), 200

@position_views.route('/api/positions/<int:position_id>', methods=['GET'])
def get_position_details(position_id):
    position_json = get_position_json(position_id)
    if not position_json:
        return jsonify({"error": "Position not found"}), 404
    return jsonify(position_json), 200

@position_views.route('/api/positions/<int:position_id>', methods=['PUT'])
@require_role('employer')
def edit_position(position_id):
    position = get_position(position_id)
    if not position:
        return jsonify({"error": "Position not found"}), 404

    if position.created_by != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.json or {}

    title = data.get('title')
    number = data.get('number')
    description = data.get('description')

    if title is None and number is None and description is None:
        return jsonify({"error": "No updatable fields provided"}), 400

    updated = update_position(
        position_id,
        title=title,
        number_of_positions=number,
        description=description
    )

    if not updated:
        return jsonify({"error": "Failed to update position"}), 400

    return jsonify(updated.get_json()), 200

@position_views.route('/api/positions/<int:position_id>/close', methods=['PUT'])
@require_role('employer')
def close_position(position_id):
    position = get_position(position_id)
    if not position:
        return jsonify({"error": "Position not found"}), 404

    if position.created_by != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    if position.status == PositionStatus.CLOSED:
        return jsonify({"error": "Position already closed"}), 400

    updated = update_position_status(position_id, PositionStatus.CLOSED)
    if not updated:
        return jsonify({"error": "Failed to close position"}), 400

    return jsonify(updated.get_json()), 200

@position_views.route('/api/positions/<int:position_id>/apply', methods=['POST'])
@require_role('student')
def apply_for_position_route(position_id):
    result = apply_for_position(current_user.id, position_id)

    if isinstance(result, dict) and "error" in result:
        msg = result["error"]
        if msg == "Position not found":
            return jsonify(result), 404
        return jsonify(result), 400

    if not result:
        return jsonify({"error": "Failed to apply for position"}), 400

    return jsonify(result.get_json()), 201

@position_views.route('/api/positions', methods=['POST'])
@require_role('employer')
def create_position_api():
    data = request.json
    if not data or 'title' not in data or 'number' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    description = data.get('description', None)
    position = open_position(
        title=data['title'],
        user_id=current_user.id,
        number_of_positions=data['number'],
        description=description
    )

    if position:
        return jsonify(position.get_json()), 201
    return jsonify({"error": "Failed to create position"}), 400

@position_views.route('/api/positions/company/<int:company_id>', methods=['GET'])
def get_company_positions(company_id):
    positions = get_positions_by_company_json(company_id)
    return jsonify(positions), 200


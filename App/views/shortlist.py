from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from App.controllers import (
    add_student_to_shortlist,
    decide_shortlist,
    get_shortlist_by_student,
    get_shortlist_by_position,
    require_role
)

shortlist_views = Blueprint('shortlist_views', __name__)


@shortlist_views.route('/api/shortlist', methods=['POST'])
@require_role('staff')
def add_student_shortlist():
    data = request.json
    request_result = add_student_to_shortlist(
        student_id=data['student_id'],
        position_id=data['position_id'],
        staff_id=current_user.id
    )

    if request_result:
        return jsonify(request_result.toJSON()), 200
    else:
        return jsonify({"error": "Failed to add to shortlist"}), 401


@shortlist_views.route('/api/shortlist/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_shortlist(student_id):
    # Students can only view their own shortlist
    if current_user.role == 'student' and current_user.id != student_id:
        return jsonify({"message": "Unauthorized user"}), 403

    shortlists = get_shortlist_by_student(student_id)
    return jsonify([s.toJSON() for s in shortlists]), 200


@shortlist_views.route('/api/shortlist', methods=['PUT'])
@require_role('employer')
def shortlist_decide():
    data = request.json
    if not data or 'student_id' not in data or 'position_id' not in data or 'decision' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    request_result = decide_shortlist(data['student_id'], data['position_id'], data['decision'])

    if request_result:
        return jsonify(request_result.toJSON()), 200
    else:
        return jsonify({"error": "Failed to update shortlist"}), 400


@shortlist_views.route('/api/shortlist/position/<int:position_id>', methods=['GET'])
@require_role('employer', 'staff')
def get_position_shortlist(position_id):
    shortlists = get_shortlist_by_position(position_id)
    return jsonify([s.toJSON() for s in shortlists]), 200
     
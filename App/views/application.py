from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from App.controllers import (
    create_application,
    shortlist_application,
    accept_application,
    reject_application,
    get_applications_by_student,
    get_applications_by_position,
    get_application,
    require_role
)
application_views = Blueprint('application_views', __name__)


@application_views.route('/api/application', methods=['POST'])
@require_role('staff')
def create_application_route():
    data = request.json
    if not data or 'student_id' not in data or 'position_id' not in data or 'staff_id' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    application = create_application(data['student_id'], data['position_id'], data['staff_id'])
    if application:
        return jsonify(application.toJSON()), 201
    else:
        return jsonify({"error": "Failed to create application"}), 400


@application_views.route('/api/application/<int:id>', methods=['GET'])
@jwt_required()
@require_role('employer', 'staff')
def get_application_by_id(id):
    application = get_application(id)
    if application:
        return jsonify(application.toJSON()), 200
    else:
        return jsonify({"error": "Application not found"}), 404
    


@application_views.route('/api/application/student/<int:student_id>', methods=['GET'])
@jwt_required()
@require_role('employer')
def get_application_by_student(student_id):
    applications = get_applications_by_student(student_id)
    return jsonify([app.toJSON() for app in applications]), 200


@application_views.route('/api/application/position/<int:position_id>', methods=['GET'])
@jwt_required()
def get_application_by_position(position_id):
    applications = get_applications_by_position(position_id)
    return jsonify([app.toJSON() for app in applications]), 200


@application_views.route('/api/application/<int:id>/shortlist', methods=['PUT'])
@require_role('staff')
def shortlist_application_route(id):
    application = shortlist_application(id)
    if application:
        return jsonify(application.toJSON()), 200
    else:
        return jsonify({"error": "Application not found"}), 404
    

@application_views.route('/api/application/<int:id>/accept', methods=['PUT'])
@require_role('staff')
def accept_application_route(id):
    application = accept_application(id)
    if application:
        return jsonify(application.toJSON()), 200
    else:
        return jsonify({"error": "Application not found"}), 404
    
@application_views.route('/api/application/<int:id>/reject', methods=['PUT'])
@require_role('staff')
def reject_application_route(id):
    application = reject_application(id)
    if application:
        return jsonify(application.toJSON()), 200
    else:
        return jsonify({"error": "Application not found"}), 404
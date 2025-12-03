from flask import Blueprint, jsonify
from flask_jwt_extended import current_user
from App.controllers import (
    shortlist_application,
    accept_application,
    reject_application,
    get_applications_by_position,
    get_application,
    get_applications,
    require_role,
    withdraw_application
)
from App.database import db

application_views = Blueprint('application_views', __name__)


def _staff_can_access_application(staff_user, application):
    """Check if staff member can access this application (same company)."""
    return application.position.employer.company_id == staff_user.company_id


@application_views.route('/api/applications', methods=['GET'])
@require_role('staff', 'student')
def view_all_applications():
    """View all applications (staff and students)."""
    applications = get_applications(current_user)
    return jsonify([app.get_json() for app in applications]), 200


@application_views.route('/api/applications/<int:application_id>', methods=['GET'])
@require_role('staff', 'student')
def view_application(application_id):
    """View a single application by ID (staff and students)."""
    application = get_application(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    # Authorization: students can only view their own, staff only their company's
    if current_user.role == "student":
        if application.student_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403
    elif current_user.role == "staff":
        if not _staff_can_access_application(current_user, application):
            return jsonify({"error": "Unauthorized"}), 403
    return jsonify(application.get_json()), 200


@application_views.route('/api/applications/<int:application_id>/shortlist', methods=['PUT'])
@require_role('staff')
def shortlist_application_route(application_id):
    """Shortlist a single application by ID (staff only)."""
    application = get_application(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    if not _staff_can_access_application(current_user, application):
        return jsonify({"error": "Unauthorized"}), 403
    result = shortlist_application(application_id)
    if isinstance(result, dict) and 'error' in result:
        return jsonify({"error": result['error'], "status": result['application'].status.value}), 400
    return jsonify(result.get_json()), 200


@application_views.route('/api/applications/<int:application_id>/accept', methods=['PUT'])
@require_role('staff')
def accept_application_route(application_id):
    """Accept a single application by ID (staff only)."""
    application = get_application(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    if not _staff_can_access_application(current_user, application):
        return jsonify({"error": "Unauthorized"}), 403
    result = accept_application(application_id)
    if isinstance(result, dict) and 'error' in result:
        return jsonify({"error": result['error'], "status": result['application'].status.value}), 400
    return jsonify(result.get_json()), 200


@application_views.route('/api/applications/<int:application_id>/reject', methods=['PUT'])
@require_role('staff')
def reject_application_route(application_id):
    """Reject a single application by ID (staff only)."""
    application = get_application(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    if not _staff_can_access_application(current_user, application):
        return jsonify({"error": "Unauthorized"}), 403
    result = reject_application(application_id)
    if isinstance(result, dict) and 'error' in result:
        return jsonify({"error": result['error'], "status": result['application'].status.value}), 400
    return jsonify(result.get_json()), 200


@application_views.route('/api/applications/<int:application_id>/withdraw', methods=['PUT'])
@require_role('student')
def withdraw_application_route(application_id):
    """Withdraw a single application by ID (student only)."""
    application = get_application(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    # Authorization: students can only withdraw their own applications
    if application.student_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    result = withdraw_application(application_id)
    if isinstance(result, dict) and 'error' in result:
        return jsonify({"error": result['error'], "status": result['application'].status.value}), 400
    return jsonify(result.get_json()), 200


@application_views.route('/api/applications/position/<int:position_id>', methods=['GET'])
@require_role('staff')
def view_applications_by_position(position_id):
    """View applications by position ID (staff only)."""
    from App.models import Position
    position = db.session.get(Position, position_id)
    if not position:
        return jsonify({"error": "Position not found"}), 404
    # Authorization: staff can only view applications for their company's positions
    if position.employer.company_id != current_user.company_id:
        return jsonify({"error": "Unauthorized"}), 403
    applications = get_applications_by_position(position_id)
    return jsonify([app.get_json() for app in applications]), 200

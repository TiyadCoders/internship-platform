from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.models import Student

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    jwt_required,
    get_user
)

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'])
    return redirect(url_for('user_views.get_user_page'))

@user_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@user_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    user = create_user(data['username'], data['password'])
    if not user:
        return jsonify({'error': 'Failed to create user'}), 400
    return jsonify({'message': f"user {user.username} created with id {user.id}"}), 201

@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')

@user_views.route('/api/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_details(student_id):
    if jwt_current_user.role not in ['employer', 'staff']:
        return jsonify({"error": "Forbidden"}), 403

    user = get_user(student_id)
    if not user or not isinstance(user, Student):
        return jsonify({"error": "Student not found"}), 404

    data = user.get_json()
    data["type"] = "Student"

    return jsonify(data), 200

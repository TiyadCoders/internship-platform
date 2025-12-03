from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
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
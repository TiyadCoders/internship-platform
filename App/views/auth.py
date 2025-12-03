from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, flash, redirect
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies

from App.controllers import (
    login,
    create_user,
)

STUDENT_REQUIRED_FIELDS = ['email', 'dob', 'gender', 'degree', 'phone', 'gpa', 'resume']

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')


# Page/Action Routes

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")


@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    response = redirect(request.referrer)
    if not token:
        flash('Bad username or password given')
    else:
        flash('Login Successful')
        set_access_cookies(response, token)
    return response

@auth_views.route('/signup', methods=['POST'])
def signup_action():
    data = request.form
    response = redirect(request.referrer)

    if 'username' not in data or 'password' not in data or 'type' not in data:
        flash('Missing required fields: username, password, and type are required')
        return response

    if data['type'] not in ['student', 'employer', 'staff']:
        flash('Invalid user type')
        return response

    student_data = None
    if data['type'] == 'student':
        missing_fields = [field for field in STUDENT_REQUIRED_FIELDS if field not in data]
        if missing_fields:
            flash(f'Missing required fields: {", ".join(missing_fields)}')
            return response

        try:
            dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format for dob. Use YYYY-MM-DD')
            return response

        try:
            gpa = float(data['gpa'])
        except ValueError:
            flash('Invalid value for gpa. Must be a number')
            return response

        student_data = {
            'email': data['email'],
            'dob': dob,
            'gender': data['gender'],
            'degree': data['degree'],
            'phone': data['phone'],
            'gpa': gpa,
            'resume': data['resume']
        }

    user, error = create_user(data['username'], data['password'], data['type'], student_data=student_data)
    if error:
        flash(f'Signup failed: {error}')
    else:
        token = login(data['username'], data['password'])
        flash('Signup Successful')
        set_access_cookies(response, token)
    return response


@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer)
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

# API Routes

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
    data = request.json
    token = login(data['username'], data['password'])
    if not token:
        return jsonify(message='bad username or password given'), 401
    return jsonify(access_token=token)

@auth_views.route('/api/signup', methods=['POST'])
def signup_api():
    data = request.json

    if not data:
        return jsonify(message='Request body is required'), 400

    if 'username' not in data or 'password' not in data or 'type' not in data:
        return jsonify(message='Missing required fields: username, password, and type are required'), 400

    if data['type'] not in ['student', 'employer', 'staff']:
        return jsonify(message='Invalid user type. Must be student, employer, or staff'), 400

    student_data = None
    if data['type'] == 'student':
        missing_fields = [field for field in STUDENT_REQUIRED_FIELDS if field not in data]
        if missing_fields:
            return jsonify(message=f'Missing required fields: {", ".join(missing_fields)}'), 400

        try:
            dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify(message='Invalid date format for dob. Use YYYY-MM-DD'), 400

        try:
            gpa = float(data['gpa'])
        except (ValueError, TypeError):
            return jsonify(message='Invalid value for gpa. Must be a number'), 400

        student_data = {
            'email': data['email'],
            'dob': dob,
            'gender': data['gender'],
            'degree': data['degree'],
            'phone': data['phone'],
            'gpa': gpa,
            'resume': data['resume']
        }

    user, error = create_user(data['username'], data['password'], data['type'], student_data=student_data)
    if error:
        status_code = 409 if "already taken" in error else 400
        return jsonify(message=error), status_code

    token = login(data['username'], data['password'])
    if not token:
        return jsonify(message='User created but login failed'), 500
    return jsonify(access_token=token), 201

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response

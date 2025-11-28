from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from App.controllers import (
    create_company,
    get_company,
    get_all_companies,
    update_company,
    delete_company,
    require_role
)

company_views = Blueprint('company_views', __name__)


@company_views.route('/api/company', methods=['POST'])
@jwt_required()
@require_role('staff')
def create_company_route():
    data = request.json
    if not data or 'name' not in data or 'description' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    company = create_company(data['name'], data['description'])
    if company:
        return jsonify(company.get_json()), 201
    else:
        return jsonify({"error": "Failed to create company"}), 400


@company_views.route('/api/company/<int:id>', methods=['GET'])
@jwt_required()
def get_company_by_id(id):
    company = get_company(id)
    if company:
        return jsonify(company.get_json()), 200
    else:
        return jsonify({"error": "Company not found"}), 404


@company_views.route('/api/companies', methods=['GET'])
@jwt_required()
def get_all_companies_route():
    companies = get_all_companies()
    return jsonify([company.get_json() for company in companies]), 200


@company_views.route('/api/company/<int:id>', methods=['PUT'])
@jwt_required()
@require_role('staff')
def update_company_route(id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    company = update_company(id, name=data.get('name'), description=data.get('description'))
    if company:
        return jsonify(company.get_json()), 200
    else:
        return jsonify({"error": "Company not found"}), 404


@company_views.route('/api/company/<int:id>', methods=['DELETE'])
@jwt_required()
@require_role('staff')
def delete_company_route(id):
    result = delete_company(id)
    if result:
        return jsonify({"message": "Company deleted successfully"}), 200
    else:
        return jsonify({"error": "Company not found"}), 404

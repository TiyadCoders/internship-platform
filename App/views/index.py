from flask import Blueprint, render_template, jsonify
from App.controllers import initialize

index_views = Blueprint('index_views', __name__, template_folder='../templates')


@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')


@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@index_views.route('/api/init', methods=['POST'])
def initialize_api():
    initialize()
    return jsonify({'message': 'Database initialized with test data'}), 200

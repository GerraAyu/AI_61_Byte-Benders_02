from flask import Blueprint, request, jsonify

from data_services import database
from services.services_middleware import session_required

auth_bp = Blueprint('auth', __name__)


# Route to Login
@auth_bp.route('/sign-in', methods=['POST'])
def sign_in():
    email = request.json.get('EmployeeEmail', '').strip()
    passwd = request.json.get('EmployeePassword', '').strip()

    if email != '' and passwd != '':
        serv_res = database.user_sign_in_service(email, passwd)
        if serv_res['data'] is None:
            return jsonify(serv_res)
        
        user_id = serv_res['data']['_id']
        serv_res = database.create_session_service(user_id)
        return jsonify(serv_res)
        
    return jsonify({"data": None, "message": "Credentials cannot be empty"})


# Route to Logout
@auth_bp.route('/sign-out', methods=['POST'])
@session_required
def sign_out():
    serv_res = database.delete_session_service(request.session_data['SessionToken'])
    return jsonify(serv_res)


# Create new user
@auth_bp.route('/sign-up', methods=['POST'])
def new_user():
    user = request.json

    if user['EmployeeEmail'] != '' and user['EmployeePassword'] != '':
        serv_res = database.user_sign_up_service(user)
        if serv_res['data'] is None:
            return jsonify(serv_res)
        
        user_id = serv_res['data']['EmployeeID']
        serv_res = database.create_session_service(user_id)
        return jsonify(serv_res)

    return jsonify({"data": None, "message": "Credentials cannot be empty"})


# Route to Get User
@auth_bp.route('/get-user', methods=['GET'])
@session_required
def get_user():
    serv_res = database.get_user_service(request.session_data['EmployeeID'])
    return jsonify(serv_res)

from flask import Blueprint, request, jsonify

from data_services import database
from services.services_middleware import session_required

session_bp = Blueprint('session', __name__)


# Create a session
@session_bp.route('/create', methods=['POST'])
def create_session():
    user_id = request.json.get('EmployeeID', None)
    if user_id and database.verify({'EmployeeID' : user_id}):
        serv_res = database.create_session_service(user_id)
        return jsonify(serv_res)
    return jsonify({"data": None, "message": "Invalid user ID"}), 400


# Delete a session
@session_bp.route('/delete', methods=['POST'])
@session_required
def delete_session():
    serv_res = database.delete_session_service(request.session_data['SessionToken'])
    return jsonify(serv_res)

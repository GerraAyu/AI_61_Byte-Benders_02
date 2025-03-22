from flask import Blueprint, request, jsonify

from data_services import database
from services.services_query import get_user_intent, verify_access, initialize_retriever, process_general_query

query_bp = Blueprint('query', __name__)


query_bp.route('/query')
def handle_query():
    user_id = request.session_data['user_id']
    user_query = request.params.get('query')
    user_intent, departments = get_user_intent(user_query)

    if user_intent == 'General':
        retriever = initialize_retriever()
        response = process_general_query(user_query, retriever)
        return response
    
    if user_intent == 'L1':
        response = raise_L1_ticket()
        return response
    
    if user_intent == 'ERP':
        if verify_access(user_id, departments):
            response = get_query_response(user_intent, user_query, departments)
            return response
        else:
            return jsonify({"data": None, "error": "Unauthorized user"})
    
    database.store_query_service(user_id, user_query, response['data'])

    return jsonify({"data": None, "error": "An error occurred!"})



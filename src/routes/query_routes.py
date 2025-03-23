import json
from flask import Blueprint, request, jsonify

from data_services import database
from services.services_middleware import session_required
from services.services_query import get_user_intent, verify_access, initialize_retriever, process_general_query, raise_L1_ticket, generate_response

query_bp = Blueprint('query', __name__)


@query_bp.route('/query')
@session_required
def handle_query():
    user_id = request.session_data['EmployeeID']
    user_query = request.values.get('query')

    user_intent = ''
    departments_list = []

    try:
        intent = get_user_intent(user_query)
        intent_split = intent[1:-1].split(', ')
        user_intent = intent_split[0].replace("'", '')
        departments = intent_split[1][1:-1].replace("'", '')
        departments_list = departments.split(', ')
    except:
        return jsonify({"data": None, "error": "An error occurred!"})

    if user_intent == 'General':
        print("For General request")
        retriever = initialize_retriever()
        response = process_general_query(user_query, retriever)
        try:
            database.store_query_service(user_id, user_query, response['data'])
        except: pass
        return response
    
    if user_intent == 'L1':
        print("For L1 request")
        response = raise_L1_ticket(user_id, user_query)
        try:
            database.store_query_service(user_id, user_query, response['data'])
        except: pass
        return response
    
    if user_intent == 'ERP':
        print("For ERP request")
        if verify_access(user_id, departments_list):
            response = generate_response(user_query)
            try:
                database.store_query_service(user_id, user_query, response['data'])
            except: pass
            return response
        else:
            return jsonify({"data": None, "error": "Unauthorized user"})

    return jsonify({"data": None, "error": "An error occurred!"})

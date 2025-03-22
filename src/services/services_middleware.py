from functools import wraps
from flask import request, jsonify
from data_services.database import user_col, session_col


# Middleware decorator to check if a session is valid
def session_required(f):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_token = request.headers.get('Authorization')
            if not session_token:
                return jsonify({'data': None, 'message': 'Session token is missing'}), 401
            
            session_result = session_col.validate_session(session_token)
            if session_result['data'] is None:
                return jsonify(session_result), 401  # Invalid or expired session
            
            request.session_data = session_result['data']
            return f(*args, **kwargs)  # Pass session data to route
        return decorated_function
    return decorator(f)


# Middleware decorator to check if a session is valid and the user is an admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.headers.get('Authorization')
        if not session_token:
            return jsonify({'data': None, 'message': 'Session token is missing'}), 401

        session_result = session_col.validate_session(session_token)
        if session_result['data'] is None:
            return jsonify(session_result), 401  # Invalid or expired session

        user_id = session_result['data']['user_id']
        user_result = user_col.get_user_by_id(user_id)

        if user_result['data'] is None or not user_result['data'].get('is_admin', False):
            return jsonify({'data': None, 'message': 'Admin access required'}), 403
        
        request.session_data = session_result['data']
        return f(*args, **kwargs)

    return decorated_function
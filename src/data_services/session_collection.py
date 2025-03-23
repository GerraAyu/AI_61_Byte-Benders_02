import bson
import secrets
from datetime import datetime, timedelta
from .collection import _Collection


class SessionCollection(_Collection):
    def __init__(self, collection, user_col):
        super().__init__(collection)
        self.user_col = user_col


    # Function to create a new session
    def create_session(self, user_id):
        print(user_id)
        user = self.user_col.find_document({'_id': bson.ObjectId(user_id)})
        if user is None:
            return {'data': None, 'message': "User does not exist"}
        existing_sessions = self.find_documents({"EmployeeID": user_id})
        for session in existing_sessions:
            self.remove_document({"_id": session["_id"]})
            
        session_token = secrets.token_hex(32)
        expiration_time = datetime.now() + timedelta(hours=24)  # Session expires in 24 hours

        session = {
            "EmployeeID": user_id,
            "SessionToken": session_token,
            "CreatedAt": str(datetime.now()),
            "ExpiresAt": str(expiration_time),
        }

        insert_result = self.insert_document(session)
        session_id = str(insert_result.inserted_id)
        session['_id'] = session_id

        # Update user document with new session ID
        self.user_col.update_document({'_id': bson.ObjectId(user_id)}, {"$set": {"SessionID": session_id}}) 

        return {'data': session, 'message': "Session created successfully"}


    # Function to validate a session
    def validate_session(self, session_token):
        session = self.find_document({"SessionToken": session_token})
        if session is None:
            return {'data': None, 'message': "Invalid session token"}
        
        expiration_time = datetime.strptime(session["ExpiresAt"], "%Y-%m-%d %H:%M:%S.%f")
        if datetime.now() >= expiration_time:
            self.remove_document({"_id": session["_id"]})
            return {'data': None, 'message': "Session has expired"}

        return {'data': session, 'message': "Session is valid"}


    # Function to delete a session
    def delete_session(self, session_token):
        session = self.find_document({"SessionToken": session_token})
        self.remove_document({"_id": session["_id"]})
        return {'data': True, 'message': "Session deleted successfully"}


    # Function to retrieve all sessions for a user
    def get_sessions_for_user(self, user_id):
        sessions = self.find_documents({"EmployeeID": user_id})
        if not sessions:
            return {'data': [], 'message': "No active sessions found"}

        session_list = [
            {
                "SessionID": str(session["_id"]),
                "SessionToken": session["SessionToken"],
                "CreatedAt": session["CreatedAt"],
                "ExpiresAt": session["ExpiresAt"],
            }
            for session in sessions
        ]
        return {'data': session_list, 'message': "Sessions retrieved successfully"}

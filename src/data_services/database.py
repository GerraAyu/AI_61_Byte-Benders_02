import config

from .cluster_manager import ClusterManager
from .user_collection import UserCollection
from .query_collection import QueryCollection
from .session_collection import SessionCollection

# Initialize collections
cluster_manager = ClusterManager(config.MONGO_URI)
user_col = UserCollection(cluster_manager.get_collection(config.DB, config.USER_COLLECTION))
query_col = QueryCollection(cluster_manager.get_collection(config.DB, config.QUERY_COLLECTION), user_col)
session_col = SessionCollection(cluster_manager.get_collection(config.DB, config.SESSION_COLLECTION), user_col)


# User Sign-In Service
def user_sign_in_service(email, passwd):
    return user_col.retrieve_user(email, passwd)


# User Sign-Up Service
def user_sign_up_service(user):
    return user_col.create_user(user)


# Create Session Service
def create_session_service(user_id):
    session = session_col.create_session(user_id).get('data', None)
    if session is not None:
        del session["_id"], session["user_id"]
        return {"data": {"session": session}, "message": "Session created successfully"}
    return {"data": None, "message": "Failed to create session"}


# Delete Session Service
def delete_session_service(token):
    deleted = session_col.delete_session(token)
    if deleted['data']:
        return {"data": None, "message": "Session deleted successfully"}
    return {"data": None, "message": "Invalid session token"}


# Get User by ID
def get_user_service(user_id):
    return user_col.get_user_by_id(user_id)


# Store Query Service
def store_query_service(user_id, query_text, response_text):
    return query_col.store_query(user_id, query_text, response_text)


# Get Query by ID Service
def get_query_by_id_service(query_id):
    return query_col.get_query_by_id(query_id)


# Get Queries by User Service
def get_queries_by_user_service(user_id):
    return query_col.get_queries_by_user(user_id)


# Get All Queries Service
def get_all_queries_service():
    return query_col.get_all_queries()


# Get Frequent Queries Service
def get_frequent_queries_service(threshold=0.8):
    return query_col.get_frequent_queries(threshold)

import bson
from datetime import datetime
from .collection import _Collection
from bcrypt import hashpw, checkpw, gensalt


class UserCollection(_Collection):
    def __init__(self, collection):
        super().__init__(collection)


    # Function to create a new user
    def create_user(self, user):
        if self.find_document({'EmployeeEmail': user['EmployeeEmail']}) is not None:
            return {'data': None, 'message': "User with this email already exists"}

        user_doc = {
            'EmployeeID': user['EmployeeID'],
            'EmployeeName': user['EmployeeName'],
            'Department': user['Department'],
            'JobTitle': user['JobTitle'],
            'AccessLevel': user['AccessLevel'],
            'SalesAccess': user['SalesAccess'],
            'PlanningAccess': user['PlanningAccess'],
            'PurchaseAccess': user['PurchaseAccess'],
            'StoresAccess': user['StoresAccess'],
            'ProductionAccess': user['ProductionAccess'],
            'MaintenanceAccess': user['MaintenanceAccess'],
            'QualityAccess': user['QualityAccess'],
            'DispatchAccess': user['DispatchAccess'],
            'HRAccess': user['HRAccess'],
            'AccountsAccess': user['AccountsAccess'],
            'SettingsAccess': user['SettingsAccess'],
            'EmployeeEmail': user['EmployeeEmail'],
            'EmployeePassword': hashpw(user['EmployeePassword'].encode('utf-8'), gensalt()),
            'EmployeeIsAdmin': user.get('EmployeeIsAdmin', False),
            'JoinedAt': str(datetime.now())
        }

        insert_result = self.insert_document(user_doc)
        return {'data': {'EmployeeID' : str(insert_result.inserted_id)}, 'message': "User created successfully"}


    # Function to retrieve a user
    def retrieve_user(self, email, passwd):
        user = self.find_document({'EmployeeEmail': email})
        if user is not None:
            if checkpw(passwd.encode("utf-8"), user["EmployeePassword"]):
                del user["EmployeePassword"]
                user["_id"] = str(user["_id"])
                return {'data': user, 'message': "User retrieved successfully"}
            return {'data': None, 'message': "Invalid credentials"}
        return {'data': None, 'message': "User does not exist"}


    # Function to Retrieve User by ID
    def get_user_by_id(self, user_id):
        user = self.find_document({'_id': bson.ObjectId(user_id)})
        if user is not None:
            del user["EmployeePassword"]
            del user["_id"]
            return {'data': user, 'message': "User retrieved successfully"}
        return {'data': None, 'message': "User does not exist"}
    

    # Function to Delete User and all their associated Chats
    def delete_user(self, user_id):
        delete_result = self.remove_document({'_id': bson.ObjectId(user_id)})
        if delete_result.deleted_count > 0:
            return {'data': True, 'message': "User deleted successfully"}
        return {'data': None, 'message': "Failed to delete user"}
    
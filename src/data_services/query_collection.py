import bson
from datetime import datetime
from .collection import _Collection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class QueryCollection(_Collection):
    def __init__(self, collection, user_col):
        super().__init__(collection)
        self.user_col = user_col


    # Function to store a new query along with its response
    def store_query(self, user_id, query_text, response_text):
        if not self.user_col.verify(user_id):
            return {'data': None, 'message': 'User does not exist'}
        
        query_doc = {
            'EmployeeID': bson.ObjectId(user_id),
            'QueryText': query_text,
            'ResponseText': response_text,
            'Timestamp': str(datetime.now())
        }
        
        insert_result = self.insert_document(query_doc)
        return {'data': {'query_id': str(insert_result.inserted_id)}, 'message': 'Query stored successfully'}


    # Function to retrieve a query by query_id
    def get_query_by_id(self, query_id):
        query = self.find_document({'_id': bson.ObjectId(query_id)})
        if query is not None:
            query['_id'] = str(query['_id'])
            query['EmployeeID'] = str(query['EmployeeID'])
            return {'data': query, 'message': 'Query retrieved successfully'}
        return {'data': None, 'message': 'Query does not exist'}


    # Function to retrieve all queries by user_id
    def get_queries_by_user(self, user_id):
        if not self.user_col.verify(user_id):
            return {'data': None, 'message': 'User does not exist'}
        
        queries = self.find_documents({'user_id': bson.ObjectId(user_id)})
        query_list = [{'query_id': str(q['_id']), 'QueryText': q['QueryText'], 'ResponseText': q['ResponseText'], 'Timestamp': q['Timestamp']} for q in queries]
        
        return {'data': query_list, 'message': 'Queries retrieved successfully'}


    # Function to retrieve all queries in the database
    def get_all_queries(self):
        queries = self.find_documents({})
        query_list = [{'query_id': str(q['_id']), 'EmployeeID': str(q['EmployeeID']), 'QueryText': q['QueryText'], 'ResponseText': q['ResponseText'], 'Timestamp': q['Timestamp']} for q in queries]
        
        return {'data': query_list, 'message': 'All queries retrieved successfully'}


    # Function to identify most frequent queries using cosine similarity
    def get_frequent_queries(self, threshold=0.8):
        queries = self.get_all_queries()['data']
        if not queries:
            return {'data': None, 'message': 'No queries available'}
        
        query_texts = [q['QueryText'] for q in queries]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(query_texts)
        
        similarities = cosine_similarity(tfidf_matrix)
        frequent_queries = {}
        
        for i, query in enumerate(query_texts):
            for j in range(i + 1, len(query_texts)):
                if similarities[i][j] >= threshold:
                    frequent_queries[query] = frequent_queries.get(query, 0) + 1
        
        sorted_queries = sorted(frequent_queries.items(), key=lambda x: x[1], reverse=True)
        
        return {'data': sorted_queries, 'message': 'Frequent queries identified'}

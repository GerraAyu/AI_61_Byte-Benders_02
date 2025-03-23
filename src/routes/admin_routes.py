import os
import psycopg2

from flask import Blueprint, request, jsonify
from data_services import database
from services.services_middleware import admin_required
import dotenv
import os
dotenv.load_dotenv()
admin_bp = Blueprint('admin', __name__)


# Route to get data from specific collections
@admin_bp.route('/get-collection-data', methods=['POST'])
@admin_required
def get_collection_data():
    collections = [
        'Sales_NPD', 'Stores', 'Maintenance', 'Purchase', 'Settings',
        'Employees', 'HR_Admin', 'Production', 'Dispatch_Logistics',
        'Quality', 'Accounts_Finance', 'Planning'
    ]
    
    collection_name = request.json.get('collection_name', '').strip()
    if collection_name not in collections:
        return jsonify({"data": None, "message": "Invalid collection name"}), 400
    Supabase_URL = os.getenv("SUPABASE_URL")

    conn = psycopg2.connect(
            Supabase_URL
        )

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {collection_name}")
    collection_data = cursor.fetchall()
    cursor.close()
    conn.close()
    data_list = [doc for doc in collection_data]

    return jsonify({"data": data_list, "message": f"Data retrieved from {collection_name}"})


# Route to get all queries
@admin_bp.route('/get-all-queries', methods=['GET'])
@admin_required
def get_all_queries():
    serv_res = database.get_all_queries_service()
    return jsonify(serv_res)


# Route to get frequent queries
@admin_bp.route('/get-frequent-queries', methods=['GET'])
@admin_required
def get_frequent_queries():
    threshold = request.args.get('threshold', default=0.8, type=float)
    serv_res = database.get_frequent_queries_service(threshold)
    return jsonify(serv_res)


# Route to add a query to FAQs
@admin_bp.route('/add-to-faqs', methods=['POST'])
@admin_required
def add_to_faqs():
    query_text = request.json.get('query_text', '').strip()
    response_text = request.json.get('response_text', '').strip()

    if query_text and response_text:
        serv_res = database.faq_col.add_to_faqs(query_text, response_text)
        return jsonify(serv_res)

    return jsonify({"data": None, "message": "Query text and response text cannot be empty"}), 400

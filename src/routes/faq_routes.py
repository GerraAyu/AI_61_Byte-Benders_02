from flask import Blueprint, jsonify
from data_services.database import list_all_faqs_service

faq_bp = Blueprint("faq", __name__)


# List all FAQs
@faq_bp.route("/list", methods=["GET"])
def list_faqs():
    serv_res = list_all_faqs_service()
    return jsonify(serv_res)

from .collection import _Collection
from datetime import datetime


class FAQCollection(_Collection):
    def __init__(self, collection):
        super().__init__(collection)


    def add_to_faqs(self, query_text, response_text):
        faq_doc = {
            "query_text": query_text,
            "response_text": response_text,
            "added_at": str(datetime.now())
        }
        insert_result = self.insert_document(faq_doc)
        return {'data': {'faq_id': str(insert_result.inserted_id)}, 'message': "Query added to FAQs successfully"}


    def get_all_faqs(self):
        faqs = self.find_documents({})
        faq_list = [{"faq_id": str(f["_id"]), "query_text": f["query_text"], "response_text": f["response_text"], "added_at": f["added_at"]} for f in faqs]
        return {'data': faq_list, 'message': "All FAQs retrieved successfully"}

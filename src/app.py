from flask import Flask

from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.session_routes import session_bp
from routes.query_routes import query_bp
from routes.faq_routes import faq_bp

app = Flask(__name__)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(session_bp)
app.register_blueprint(query_bp, url_prefix='/api')
app.register_blueprint(faq_bp)

if __name__ == '__main__':
    app.run(debug=True, load_dotenv=True)

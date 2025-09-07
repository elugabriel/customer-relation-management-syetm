from flask import Flask, render_template
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
#from routes.customer import customer_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"  # 🔑 update this later for production
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    # app.register_blueprint(staff_dashboard_bp, url_prefix="/staff")
    # app.register_blueprint(customer_dashboard_bp, url_prefix="/customer")

    @app.route("/")
    def home():
        return render_template("/auth/login.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

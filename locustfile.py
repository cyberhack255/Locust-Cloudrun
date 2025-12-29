import os
from locust import HttpUser, task, events
from flask import session, url_for, redirect, request, make_response
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix

# --- CONFIGURATION ---
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# You MUST set this to a fixed string in your environment variables for Cloud Run!
SECRET_KEY = os.getenv("LOCUST_SECRET_KEY", "FIXED_SECRET_KEY_12345") 
ALLOWED_EMAILS = os.getenv("ALLOWED_EMAILS", "").split(",")

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if environment.web_ui:
        app = environment.web_ui.app
        app.secret_key = SECRET_KEY

        # --- 1. CLOUD RUN HTTPS FIXES (CRITICAL) ---
        # Trust the Cloud Run Load Balancer headers
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
        
        # Force cookies to be Secure (HTTPS only) and Lax (Modern browser standard)
        app.config.update(
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
            PREFERRED_URL_SCHEME='https'
        )

        # --- 2. Setup OAuth ---
        oauth = OAuth(app)
        oauth.register(
            name='google',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )

        @app.route('/login')
        def login():
            # Force HTTPS for the callback URL
            redirect_uri = url_for('auth', _external=True, _scheme='https')
            return oauth.google.authorize_redirect(redirect_uri)

        @app.route('/google/auth')
        def auth():
            token = oauth.google.authorize_access_token()
            user_info = token.get('userinfo')
            
            if ALLOWED_EMAILS and ALLOWED_EMAILS != [''] and user_info['email'] not in ALLOWED_EMAILS:
                return f"Access Denied: {user_info['email']} is not authorized.", 403

            # Save to session (This is where it was failing before)
            session['user'] = user_info
            
            # Make the session permanent (optional, keeps you logged in longer)
            session.permanent = True
            
            return redirect('/')

        @app.route('/logout')
        def logout():
            session.pop('user', None)
            return redirect('/')

        @app.before_request
        def protect_routes():
            # Health check for Cloud Run (prevents internal 500 errors)
            if request.path == "/health":
                return "OK", 200

            if request.path.startswith("/static") or \
               request.path == "/login" or \
               request.path == "/google/auth":
                return

            if session.get('user'):
                return

            # API calls return 401 instead of redirecting (Fixes CLEANUP bug)
            if request.path.startswith("/stats") or request.path.startswith("/exceptions") or request.path.startswith("/tasks"):
                 return make_response("Unauthorized", 401)

            return redirect('/login')

class MyUser(HttpUser):
    @task
    def my_task(self):
        self.client.get("/")
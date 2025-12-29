import os
from locust import HttpUser, task, events
from flask import session, url_for, redirect, request, make_response
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix # <--- REQUIRED FOR CLOUD RUN

# --- CONFIGURATION ---
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("LOCUST_SECRET_KEY", "change_me_to_something_secure")
ALLOWED_EMAILS = os.getenv("ALLOWED_EMAILS", "").split(",")

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if environment.web_ui:
        app = environment.web_ui.app
        app.secret_key = SECRET_KEY

        # --- CLOUD RUN FIX: Handle HTTPS Proxies ---
        # This tells Flask to trust the X-Forwarded-Proto headers from Cloud Run
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

        # 1. Setup OAuth
        oauth = OAuth(app)
        oauth.register(
            name='google',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )

        # 2. Login Route
        @app.route('/login')
        def login():
            # Force HTTPS for the redirect URI
            redirect_uri = url_for('auth', _external=True, _scheme='https')
            return oauth.google.authorize_redirect(redirect_uri)

        # 3. Callback Route
        @app.route('/google/auth')
        def auth():
            token = oauth.google.authorize_access_token()
            user_info = token.get('userinfo')
            
            # Email allowlist check
            if ALLOWED_EMAILS and ALLOWED_EMAILS != [''] and user_info['email'] not in ALLOWED_EMAILS:
                return f"Access Denied: {user_info['email']} is not authorized.", 403

            session['user'] = user_info
            return redirect('/')

        # 4. Logout Route
        @app.route('/logout')
        def logout():
            session.pop('user', None)
            return redirect('/')

        # 5. The Gatekeeper
        @app.before_request
        def protect_routes():
            if request.path.startswith("/static") or \
               request.path == "/login" or \
               request.path == "/google/auth" or \
               request.path == "/health": # Cloud Run health check
                return

            if session.get('user'):
                return

            if request.path.startswith("/stats") or request.path.startswith("/exceptions") or request.path.startswith("/tasks"):
                 return make_response("Unauthorized", 401)

            return redirect('/login')

class MyUser(HttpUser):
    @task
    def my_task(self):
        self.client.get("/")
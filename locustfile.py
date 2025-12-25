from locust import HttpUser, task, events
from flask import request, redirect, url_for, render_template_string, session

# --- CONFIGURATION ---
USERNAME = "admin"
PASSWORD = "password123"
SECRET_KEY = "my_secret_key_123"

# --- LOGIN HTML ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Security Check</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #333; color: white; }
        .box { background: #444; padding: 40px; border-radius: 10px; text-align: center; border: 2px solid #555; }
        input { display: block; margin: 15px auto; padding: 10px; width: 200px; border-radius: 5px; border: none; }
        button { padding: 10px 20px; background: #28a745; color: white; border: none; cursor: pointer; border-radius: 5px; font-weight: bold;}
        button:hover { background: #218838; }
        .error { color: #ff6b6b; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>restricted access</h2>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Unlock</button>
        </form>
    </div>
</body>
</html>
"""

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if environment.web_ui:
        app = environment.web_ui.app
        app.secret_key = SECRET_KEY

        # 1. Register our custom login route
        @app.route("/custom-login", methods=["GET", "POST"])
        def custom_login():
            if request.method == "POST":
                if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
                    session["logged_in"] = True
                    return redirect("/") # Send them to the main dashboard
                else:
                    return render_template_string(LOGIN_HTML, error="Invalid Credentials")
            return render_template_string(LOGIN_HTML, error=None)

        # 2. Register a logout route
        @app.route("/logout")
        def logout():
            session.pop("logged_in", None)
            return redirect("/custom-login")

        # 3. The Gatekeeper: Run this before EVERY request
        @app.before_request
        def protect_routes():
            # Allow static files (css/js) so the page looks right
            if request.path.startswith("/static"):
                return
            
            # Allow the login page itself (otherwise infinite loop)
            if request.path == "/custom-login":
                return

            # If not logged in, FORCE redirect to login
            if not session.get("logged_in"):
                return redirect("/custom-login")

class MyUser(HttpUser):
    @task
    def my_task(self):
        self.client.get("/")
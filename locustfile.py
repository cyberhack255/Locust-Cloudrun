import os
from locust import HttpUser, task, events
from flask import request, redirect, url_for, render_template_string, session, make_response

# --- 1. CONFIGURATION ---
# Use environment variables for security, or default to these values
USERNAME = os.getenv("LOCUST_USERNAME", "hacker")
PASSWORD = os.getenv("LOCUST_PASSWORD", "")
SECRET_KEY = os.getenv("LOCUST_SECRET_KEY", "")

# --- 2. LOGIN PAGE HTML ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Locust Security</title>
    <style>
        body { font-family: 'Helvetica', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #2c3e50; margin: 0; }
        .login-card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center; width: 300px; }
        h2 { margin-top: 0; color: #333; }
        input { display: block; width: 90%; padding: 10px; margin: 15px auto; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; box-sizing: border-box; }
        button { width: 90%; padding: 10px; background: #27ae60; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; transition: background 0.3s; }
        button:hover { background: #2ecc71; }
        .error { color: #e74c3c; font-size: 13px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>Locked Locust</h2>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Unlock Dashboard</button>
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

        # --- A. Define Custom Login Routes ---
        
        @app.route("/custom-login", methods=["GET", "POST"])
        def custom_login():
            if request.method == "POST":
                # Check credentials
                if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
                    session["logged_in"] = True
                    return redirect("/")  # Redirect to main dashboard
                else:
                    return render_template_string(LOGIN_HTML, error="Invalid Credentials")
            
            # Show the login page
            return render_template_string(LOGIN_HTML, error=None)

        @app.route("/logout")
        def logout():
            session.pop("logged_in", None)
            return redirect("/custom-login")

        # --- B. The Gatekeeper (Fixes the CLEANUP/Offline bug) ---
        
        @app.before_request
        def protect_routes():
            # 1. Always allow static files (CSS, JS, Images)
            if request.path.startswith("/static"):
                return
            
            # 2. Always allow the login page itself
            if request.path == "/custom-login":
                return

            # 3. Check if user is logged in
            if session.get("logged_in"):
                return  # Access granted
            
            # 4. Handle API calls specifically (The Fix)
            # If the dashboard tries to fetch stats while not logged in, 
            # return a 401 error instead of redirecting to HTML.
            # This prevents the UI from trying to parse HTML as JSON.
            if request.path.startswith("/stats") or request.path.startswith("/exceptions") or request.path.startswith("/tasks"):
                return make_response("Unauthorized", 401)

            # 5. For standard page loads, redirect to login
            return redirect("/custom-login")

# --- 3. YOUR LOAD TEST ---
class MyUser(HttpUser):
    @task
    def my_task(self):
        self.client.get("/")
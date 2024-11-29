from flask import Flask
from routes.healthz import healthz_blueprint
from routes.records import record_blueprint
from routes.login import login_blueprint

app = Flask(__name__)

# Register blueprints
app.register_blueprint(healthz_blueprint)
app.register_blueprint(record_blueprint)
app.register_blueprint(login_blueprint)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
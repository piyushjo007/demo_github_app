import time
import requests
import flask
import threading
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from functools import wraps

app = flask.Flask(__name__)

request_count = Counter('flask_request_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('flask_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
requests_in_progress = Gauge('flask_requests_in_progress', 'Requests in progress')


def track_metrics(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        requests_in_progress.inc()
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            status = result[1] if isinstance(result, tuple) else 200
            return result
        finally:
            duration = time.time() - start_time
            request_duration.labels(method=flask.request.method, endpoint=flask.request.endpoint).observe(duration)
            request_count.labels(method=flask.request.method, endpoint=flask.request.endpoint, status=status).inc()
            requests_in_progress.dec()
    return decorated_function


@app.before_request
def before_request():
    flask.g.start_time = time.time()

@app.after_request
def after_request(response):
    return response

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


READY = False
START_TIME = time.time()

def init_app():
    global READY
    time.sleep(5)  # Simulate initialization delay of 5 seconds for testing purposes
    READY = True

@app.route("/startup")
@track_metrics
def startup():
    if READY:
        return flask.jsonify(status="started"), 200
    return flask.jsonify(status="starting"), 503


@app.route("/health")
@track_metrics
def health():
    # Liveness: process is running
    return flask.jsonify(status="ok"), 200


@app.route("/ready")
@track_metrics
def readiness():
    # Readiness: app is ready to serve traffic
    if READY:
        return flask.jsonify(status="ready"), 200
    return flask.jsonify(status="not ready"), 503


@app.route("/live")
@track_metrics
def liveness():
    uptime = time.time() - START_TIME
    return flask.jsonify(status="alive", uptime_seconds=int(uptime)), 200


@app.route("/<user>")
@track_metrics
def get_gists(user):
    url = f"https://api.github.com/users/{user}/gists"
    response = requests.get(url)
    return flask.jsonify(response.json())


if __name__ == "__main__":
    # init_app() # this will fail the startup logic and show not reachable as it will never reach app.run() until the init_app() finishes. To simulate the startup logic, we can run init_app() in a separate thread.
    threading.Thread(target=init_app, daemon=True).start() # initiate seperate threads to run the init_app() function in the background while the main thread continues to run the Flask app.

    app.run(host="0.0.0.0", port=8080)

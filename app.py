from flask import Flask, jsonify
import threading

app = Flask(__name__)

lock           = threading.Lock()
total_requests = 0
total_errors   = 0
is_healthy     = True


@app.route("/health")
def health():
    global total_requests, total_errors

    with lock:
        total_requests += 1

        if not is_healthy:
            total_errors += 1
            return jsonify({
                "status":         "unhealthy",
                "total_requests": total_requests,
                "error_rate":     total_errors / total_requests,
            }), 503

        return jsonify({
            "status":         "healthy",
            "total_requests": total_requests,
            "error_rate":     total_errors / total_requests if total_requests > 0 else 0.0,
        }), 200


@app.route("/fail")
def fail():
    global is_healthy
    is_healthy = False
    return jsonify({"status": "failure mode activated"}), 200


@app.route("/recover")
def recover():
    global is_healthy
    is_healthy = True
    return jsonify({"status": "recovery mode activated"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
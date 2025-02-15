from flask import Flask, request, jsonify
from flask_cors import CORS
from agents import AgentManager

app = Flask(__name__)

# ✅ Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

agent_manager = AgentManager()

@app.before_request
def handle_options():
    """Handle CORS Preflight Requests."""
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS Preflight Passed"}), 200

@app.route("/")
def home():
    return jsonify({"message": "LinkedIn Automation API is running!"})

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400

    summary = agent_manager.get_agent("summarize").execute(text)
    validation_agent = agent_manager.get_agent("summarize_validator")
    validation = validation_agent.execute(text, summary) if validation_agent else "Validation agent not found"

    return jsonify({"summary": summary, "validation": validation})

@app.route("/write_post", methods=["POST"])
def write_post():
    data = request.get_json()
    topic = data.get("topic")
    outline = data.get("outline", "")

    if not topic:
        return jsonify({"error": "Missing 'topic' field"}), 400

    post = agent_manager.get_agent("write_post").execute(topic, outline)
    validation = agent_manager.get_agent("write_post_validator").execute(topic, post)

    return jsonify({"post": post, "validation": validation})

@app.route("/sanitize_data", methods=["POST"])
def sanitize_data():
    data = request.get_json()
    original_data = data.get("data")

    if not original_data:
        return jsonify({"error": "Missing 'data' field"}), 400

    sanitized_data = agent_manager.get_agent("sanitize_data").execute(original_data)
    validation = agent_manager.get_agent("sanitize_data_validator").execute(original_data, sanitized_data)

    return jsonify({"sanitized_data": sanitized_data, "validation": validation})

@app.route("/refine_post", methods=["POST"])
def refine_post():
    data = request.get_json()
    draft = data.get("draft")

    if not draft:
        return jsonify({"error": "Missing 'draft' field"}), 400

    refined_post = agent_manager.get_agent("refiner").execute(draft)
    return jsonify({"refined_post": refined_post})

@app.route("/validate_post", methods=["POST"])
def validate_post():
    data = request.get_json()
    topic = data.get("topic")
    article = data.get("article")

    if not topic or not article:
        return jsonify({"error": "Missing 'topic' or 'article' field"}), 400

    validation = agent_manager.get_agent("validator").execute(topic, article)
    return jsonify({"validation": validation})

@app.route("/generate_comment", methods=["POST"])
def generate_comment():
    data = request.get_json()
    post_content = data.get("post_content")

    if not post_content:
        return jsonify({"error": "Missing 'post_content' field"}), 400

    comment = agent_manager.get_agent("generate_comment").execute(post_content)
    return jsonify({"comment": comment})

@app.route("/sentiment_analysis", methods=["POST"])
def sentiment_analysis():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400

    sentiment = agent_manager.get_agent("sentiment_analysis").execute(text)
    return jsonify({"sentiment": sentiment})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

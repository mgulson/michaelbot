from flask import Flask, request, jsonify
from services.youtube import get_authenticated_service, upload_video, upload_video_from_prompt

app = Flask(__name__)


youtube_cache = None

@app.route("/", methods=["GET"])
def home():
  return jsonify({"message": "Welcome to Michael's Youtube Bot"}), 200

@app.route("/login", methods=["POST"])
def login():
  global youtube_cache
  breakpoint()
  youtube_cache = get_authenticated_service()
  return jsonify({"message": "Login successful!"}), 200


@app.route("/generate_video", methods=["POST"])
def generate_video():
  prompt = request.args.get("prompt", "")
  global youtube_cache
  if not youtube_cache:
    return jsonify({"message": "User not authenticated with YouTube. Please log in first on the /login endpoint."}), 401
  
  try:
    result = upload_video_from_prompt(prompt, youtube_cache)
    return jsonify({"message": "Video generated and uploaded successfully!", "video_id": result["video_id"], "video_url": result["video_url"]}), 200
  except Exception as e:
    return jsonify({"message": str(e)}), 500

  
if __name__ == "__main__":
  app.run(debug=True)
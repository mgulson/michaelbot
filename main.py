from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse as jsonResponse, RedirectResponse
from dotenv import load_dotenv
import uvicorn

load_dotenv()

from services.youtube import upload_video, upload_video_from_prompt, get_auth_url, handle_oauth_callback, verify_youtube_login


app = FastAPI()
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


youtube_cache = None

@app.get("/")
def home():
  return {"message": "Welcome to Michael's Youtube Bot"}

@app.get("/auth")
def auth():
  auth_url, state = get_auth_url()
  response = RedirectResponse(auth_url)
  response.set_cookie("oauth_state", state, httponly=True, samesite="lax")
  return response

@app.get("/oauth2callback")
def callback(request: Request):
  global youtube_cache
  code = request.query_params.get("code")
  state = request.query_params.get("state")
  expected_state = request.cookies.get("oauth_state")
  
  youtube_cache = handle_oauth_callback(str(request.url))
  response = jsonResponse({"message": "Login successful!"}, status_code=200)
  response.delete_cookie("oauth_state")
  return response

@app.post("/check_login")
def check_login():
  global youtube_cache
  login_status = verify_youtube_login(youtube_cache)
  return jsonResponse(login_status, status_code=200)


@app.post("/generate_video")
def generate_video(request: Request):
  prompt = request.query_params.get("prompt", "")
  if len(prompt) == 0:
     return jsonResponse({"message": "prompt is required"}, status_code=400)
  global youtube_cache
  if not youtube_cache:
    return jsonResponse({"message": "User not authenticated with YouTube. Please log in first on the /login endpoint."}, status_code=401)
  
  try:
    result = upload_video_from_prompt(prompt, youtube_cache)
    return jsonResponse({"message": "Video generated and uploaded successfully!", "video_id": result["video_id"], "video_url": result["video_url"]}, status_code=200)
  except Exception as e:
    return jsonResponse({"message": str(e)}, status_code=500)


if __name__ == "__main__":
  uvicorn.run("main:app", host="127.0.0.1", port=3000)

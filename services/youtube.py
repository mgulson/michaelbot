import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from services.gemini import generate_video, generate_text_request

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
  "https://www.googleapis.com/auth/youtube.upload",
  "https://www.googleapis.com/auth/youtube.readonly",
]
TOKEN_FILE = "token.json"
CLIENT_SECRET_FILE = "client_secret_5_17_26.json"

# Global variable to store the flow state between auth and callback
_flow = None


def is_appropriate_content(prompt):
  prompt = f"""Determine whether the following prompt will violate the youtube content policy. Respond with a boolean value. Specifically beware of any inappropriate content such asnudity, drugs alcohol, or violence. Respond in the following format {{ "valid": true }} Prompt: '{prompt}'"""

  is_valid = generate_text_request(prompt)
  if not is_valid:
    print("Content violates YouTube policy. Aborting video generation.")
    return False
  
  print("Content is valid. Proceeding with video generation.")
  return True

# TODO DELETE
# def get_authenticated_service():
#     creds = None

#     if os.path.exists(TOKEN_FILE):
#         creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

#     if not creds or not creds.valid:
#         flow = Flow.from_client_secrets_file(
#         CLIENT_SECRET_FILE,
#         scopes=SCOPES,
#         )
#         auth_url, state = flow.authorization_url(prompt='consent')
        
#         authorization_response = 
#         flow.fetch_token(authorization_response=authorization_response)
        
#         creds = flow.credentials

#         with open(TOKEN_FILE, "w") as token:
#             token.write(creds.to_json())

#     return build("youtube", "v3", credentials=creds)


def upload_video(youtube, file_path, title, description):
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": "public"  # or "public", "unlisted"
        }
    }

    media = MediaFileUpload(
        file_path,
        chunksize=-1,
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    print(response['status'])

    print("Upload complete!")
    video_id = response["id"]
    video_url = "https://www.youtube.com/watch?v=" + video_id
    print("Video ID:", video_id)
    print("Video URL:", video_url)
    
    return {"video_id": video_id, "video_url": video_url}


def upload_video_from_prompt(prompt, youtube_app, title="AI Generated Video", description="Michael's AI generated video"):
  if not is_appropriate_content(prompt):
    raise Exception("Content violates YouTube policy. Aborting video generation.")

  if not youtube_app:
    raise Exception("User not authenticated with YouTube. Please log in first.")
  
  video_name = generate_video(prompt)

  return upload_video(
      youtube_app,
      file_path=f"/Users/mgulson2/code/michaelbot/{video_name}",
      title=title,
      description=description
  )


def verify_youtube_login(youtube_app):
  if not youtube_app:
    return {"logged_in": False, "message": "No YouTube client cached."}

  try:
    response = youtube_app.channels().list(
      part="id",
      mine=True,
      maxResults=1,
    ).execute()

  except Exception as e:
    return {"logged_in": False, "message": f"YouTube credential check failed: {str(e)}"}

  items = response.get("items", [])
  if not items:
    return {"logged_in": False, "message": "Authenticated Google account has no YouTube channel."}

  return {
    "logged_in": True,
    "channel_id": items[0].get("id"),
  }


def get_auth_url():
    """Generate the OAuth authorization URL"""
    global _flow
    _flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:3000/oauth2callback"

    )
    auth_url, state = _flow.authorization_url(prompt='consent')
    return auth_url, state


def handle_oauth_callback(authorization_response):
    """Handle the full OAuth callback URL returned by Google."""
    global _flow
    if _flow is None:
        raise ValueError("OAuth flow not initialized. Visit /auth before opening the callback URL.")
    
    _flow.fetch_token(authorization_response=authorization_response)
    creds = _flow.credentials
    
    # Save credentials for future use
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())
    
    return build("youtube", "v3", credentials=creds)


if __name__ == "__main__":
    youtube = get_authenticated_service()

    upload_video(
        youtube,
        file_path="/Users/mgulson2/code/michaelbot/ai_video.mp4",
        title="AI Generated Video",
        description="AI generated video of anime girls dancing to the latest TikTok dance trend."
    )

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from services.gemini import generate_video, generate_text_request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "token.json"
CLIENT_SECRET_FILE = "client_secret.json"


def is_appropriate_content(prompt):
  prompt = f"""Determine whether the following prompt will violate the youtube content policy. Respond with a boolean value. Specifically beware of any inappropriate content such asnudity, drugs alcohol, or violence. Respond in the following format {{ "valid": true }} Prompt: '{prompt}'"""

  is_valid = generate_text_request(prompt)
  if not is_valid:
    print("Content violates YouTube policy. Aborting video generation.")
    return False
  
  print("Content is valid. Proceeding with video generation.")
  return True


def get_authenticated_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


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


if __name__ == "__main__":
    youtube = get_authenticated_service()

    upload_video(
        youtube,
        file_path="/Users/mgulson2/code/michaelbot/ai_video.mp4",
        title="AI Generated Video",
        description="AI generated video of anime girls dancing to the latest TikTok dance trend."
    )
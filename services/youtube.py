import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "token.json"
CLIENT_SECRET_FILE = "client_secret.json"


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
    print("Video ID:", response["id"])
    print("Video URL: https://www.youtube.com/watch?v=" + response["id"])


if __name__ == "__main__":
    youtube = get_authenticated_service()

    upload_video(
        youtube,
        file_path="/Users/mgulson2/code/michaelbot/ai_video.mp4",
        title="AI Generated Video",
        description="AI generated video of anime girls dancing to the latest TikTok dance trend."
    )
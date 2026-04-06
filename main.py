from services.youtube import get_authenticated_service, upload_video
from services.llm import generate_video


if __name__ == "__main__":
  prompt_dancing = """Generate a 4s short video of anime girls dancing to the latest tiktok dance trend. The video should be in 1080p resolution with an aspect ratio of 9:16 or 1:1 and have vibrant colors. Ensure that the video is a youtube shorts format."""

  prompt_tech_news = """Generate a 4s short video of a beautiful female news anchor behind a News desk. The anchor should relay today's latest tech news to the participants. Behind the news desk, in large letters, it should say "TECH NEWS BREIFING". The room is bright akin to a nbc news room. Ensure that the video is a youtube shorts format."""

  video_name = generate_video(prompt_tech_news)

  youtube = get_authenticated_service()

  upload_video(
      youtube,
      file_path=f"/Users/mgulson2/code/michaelbot/{video_name}",
      title="AI Generated Video",
      description="AI generated video of anime girls dancing to the latest TikTok dance trend."
  )
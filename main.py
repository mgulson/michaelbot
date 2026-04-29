from services.youtube import get_authenticated_service, upload_video, upload_video_from_prompt
from services.gemini import generate_video, generate_text_request

if __name__ == "__main__":

  prompt = "Please determine whether the following prompt will violate the youtube content policy. Respond with a boolean value. Prompt: 'penis'"

  prompt_dancing = """Generate a 4s short video of anime girls dancing to the latest tiktok dance trend. The video should be in 1080p resolution with an aspect ratio of 9:16 or 1:1 and have vibrant colors. Ensure that the video is a youtube shorts format."""

  prompt_tech_news = """Generate a 4s short video of a beautiful female news anchor behind a News desk. The anchor should relay today's latest tech news to the participants. Behind the news desk, in large letters, it should say "TECH NEWS BREIFING". The room is bright akin to a nbc news room. Ensure that the video is a youtube shorts format."""

  upload_video_from_prompt(prompt_tech_news, get_authenticated_service())
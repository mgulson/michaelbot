import time
from google import genai
from google.genai import types
import os
import datetime


def generate_video(prompt):
  client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


  operation = client.models.generate_videos(
      model="veo-3.1-generate-preview",
      prompt=prompt,
  )

  # Poll the operation status until the video is ready.
  while not operation.done:
      print("Waiting for video generation to complete...")
      time.sleep(10)
      operation = client.operations.get(operation)

  # Download the generated video.
  print("operation.response:", operation.response)
  print("operation.response.generated_videos:", operation.response.generated_videos)
  generated_video = operation.response.generated_videos[0]
  client.files.download(file=generated_video.video)

  datetime_str = datetime.datetime.now().strftime("%m_%d_%Y-%H-%M-%S")
  filename = f"ai_video_{datetime_str}.mp4"
  generated_video.video.save(filename)
  print("Generated video saved to dialogue_example.mp4")
  return filename


def generate_text_request(prompt):
  operation = client.models.generate_content(
      model="gemini-2.0-flash",
      prompt=prompt,
  )
  return operation.response
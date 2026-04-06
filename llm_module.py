from openai import OpenAI
import base64

client = OpenAI()

# Prompt describing the video scene
prompt = """
Two stylized anime cat girls dancing together in sync to a modern TikTok-style dance trend,
bright colorful lighting, energetic choreography, smooth camera movement,
cute expressions, highly detailed anime style, vibrant neon background.
"""

# Generate a 6-second video
response = client.responses.create(
    model="gpt-4.1",
    modalities=["video"],
    video={
        "duration": 6,
        "resolution": "1024x1024"
    },
    input=prompt
)

# The API returns base64-encoded video data
video_base64 = result.data[0].b64_video
video_bytes = base64.b64decode(video_base64)

# Save to file
with open("catgirls_dance.mp4", "wb") as f:
    f.write(video_bytes)

print("Video saved to catgirls_dance.mp4")
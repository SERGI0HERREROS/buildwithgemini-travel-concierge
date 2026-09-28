"""Video generation tool for travel-concierge agent using gemini-omni-flash-preview."""

import base64
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# CRITICAL: Hardcode project ID and Cloud Storage bucket name as string literals.
PROJECT_ID = "qwiklabs-gcp-03-914ab565751f"
BUCKET_NAME = "travel-concierge-assets-qwiklabs-gcp-03-914ab565751f"

# Initialize genai client in the 'global' region
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
storage_client = storage.Client(project=PROJECT_ID)


def generate_destination_video(
    prompt: str,
    tool_context: ToolContext = None,
) -> str:
    """Generate a short video preview for a travel destination, landmark, scene, or attraction using Google's Omni model (gemini-omni-flash-preview).

    Args:
        prompt: Description of the video to generate (e.g., 'A short cinematic video of a sunny tropical beach in Hawaii').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        The public HTTPS URL of the generated MP4 video stored in Cloud Storage.
    """
    try:
        interaction = genai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_bytes = None
        if hasattr(interaction, "output_video") and interaction.output_video:
            data = getattr(interaction.output_video, "data", None)
            if data:
                if isinstance(data, str):
                    video_bytes = base64.b64decode(data)
                else:
                    video_bytes = data

        if not video_bytes:
            return "Error: Video generation model did not return video bytes."

        filename = f"generated_video_{uuid.uuid4().hex[:8]}.mp4"
        mime_type = "video/mp4"

        # (1) Save video artifact via tool_context.save_artifact if tool_context is provided
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # (2) Upload video bytes directly to public Cloud Storage bucket without writing local files
        object_name = f"generated_videos/{filename}"
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"
        return public_url

    except Exception as e:
        return f"Error generating destination video: {str(e)}"

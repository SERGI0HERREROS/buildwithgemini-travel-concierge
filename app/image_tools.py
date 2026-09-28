"""Image generation tools for travel-concierge agent using gemini-3.1-flash-lite-image."""

import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# CRITICAL: Hardcode project ID and Cloud Storage bucket name as string literals.
PROJECT_ID = "qwiklabs-gcp-03-914ab565751f"
BUCKET_NAME = "travel-concierge-assets-qwiklabs-gcp-03-914ab565751f"

# Initialize genai client in the 'global' region as requested
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
storage_client = storage.Client(project=PROJECT_ID)


def generate_destination_image(
    prompt: str,
    tool_context: ToolContext = None,
) -> str:
    """Generate a custom image for a travel destination, landmark, cuisine, or attraction using Gemini 3.1 Flash Lite Image.

    Args:
        prompt: Detailed description of the image to generate (e.g., 'Eiffel Tower at sunset in Paris with golden lighting').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        The public HTTPS URL of the generated image stored in Cloud Storage.
    """
    try:
        # Generate image using gemini-3.1-flash-lite-image in global region
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        img_bytes = None
        mime_type = "image/jpeg"

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    img_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not img_bytes:
            return "Error: Image generation model did not return image bytes."

        filename = f"generated_image_{uuid.uuid4().hex[:8]}.jpg"

        # (1) Save artifact via tool_context.save_artifact if tool_context is provided
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # (2) Upload image bytes to public Cloud Storage bucket without local files
        object_name = f"generated_images/{filename}"
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_string(img_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"
        return public_url

    except Exception as e:
        return f"Error generating destination image: {str(e)}"

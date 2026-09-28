# 🌴 Travel Concierge Agent

An intelligent, multi-tool AI Travel Assistant built with the Google Agent Development Kit (ADK) and deployed to Vertex AI Agent Platform. It assists travelers by exploring destinations, finding nearby attractions, generating custom AI media previews, calculating trip budget splits, and remembering dietary and health preferences across sessions.

![Travel Concierge Demo](./demo.gif)

---

## 🌟 Key Capabilities & Implemented Features

* **Cross-Session Long-Term Memory (Vertex AI Memory Bank)**: Automatically retains user health preferences, dietary restrictions, and food allergies across conversations to personalize travel recommendations safely.
* **Structured UI Rendering (A2UI v0.8)**: Generates rich visual surfaces (Cards, Columns, Rows, Images) using the A2UI Basic Catalog schema instead of standard plain text.
* **Custom AI Image Previews**: Generates destination and cuisine visual previews using `gemini-3.1-flash-lite-image`.
* **Custom AI Video Previews**: Generates short destination video previews using Google's `gemini-omni-flash-preview` model in the global region.
* **Firestore Data Persistence**: Stores and queries user travel destinations and calculates trip budget splits directly in Google Cloud Firestore.
* **Google Cloud Storage Integration**: Uploads generated images and video previews to a public GCS asset bucket and embeds public HTTPS links inside A2UI responses.
* **Location & Geocoding Services**: Resolves addresses and discovers nearby places using Google Maps APIs (`geocode_address`, `find_nearby_places`).
* **Live Weather Information**: Fetches destination weather forecasts via `get_live_destination_weather`.
* **Code Sandbox Execution**: Runs Python computations safely in an isolated sandbox environment via `AgentEngineSandboxCodeExecutor`.

---

## 🛠️ Integrated Google Cloud Services

* **Vertex AI Agent Platform / Reasoning Engine**: Remote deployment and hosting for agent execution over A2A protocol.
* **Vertex AI Memory Bank**: Managed memory service for cross-session preference tracking.
* **Google Cloud Firestore**: NoSQL database for destination records and trip budget persistence.
* **Google Cloud Storage (GCS)**: Cloud storage bucket hosting generated image and video assets.
* **Gemini Models**:
  * `gemini-flash-latest` (Root reasoning agent model)
  * `gemini-3.1-flash-lite-image` (Image generation)
  * `gemini-omni-flash-preview` (Video generation)

---

## 📁 Repository Structure

```
.
├── app/
│   ├── agent.py            # Main ADK root agent configuration & A2UI system prompt
│   ├── a2ui_utils.py       # A2UI after_model_callback transformer
│   ├── firestore_tools.py  # Firestore destination & budget storage tools
│   ├── image_tools.py      # Gemini 3.1 Flash Lite Image generation & GCS upload tool
│   ├── video_tools.py      # Gemini Omni Flash video generation & GCS upload tool
│   ├── maps_tools.py       # Google Maps geocoding & nearby places tools
│   └── external_tools.py   # Live weather integration tool
├── frontend/
│   ├── main.py             # FastAPI proxy connecting UI to agent over A2A protocol
│   ├── static/index.html   # Custom ocean-teal chat UI with built-in A2UI card renderer
│   └── Dockerfile          # Container configuration for frontend deployment
├── agents-cli-manifest.yaml# ADK project deployment manifest
└── demo.gif                # Recorded demonstration preview
```

---

## 🚀 Local Setup & Running Instructions

### Prerequisites
* Python 3.11+
* Google Cloud CLI (`gcloud`) authenticated to your GCP project
* Environment variables set in `.env`:
  ```bash
  GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
  GOOGLE_CLOUD_LOCATION="us-central1"
  GOOGLE_MAPS_API_KEY="<your-google-maps-api-key>"
  ```

### 1. Run Local ADK Playground
To test the agent locally using the ADK Web interface:

```bash
uv run adk web . --port 8080 --reload_agents
```

### 2. Run the Custom Web Frontend Locally
To start the FastAPI proxy and chat interface locally:

```bash
cd frontend
pip install -r requirements.txt
python main.py
```

### 3. Deploy Agent to Vertex AI Agent Platform
To deploy the backend agent to Vertex AI Agent Runtime:

```bash
agents-cli deploy agent_runtime --project <your-gcp-project-id> --region us-central1
```

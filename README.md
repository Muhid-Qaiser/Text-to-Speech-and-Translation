# Text-to-Speech gRPC Streamlit Application

## Project Overview

This repository provides a complete setup for a text-to-speech (TTS) application using a gRPC server and a Streamlit front-end. It leverages the Seamless M4T v2 model hosted on Hugging Face Spaces to convert input text into audio. The architecture consists of:

- A gRPC server (`server.py`) defined by a Protocol Buffers (`.proto`) schema. Server can handle asynchronous requests from multiple clients.
- A Streamlit app (`app.py`) deployed remotely on Hugging Face Spaces.
- A local Streamlit client (`local_app.py`) that interacts with the gRPC server.
- Utility scripts for testing, JSON handling, and audio conversion.
- A Dockerfile for containerizing the service.

## Repository Structure

```
├── tts.proto                 # Protocol Buffers definition
├── tts_pb2.py                # Protocol File 1
├── tts_pb2_gprc.py           # Protocol File 2
├── server.py                 # gRPC server implementation
├── client.py                 # Test client for gRPC server
├── local_app.py              # Local Streamlit app using gRPC server
├── app.py                    # Deployed Streamlit app (Hugging Face Spaces)
├── return_json.py            # Fetch JSON from server and save it
├── json_2_audio.py           # Convert saved JSON (from Postman/cURL) to audio
├── Dockerfile                # Docker image definition
└── requirements.txt          # Python dependencies
```

## Prerequisites

- Python 3.8+ installed
- `virtualenv` or `venv` for creating isolated environments
- Docker (optional, for containerization)

## Installation

1. **Clone the repository**
   ```bash
   git clone <REPO_URL>
   cd <REPO_DIR>
   ```

2. **Create and activate a virtual environment**

   - Using `venv` (built‑in):
     ```bash
     python3 -m venv venv
     source venv/bin/activate   # Linux/macOS
     venv\Scripts\activate    # Windows
     ```

   - Using `virtualenv`:
     ```bash
     virtualenv venv
     source venv/bin/activate
     ```

3. **Install Python dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Generating gRPC Code from `.proto`

Before running the server, generate Python classes from the `text_to_speech.proto` file:

```bash
python -m grpc_tools.protoc \
  --proto_path=. \
  --python_out=. \
  --grpc_python_out=. \
  text_to_speech.proto
```

This will create `text_to_speech_pb2.py` and `text_to_speech_pb2_grpc.py`.

## Running the Local Application

1. **Start the gRPC server**
   Open a terminal and run:
   ```bash
   python server.py
   ```
   The server will listen on `localhost:50051` by default.

2. **Launch the local Streamlit app**
   In a new terminal (with the same virtual environment active):
   ```bash
   streamlit run local_app.py
   ```

3. **Use the app**
   - Open the URL shown in the console (e.g., `http://localhost:8501`).
   - Enter text in the input field and click **Generate**.
   - The app calls the gRPC server, which returns audio that plays in the browser.

## Remote Deployment (Hugging Face Spaces)

The `app.py` is configured for deployment on Hugging Face Spaces. It directly wraps the Seamless M4T v2 TTS model API. To deploy:

1. Push `app.py`, `requirements.txt`, and a `README.md` to a new Hugging Face Space.
2. The space will auto-install dependencies and launch the Streamlit UI.

## Testing the gRPC Server

The `client.py` script includes sample requests to verify server functionality and save the resulting audio files locally.

```bash
python client.py
```

The tests will:

- Send example text payloads to the server.
- Receive responses (binary audio data).
- Save `.wav` files under the project directory.

## JSON Handling

### return_json.py

Fetches and saves the raw JSON response from the gRPC server.

```bash
python return_json.py
# Output: response.json
```

### json_2_audio.py

Reads a JSON file (e.g., from Postman or cURL) and converts the encoded audio field back into a `.wav` file.
Just copy and paste the response json into the file's variable and run.

```bash
python json_2_audio.py 
```

## Docker Containerization

Build and run the Docker image for the full service:

```bash
# Build the image
docker build -t tts-grpc-app .

# Run the container (exposes port 50051)
docker run -p 50051:50051 tts-grpc-app
```

You can then point the `local_app.py` or any gRPC client to `localhost:50051`.

## Architecture, Model Sources, and Limitations

- Architecture: A straightforward TTS pipeline where user input is captured via the Streamlit frontend, sent to the model for inference, and the generated audio is streamed back and played in the UI.

- Model Source: Utilizes Hugging Face’s seamless-m4t-large-v2 model hosted on the Hugging Face Hub.

- Limitations: Inference can be slow on CPUs due to the model’s size and computational demands.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for bug fixes and new features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.



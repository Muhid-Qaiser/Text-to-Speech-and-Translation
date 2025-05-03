import streamlit as st
import grpc
import tts_pb2
import tts_pb2_grpc
import base64
import tempfile

# * gRPC connection
def get_grpc_stub():
    channel = grpc.insecure_channel('localhost:50051')
    stub = tts_pb2_grpc.TTSServiceStub(channel)
    return stub

# * Function to call the GenerateSpeechBase64 gRPC method
def generate_speech_base64(text, language):
    stub = get_grpc_stub()
    request = tts_pb2.TTSRequest(text=text, language=language)
    
    try:
        response = stub.GenerateSpeechBase64(request)
        return response.audio_base64
    except grpc.RpcError as e:
        st.error(f"Error: {e.details()}")
        return None

# * Decode base64 to audio bytes and save as WAV file
def decode_base64_audio(audio_base64):
    audio_bytes = base64.b64decode(audio_base64)
    # * Save the audio to a temporary WAV file
    tmp_path = tempfile.mktemp(suffix=".wav")
    with open(tmp_path, 'wb') as audio_file:
        audio_file.write(audio_bytes)
    return tmp_path

# * Streamlit UI
def main():
    st.title("Text-to-Speech with gRPC")

    # * Text input
    text_input = st.text_area("Enter text", "Hello, this is a test message.")
    
    # * Language selection
    language = st.selectbox("Select language", ["eng", "spa", "fra"])

    if st.button("Generate Speech"):
        if text_input.strip():
            st.write("Generating speech...")
            # * Generate speech in base64 format
            audio_base64 = generate_speech_base64(text_input, language)

            if audio_base64:
                # * Decode base64 to audio file and save
                audio_path = decode_base64_audio(audio_base64)

                # * Display audio player in the UI
                st.audio(audio_path)
                st.success("Speech generated successfully!")
        else:
            st.error("Text input cannot be empty!")

if __name__ == "__main__":
    main()

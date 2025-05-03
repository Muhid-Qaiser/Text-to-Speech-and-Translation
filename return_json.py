import grpc
import base64
import tts_pb2
import tts_pb2_grpc

# * Connect to gRPC server
channel = grpc.insecure_channel("localhost:50051")
stub = tts_pb2_grpc.TTSServiceStub(channel)

# * Call GenerateSpeechBase64
request = tts_pb2.TTSRequest(text="Hello, skibidi", language="eng")
response = stub.GenerateSpeechBase64(request)

# * Access the audio_base64 field
audio_base64 = response.audio_base64

# * Save to .wav file
with open("grpc_output.wav", "wb") as f:
    f.write(base64.b64decode(audio_base64))

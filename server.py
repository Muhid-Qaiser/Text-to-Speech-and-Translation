import asyncio
import grpc
import tts_pb2
import tts_pb2_grpc
import torch
from transformers import AutoProcessor, SeamlessM4Tv2Model
import tempfile
import base64
import torchaudio
from grpc_reflection.v1alpha import reflection


class TTSService(tts_pb2_grpc.TTSServiceServicer):
    def __init__(self):
        # cache_dir = "/app/.cache/huggingface"
        self.processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
        self.model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    async def GenerateSpeech(self, request, context):
        if not request.text.strip() or request.text == '':
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Text input is empty.")
        if request.language not in ["eng", "spa", "fra"]:  # Add supported languages as needed
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Unsupported language: {request.language}")
        try:
            inputs = self.processor(text=request.text, return_tensors="pt").to(self.device)
            with torch.no_grad():
                speech = self.model.generate(**inputs, tgt_lang=request.language)
            audio_array = speech[0].cpu().numpy().squeeze()
            audio_bytes = audio_array.tobytes()
            return tts_pb2.TTSResponse(audio=audio_bytes)
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, f"Server error: {str(e)}")

    async def GenerateSpeechBase64(self, request, context):
        txt = request.text.strip()
        if not txt:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Text input is empty.")
        if request.language not in ["eng", "spa", "fra"]:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Unsupported language: {request.language}")

        try:
            inputs = self.processor(text=txt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                speech = self.model.generate(**inputs, tgt_lang=request.language)
            audio_array = speech[0].cpu().numpy().squeeze()

            # * Save to WAV file
            tmp_path = tempfile.mktemp(suffix=".wav")
            torchaudio.save(tmp_path, torch.tensor(audio_array).unsqueeze(0), 16000)

            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()

            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            return tts_pb2.TTSBase64Response(audio_base64=audio_base64)

        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, f"Server error: {e}")


async def serve():
    server = grpc.aio.server()
    tts_pb2_grpc.add_TTSServiceServicer_to_server(TTSService(), server)
    server.add_insecure_port('[::]:50051')

    
    SERVICE_NAMES = (
        tts_pb2.DESCRIPTOR.services_by_name['TTSService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)


    await server.start()
    print("Server started on port 50051")
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())


# ! gRPCE in URL
# grpc://localhost:50051 
# { "text" : "Hello, this is a test message.", "language": "eng" }

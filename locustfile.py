import time
import grpc
import grpc.experimental.gevent as grpc_gevent
from locust import User, task, between, events

import tts_pb2
import tts_pb2_grpc

# * Use gevent-friendly gRPC
grpc_gevent.init_gevent()


class GrpcClient:
    def __init__(self, target: str):
        # * target must be "host:port", not a URI
        self.channel = grpc.insecure_channel(target)
        self.stub = tts_pb2_grpc.TTSServiceStub(self.channel)

    def generate_speech(self, text: str, language: str):
        req = tts_pb2.TTSRequest(text=text, language=language)
        return self.stub.GenerateSpeech(req)

    def generate_speech_base64(self, text: str, language: str):
        req = tts_pb2.TTSRequest(text=text, language=language)
        return self.stub.GenerateSpeechBase64(req)


class TTSUser(User):
    abstract = False
    wait_time = between(1, 3)

    host = "localhost:50051"

    def __init__(self, environment):
        super().__init__(environment)
        # * pass the bare host:port
        self.client = GrpcClient(self.host)

    @task(2)
    def generate_speech(self):
        start = time.time()
        try:
            resp = self.client.generate_speech("Hello from Locust", "eng")
            elapsed = int((time.time() - start) * 1000)
            events.request.fire(
                request_type="grpc",
                name="GenerateSpeech",
                response_time=elapsed,
                response_length=len(resp.audio),
                exception=None,
            )
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            events.request.fire(
                request_type="grpc",
                name="GenerateSpeech",
                response_time=elapsed,
                response_length=0,
                exception=e,
            )

    @task(1)
    def generate_speech_base64(self):
        start = time.time()
        try:
            resp = self.client.generate_speech_base64("¡Hola, prueba!", "spa")
            elapsed = int((time.time() - start) * 1000)
            events.request.fire(
                request_type="grpc",
                name="GenerateSpeechBase64",
                response_time=elapsed,
                response_length=len(resp.audio_base64),
                exception=None,
            )
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            events.request.fire(
                request_type="grpc",
                name="GenerateSpeechBase64",
                response_time=elapsed,
                response_length=0,
                exception=e,
            )



# run using:
# locust

# pip install locust grpcio grpcio-tools gevent
import asyncio
import grpc
import tts_pb2
import tts_pb2_grpc
import numpy as np
import soundfile as sf

async def send_request(text, language='eng', filename='output.wav'):
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = tts_pb2_grpc.TTSServiceStub(channel)
        try:
            request = tts_pb2.TTSRequest(text=text, language=language)
            response = await stub.GenerateSpeech(request)
            audio_array = np.frombuffer(response.audio, dtype=np.float32)
            sf.write(filename, audio_array, 16000)
            print(f"Audio saved to {filename}\n")
            # print("Status code: 200")
            # print(f"Status: {grpc.StatusCode.OK.name} ({grpc.StatusCode.OK.value})\n")
            return {
                "success": True,
                "status_code": grpc.StatusCode.OK.value,
                "status_name": grpc.StatusCode.OK.name,
                "filename": filename
            }

        except grpc.aio.AioRpcError as e:
            # print(f"gRPC error: {e.code()} - {e.details()}")
            status_code = e.code()
            print(f"{filename}, gRPC error: {status_code.name} ({status_code.value}) - {e.details()}\n")
            return {
                "success": False,
                "status_code": status_code.value,
                "status_name": status_code.name,
                "error": e.details()
            }

async def main():
    tasks = [
        send_request("Hello, this is request one.", filename="output1.wav"),
        send_request("Hi there, this is request two.", filename="output2.wav"),
        send_request("Greetings, this is request three.", filename="output3.wav"),
        send_request("", filename="output4.wav"),
        send_request("Yo, this is request five.", language="enla", filename="output5.wav"),
        send_request("", language="", filename="output6.wav"),
    ]
    # await asyncio.gather(*tasks)
    results = await asyncio.gather(*tasks)
    
    # Process results
    for i, result in enumerate(results):
        print(f"\nRequest {i+1} result:")
        print(f"  Success: {result['success']}")
        print(f"  Status: {result['status_name']} ({result['status_code']})")
        if result['success']:
            print(f"  Saved to: {result['filename']}")
        else:
            print(f"  Error: {result['error']}")
        print()


if __name__ == '__main__':
    asyncio.run(main())

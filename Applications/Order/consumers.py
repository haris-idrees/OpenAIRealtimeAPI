import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from Applications.Order.openai_websocket import connect_to_openai
from pydub import AudioSegment
import wave
from io import BytesIO


class Socket1Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "audio_group"
        await self.accept()

        # Connect to OpenAI WebSocket once when the consumer connects
        self.ws = await asyncio.to_thread(connect_to_openai)
        print("OpenAI WebSocket connection established.")


    async def disconnect(self, close_code):
        # Close OpenAI WebSocket connection when the consumer disconnects
        if hasattr(self, 'ws'):
            await asyncio.to_thread(self.ws.close)
            print("OpenAI WebSocket connection closed.")

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            print(f"Received audio data, {len(bytes_data)} bytes")
            try:
                # Use the wave module to read the WAV file from bytes
                with wave.open(BytesIO(bytes_data), 'rb') as wav_file:
                    nchannels = wav_file.getnchannels()
                    sampwidth = wav_file.getsampwidth()
                    framerate = wav_file.getframerate()
                    nframes = wav_file.getnframes()
                    audio_data = wav_file.readframes(nframes)

                # Create an AudioSegment from the raw PCM data
                audio = AudioSegment(
                    data=audio_data,
                    sample_width=sampwidth,
                    frame_rate=framerate,
                    channels=nchannels
                )

                # Convert to PCM 16-bit, 16kHz, mono if necessary
                pcm_audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

                # Export PCM audio to BytesIO buffer
                pcm_audio_buffer = BytesIO()
                pcm_audio.export(pcm_audio_buffer, format="wav")
                pcm_audio_data = pcm_audio_buffer.getvalue()

                print("Audio converted to PCM16.")

                # Send PCM audio data to OpenAI
                await self.send_audio_to_openai(pcm_audio_data)

            except Exception as e:
                print(f"Error processing audio: {e}")

    async def send_audio_to_openai(self, audio_data):
        if not hasattr(self, 'ws'):
            print("OPENAI WebSocket connection is not established.")
            return

        try:
            print("Sending audio to OpenAI WebSocket...")
            await asyncio.to_thread(self.ws.send, audio_data)

            print("Waiting for OpenAI response...")
            response = await asyncio.to_thread(self.ws.recv)

            if response:
                print("Received response from OpenAI:", response)
                await self.send(text_data=json.dumps({
                    'message': response
                }))
            else:
                print("No response received from OpenAI.")

        except Exception as e:
            print("Error while communicating with OpenAI:", e)
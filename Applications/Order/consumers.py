import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from Applications.Order.openai_websocket import connect_to_openai
import websocket
import socket


class Socket1Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "audio_group"
        # Accept WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Handle WebSocket disconnect
        pass

    async def receive(self, text_data=None, bytes_data=None):
        # Check if the data is text or binary (audio)
        if text_data:
            # Handle text data (if any)
            print(f"Received text data: {text_data}")
            # Process text data if needed
        elif bytes_data:
            # Handle audio (binary) data
            print(f"Received audio data, {len(bytes_data)} bytes")
            # Send the audio to OpenAI (via Socket2)
            await self.send_audio_to_openai(bytes_data)

    async def send_audio_to_openai(self, audio_data):
        # Connect to OpenAI WebSocket (Socket2)
        ws = await asyncio.to_thread(connect_to_openai)

        # Send the audio data to OpenAI via Socket2
        try:
            print("Sending audio to OpenAI WebSocket...")
            await asyncio.to_thread(ws.send, audio_data)

            # Receive OpenAI response
            print("Waiting for OpenAI response...")
            response = await asyncio.to_thread(ws.recv)

            if response:
                print("Received response from OpenAI:", response)
                # Send OpenAI response to frontend (Socket1)
                await self.send(text_data=json.dumps({
                    'message': response.decode('utf-8')  # Assuming OpenAI sends text
                }))
            else:
                print("No response received from OpenAI.")
        except Exception as e:
            print("Error while communicating with OpenAI:", e)


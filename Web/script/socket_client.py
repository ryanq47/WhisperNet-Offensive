# socket_client.py
import socketio

sio_client = socketio.AsyncClient()


async def connect():
    if not sio_client.connected:
        await sio_client.connect("http://localhost:5000")

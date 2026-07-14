import asyncio
import json
import threading

latest_landmarks = None
_server = None

async def _handler(websocket, path):
    # Send the latest landmarks periodically
    try:
        while True:
            if latest_landmarks is None:
                await asyncio.sleep(0.05)
                continue
            try:
                await websocket.send(json.dumps({'type':'landmarks','data': latest_landmarks}))
            except Exception:
                break
            await asyncio.sleep(0.04)
    except asyncio.CancelledError:
        pass

async def _run_server(host='0.0.0.0', port=8765):
    import websockets
    async with websockets.serve(_handler, host, port):
        await asyncio.Future()  # run forever

def start(host='0.0.0.0', port=8765):
    global _server
    if _server is not None:
        return
    def runner():
        asyncio.run(_run_server(host, port))
    _server = threading.Thread(target=runner, daemon=True)
    _server.start()

def stop():
    # Not easy to stop cleanly without more complex handling; rely on process exit
    global _server
    _server = None

if __name__ == '__main__':
    start()
    import time
    print('WebSocket server started on ws://0.0.0.0:8765')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

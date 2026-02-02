import asyncio
import json
from websockets import serve

# In-memory storage for whiteboard state and connected clients
whiteboard_data = {
    "lines": []
}
clients = set()


async def broadcast(message):
    """Sends a message to all connected clients."""
    if clients:
        message_json = json.dumps(message)
        # Using gather with return_exceptions=True to ensure one failing client doesn't stop others
        await asyncio.gather(
            *[client.send(message_json) for client in clients],
            return_exceptions=True
        )


async def handle_message(websocket, message):
    """Handles incoming messages from clients."""
    try:
        data = json.loads(message)
        action = data.get("action")

        if action == "draw":
            line = data.get("line")
            if line:
                whiteboard_data["lines"].append(line)
                await broadcast({"action": "draw", "line": line})
        elif action == "clear":
            whiteboard_data["lines"] = []
            await broadcast({"action": "clear"})
        elif action == "sync":
            await websocket.send(json.dumps({"action": "sync", "lines": whiteboard_data["lines"]}))
        elif action == "undo":
            if whiteboard_data["lines"]:
                last_line = whiteboard_data["lines"].pop()
                await broadcast({"action": "undo", "removed_line": last_line})
        elif action == "mouse_move":
            await broadcast({"action": "mouse_move", "coords": data.get("coords"), "client_id": str(websocket.remote_address)})
        elif action == "mouse_up":
            await broadcast({"action": "mouse_up", "client_id": str(websocket.remote_address)})
        elif action == "mouse_down":
            await broadcast({"action": "mouse_down", "coords": data.get("coords"), "client_id": str(websocket.remote_address)})

    except json.JSONDecodeError:
        print(f"Received invalid JSON: {message}")
    except Exception as e:
        print(f"Error handling message: {e}")


async def handler(websocket):
    """Handles a new WebSocket connection."""
    clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")

    try:
        # Immediately send the current whiteboard state to the new client
        await websocket.send(json.dumps({"action": "sync", "lines": whiteboard_data["lines"]}))

        async for message in websocket:
            await handle_message(websocket, message)
    except Exception as e:
        print(f"Connection error with {websocket.remote_address}: {e}")
    finally:
        clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")


async def main():
    """Starts the WebSocket server."""
    print("Starting WebSocket server on ws://localhost:8765")
    async with serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")

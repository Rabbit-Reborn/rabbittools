# getvnc.py

This module provides a Rabbit VNC instance

## Functions

### getVNC(vnc_type: str) -> str

Attempts to establish a VNC session with a server. The type of VNC session is determined by the `vnc_type` parameter.

**Parameters:**

- `vnc_type (str)`: The type of VNC session to establish.

**Returns:**

- `str`: The URL of the established VNC session. If the function fails to establish a VNC session, it returns 'False' or 'timeout-vnc'.

### keep_alive(websocket, stop_event)

Note that you dont need to call this function as getVNC() will set everything up including keep_alive

Sends a ping message to the server every 10 seconds to keep the WebSocket connection alive.

This is required in order to make rabbit not stop the VNC instance

**Parameters:**

- `websocket`: The WebSocket connection to keep alive.
- `stop_event`: An event that, when set, stops the keep_alive function.

## Environment Variables

- `VNC_URL`: The base URL of the VNC server.
- `VNC_AUTH`: The authentication token to start a new VNC (you can get this from `loginSession`).
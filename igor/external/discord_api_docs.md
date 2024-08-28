# Discord API Client Documentation

## 1. Initialization
When the `DiscordAPI` class is instantiated:

- It sets up basic attributes like the API base URL, token, and version.
- Initializes variables for managing the connection: ``sequence_number``, `heartbeat_interval`, ``session_id``, and ``resume_gateway_url``.

## 2. Connection Process
The `connect`method initiates the connection:

- Fetches the WebSocket gateway URL using a REST API call.
- Establishes a WebSocket connection to this URL.
- Receives the initial HELLO event from Discord.
- Sets the `heartbeat_interval` based on the HELLO event.
- Calls the `identify` method to authenticate with Discord.
- Starts two concurrent tasks: `heartbeat` and `receive`.

## 3. Heartbeat Process
The `heartbeat` method:

- Runs in a loop, sending heartbeat messages at the interval specified by Discord.
- This keeps the connection alive and informs Discord that the client is still active.

## 4. Receiving Messages
The `receive` method:

- Continuously listens for messages from Discord.
- Processes different types of messages based on their opcode:
  - DISPATCH events (e.g., READY event, which provides ``resume_gateway_url`` and ``session_id``)
  - HEARTBEAT requests
  - HEARTBEAT_ACK responses
  - RECONNECT instructions
- Updates the ``sequence_number`` with each message.

## 5. Handling Disconnections
If a disconnection occurs:

- The client attempts to reconnect using the `reconnect` method.
- If a `resume_gateway_url` is available, it tries to resume the session.
- If resuming fails or isn't possible, it falls back to establishing a new connection.

## 6. Resuming a Session
The `resume` method:

- Sends a RESUME opcode to Discord with the `session_id` and last `sequence_number`.
- This allows the client to pick up where it left off without needing to re-authenticate.

## 7. Sending Messages
The `send_message` method:

- Allows sending messages to a specific channel.
- It uses a REST API call to post the message.

## 8. Other Utility Methods

- `send_request`: A general-purpose method for making REST API calls to Discord.
- `get_guild_id`, `get_channels`, `get_channel_id`: Helper methods for retrieving information about guilds and channels.

This client implements the core functionality needed to maintain a connection with Discord, handle events, and send messages. It follows Discord's WebSocket protocol, including proper handling of heartbeats and session resuming.

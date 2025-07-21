import asyncio
import websockets
import pyaudio
import logging
import os
import webbrowser

# Configure logging to show informational messages
logging.basicConfig(level=logging.INFO)

# --- Audio Configuration ---
FORMAT = pyaudio.paInt16  # 16-bit PCM
CHANNELS = 1             # Mono audio
RATE = 44100             # Sample rate
CHUNK = 1024             # Number of frames per buffer

# Initialize PyAudio
try:
    audio = pyaudio.PyAudio()
except Exception as e:
    logging.error(f"Failed to initialize PyAudio: {e}")
    exit()

# --- PyAudio Stream Management ---
# Global stream variables
output_stream = None
input_stream = None

def start_audio_streams():
    """Initializes and starts the PyAudio input and output streams."""
    global output_stream, input_stream
    logging.info("Starting audio streams...")
    
    # Stream for playing received audio
    output_stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK
    )
    
    # Stream for recording and sending audio
    input_stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    logging.info("Audio streams started successfully.")

def stop_audio_streams():
    """Stops and closes the PyAudio streams."""
    global output_stream, input_stream
    if output_stream and output_stream.is_active():
        output_stream.stop_stream()
        output_stream.close()
        logging.info("Output stream stopped.")
    if input_stream and input_stream.is_active():
        input_stream.stop_stream()
        input_stream.close()
        logging.info("Input stream stopped.")

# --- WebSocket Handler ---
# This is the corrected line. The function now accepts 'websocket' and 'path'.
async def audio_stream_handler(websocket, path=None):
    """
    Handles the bi-directional audio stream for a single WebSocket client.
    """
    logging.info(f"Client connected from {websocket.remote_address} at path '{path}'")
    
    try:
        # This loop continuously processes audio in both directions
        while True:
            # --- Receiving from Client and Playing ---
            # Wait for audio data from the client (browser)
            client_audio_data = await websocket.recv()
            # Play the received audio data on the server's speakers
            if output_stream:
                output_stream.write(client_audio_data)

            # --- Recording from Server and Sending ---
            # Record a chunk of audio from the server's microphone
            if input_stream:
                server_audio_data = input_stream.read(CHUNK, exception_on_overflow=False)
                # Send the recorded audio data back to the client
                await websocket.send(server_audio_data)

    except websockets.exceptions.ConnectionClosed:
        logging.warning(f"Client {websocket.remote_address} disconnected.")
    except Exception as e:
        logging.error(f"An error occurred with client {websocket.remote_address}: {e}")
    finally:
        logging.info("Handler finished.")


# --- Main Server Function ---
async def main():
    """
    Sets up and starts the WebSocket server.
    """
    # Ensure audio streams are ready before starting the server
    start_audio_streams()
    
    # Define the server host and port. "0.0.0.0" makes it accessible on the local network.
    host = "0.0.0.0"
    port = 8765
    
    logging.info(f"Starting WebSocket server on ws://{host}:{port}")
    
    # Start the WebSocket server
    async with websockets.serve(audio_stream_handler, host, port):
        await asyncio.Future()  # This keeps the server running indefinitely

    # # Open main.html in the default web browser
    # html_file_path = os.path.abspath('main.html')
    # webbrowser.open(f'file://{html_file_path}')

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server shutting down manually.")
    finally:
        # Clean up PyAudio resources
        stop_audio_streams()
        if audio:
            audio.terminate()
        logging.info("PyAudio terminated. Goodbye.")

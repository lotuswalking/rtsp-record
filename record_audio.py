import av
import datetime
import threading
import time

# RTSP stream URL
rtsp_url = "rtsp://admin:Ottawa2024@192.168.2.225/live/ch00_01"

# Generate the output filename with current date and time
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"audio_recording_{current_time}.aac"

# Open the RTSP stream
input_container = av.open(rtsp_url)

# Create an output container
output_container = av.open(output_filename, mode='w')

# Find the audio stream
input_audio_stream = next(stream for stream in input_container.streams if stream.type == 'audio')

# Add an audio stream to the output container
output_audio_stream = output_container.add_stream('aac', rate=input_audio_stream.rate)
output_audio_stream.channels = input_audio_stream.channels
output_audio_stream.format = 'fltp'

# Function to capture audio
def capture_audio():
    start_time = time.time()
    for frame in input_container.decode(input_audio_stream):
        if time.time() - start_time > 30:  # Stop recording after 30 seconds
            break
        for packet in output_audio_stream.encode(frame):
            output_container.mux(packet)

# Start audio capture thread
audio_thread = threading.Thread(target=capture_audio)
audio_thread.start()

# Wait for audio thread to finish
audio_thread.join()

# Finish encoding
for packet in output_audio_stream.encode():
    output_container.mux(packet)

# Close the containers
output_container.close()
input_container.close()

print(f"Audio recording saved to {output_filename}")

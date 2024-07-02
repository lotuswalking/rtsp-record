import cv2
import av
import datetime
import threading
import time

# RTSP stream URL
rtsp_url = "rtsp://admin:Ottawa2024@192.168.2.225/live/ch00_01"

duration = 30  #视频录制时长
# Generate the output filename with current date and time
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"recording_{current_time}.mp4"

# Video capture setup
cap = cv2.VideoCapture(rtsp_url)

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# PyAV container and streams
container = av.open(output_filename, mode='w')

video_stream = container.add_stream('h264', rate=fps)
output_audio_stream  = container.add_stream('aac')


video_stream.width = width
video_stream.height = height
video_stream.pix_fmt = 'yuv420p'

# Function to capture audio
def capture_audio():
    input_container = av.open(rtsp_url)
    input_audio_stream = next(stream for stream in input_container.streams if stream.type == 'audio')
    output_audio_stream.rate = input_audio_stream.rate
    output_audio_stream.channels = input_audio_stream.channels
    output_audio_stream.format = 'fltp'
    start_time = time.time()
    for frame in input_container.decode(input_audio_stream):
        if time.time() - start_time > duration:
            break
        packet = output_audio_stream.encode(frame)
        container.mux(packet)

# Start audio capture thread
audio_thread = threading.Thread(target=capture_audio)
audio_thread.start()

# Video capture loop
start_time = time.time()
while time.time() - start_time < duration:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to the format required by PyAV
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = av.VideoFrame.from_ndarray(frame, format='rgb24')
    for packet in video_stream.encode(frame):
        container.mux(packet)

# Finish encoding
for packet in video_stream.encode():
    container.mux(packet)

# Wait for audio thread to finish
audio_thread.join()

# Close the container
container.close()

# Release resources
cap.release()

print(f"Recording saved to {output_filename}")

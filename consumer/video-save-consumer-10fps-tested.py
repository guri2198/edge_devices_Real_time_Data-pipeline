import cv2
import json
import base64
import time
from kafka import KafkaConsumer
import numpy as np

# Kafka Configurations
kafka_servers = ['10.1.56.46:9092', '10.1.56.46:9093', '10.1.56.46:9094']  # Kafka brokers
topic_name = 'FrontGATE1'  # Kafka topic name
output_video_path = '/KafkaSSD/data/FrontGATE1.avi'  # Path to save the video file

# Set up Kafka consumer
consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=kafka_servers,
    auto_offset_reset='earliest',  # Start reading messages from the beginning
    enable_auto_commit=True,
    group_id='video_consumer_group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# Initialize video writer
video_writer = None
frame_width = 640  # Width of the frame (same as in producer)
frame_height = 480  # Height of the frame (same as in producer)
fps = 10  # Frames per second (same as in producer)
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Video codec for AVI format

try:
    print("Starting to consume frames...")

    for message in consumer:
        # Decode the JSON message
        data = message.value

        # Extract Base64 frame data and decode
        frame_data_base64 = data.get('frame', None)
        if not frame_data_base64:
            print("Warning: Received message without 'frame' key.")
            continue

        frame_data = base64.b64decode(frame_data_base64)
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)

        # Initialize the video writer if not already done
        if video_writer is None:
            video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

        # Write the frame to the video file
        video_writer.write(frame)

        # Print log with frame information
        timestamp = data.get('timestamp', 'N/A')
        frame_size_kb = data.get('size', 'N/A')
        print(f"Decoded frame at {timestamp} | Size: {frame_size_kb:.2f} KB | Saved to video.")

except KeyboardInterrupt:
    print("Consumer interrupted. Closing...")
finally:
    # Release video writer and close consumer
    if video_writer:
        video_writer.release()
    consumer.close()
    print("Resources released. Video saved at", output_video_path)













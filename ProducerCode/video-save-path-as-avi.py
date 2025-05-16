import numpy as np
import os
import time
import cv2
import logging
from kafka import KafkaConsumer
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def initialize_video_writer(output_dir, frame_width, frame_height, fps=20):
    """
    Initialize the OpenCV VideoWriter.

    :param output_dir: Directory to save the video
    :param frame_width: Width of the video frame
    :param frame_height: Height of the video frame
    :param fps: Frames per second for the video
    :return: Initialized VideoWriter object and video file path
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    video_filename = f"video_{timestamp}.avi"
    video_filepath = os.path.join(output_dir, video_filename)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(video_filepath, fourcc, fps, (frame_width, frame_height))

    return video_writer, video_filepath

if __name__ == "__main__":
    # Kafka configuration
    kafka_servers = '10.1.56.46:9092,10.1.56.46:9093,10.1.56.46:9094'
    topic = 'LabTappoCam1'

    # Output directory
    output_dir = "/media/user/Extreme SSD/DATAPIPELINE/DIXON-LAB-TAPPO-CAM"

    # Create output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create Kafka consumer
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=kafka_servers,
        auto_offset_reset='earliest',  # Start consuming from the earliest message
        enable_auto_commit=True,
        group_id='frame_consumer_group',
        value_deserializer=lambda m: m  # Keep the message in binary format
    )

    frame_index = 0  # Frame counter
    video_writer = None  # Placeholder for the VideoWriter object
    video_filepath = None

    try:
        for message in consumer:
            start_time = time.time()

            # Decode the buffer into a numpy array
            frame = cv2.imdecode(np.frombuffer(message.value, np.uint8), cv2.IMREAD_COLOR)

            if frame is None:
                logging.warning(f"Frame {frame_index} is invalid. Skipping.")
                continue

            # Initialize the video writer on the first frame
            if video_writer is None:
                frame_height, frame_width = frame.shape[:2]
                video_writer, video_filepath = initialize_video_writer(output_dir, frame_width, frame_height)

            # Write the frame to the video
            video_writer.write(frame)
            frame_index += 1

            # Maintain a log for processing time per frame
            elapsed_time = time.time() - start_time
            logging.info(f"Processed frame {frame_index} in {elapsed_time:.3f} seconds.")

    except KeyboardInterrupt:
        logging.info("Shutdown signal received. Exiting...")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    finally:
        if video_writer is not None:
            video_writer.release()
            logging.info(f"Video saved to {video_filepath}")

        consumer.close()
        logging.info("Kafka consumer closed.")



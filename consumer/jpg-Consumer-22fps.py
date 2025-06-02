import numpy as np
import os
import time
import cv2
import logging
from kafka import KafkaConsumer
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def save_frame(buffer, output_dir, frame_index):
    """
    Save a single frame as a JPEG image.

    :param buffer: Binary frame data
    :param output_dir: Directory to store frames
    :param frame_index: Unique index for naming the frame
    """
    try:
        # Decode the buffer into a numpy array
        frame = cv2.imdecode(np.frombuffer(buffer, np.uint8), cv2.IMREAD_COLOR)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"frame_{frame_index:06d}_{timestamp}.jpg"
        filepath = os.path.join(output_dir, filename)

        # Save the frame
        cv2.imwrite(filepath, frame)
        logging.info(f"Saved frame {frame_index} to {filepath}")
    except Exception as e:
        logging.error(f"Error saving frame {frame_index}: {e}")

if __name__ == "__main__":
    # Kafka configuration
    kafka_servers = '10.1.56.46:9092,10.1.56.46:9093,10.1.56.46:9094'
    topic = 'LabTappoCam1'

    # Output directory
    output_dir = "/KafkaSSD/data/fps test data/labtappocam1"

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

    try:
        for message in consumer:
            start_time = time.time()

            # Save the frame to disk
            save_frame(message.value, output_dir, frame_index)

            frame_index += 1

            # Maintain a log for processing time per frame
            elapsed_time = time.time() - start_time
            logging.info(f"Processed frame {frame_index} in {elapsed_time:.3f} seconds.")

    except KeyboardInterrupt:
        logging.info("Shutdown signal received. Exiting...")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    finally:
        consumer.close()
        logging.info("Kafka consumer closed.")

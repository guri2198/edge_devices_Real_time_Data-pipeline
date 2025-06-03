import cv2
from kafka import KafkaProducer
import time
import logging
import signal
from termcolor import colored  # To add color to terminal output

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def signal_handler(signal, frame):
    logging.info("Shutdown signal received. Closing Kafka producer...")
    producer.flush()
    producer.close()
    exit(0)

# Register signal handler for graceful shutdown (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def send_video_frames(producer, topic, video_source, fps=30):
    """
    Captures video frames from the given video source and sends them to Kafka.

    :param producer: KafkaProducer object
    :param topic: Kafka topic name
    :param video_source: Video source URL or device ID
    :param fps: Target frames per second
    """
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        logging.error(f"Error: Could not open video source: {video_source}")
        return

    frame_interval = 1.0 / fps  # Time interval between frames
    start_time = time.time()
    frame_count = 0
    second_counter = 0
    frame_index = 0

    try:
        while True:
            frame_start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                logging.warning("Warning: Failed to capture frame.")
                break

            # Encode frame as JPG
            _, buffer = cv2.imencode('.jpg', frame)

            # Frame size in bytes, convert to KB
            frame_size_kb = len(buffer.tobytes()) / 1024

            # Color coding for frame size
            if frame_size_kb < 50:
                frame_size_colored = colored(f"{frame_size_kb:.2f} KB", 'green')  # Small frames in green
            elif frame_size_kb < 100:
                frame_size_colored = colored(f"{frame_size_kb:.2f} KB", 'yellow')  # Medium frames in yellow
            else:
                frame_size_colored = colored(f"{frame_size_kb:.2f} KB", 'red')  # Large frames in red

            # Send frame to Kafka
            producer.send(topic, buffer.tobytes())

            # Log less frequently to reduce logging overhead
            if frame_index % 100 == 0:
                logging.info(f"Frame {frame_index} sent to Kafka topic: {topic} (Second: {second_counter}) | Frame Size: {frame_size_colored}")

            frame_count += 1
            frame_index += 1

            # Calculate and log actual FPS every second
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1.0:
                fps_actual = frame_count / elapsed_time
                logging.info("Second: %d | Frames Sent: %d | Actual FPS: %.2f", second_counter, frame_count, fps_actual)
                start_time = time.time()  # Reset timer
                frame_count = 0  # Reset frame count
                second_counter += 1  # Increment second counter
                frame_index = 0  # Reset frame index for the new second

            # Calculate frame processing time and adjust sleep to maintain FPS
            frame_processing_time = time.time() - frame_start_time
            sleep_time = frame_interval - frame_processing_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    except Exception as e:
        logging.error("Error while streaming video: %s", e)
    finally:
        cap.release()
        logging.info("Video capture released.")

def create_producer(kafka_servers, max_retries=5):
    """
    Creates a Kafka producer and retries if it fails.

    :param kafka_servers: Kafka bootstrap servers as a string
    :return: KafkaProducer object
    """
    retries = 0
    while retries < max_retries:
        try:
            producer = KafkaProducer(bootstrap_servers=kafka_servers)
            logging.info("Kafka producer created.")
            return producer
        except Exception as e:
            retries += 1
            logging.error("Error creating Kafka producer: %s. Retry %d/%d", e, retries, max_retries)
            time.sleep(2 ** retries)  # Exponential backoff
    logging.critical("Failed to create Kafka producer after %d retries.", max_retries)
    return None  # Return None if it fails after max_retries

if __name__ == "__main__":
    # Kafka configuration
    kafka_servers = '10.1.56.46:9092,10.1.56.46:9093,10.1.56.46:9094'
    topic = 'AgriCam3'

    # Video stream URL
    video_stream_url = "http://10.1.56.46:9085"

    while True:
        # Create Kafka producer
        producer = create_producer(kafka_servers)
        if producer is None:
            logging.error("Could not create Kafka producer. Exiting...")
            break

        # Send video frames to Kafka
        send_video_frames(producer, topic, video_source=video_stream_url, fps=30)

        # Close producer after streaming ends
        producer.flush()
        producer.close()
        logging.info("Kafka producer closed. Restarting in 5 seconds...")
        time.sleep(5)  # Retry after delay



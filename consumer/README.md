# Kafka Video Stream Consumers

A collection of Python-based Kafka consumers for processing real-time video streams. This repository contains three distinct consumer implementations, each designed for specific video data processing and storage requirements.

## System Architecture
---

```mermaid
flowchart TD
    A[Kafka Cluster<br/>10.1.56.46:9092,9093,9094] --> B[Topic: LabTappoCam1]
    A --> C[Topic: FrontGATE1]
    
    B --> D[JPEG Consumer<br/>jpg-Consumer-22fps.py]
    B --> E[Dynamic AVI Consumer<br/>video-save-path-as-avi.py]
    C --> F[AVI Consumer<br/>video-save-consumer-10fps-tested.py]
    
    D --> G[Binary Frame Data]
    G --> H[OpenCV Decode]
    H --> I[Individual JPEG Files<br/>/KafkaSSD/data/fps test data/labtappocam1]
    
    E --> J[Binary Frame Data]
    J --> K[OpenCV Decode]
    K --> L[Single AVI Video<br/>/media/user/Extreme SSD/DATAPIPELINE/DIXON-LAB-TAPPO-CAM]
    
    F --> M[JSON + Base64 Data]
    M --> N[JSON Parse + Base64 Decode]
    N --> O[Single AVI Video<br/>/KafkaSSD/data/FrontGATE1.avi]
```

## Prerequisites

### System Requirements
- Python 3.7 or higher
- Access to Kafka cluster at `10.1.56.46` (ports 9092, 9093, 9094)
- Sufficient storage space at designated output paths

### Python Dependencies
```bash
pip install kafka-python opencv-python numpy
```
### General Consumer Processing Flow 

```mermaid
sequenceDiagram
    participant K as Kafka Broker
    participant JC as JPEG Consumer
    participant AC as AVI Consumer
    participant DC as Dynamic AVI Consumer
    participant FS as File System
    
    K->>JC: Binary Frame Data
    JC->>JC: cv2.imdecode()
    JC->>FS: Save JPEG file
    
    K->>AC: JSON + Base64 Data
    AC->>AC: json.loads()
    AC->>AC: base64.decode()
    AC->>AC: cv2.imdecode()
    AC->>FS: Write to AVI file
    
    K->>DC: Binary Frame Data
    DC->>DC: cv2.imdecode()
    DC->>DC: Initialize VideoWriter (first frame)
    DC->>FS: Write to timestamped AVI
```

## Consumer Implementations

### 1. JPEG Frame Consumer (`jpg-Consumer-22fps.py`)

Processes binary video frames from Kafka and saves each frame as individual JPEG files.

#### Technical Specifications

| Parameter | Value |
|-----------|-------|
| **Topic** | `LabTappoCam1` |
| **Consumer Group** | `frame_consumer_group` |
| **Output Format** | Individual JPEG files |
| **Storage Location** | `/KafkaSSD/data/fps test data/labtappocam1` |
| **Frame Rate** | N/A |
| **Resolution** | Original (preserved from source) |
| **Codec** | N/A (JPEG compression) |
| **Naming Convention** | `frame_{index:06d}_{timestamp}.jpg` |

#### Configuration
```python
kafka_servers = '10.1.56.46:9092,10.1.56.46:9093,10.1.56.46:9094'
topic = 'LabTappoCam1'
output_dir = "/KafkaSSD/data/fps test data/labtappocam1"
consumer_group = 'frame_consumer_group'
```

#### Data Processing
- **Input**: Binary frame data from Kafka messages
- **Processing**: `cv2.imdecode(np.frombuffer(buffer, np.uint8), cv2.IMREAD_COLOR)`
- **Output**: JPEG files named `frame_{index:06d}_{timestamp}.jpg`

#### Key Features
- Creates output directory automatically if missing
- Logs processing time per frame
- Handles frame decoding errors gracefully
- Uses timestamp-based file naming

#### Usage
```bash
python jpg-Consumer-22fps.py
```

#### Error Handling
- Catches exceptions during frame saving operations
- Logs errors with frame index information
- Continues processing subsequent frames on individual failures

### Error Flow diagram 

```mermaid
flowchart TD
    A[Receive Kafka Message] --> B[Decode Binary Data]
    B --> C{Frame Valid?}
    C -->|Yes| D[Generate Filename]
    C -->|No| E[Log Error]
    E --> F[Continue to Next Frame]
    D --> G[Save JPEG File]
    G --> H{Save Successful?}
    H -->|Yes| I[Log Success]
    H -->|No| J[Log Error]
    I --> F
    J --> F
    F --> A
```
---

### 2. AVI Video Consumer (`video-save-consumer-10fps-tested.py`)

Compiles JSON-encoded video frames into a single AVI video file at 10 FPS.

#### Technical Specifications

| Parameter | Value |
|-----------|-------|
| **Topic** | `FrontGATE1` |
| **Consumer Group** | `video_consumer_group` |
| **Output Format** | Single AVI video file |
| **Storage Location** | `/KafkaSSD/data/FrontGATE1.avi` |
| **Frame Rate** | 10 FPS |
| **Resolution** | 640x480 pixels |
| **Codec** | XVID |
| **Naming Convention** | `FrontGATE1.avi` (fixed filename) |

#### Configuration
```python
kafka_servers = ['10.1.56.46:9092', '10.1.56.46:9093', '10.1.56.46:9094']
topic_name = 'FrontGATE1'
output_video_path = '/KafkaSSD/data/FrontGATE1.avi'
consumer_group = 'video_consumer_group'
frame_width = 640
frame_height = 480
fps = 10
```

#### Message Format
The consumer expects JSON messages with the following structure:
```json
{
  "frame": "base64_encoded_frame_data",
  "timestamp": "frame_timestamp", 
  "size": frame_size_in_kb
}
```

#### Data Processing
- **Input**: JSON messages with Base64-encoded frame data
- **Processing**: JSON parsing → Base64 decoding → OpenCV frame reconstruction
- **Output**: Single AVI file using XVID codec

#### Key Features
- Lazy initialization of video writer on first frame
- Logs frame metadata (timestamp, size)
- Validates JSON message structure
- Uses XVID codec for video compression

#### Usage
```bash
python video-save-consumer-10fps-tested.py
```

#### Error Handling
- Validates presence of 'frame' key in JSON messages
- Skips malformed messages with warning logs
- Ensures proper resource cleanup on termination

---

### 3. Dynamic AVI Consumer (`video-save-path-as-avi.py`)

Creates timestamped AVI video files with dynamic frame dimension detection.

#### Technical Specifications

| Parameter | Value |
|-----------|-------|
| **Topic** | `LabTappoCam1` |
| **Consumer Group** | `frame_consumer_group` |
| **Output Format** | Timestamped AVI video files |
| **Storage Location** | `/media/user/Extreme SSD/DATAPIPELINE/DIXON-LAB-TAPPO-CAM` |
| **Frame Rate** | 20 FPS (configurable) |
| **Resolution** | Dynamic (determined from first frame) |
| **Codec** | XVID |
| **Naming Convention** | `video_{timestamp}.avi` |

#### Configuration
```python
kafka_servers = '10.1.56.46:9092,10.1.56.46:9093,10.1.56.46:9094'
topic = 'LabTappoCam1'
output_dir = "/media/user/Extreme SSD/DATAPIPELINE/DIXON-LAB-TAPPO-CAM"
consumer_group = 'frame_consumer_group'
fps = 20
```

#### Data Processing
- **Input**: Binary frame data from Kafka messages
- **Processing**: Binary decoding → Frame validation → Dynamic video writer initialization
- **Output**: Timestamped AVI files named `video_{YYYYMMDD_HHMMSS}.avi`

#### Key Features
- Detects frame dimensions automatically from first valid frame
- Creates timestamped video files for each session
- Validates frames before processing (skips null frames)
- Configurable frame rate (default: 20 FPS)

#### Video Writer Initialization
```python
def initialize_video_writer(output_dir, frame_width, frame_height, fps=20):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    video_filename = f"video_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(video_filepath, fourcc, fps, (frame_width, frame_height))
```

#### Usage
```bash
python video-save-path-as-avi.py
```

#### Error Handling
- Validates decoded frames before processing
- Handles invalid frame data gracefully
- Ensures proper cleanup of video writer resources
- Comprehensive logging for debugging

## Deployment

### Directory Structure
Ensure the following directories exist or can be created by the consumers:
```
/KafkaSSD/data/fps test data/labtappocam1/          # JPEG Consumer output
/KafkaSSD/data/                                     # AVI Consumer output  
/media/user/Extreme SSD/DATAPIPELINE/DIXON-LAB-TAPPO-CAM/  # Dynamic AVI Consumer output
```

### Running Consumers
Each consumer runs independently as a standalone process:

```bash
# Terminal 1 - JPEG Consumer
python jpg-Consumer-22fps.py

# Terminal 2 - AVI Consumer  
python video-save-consumer-10fps-tested.py

# Terminal 3 - Dynamic AVI Consumer
python video-save-path-as-avi.py
```

### Monitoring
All consumers implement structured logging. Monitor logs for:
- Frame processing rates
- Error frequencies
- Storage operation status
- Consumer connectivity health

### Graceful Shutdown
All consumers handle `SIGINT` (Ctrl+C) for graceful shutdown:
- Closes Kafka consumer connections
- Releases video writer resources
- Logs final statistics

### Consumer Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> Connecting : Load Config
    Connecting --> Consuming : Kafka Connection Established
    Consuming --> Processing : Message Received
    Processing --> Consuming : Frame Processed
    Processing --> Error : Processing Failed
    Error --> Consuming : Log Error & Continue
    Consuming --> Shutdown : SIGINT Received
    Shutdown --> Cleanup : Close Resources
    Cleanup --> [*] : Exit
```

## Technical Specifications

| Consumer | Topic | Data Format | Output Format | Frame Rate | Storage Location |
|----------|-------|-------------|---------------|------------|------------------|
| JPEG Consumer | LabTappoCam1 | Binary | Individual JPEG | N/A | `/KafkaSSD/data/fps test data/labtappocam1` |
| AVI Consumer | FrontGATE1 | JSON+Base64 | Single AVI | 10 FPS | `/KafkaSSD/data/FrontGATE1.avi` |
| Dynamic AVI Consumer | LabTappoCam1 | Binary | Timestamped AVI | 20 FPS | `/media/user/Extreme SSD/DATAPIPELINE/DIXON-LAB-TAPPO-CAM` |

## Troubleshooting

### Generalised System Health Monitoring Flow 

```mermaid
graph LR
    A[Kafka Cluster Health] --> B[Consumer Lag Monitoring]
    B --> C[Processing Rate Analysis]
    C --> D[Storage I/O Monitoring]
    D --> E[Error Rate Tracking]
    E --> F[Resource Utilization]
    F --> G[Alert Generation]
    
    subgraph Metrics
        H[Frames/Second]
        I[Queue Depth]
        J[Disk Usage]
        K[Memory Usage]
    end
    
    C --> H
    B --> I  
    D --> J
    F --> K
```


### Common Issues

**Connection Failures**
- Verify Kafka broker accessibility at `10.1.56.46`
- Check network connectivity to ports 9092, 9093, 9094

**Storage Issues**  
- Ensure write permissions on output directories
- Monitor available disk space
- Verify directory paths exist or can be created

**Frame Processing Errors**
- Check frame data integrity in Kafka topics
- Monitor consumer logs for decode failures
- Verify OpenCV installation and functionality

### Performance Tuning
- Adjust consumer fetch parameters for throughput optimization
- Monitor consumer lag using Kafka administrative tools
- Consider storage I/O optimization for high-throughput scenarios

## License

This project is provided as-is for technical implementation reference.

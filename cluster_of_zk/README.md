# ZooKeeper Cluster Configuration Documentation

## Overview

This directory contains configuration files for a 3-node ZooKeeper ensemble that provides coordination services for a distributed Kafka cluster. The ZooKeeper cluster ensures high availability, fault tolerance, and distributed consensus for the Kafka brokers.

---

## Architecture Diagram

```mermaid
graph TB
    subgraph "ZooKeeper Ensemble (3 Nodes)"
        ZK1["ZooKeeper Node 1<br/>10.1.57.192:2181<br/>Leader/Follower"]
        ZK2["ZooKeeper Node 2<br/>10.1.56.46:2181<br/>Leader/Follower"]
        ZK3["ZooKeeper Node 3<br/>10.1.57.15:2181<br/>Leader/Follower"]
    end
    
    subgraph "Inter-ZooKeeper Communication"
        ZK1 -.->|"Election: 3888<br/>Peer: 2888"| ZK2
        ZK2 -.->|"Election: 3888<br/>Peer: 2888"| ZK3
        ZK3 -.->|"Election: 3888<br/>Peer: 2888"| ZK1
    end
    
    subgraph "Kafka Brokers (Clients)"
        KB1["Kafka Broker 0<br/>10.1.56.46:9092"]
        KB2["Kafka Broker 1<br/>10.1.56.46:9092"]
    end
    
    subgraph "Data Storage"
        DS1["Data Directory<br/>/home/iotlab-linux-node/zookeeper_data2"]
        DL1["Log Directory<br/>/home/iotlab-linux-node/zookeeper_logs2"]
    end
    
    KB1 -->|"Client Connect: 2181"| ZK1
    KB1 -->|"Client Connect: 2181"| ZK2
    KB1 -->|"Client Connect: 2181"| ZK3
    
    KB2 -->|"Client Connect: 2181"| ZK1
    KB2 -->|"Client Connect: 2181"| ZK2
    KB2 -->|"Client Connect: 2181"| ZK3
    
    ZK1 --> DS1
    ZK2 --> DS1
    ZK3 --> DS1
    
    ZK1 --> DL1
    ZK2 --> DL1
    ZK3 --> DL1
    
    style ZK1 fill:#e1f5fe
    style ZK2 fill:#e1f5fe
    style ZK3 fill:#e1f5fe
    style KB1 fill:#f3e5f5
    style KB2 fill:#f3e5f5
    style DS1 fill:#e8f5e8
    style DL1 fill:#fff3e0
```

---

## File Inventory

| File Name | Type | Purpose | Target Machine | Size |
|-----------|------|---------|----------------|------|
| `zookeeper.properties.M1` | ZooKeeper Config | Node 1 configuration | Machine 1 (10.1.57.192) | 1,548 bytes |
| `zookeeper.properties.M2` | ZooKeeper Config | Node 2 configuration | Machine 2 (10.1.56.46) | 1,548 bytes |
| `zookeeper.properties.M3` | ZooKeeper Config | Node 3 configuration | Machine 3 (10.1.57.15) | 1,548 bytes |
| `server.propertiesM1` | Kafka Config | Broker 0 configuration | Machine 1 | 535 bytes |
| `server_1.propertiesM1` | Kafka Config | Broker 1 configuration | Machine 1 | 535 bytes |

---

## ZooKeeper Ensemble Configuration

### Cluster Topology

```mermaid
flowchart TD
    subgraph "ZooKeeper Quorum Formation"
        A["Node 1: 10.1.57.192<br/>server.1"]
        B["Node 2: 10.1.56.46<br/>server.2"]
        C["Node 3: 10.1.57.15<br/>server.3"]
    end
    
    subgraph "Port Allocation"
        D["Client Port: 2181<br/>Application connections"]
        E["Peer Port: 2888<br/>Follower-Leader sync"]
        F["Election Port: 3888<br/>Leader election"]
    end
    
    A --> D
    B --> D
    C --> D
    
    A --> E
    B --> E
    C --> E
    
    A --> F
    B --> F
    C --> F
    
    style A fill:#ffcdd2
    style B fill:#c8e6c9
    style C fill:#bbdefb
```

### ZooKeeper Configuration Parameters

| Parameter | Value | Description | Impact |
|-----------|-------|-------------|--------|
| **dataDir** | `/home/iotlab-linux-node/zookeeper_data2` | Snapshot storage location | Data persistence |
| **dataLogDir** | `/home/iotlab-linux-node/zookeeper_logs2` | Transaction log storage | Performance optimization |
| **tickTime** | `2000` ms | Basic time unit for heartbeats | Session timeout calculation |
| **initLimit** | `5` ticks | Follower connection timeout to leader | Cluster formation time |
| **syncLimit** | `2` ticks | Follower sync timeout with leader | Network tolerance |
| **clientPort** | `2181` | Client connection port | Application connectivity |
| **maxClientCnxns** | `60` | Maximum concurrent client connections | Scalability limit |
| **admin.enableServer** | `false` | Administrative HTTP server status | Security configuration |
| **electionPortBindRetry** | `5` | Election port binding retry attempts | Fault tolerance |

### Server Definitions

| Server ID | IP Address | Peer Port | Election Port | Role |
|-----------|------------|-----------|---------------|------|
| `server.1` | `10.1.57.192` | `2888` | `3888` | Ensemble Member |
| `server.2` | `10.1.56.46` | `2888` | `3888` | Ensemble Member |
| `server.3` | `10.1.57.15` | `2888` | `3888` | Ensemble Member |

---

## Kafka Broker Integration

### Broker Configuration Analysis

```mermaid
sequenceDiagram
    participant KB0 as Kafka Broker 0
    participant KB1 as Kafka Broker 1
    participant ZK as ZooKeeper Ensemble
    participant FS as File System
    
    Note over KB0,FS: Broker Registration & Coordination
    
    KB0->>ZK: Register broker.id=0 at 10.1.56.46:9092
    KB1->>ZK: Register broker.id=1 at 10.1.56.46:9092
    
    ZK->>KB0: Acknowledge registration
    ZK->>KB1: Acknowledge registration
    
    KB0->>FS: Write logs to /home/user/NasStorage/BROKER_SERVER_LOGS/broker-0-logs
    KB1->>FS: Write logs to /home/user/NasStorage/BROKER_SERVER_LOGS/broker-1-logs
    
    Note over KB0,ZK: Ongoing coordination
    KB0->>ZK: Heartbeat & metadata updates
    KB1->>ZK: Heartbeat & metadata updates
    
    ZK->>KB0: Partition assignments
    ZK->>KB1: Partition assignments
```

### Kafka Broker Parameters

#### Broker Identity & Network
| Parameter | Broker 0 Value | Broker 1 Value | Description |
|-----------|----------------|----------------|-------------|
| **broker.id** | `0` | `1` | Unique broker identifier |
| **listeners** | `PLAINTEXT://10.1.56.46:9092` | `PLAINTEXT://10.1.56.46:9092` | Internal listener configuration |
| **advertised.listeners** | `PLAINTEXT://10.1.56.46:9092` | `PLAINTEXT://10.1.56.46:9092` | External client connection endpoint |

#### Storage Configuration
| Parameter | Broker 0 Value | Broker 1 Value | Description |
|-----------|----------------|----------------|-------------|
| **log.dirs** | `/home/user/NasStorage/BROKER_SERVER_LOGS/broker-0-logs` | `/home/user/NasStorage/BROKER_SERVER_LOGS/broker-1-logs` | Data storage location |

#### ZooKeeper Integration
| Parameter | Value | Description |
|-----------|-------|-------------|
| **zookeeper.connect** | `10.1.57.192:2181,10.1.56.46:2181,10.1.57.15:2181` | ZooKeeper ensemble connection string |
| **zookeeper.connection.timeout.ms** | `18000` | Connection timeout (18 seconds) |

#### Performance Tuning
| Parameter | Value | Description | Performance Impact |
|-----------|-------|-------------|--------------------|
| **num.network.threads** | `3` | Network request handler threads | Network throughput |
| **num.io.threads** | `8` | I/O operation threads | Disk I/O performance |
| **socket.send.buffer.bytes** | `102400` (100KB) | TCP send buffer size | Network efficiency |
| **socket.receive.buffer.bytes** | `102400` (100KB) | TCP receive buffer size | Network efficiency |
| **socket.request.max.bytes** | `104857600` (100MB) | Maximum request size | Message size limit |

#### Data Retention
| Parameter | Value | Description | Storage Impact |
|-----------|-------|-------------|----------------|
| **log.retention.hours** | `168` (7 days) | Data retention period | Storage utilization |
| **log.segment.bytes** | `1073741824` (1GB) | Log segment size | File management |
| **log.retention.check.interval.ms** | `300000` (5 minutes) | Cleanup check frequency | Maintenance overhead |

---

## Network Architecture

### Port Allocation Matrix

| Service | Node 1 (10.1.57.192) | Node 2 (10.1.56.46) | Node 3 (10.1.57.15) | Purpose |
|---------|----------------------|---------------------|---------------------|----------|
| **ZooKeeper Client** | 2181 | 2181 | 2181 | Client connections |
| **ZooKeeper Peer** | 2888 | 2888 | 2888 | Follower-Leader sync |
| **ZooKeeper Election** | 3888 | 3888 | 3888 | Leader election |
| **Kafka Broker** | - | 9092 | - | Message brokering |

### Communication Flow

```mermaid
graph LR
    subgraph "External Clients"
        PC["Producer Clients"]
        CC["Consumer Clients"]
        AC["Admin Clients"]
    end
    
    subgraph "Kafka Layer"
        KB["Kafka Brokers<br/>10.1.56.46:9092"]
    end
    
    subgraph "Coordination Layer"
        ZK["ZooKeeper Ensemble<br/>2181"]
    end
    
    subgraph "Storage Layer"
        NAS["NAS Storage<br/>/home/user/NasStorage"]
        ZKD["ZK Data<br/>/home/iotlab-linux-node"]
    end
    
    PC --> KB
    CC --> KB
    AC --> KB
    
    KB --> ZK
    
    KB --> NAS
    ZK --> ZKD
    
    style PC fill:#e3f2fd
    style CC fill:#e3f2fd
    style AC fill:#e3f2fd
    style KB fill:#f3e5f5
    style ZK fill:#e8f5e8
    style NAS fill:#fff3e0
    style ZKD fill:#fff3e0
```

---

## Configuration Consistency Analysis

### ZooKeeper Configuration Uniformity

| Configuration Aspect | M1 | M2 | M3 | Status |
|-----------------------|----|----|----|--------|
| **dataDir Path** | ✅ Identical | ✅ Identical | ✅ Identical | Consistent |
| **dataLogDir Path** | ✅ Identical | ✅ Identical | ✅ Identical | Consistent |
| **tickTime** | ✅ 2000ms | ✅ 2000ms | ✅ 2000ms | Consistent |
| **initLimit** | ✅ 5 ticks | ✅ 5 ticks | ✅ 5 ticks | Consistent |
| **syncLimit** | ✅ 2 ticks | ✅ 2 ticks | ✅ 2 ticks | Consistent |
| **clientPort** | ✅ 2181 | ✅ 2181 | ✅ 2181 | Consistent |
| **maxClientCnxns** | ✅ 60 | ✅ 60 | ✅ 60 | Consistent |
| **Server Definitions** | ✅ Complete | ✅ Complete | ✅ Complete | Consistent |

### Kafka Broker Configuration Analysis

| Configuration Aspect | server.propertiesM1 | server_1.propertiesM1 | Analysis |
|-----------------------|---------------------|----------------------|----------|
| **broker.id** | 0 | 1 | ✅ Unique IDs |
| **listeners** | Same IP:Port | Same IP:Port | ⚠️ Port conflict potential |
| **advertised.listeners** | Same IP:Port | Same IP:Port | ⚠️ Port conflict potential |
| **log.dirs** | broker-0-logs | broker-1-logs | ✅ Separate directories |
| **zookeeper.connect** | Identical | Identical | ✅ Consistent ensemble |

---

## High Availability & Fault Tolerance

### ZooKeeper Quorum Requirements

```mermaid
pie title ZooKeeper Fault Tolerance (3-Node Ensemble)
    "Healthy Nodes Required" : 2
    "Nodes That Can Fail" : 1
```

| Scenario | Healthy Nodes | Quorum Status | Service Availability |
|----------|---------------|---------------|---------------------|
| All nodes up | 3/3 | ✅ Active | Full service |
| One node down | 2/3 | ✅ Active | Full service |
| Two nodes down | 1/3 | ❌ Lost | Service unavailable |
| All nodes down | 0/3 | ❌ Lost | Complete outage |

### Leader Election Process

```mermaid
stateDiagram-v2
    [*] --> Looking
    Looking --> Following : Discover Leader
    Looking --> Leading : Win Election
    Following --> Looking : Leader Lost
    Leading --> Looking : Lose Leadership
    
    note right of Looking
        All nodes start here
        Election algorithm runs
    end note
    
    note right of Following
        Sync with leader
        Handle client reads
    end note
    
    note right of Leading
        Handle all writes
        Coordinate followers
    end note
```

---

## Storage Architecture

### Directory Structure

```mermaid
graph TD
    subgraph "ZooKeeper Storage"
        ZKR["/home/iotlab-linux-node/"]
        ZKD["zookeeper_data2/<br/>• Snapshots<br/>• myid file<br/>• Version info"]
        ZKL["zookeeper_logs2/<br/>• Transaction logs<br/>• Write-ahead logs"]
    end
    
    subgraph "Kafka Storage"
        KR["/home/user/NasStorage/BROKER_SERVER_LOGS/"]
        KB0["broker-0-logs/<br/>• Topic partitions<br/>• Index files<br/>• Log segments"]
        KB1["broker-1-logs/<br/>• Topic partitions<br/>• Index files<br/>• Log segments"]
    end
    
    ZKR --> ZKD
    ZKR --> ZKL
    KR --> KB0
    KR --> KB1
    
    style ZKD fill:#e8f5e8
    style ZKL fill:#fff3e0
    style KB0 fill:#f3e5f5
    style KB1 fill:#f3e5f5
```

### Storage Capacity Planning

| Component | Storage Type | Location | Estimated Usage | Retention |
|-----------|--------------|----------|----------------|----------|
| **ZK Snapshots** | Data | `/home/iotlab-linux-node/zookeeper_data2` | 10-100MB | Automatic |
| **ZK Logs** | Transaction | `/home/iotlab-linux-node/zookeeper_logs2` | 1-10GB | Configurable |
| **Kafka Logs** | Message Data | `/home/user/NasStorage/BROKER_SERVER_LOGS/` | 100GB+ | 7 days |

---

## Security Configuration

### Current Security Posture

| Security Aspect | Configuration | Risk Level | Recommendation |
|-----------------|---------------|------------|----------------|
| **ZK Admin Server** | Disabled | ✅ Low | Maintain disabled |
| **Client Authentication** | None | ❌ High | Implement SASL |
| **Inter-node Communication** | Plain TCP | ❌ Medium | Enable TLS |
| **Kafka Security** | PLAINTEXT | ❌ High | Enable SSL/SASL |
| **Network Isolation** | None visible | ❌ Medium | Implement VLANs |

---

## Performance Characteristics

### Timing Configuration Analysis

| Parameter | Value | Calculated Timeout | Impact |
|-----------|-------|--------------------|--------|
| **tickTime** | 2000ms | Base unit | Heartbeat interval |
| **initLimit** | 5 ticks | 10 seconds | Follower connection timeout |
| **syncLimit** | 2 ticks | 4 seconds | Follower sync timeout |
| **ZK Connection Timeout** | 18000ms | 18 seconds | Kafka-ZK connection |

### Resource Allocation

```mermaid
graph LR
    subgraph "Network Resources"
        NT["Network Threads: 3"]
        SB["Send Buffer: 100KB"]
        RB["Receive Buffer: 100KB"]
    end
    
    subgraph "I/O Resources"
        IT["I/O Threads: 8"]
        MR["Max Request: 100MB"]
    end
    
    subgraph "Storage Resources"
        SS["Segment Size: 1GB"]
        RH["Retention: 168h"]
        CI["Check Interval: 5min"]
    end
    
    NT --> IT
    IT --> SS
    
    style NT fill:#e3f2fd
    style IT fill:#f3e5f5
    style SS fill:#e8f5e8
```

---

## Deployment Considerations

### Machine Requirements

| Machine | IP Address | Services | Configuration Files |
|---------|------------|----------|--------------------|
| **Machine 1** | 10.1.57.192 | ZooKeeper Node 1 | `zookeeper.properties.M1` |
| **Machine 2** | 10.1.56.46 | ZooKeeper Node 2, Kafka Brokers | `zookeeper.properties.M2`, `server.propertiesM1`, `server_1.propertiesM1` |
| **Machine 3** | 10.1.57.15 | ZooKeeper Node 3 | `zookeeper.properties.M3` |

### Configuration Deployment Checklist

- [ ] Deploy appropriate ZooKeeper configuration to each machine
- [ ] Create myid files in ZooKeeper data directories (1, 2, 3)
- [ ] Ensure Kafka brokers use different ports if on same machine
- [ ] Verify network connectivity between all nodes
- [ ] Create required directory structures
- [ ] Set appropriate file permissions
- [ ] Configure firewall rules for required ports

---

## Monitoring & Troubleshooting

### Key Metrics to Monitor

| Component | Metric | Normal Range | Alert Threshold |
|-----------|--------|--------------|----------------|
| **ZooKeeper** | Latency | <50ms | >200ms |
| **ZooKeeper** | Outstanding Requests | <10 | >100 |
| **ZooKeeper** | Active Connections | <60 | >55 |
| **Kafka** | Under-replicated Partitions | 0 | >0 |
| **Kafka** | Leader Election Rate | <1/hour | >5/hour |

### Common Issues & Solutions

| Issue | Symptoms | Root Cause | Solution |
|-------|----------|------------|----------|
| **Split Brain** | Multiple leaders | Network partition | Check network connectivity |
| **High Latency** | Slow responses | Disk I/O bottleneck | Monitor disk performance |
| **Connection Timeouts** | Client disconnections | Network issues | Verify ZK connection string |
| **Port Conflicts** | Broker startup failure | Same port configuration | Use different ports per broker |

---

## Configuration Summary

This ZooKeeper cluster configuration provides:

✅ **High Availability**: 3-node ensemble with fault tolerance  
✅ **Performance Optimization**: Separated data and log directories  
✅ **Scalability**: Support for 60 concurrent connections per node  
✅ **Integration Ready**: Proper Kafka broker coordination  

⚠️ **Areas for Improvement**:  
- Enable security features (SASL, TLS)  
- Resolve potential Kafka broker port conflicts  
- Implement monitoring and alerting  
- Add backup and disaster recovery procedures  

---

*This documentation is based on the configuration files present in the cluster_of_zk directory as of the analysis date.*


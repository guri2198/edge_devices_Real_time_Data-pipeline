# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# the directory where the snapshot is stored.
dataDir=/home/iotlab-linux-node/zookeeper_data2
dataLogDir=/home/iotlab-linux-node/zookeeper_logs2
tickTime=2000
initLimit=5
syncLimit=2
# the port at which the clients will connect
clientPort=2181
# disable the per-ip limit on the number of connections since this is a non-production config
maxClientCnxns=60
# Disable the adminserver by default to avoid port conflicts.
# Set the port to something non-conflicting if choosing to enable this
admin.enableServer=false
# admin.serverPort=8080
List of servers for quorum (if running in clustered mode)
# For a single node, you can omit this section
server.1=10.1.57.192:2888:3888
server.2=10.1.56.46:2888:3888
server.3=10.1.57.15:2888:3888
zookeeper.electionPortBindRetry=5

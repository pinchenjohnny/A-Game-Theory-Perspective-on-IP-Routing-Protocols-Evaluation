import numpy as np
import numpy.random as random
import math

#================ module vars ==============
MESH_LEN = 5
N_NODES = MESH_LEN**2
MAX_LANRTENCY = 1e3
# 每轮包数
N_PACKETS = 20

#=========== 初始图 =================

# 获取邻接表
# 返回：
#   edges：邻接表
def genMesh():
    # 邻接表
    edges = [[]] * N_NODES

    # 第一行
    for nodeI in range(0, MESH_LEN):
        if nodeI == 0:
            edges[nodeI] = [nodeI + 1, nodeI + MESH_LEN]
        elif nodeI == MESH_LEN - 1:
            edges[nodeI] = [nodeI - 1, nodeI + MESH_LEN]
        else:
            edges[nodeI] = [nodeI - 1, nodeI + 1, nodeI + MESH_LEN]
    # 中间行
    for row in range(1, MESH_LEN - 1):
        for col in range(0, MESH_LEN):
            nodeI = row * MESH_LEN + col
            if nodeI == row * MESH_LEN:
                edges[nodeI] = [nodeI - MESH_LEN, nodeI + 1, nodeI + MESH_LEN]
            elif nodeI == (row + 1) * MESH_LEN - 1:
                edges[nodeI] = [nodeI - MESH_LEN, nodeI - 1, nodeI + MESH_LEN]
            else:
                edges[nodeI] = [nodeI-MESH_LEN, nodeI-1, nodeI+1, nodeI+MESH_LEN]
    # 最后一行
    for nodeI in range((MESH_LEN-1)*MESH_LEN, MESH_LEN**2):
        if nodeI == (MESH_LEN-1)*MESH_LEN:
            edges[nodeI] = [nodeI-MESH_LEN, nodeI+1]
        elif nodeI == MESH_LEN**2-1:
            edges[nodeI] = [nodeI-MESH_LEN, nodeI-1]
        else:
            edges[nodeI] = [nodeI-MESH_LEN, nodeI-1, nodeI+1]
    return edges

# 设置带宽
# 输入：
#   edges：邻接表
#   lowBandwidth：最小带宽
#   highBandwidth：最大带宽
# 返回：
#   bandwidths：记录各边带宽的二维矩阵
def getBandwidths(edges, lowBandwidth, highBandwidth):
    # 不存在的边带宽为0
    bandwidths = np.zeros((N_NODES, N_NODES),int)
    for src in range(len(edges)):
        for dst in edges[src]:
            bandwidths[src, dst] = random.randint(lowBandwidth, highBandwidth)
    return bandwidths



#=========== 求最短路径 ==============

# Floyd-Warshall求所有节点对最短路径
# 输入：
#   latencies：当前各边延迟，相当于距离
# 返回：
#   D1：记录各节点对最短距离的二维矩阵
#   PI1：最短路径的前驱节点矩阵
def getShortestPaths(latencies):
    n = N_NODES
    # 距离
    D0 = latencies.copy()
    # 前驱节点
    PI0 = np.full((n,n),-1,int)
    for i in range(n):
        for j in range(n):
            if i!=j and latencies[i,j]<MAX_LANRTENCY:
                PI0[i,j] = i

    for k in range(0,n):
        D1 = np.full((n,n), MAX_LANRTENCY, int)
        PI1 = np.full((n,n),-1,int)
        for i in range(0,n):
            for j in range(0,n):
                D1[i,j] = min(D0[i,j], D0[i,k]+D0[k,j])
                if D0[i,j]<= D0[i,k]+D0[k,j]:
                    PI1[i,j] = PI0[i,j]
                else:
                    PI1[i,j] = PI0[k,j]
        D0 = D1.copy()
        PI0 = PI1.copy()
    return D1, PI1




#============ 生成包，更新延迟 ==============

# 产生包
# 输入：
#   nPackets：包数
# 返回：
#   packets：记录每个包src和dst的列表
def genPackets(nPackets = N_PACKETS):
    packets = []
    for packetI in range(0, nPackets):
        src = random.randint(0, N_NODES)
        dst = random.randint(0, N_NODES)
        while dst==src:
            dst = random.randint(0, N_NODES)
        packets.append([src, dst])
    return packets


# 由packets的选路信息PI，以及网络bandwidths，确定各链路latencies
# 输入：
#   packets：记录包src和dst的列表
#   PI：所有节点对最短路径的前驱节点矩阵
#   bandwidths：记录各边带宽的二维矩阵
# 返回：
#   latencies：记录各边延迟的二维矩阵
def getLatencies(packets, PI, bandwidths):
    # 求flows：二维矩阵，记录每条边的流量
    flows = np.zeros((N_NODES, N_NODES), int)
    for packet in packets:
        src = packet[0]
        mid = packet[1]
        pre = PI[src,mid]
        # mesh保证所有节点对一定连通
        while(pre!=src):
            flows[pre, mid] += 1
            mid = pre
            pre = PI[src, mid]
        flows[pre,mid] += 1

    # 求latencies
    latencies = np.full((N_NODES,N_NODES), MAX_LANRTENCY, int)
    for i in range(N_NODES):
        for j in range(N_NODES):
            if bandwidths[i,j]!=0:
                # i,j有边
                latencies[i,j] = math.ceil(flows[i,j]/bandwidths[i,j])
    return latencies




# ================ 第t轮实际选路 ==================

# 求第t轮各包实际延迟
# 输入：
#   packets：包
#   PI: 第t轮实际选路前驱节点矩阵
#   actualLinkLatencies：第t轮实际选路造成的各边延迟
# 返回：
#   packetsActualLatencies：各包第t轮实际延迟
def getPacketsActualLatencies(packets, PI, actualLinkLatencies):
    packetsActualLatencies = np.zeros(len(packets), int)

    for i in range(len(packets)):
        packet = packets[i]
        packetsActualLatencies[i] = getPacketLatency(packet, PI, actualLinkLatencies)

    return packetsActualLatencies


# 由当前轮选路、各边延迟，求packet延迟
# 输入：
#   packet：待求延迟的包
#   PI：当前轮选路前驱节点矩阵
#   linkLatencies：当前轮选路造成的各边延迟
# 输出：
#   packetLatency：packet延迟
def getPacketLatency(packet, PI, linkLatencies):
    src = packet[0]
    dst = packet[1]
    cur = dst
    pre = PI[src, dst]
    packetLatency = 0
    while pre != src:
        packetLatency += linkLatencies[pre, cur]
        cur = pre
        pre = PI[src, pre]
    packetLatency += linkLatencies[pre, cur]
    return packetLatency



#============================ 第t轮最优选路 ========================

# 求第t轮各包最优延迟
# 输入：
#   packets：所有包
#   PI：第t轮实际选路前驱节点矩阵
#   bandwidths：各边带宽
# 返回：
#   packetsOptLatencies：各包第t轮最优延迟
def getPacketsOptLatencies(packets, PI, bandwidths, packetsActualLatencies):
    packetsOptLatencies = np.zeros(len(packets), int)

    for i in range(len(packets)):
        packetsOptLatencies[i] = getPacketOptLatency(packets, i, PI, bandwidths, packetsActualLatencies[i])

    return packetsOptLatencies


# 求packet_i的最优延迟
# 输入：
#   packets：所有包
#   iPacket：第i个包编号
#   PI：第t轮实际选路前驱节点矩阵
#   bandwidths：各边带宽
# 返回：
#   packet_i的最优延迟
def getPacketOptLatency(packets, iPacket, PI, bandwidths, packetActualLatency):
    # 求tmpFlows：packets[iPacket]作最优选路时，各边的流量
    # 相当于实际选路的flows_minusI，然后各边再+1流量，表i选该边增加的流量

    # 先将各边+1流量加上
    tmpFlows = np.full((N_NODES, N_NODES), 1, int)
    # 再加上实际选路的flows_minusI
    for i in range(len(packets)):
        packet = packets[i]
        if(i==iPacket):
            packet_i = packet
            continue
        src = packet[0]
        mid = packet[1]
        pre = PI[src,mid]
        # mesh保证所有节点对一定连通
        while(pre!=src):
            tmpFlows[pre, mid] += 1
            mid = pre
            pre = PI[src, mid]
        tmpFlows[pre,mid] += 1

    # 由tmpFlows，求各边tmpLatencies
    tmpLatencies = np.full((N_NODES,N_NODES), MAX_LANRTENCY, int)
    for i in range(N_NODES):
        for j in range(N_NODES):
            if bandwidths[i,j]!=0:
                # i,j有边
                tmpLatencies[i,j] = math.ceil(tmpFlows[i,j]/bandwidths[i,j])

    # 由tmpLatencies，求packet_i的最优延迟
    tmpD, tmpPI = getShortestPaths(tmpLatencies)
    tmpLinkLatencies = getLatencies(packets, tmpPI, bandwidths)
    tmpPacketLatency = getPacketLatency(packet_i, tmpPI, tmpLinkLatencies)
    return min(tmpPacketLatency, packetActualLatency)



#=============================== 改进选路依据--各边延迟 ======================

# t-1轮的高延迟，导致t轮各包倾向避开高延迟的边，继而导致不均衡，减小高延迟以改进
# 输入：
#   actualLinkLatencies：t-1轮各边延迟
# 输出：
#   latencies：改进后的延迟
def getModifiedLatencies(orginalLinkLatencies):
    latencies = orginalLinkLatencies.copy()

    # 求小于MAX_LATENCY的延迟的均值
    selectedLatencies = []
    for i in range(latencies.shape[0]):
        for j in range(latencies.shape[1]):
            if latencies[i, j] < MAX_LANRTENCY:
                selectedLatencies.append(latencies[i, j])
    selectedLatencies = np.array(selectedLatencies)
    selectedLatenciesMean = np.mean(selectedLatencies)

    # 将小于MAX_LATENCY，且大于均值的延迟，降到均值
    for i in range(latencies.shape[0]):
        for j in range(latencies.shape[1]):
            if latencies[i, j] < MAX_LANRTENCY and latencies[i, j] >= selectedLatenciesMean:
                latencies[i, j] = selectedLatenciesMean

    return latencies
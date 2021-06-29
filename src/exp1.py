import numpy as np
import matplotlib.pyplot as plt
import os

import src.core as core

# ============== module vars =============

# 实验
N_TURNS = 100

# 画图
PERCENTAGE_COLOR = "crimson"
PERCENTAGE_IMPROVED_COLOR = "royalblue"

ACTUAL_COST_COLOR = "red"
ACTUAL_COST_IMPROVED_COLOR = "orangered"
OPT_COST_COLOR = "limegreen"
OPT_COST_IMPROVED_COLOR = "dodgerblue"

NONFEATURE_ORIGIN_LINESTYLE = "solid"
NONFEATURE_IMPROVED_LINESTYLE = "dashed"
FEATURE_LINESTYLE = "dotted"

NONFEATURE_ALPHA = 0.7
FEATURE_ALPHA = 1

# 文件
PATH = os.path.join(os.path.dirname(__file__), "..", "res")
FILE_EXT = ".txt"
EXP1_RES1_FNAME = os.path.join(PATH, "exp1-originalRes" + FILE_EXT)
EXP1_RES2_FNAME = os.path.join(PATH, "exp1-improvedRes" + FILE_EXT)
EXP1_ANALYSIS_FNAME = os.path.join(PATH, "exp1-resAnalysis" + FILE_EXT)

RES_NAMES = ["ineqPerCentages", "allPacketsAvgActualLatencies", "allPacketsAvgOptLatencies"]

FIG_PATH = os.path.join(os.path.dirname(__file__), "..", "fig")
EXP1_FIG1_FNAME = os.path.join(FIG_PATH, "exp1-percentage")
EXP1_FIG2_FNAME = os.path.join(FIG_PATH, "exp1-cost")


# ======================= exp1 =====================

# 对比original、improved的percentage、actual cost、opt cost
# 输入：
#   nTurns：实验nTurns轮
def exp1(nTurns=N_TURNS):
    # 初始图
    edges = core.genMesh()
    bandwidths = core.getBandwidths(edges, 2, 4)

    # 初始latencies
    latencies = np.full((core.N_NODES, core.N_NODES), core.MAX_LANRTENCY, int)
    for node in range(core.N_NODES):
        for neighbor in edges[node]:
            latencies[node, neighbor] = 0
    # 初始改进后的延迟
    modifiedLatencies = core.getModifiedLatencies(latencies)

    # 各轮数据
    ineqPerCentages = [0] * nTurns
    allPacketsAvgActualLatencies = [0] * nTurns
    allPacketsAvgOptLatencies = [0] * nTurns
    # 改进延迟后的数据
    ineqPerCentagesImproved = [0] * nTurns
    allPacketsAvgActualLatenciesImproved = [0] * nTurns
    allPacketsAvgOptLatenciesImproved = [0] * nTurns

    # 各轮选路，及数据统计
    print("round ", end='')
    for turn in range(nTurns):
        print(f"{turn}", end=', ')
        packets = core.genPackets(core.N_PACKETS)

        # 本轮改进前的选路
        # 求本轮各边延迟、各包实际/最优延迟
        latencies, packetsActualLatencies, packetsOptLatencies = getPacketsLatencies(latencies, packets, bandwidths)
        calStatistics(turn, packetsActualLatencies, packetsOptLatencies,
                      ineqPerCentages, allPacketsAvgActualLatencies, allPacketsAvgOptLatencies)

        # 改进后
        modifiedLatencies, packetsActualLatenciesImproved, packetsOptLatenciesImproved = getPacketsLatencies(
            modifiedLatencies, packets, bandwidths)
        calStatistics(turn, packetsActualLatenciesImproved, packetsOptLatenciesImproved,
                      ineqPerCentagesImproved, allPacketsAvgActualLatenciesImproved, allPacketsAvgOptLatenciesImproved)
        # 本轮改进后延迟
        modifiedLatencies = core.getModifiedLatencies(latencies)

    print()

    # 将结果存到文件
    save(ineqPerCentages, allPacketsAvgActualLatencies, allPacketsAvgOptLatencies, RES_NAMES, EXP1_RES1_FNAME)
    save(ineqPerCentagesImproved, allPacketsAvgActualLatenciesImproved, allPacketsAvgOptLatenciesImproved,
         RES_NAMES, EXP1_RES2_FNAME)


# 分析结果，并作图
def analyzeExp1Res(nTurns=N_TURNS):
    ineqPerCentages, allPacketsAvgActualLatencies, allPacketsAvgOptLatencies = read(EXP1_RES1_FNAME, RES_NAMES)
    ineqPerCentagesImproved, allPacketsAvgActualLatenciesImproved, allPacketsAvgOptLatenciesImproved = read(
        EXP1_RES2_FNAME, RES_NAMES)

    analysis = ""
    resSeparator = "------------------------------------------------------------------\n"

    # 先分析改进前后的ineqPerCentages
    ineqPerCentagesMean = np.mean(ineqPerCentages)
    ineqPerCentagesImprovedMean = np.mean(ineqPerCentagesImproved)

    analysis += resSeparator \
                + f"ineqPerCentages mean of all turns:  {ineqPerCentagesMean}\n" \
                + f"ineqPerCentages mean of all turns:  {ineqPerCentagesImprovedMean}\n" \
                + resSeparator \
                + '\n'

    turns = list(range(1, nTurns + 1))

    plt.figure(figsize=(6.4,5.5), dpi=300)
    ax = plt.subplot(111)
    ax.set_title("Proportion of packets with non-minimized costs in each round")
    ax.set_xlabel("Round")
    ax.set_ylabel("Proportion")
    # 改进前
    ax.plot(turns, ineqPerCentages, linestyle=NONFEATURE_ORIGIN_LINESTYLE, color=PERCENTAGE_COLOR,
             alpha=NONFEATURE_ALPHA, label="Original")
    ax.axhline(y=ineqPerCentagesMean, linestyle=FEATURE_LINESTYLE, color=PERCENTAGE_COLOR, alpha=FEATURE_ALPHA,
                label="Original mean")
    # 改进后
    ax.plot(turns, ineqPerCentagesImproved, linestyle=NONFEATURE_IMPROVED_LINESTYLE, color=PERCENTAGE_IMPROVED_COLOR,
             alpha=NONFEATURE_ALPHA, label="Improved")
    ax.axhline(y=ineqPerCentagesImprovedMean, linestyle=FEATURE_LINESTYLE, color=PERCENTAGE_IMPROVED_COLOR,
                alpha=FEATURE_ALPHA, label="Improved mean")

    # legend设在坐标图下
    ax.legend(ncol=2, bbox_to_anchor=(0.78, -0.1))
    plt.tight_layout()
    plt.savefig(EXP1_FIG1_FNAME)

    # 分析cost
    allPacketsAvgActualLatenciesMean, allPacketsAvgOptLatenciesMean = np.mean(allPacketsAvgActualLatencies), np.mean(
        allPacketsAvgOptLatencies)
    allPacketsAvgActualLatenciesImprovedMean, allPacketsAvgOptLatenciesImprovedMean = np.mean(
        allPacketsAvgActualLatenciesImproved), np.mean(allPacketsAvgOptLatenciesImproved)

    analysis += resSeparator \
                + f"allPacketsAvgActualLatencies mean of all turns:  {allPacketsAvgActualLatenciesMean}\n" \
                + f"allPacketsAvgOptLatencies mean of all turns:  {allPacketsAvgOptLatenciesMean}\n" \
                + resSeparator \
                + f"allPacketsAvgActualLatenciesImproved mean of all turns:  {allPacketsAvgActualLatenciesImprovedMean}\n" \
                + f"allPacketsAvgOptLatenciesImproved mean of all turns:  {allPacketsAvgOptLatenciesImprovedMean}\n" \
                + resSeparator \
                + '\n'

    plt.figure(figsize=(6.4,5.8), dpi=300)
    ax = plt.subplot(111)
    ax.set_title("Average cost per packet in each round")
    ax.set_xlabel("Round")
    ax.set_ylabel("Cost")

    # actual cost
    # 改进前
    ax.plot(turns, allPacketsAvgActualLatencies, linestyle=NONFEATURE_ORIGIN_LINESTYLE, color=ACTUAL_COST_COLOR,
             alpha=NONFEATURE_ALPHA, label="Original actual")
    ax.axhline(y=allPacketsAvgActualLatenciesMean, linestyle=FEATURE_LINESTYLE, color=ACTUAL_COST_COLOR,
                alpha=FEATURE_ALPHA, label="Original actual mean")
    # 改进后
    ax.plot(turns, allPacketsAvgActualLatenciesImproved, linestyle=NONFEATURE_IMPROVED_LINESTYLE,
             color=ACTUAL_COST_IMPROVED_COLOR,
             alpha=NONFEATURE_ALPHA, label="Improved actual")
    ax.axhline(y=allPacketsAvgActualLatenciesImprovedMean, linestyle=FEATURE_LINESTYLE,
                color=ACTUAL_COST_IMPROVED_COLOR,
                alpha=FEATURE_ALPHA, label="Improved actual mean")

    # opt cost
    # 改进前
    ax.plot(turns, allPacketsAvgOptLatencies, linestyle=NONFEATURE_ORIGIN_LINESTYLE, color=OPT_COST_COLOR,
             alpha=NONFEATURE_ALPHA, label="Original optimal")
    ax.axhline(y=allPacketsAvgOptLatenciesMean, linestyle=FEATURE_LINESTYLE, color=OPT_COST_COLOR, alpha=FEATURE_ALPHA,
                label="Original optimal mean")
    # 改进后
    ax.plot(turns, allPacketsAvgOptLatenciesImproved, linestyle=NONFEATURE_IMPROVED_LINESTYLE,
             color=OPT_COST_IMPROVED_COLOR,
             alpha=NONFEATURE_ALPHA, label="Improved optimal")
    ax.axhline(y=allPacketsAvgOptLatenciesImprovedMean, linestyle=FEATURE_LINESTYLE, color=OPT_COST_IMPROVED_COLOR,
                alpha=FEATURE_ALPHA, label="Improved optimal mean")

    ax.legend(ncol=2, bbox_to_anchor=(0.88, -0.1))
    plt.tight_layout()
    plt.savefig(EXP1_FIG2_FNAME)

    # 打印分析，并保存到文件
    print(analysis)
    with open(EXP1_ANALYSIS_FNAME, 'w') as file:
        file.write(analysis)
    print(f"Figures location: {FIG_PATH}")
    print(f"Analysis location: {EXP1_ANALYSIS_FNAME}")


# ================== 子函数 =======================

# 求本轮各包实际、最优延迟
# 输入：
#   lastLinkLatencies：上一轮各边延迟
#   packets
#   bandwidths
# 输出：
#   curLinklatencies：本轮各边延迟
#   packetsActualLatencies, packetsOptLatencies：本轮各包实际、最优延迟
def getPacketsLatencies(lastLinkLatencies, packets, bandwidths):
    # 这一轮的实际选路
    D, PI = core.getShortestPaths(lastLinkLatencies)
    # 这一轮选路造成的延迟
    curLinklatencies = core.getLatencies(packets, PI, bandwidths)

    # 这一轮各包实际、最优延迟
    packetsActualLatencies = core.getPacketsActualLatencies(packets, PI, curLinklatencies)
    packetsOptLatencies = core.getPacketsOptLatencies(packets, PI, bandwidths, packetsActualLatencies)

    return curLinklatencies, packetsActualLatencies, packetsOptLatencies


# 由各包实际、最优延迟，统计本轮指标
# 输入：
#   turn：本轮id
#   packetsActualLatencies, packetsOptLatencies：本轮各包实际、最优延迟
#   ineqPerCentages, allPacketsAvgActualLatencies, allPacketsAvgOptLatencies：要统计的指标
def calStatistics(turn, packetsActualLatencies, packetsOptLatencies, ineqPerCentages, allPacketsAvgActualLatencies,
                  allPacketsAvgOptLatencies):
    # ineq占比
    cnt = 0
    nPackets = len(packetsActualLatencies)
    for i in range(nPackets):
        if packetsActualLatencies[i] > packetsOptLatencies[i]:
            cnt += 1
        elif packetsActualLatencies[i] < packetsOptLatencies[i]:
            print("\nError: actual latency < opt latency")
            exit()
    ineqPerCentages[turn] = cnt / nPackets
    # 所有包延迟均值
    allPacketsAvgActualLatencies[turn] = np.mean(packetsActualLatencies)
    allPacketsAvgOptLatencies[turn] = np.mean(packetsOptLatencies)


# 将实验结果保存到文件
# 输入：
#   ineqPerCentages, allPacketsAvgActualLatencies, allPacketsAvgOptLatencies：实验结果
#   fileName：文件名
def save(ineqPerCentages, allPacketsAvgActualLatencies, allPacketsAvgOptLatencies, resNames, fileName):
    sep = ','
    lines = []
    for res in [ineqPerCentages, allPacketsAvgActualLatencies, allPacketsAvgOptLatencies]:
        line = [str(elem) for elem in res]
        lines.append(sep.join(line) + '\n')

    idLine = 0
    for resName in resNames:
        lines.insert(idLine, resName + '\n')
        idLine += 2

    with open(fileName, 'w') as file:
        file.writelines(lines)


# 将实验结果从文件读到列表
# 输入：
#   resFileName
# 输出：
#   results：结果列表
def read(resFileName, resNames):
    results = [0] * len(resNames)

    with open(resFileName, "r") as file:
        while True:
            resName = file.readline().strip()
            try:
                idRes = resNames.index(resName)
            except ValueError:
                break

            res = file.readline().strip().split(",")
            results[idRes] = [float(elem) for elem in res]

    return results


if __name__ == "__main__":
    nTurns = 100
    # exp1(nTurns)
    analyzeExp1Res(nTurns)
import numpy as np
import matplotlib.pyplot as plt
import os

import src.core as core
import src.exp1 as exp1

#========================= module vars =======================

# 实验
N_PACKETS_MIN = 1
N_PACKETS_MAX = 100
N_PACKETS_STEP = 1

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
PATH = exp1.PATH
FILE_EXT = exp1.FILE_EXT
EXP2_RES1_FNAME = os.path.join(PATH, "exp2-originalRes"+FILE_EXT)
EXP2_RES2_FNAME = os.path.join(PATH, "exp2-improvedRes"+FILE_EXT)
EXP2_ANALYSIS_FNAME = os.path.join(PATH, "exp2-resAnalysis"+FILE_EXT)

RES_NAMES = ["ineqPerCentagePerNPackets", "actualLatencyPerNPackets", "optLatencyPerNPackets"]

FIG_PATH = exp1.FIG_PATH
EXP2_FIG1_FNAME = os.path.join(FIG_PATH, "exp2-percentage")
EXP2_FIG2_FNAME = os.path.join(FIG_PATH, "exp2-cost")



#=========================== exp 2 ==================================

# 包种类数作自变量，探究percentage、cost和包种类数的关系
def exp2(nPacketsMin=N_PACKETS_MIN, nPacketsMax=N_PACKETS_MAX, nPacketsStep=N_PACKETS_STEP, nTurns=N_TURNS):
    # 改进前
    ineqPerCentagePerNPackets = []
    actualLatencyPerNPackets = []
    optLatencyPerNPackets = []
    # 改进后
    ineqPerCentageImprovedPerNPackets = []
    actualLatencyImprovedPerNPackets = []
    optLatencyImprovedPerNPackets = []

    for nPackets in range(nPacketsMin, nPacketsMax+1, nPacketsStep):
        print(f"num of packet types = {nPackets}: ", end='')
        ineqPerCentages, allPacketsAvgActualLatencies, allPacketsAvgOptLatencies,\
        ineqPerCentagesImproved, allPacketsAvgActualLatenciesImproved, allPacketsAvgOptLatenciesImproved = exp2PerNPackets(nPackets, nTurns)
        # 改进前
        ineqPerCentagePerNPackets.append(np.mean(ineqPerCentages))
        actualLatencyPerNPackets.append(np.mean(allPacketsAvgActualLatencies))
        optLatencyPerNPackets.append(np.mean(allPacketsAvgOptLatencies))
        # 改进后
        ineqPerCentageImprovedPerNPackets.append(np.mean(ineqPerCentagesImproved))
        actualLatencyImprovedPerNPackets.append(np.mean(allPacketsAvgActualLatenciesImproved))
        optLatencyImprovedPerNPackets.append(np.mean(allPacketsAvgOptLatenciesImproved))

    # 保存到文件
    exp1.save(ineqPerCentagePerNPackets, actualLatencyPerNPackets, optLatencyPerNPackets, RES_NAMES, EXP2_RES1_FNAME)
    exp1.save(ineqPerCentageImprovedPerNPackets, actualLatencyImprovedPerNPackets, optLatencyImprovedPerNPackets, RES_NAMES, EXP2_RES2_FNAME)


# 分析结果，并作图
def analyzeExp2Res(nPacketsMin=N_PACKETS_MIN, nPacketsMax=N_PACKETS_MAX, nPacketsStep=N_PACKETS_STEP):
    ineqPerCentagePerNPackets, actualLatencyPerNPackets, optLatencyPerNPackets = exp1.read(EXP2_RES1_FNAME, RES_NAMES)
    ineqPerCentageImprovedPerNPackets, actualLatencyImprovedPerNPackets, optLatencyImprovedPerNPackets = exp1.read(EXP2_RES2_FNAME, RES_NAMES)

    analysis = ""
    resSeparator = "------------------------------------------------------------------\n"

    # 先分析改进前后的ineqPerCentagePerNPackets
    ineqPerCentagePerNPacketsMean = np.mean(ineqPerCentagePerNPackets)
    ineqPerCentageImprovedPerNPacketsMean = np.mean(ineqPerCentageImprovedPerNPackets)

    analysis += resSeparator \
                + f"ineqPerCentagePerPackets mean of all nPackets:  {ineqPerCentagePerNPacketsMean}\n" \
                + f"improvedIneqPerCentagePerPackets mean of all nPackets:  {ineqPerCentageImprovedPerNPacketsMean}\n" \
                + resSeparator \
                + '\n'

    nPackets = list(range(nPacketsMin, nPacketsMax + 1, nPacketsStep))

    plt.figure(figsize=(6.4,5.5), dpi=300)
    ax = plt.subplot(111)
    ax.set_title("Proportion of packets with non-minimized costs\nfor each number of packet groups")
    ax.set_xlabel("Number of packet types")
    ax.set_ylabel("Proportion")
    # 改进前
    ax.plot(nPackets, ineqPerCentagePerNPackets, linestyle=NONFEATURE_ORIGIN_LINESTYLE, color=PERCENTAGE_COLOR,
             alpha=NONFEATURE_ALPHA, label="Original")
    ax.axhline(y=ineqPerCentagePerNPacketsMean, linestyle=FEATURE_LINESTYLE, color=PERCENTAGE_COLOR, alpha=FEATURE_ALPHA,
                label="Original mean")
    # 改进后
    ax.plot(nPackets, ineqPerCentageImprovedPerNPackets, linestyle=NONFEATURE_IMPROVED_LINESTYLE, color=PERCENTAGE_IMPROVED_COLOR,
             alpha=NONFEATURE_ALPHA, label="Improved")
    ax.axhline(y=ineqPerCentageImprovedPerNPacketsMean, linestyle=FEATURE_LINESTYLE, color=PERCENTAGE_IMPROVED_COLOR,
                alpha=FEATURE_ALPHA, label="Improved mean")

    # legend设在坐标图下
    ax.legend(ncol=2, bbox_to_anchor=(0.8, -0.15))
    plt.tight_layout()
    plt.savefig(EXP2_FIG1_FNAME)

    # 分析cost
    maxPower = 1
    # actual cost
    fitFuncActualLatencyPerNPackets = np.poly1d(np.polyfit(nPackets, actualLatencyPerNPackets, maxPower))
    fitFuncActualLatencyImprovedPerNPackets = np.poly1d(np.polyfit(nPackets, actualLatencyImprovedPerNPackets, maxPower))
    # opt cost
    fitFuncOptLatencyPerNPackets = np.poly1d(np.polyfit(nPackets, optLatencyPerNPackets, maxPower))
    fitFuncOptLatencyImprovedPerNPackets = np.poly1d(np.polyfit(nPackets, optLatencyImprovedPerNPackets, maxPower))

    analysis += resSeparator \
                + f"Fit function with maxpower {maxPower} of actualLatenciesPerNPackets:  {fitFuncActualLatencyPerNPackets}\n" \
                + f"Fit function with maxpower {maxPower} of optLatenciesPerNPackets:  {fitFuncOptLatencyPerNPackets}\n" \
                + resSeparator \
                + f"Fit function with maxpower {maxPower} of actualLatenciesImprovedPerNPackets:  {fitFuncActualLatencyImprovedPerNPackets}\n" \
                + f"Fit function with maxpower {maxPower} of optLatenciesImprovedPerNPackets:  {fitFuncOptLatencyImprovedPerNPackets}\n" \
                + resSeparator \
                + '\n'

    plt.figure(figsize=(6.4, 5.8), dpi=300)
    ax = plt.subplot(111)
    ax.set_title("Average cost per packet \nfor each number of packet groups")
    ax.set_xlabel("Number of packet types")
    ax.set_ylabel("Cost")

    # actual cost
    # 改进前
    ax.plot(nPackets, actualLatencyPerNPackets, linestyle=NONFEATURE_ORIGIN_LINESTYLE, color=ACTUAL_COST_COLOR,
            alpha=NONFEATURE_ALPHA, label="Original actual")
    ax.plot(nPackets, fitFuncActualLatencyPerNPackets(nPackets), linestyle=FEATURE_LINESTYLE, color=ACTUAL_COST_COLOR,
               alpha=FEATURE_ALPHA, label="Original actual fit")
    # 改进后
    ax.plot(nPackets, actualLatencyImprovedPerNPackets, linestyle=NONFEATURE_IMPROVED_LINESTYLE,
            color=ACTUAL_COST_IMPROVED_COLOR,
            alpha=NONFEATURE_ALPHA, label="Improved actual")
    ax.plot(nPackets, fitFuncActualLatencyImprovedPerNPackets(nPackets), linestyle=FEATURE_LINESTYLE,
               color=ACTUAL_COST_IMPROVED_COLOR,
               alpha=FEATURE_ALPHA, label="Improved actual fit")

    # opt cost
    # 改进前
    ax.plot(nPackets, optLatencyPerNPackets, linestyle=NONFEATURE_ORIGIN_LINESTYLE, color=OPT_COST_COLOR,
            alpha=NONFEATURE_ALPHA, label="Original optimal")
    ax.plot(nPackets, fitFuncOptLatencyPerNPackets(nPackets), linestyle=FEATURE_LINESTYLE, color=OPT_COST_COLOR, alpha=FEATURE_ALPHA,
               label="Original optimal fit")
    # 改进后
    ax.plot(nPackets, optLatencyImprovedPerNPackets, linestyle=NONFEATURE_IMPROVED_LINESTYLE,
            color=OPT_COST_IMPROVED_COLOR,
            alpha=NONFEATURE_ALPHA, label="Improved optimal")
    ax.plot(nPackets, fitFuncOptLatencyImprovedPerNPackets(nPackets), linestyle=FEATURE_LINESTYLE, color=OPT_COST_IMPROVED_COLOR,
               alpha=FEATURE_ALPHA, label="Improved optimal fit")

    ax.legend(ncol=2, bbox_to_anchor=(0.88, -0.1))
    plt.tight_layout()
    plt.savefig(EXP2_FIG2_FNAME)

    # 打印分析，并保存到文件
    print(analysis)
    with open(EXP2_ANALYSIS_FNAME, 'w') as file:
        file.write(analysis)
    print(f"Figures location: {FIG_PATH}")
    print(f"Analysis location: {EXP2_ANALYSIS_FNAME}")


#================================ 子函数 ======================================

# exp2每个nPackets的实验，基于exp1
# 输入：
#   nPackets：当前包种类数
#   nTurns：重nTurns轮取平均值
def exp2PerNPackets(nPackets, nTurns):
    # 初始图
    edges = core.genMesh()
    bandwidths = core.getBandwidths(edges, 2, 4)

    # 初始latencies
    latencies = np.full((core.N_NODES,core.N_NODES), core.MAX_LANRTENCY, int)
    for node in range(core.N_NODES):
        for neighbor in edges[node]:
            latencies[node,neighbor] = 0
    # 初始改进后的延迟
    modifiedLatencies = core.getModifiedLatencies(latencies)

    # 各轮数据
    ineqPerCentages = [0]*nTurns
    allPacketsAvgActualLatencies = [0]*nTurns
    allPacketsAvgOptLatencies = [0]*nTurns
    # 改进延迟后的数据
    ineqPerCentagesImproved = [0] * nTurns
    allPacketsAvgActualLatenciesImproved = [0] * nTurns
    allPacketsAvgOptLatenciesImproved = [0] * nTurns

    # 各轮选路，及数据统计
    print("turn ", end='')
    for turn in range(nTurns):
        print(f"{turn}", end=', ')
        packets = core.genPackets(nPackets)

        # 本轮改进前的选路
        # 求本轮各边延迟、各包实际/最优延迟
        latencies, packetsActualLatencies, packetsOptLatencies = exp1.getPacketsLatencies(latencies, packets, bandwidths)
        exp1.calStatistics(turn, packetsActualLatencies, packetsOptLatencies,
                      ineqPerCentages, allPacketsAvgActualLatencies, allPacketsAvgOptLatencies)

        # 改进后
        modifiedLatencies, packetsActualLatenciesImproved, packetsOptLatenciesImproved = exp1.getPacketsLatencies(modifiedLatencies, packets, bandwidths)
        exp1.calStatistics(turn, packetsActualLatenciesImproved, packetsOptLatenciesImproved,
                      ineqPerCentagesImproved, allPacketsAvgActualLatenciesImproved, allPacketsAvgOptLatenciesImproved)
        # 本轮改进后延迟
        modifiedLatencies = core.getModifiedLatencies(latencies)

    print()

    return ineqPerCentages, allPacketsAvgActualLatencies, allPacketsAvgOptLatencies,\
        ineqPerCentagesImproved, allPacketsAvgActualLatenciesImproved, allPacketsAvgOptLatenciesImproved


if __name__ == "__main__":
    nPacketsMax, nPacketsMin, nPacketsStep = 1,100,1
    nTurns = 100
    # exp2(nPacketsMax, nPacketsMin, nPacketsStep, nTurns)
    analyzeExp2Res(nPacketsMax, nPacketsMin, nPacketsStep)
import sys
import math
from operator import itemgetter

n = sys.argv[2]
eps = sys.argv[3]
minPts = sys.argv[4]

n = int(n)
eps = float(eps)
minPts = int(minPts)
FILE_NAME = sys.argv[1]
FILE_STRING = FILE_NAME

file = open(FILE_STRING, 'r')

file_contents = file.readlines()
cluster = dict()
for i in range(0, n):
    cluster[i] = []
dataset = []
unvisited = []
visited = []
noise = []
unclustered = []
for data in file_contents:
    data = data.strip('\n')
    data = data.split('\t')
    data[0] = int(data[0])
    data[1] = float(data[1])
    data[2] = float(data[2])
    dataset.append(data)

unvisited = dataset.copy()
unclustered = dataset.copy()


def DBSCAN(dataset, visited, unvisited, unclustered, cluster, noise, eps, minPts):
    cluster_number = -1

    for point in dataset:
        print('processing...')
        if point in visited:
            continue
        visited.append(point)
        unvisited.remove(point)
        N = regionQuery(dataset, point, eps)

        if N.__len__() < minPts:
            noise.append(point)
            unclustered.remove(point)
        else:
            cluster_number = cluster_number + 1
            if cluster_number >= n:
                return
            expandCluster(dataset, point, N, cluster[cluster_number], unclustered, eps, minPts, visited, unvisited)

def regionQuery(dataset, P, eps):
    ret = []
    x1 = float(P[1])
    y1 = float(P[2])
    for point in dataset:
        x2 = float(point[1])
        y2 = float(point[2])
        distance = math.sqrt((x1 - x2)*(x1 - x2) + (y1 - y2)*(y1 - y2))
        if distance <= eps:
            ret.append(point)

    return ret

def diff(first, second):
    return [item for item in first if item not in second]

def expandCluster(dataset, P, N, C, unclustered, eps, minPts, visited, unvisited):
    C.append(P)
    unclustered.remove(P)
    i = 0
    while i != N.__len__():
        point = N[i]
        if point not in visited:
            visited.append(point)
            unvisited.remove(point)
            N_ = regionQuery(dataset, point, eps)
            if N_.__len__() >= minPts:
                C.append(point)
                unclustered.remove(point)
                tempset = diff(N_, N)
                for item in tempset:
                    N.append(item)
        if point in unclustered:
            C.append(point)
            unclustered.remove(point)
        i += 1

DBSCAN(dataset, visited, unvisited, unclustered, cluster, noise, eps, minPts)
OUTPUTFILE_NAME = FILE_NAME[:-4] + '_cluster_'

for i in range(0, n):
    file = open(OUTPUTFILE_NAME + str(i) + '.txt', 'w')
    resultData = cluster[i]
    resultData.sort(key=lambda x: x[0])
    for data in resultData:
        file.write(str(data[0]))
        file.write('\n')
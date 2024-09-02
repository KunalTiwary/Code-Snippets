# def dfs_adj-list(node, adj_list, visited, result):
#     result.append(node)
#     visited.add(node)
#     for n in adj_list[node]:
#         if n not in visited:
#             result.append(node)
#             dfs_adj-list(n, adj_list, visited, result)
#     return result


# def bfs_adj-list(node, adj_list, visited, result):
#     visited.add(node)
#     result.append(node)
#     q = deque([node])
#     while q:
#         n = q.popleft()
#         for nod in adj_list[n]:
#             if nod not in visited:
#                 visited.add(node)
#                 result.append(nod)
#                 q.append(nod)
#     return result

# def dfs_grid(self, i, j, matrix, steps, ans):
#     if i < 0 or i >= len(matrix):
#         return
#     elif j < 0 or j >= len(matrix[0]):
#         return
#     elif matrix[i][j] == "+":
#         return
#     if (i == 0 or j == 0 or i == len(matrix)-1 or j == len(matrix[0])-1) and steps > 0:
#         ans["ans"] = min(ans["ans"], steps)
#     matrix[i][j] = "+"
#     self.dfs(i-1, j, matrix, steps+1, ans)
#     self.dfs(i+1, j, matrix, steps+1, ans)
#     self.dfs(i, j-1, matrix, steps+1, ans)
#     self.dfs(i, j+1, matrix, steps+1, ans)
#     matrix[i][j] = "."


# def bfs_grid(self, r, c, grid, steps, ans):
#     directions = [[0, -1], [-1, 0], [0, 1], [1, 0]]
#     q = deque([[r, c]])
#     steps = 0
#     grid[r][c] = "+"
#     while q:
#         x, y = q.popleft()
#         steps += 1
#         if (x == 0 or y == 0 or x == len(grid) - 1 or y == len(grid[0]) - 1) and (x, y) != (r, c):
#             return steps
#         for d in directions:
#             dx, dy = d
#             if x + dx >= 0 and x + dx < len(grid) and y + dy >= 0 and y + dy < len(grid[0]) and grid[x + dx][
#                 y + dy] == ".":
#                 grid[x][y] = "+"
#                 q.append([x + dx, y + dy])
#     return -1


# GRAPHS-  Topological sort occurs in a directed acyclic graph. It means, if there is an edge between u and v and u
# must occur before v in the sorting order. There is no Topological sorting possible in a cyclic graph.


# def topoSortDFS(graph):
#     stack = []
#     visited = [0] * len(graph)
# # Assuming the graph to be acyclic
#     def dfs(n, graph, stack, visited):
#         if visited[n]: return
#         visited[n] = 1
#         adjList = graph[n]
#         for a in adjList:
#             if not visited[a]:
#                 dfs(a, graph, stack, visited)
#         stack.append(n)
#
#     for i in range(len(visited)):
#         dfs(i, graph, stack, visited)
#     res = []
#     while stack:
#         res.append(stack.pop())
#     return res

# TC - O(N + E), SC- O(2N)
# def TopoSortBFS(n, graph):
#     inDegree = [0] * n
#     ans = []
#     # creating adjList and indegree
#     for i in range(len(graph)):
#         adjList = graph[i]
#         for a in adjList:
#             inDegree[a] += 1
#     queue = deque()
#     for i in range(n):
#         if inDegree[i] == 0:
#             queue.append(i)
#     while queue:
#         current = queue.popleft()
#         ans.append(current)
#         for next_course in graph[current]:
#             # removing the edge from current to next_course.
#             inDegree[next_course] -= 1
#             if inDegree[next_course] == 0:
#                 queue.append(next_course)
#     return ans if len(ans) == n else []

import heapq
from collections import deque
from copy import deepcopy


# It is used to find the shortest path to each node from a source node. It fails in negative edges and cycles(TLE)
# O(E(logV)) TC because, we are iterating over E edges and heap takes logV
# n - number of nodes, adj - adj list with each pair containing weights, s- source
# def djikstraMinheap(n, adj, s):
#     minHeap = []
#     dist = [float("inf")] * n
#     dist[s] = 0
#     heapq.heappush(minHeap, (0, s))
#     while minHeap: # O(V)
#         prevDist, node = heapq.heappop(minHeap) # O(log(v^2)) because the max number of nodes can be v^2
#         for a in adj[node]: # O(V-1)
#             nextNode, currDist = a
#             if dist[nextNode] > (prevDist + currDist):
#                 dist[nextNode] = prevDist + currDist
#                 heapq.heappush(minHeap, (prevDist + currDist, nextNode)) # O(log(v^2)) because the max number of nodes can be v^2
#     return dist
#
#
# adList = [[(1, 4), (2, 4)], [(0, 4), (2, 2)], [(0, 4), (1, 2), (3, 3), (4, 1), (5, 6)], [(2, 3), (5, 2)],
#           [(2, 1), (5, 3)], [(2, 6), (3, 2), (4, 3)]]
# print(djikstraMinheap(6, adList, 0))

# we use a minheap because in case when two distances of same node come one is higher and one is lower. There is
# a chance that it would consider the higher one first that would be more lengthy. Therefore minheap gives the smaller
# distance everytime.


# It is used to find the shortest path to each node from a source node
# n - number of nodes, adj - adj list with each pair containing weights, s- source
# def djikstraSet(n, adj, s):
#     st = set()
#     dist = [float("inf")] * n
#     dist[s] = 0
#     st.add((0, s))
#     while st:
#         prevDist, node = min(st)
#         st.remove((prevDist, node))
#         for a in adj[node]:
#             nextNode, currDist = a
#             if dist[nextNode] > (prevDist + currDist):
#                 dist[nextNode] = prevDist + currDist
#                 st.add((prevDist + currDist, nextNode))
#     return dist
#
#
# adList = [[(1, 4), (2, 4)], [(0, 4), (2, 2)], [(0, 4), (1, 2), (3, 3), (4, 1), (5, 6)], [(2, 3), (5, 2)],
#           [(2, 1), (5, 3)], [(2, 6), (3, 2), (4, 3)]]
# print(djikstraSet(6, adList, 0))
# We can omit the extra time complexity for priority queue by taking a queue in grid type problems.
# It is because moving from one element to other always takes 1 distance which is different from the weights problem
# where weights are different and we require the minimum.

# Bellman ford Algorithm - It is used to find the shortest path and it is applicable in directed graph.
# It does not work for cycles. The edges can be in any order.
# if you are given an undirected graph you can change it to directed graph by making 2 directed edges with same weights.
# First step - Relax all the edges n-1 times sequentially.
# TC- O(N*E), SC- O(N). It is greater than djikstra (O(NlogE)) but it is useful in negative cycles.
# def bellmanFord(n, edges, s):
#     dist = [float("inf") for _ in range(n)]
#     dist[s] = 0
#     for i in range(n-1):
#         for e in edges:
#             u, v, w = e[0], e[1], e[2]
#             if dist[u] < float("inf") and dist[u] + w < dist[v]:
#                 dist[v] = dist[u] + w
#     return dist
#
#
# print(bellmanFord(6, [(3,2,6), (5,3,1), (0,1,5), (1,5,-3), (1,2,-2), (3,4,-2), (2,4,3)], 0))

# def bellmanFordCheckCycle(n, edges, s):
#     dist = [float("inf") for _ in range(n)]
#     dist[s] = 0
#     for i in range(n-1):
#         for e in edges:
#             u, v, w = e[0], e[1], e[2]
#             if dist[u] < float("inf") and dist[u] + w < dist[v]:
#                 dist[v] = dist[u] + w
#     # Nth iteration to check negative cycle
#     for e in edges:
#         u, v, w = e[0], e[1], e[2]
#         if dist[u] < float("inf") and dist[u] + w < dist[v]:
#             return [-1 for _ in range(n)]
#     return dist


# Floyd Warshall Algorithm - It is helpful when you have to calculate the shortest distance to all the nodes from all
# the nodes. It is more like a brute force approach.

# def floydWarshall(matrix):
#     n = len(matrix)
#     for i in range(n):
#         for j in range(n):
#             if matrix[i][j] == -1:
#                 matrix[i][j] = float("inf")
#             if i == j:
#                 matrix[i][j] = 0
#
#     for k in range(n):
#         for i in range(n):
#             for j in range(n):
#                 matrix[i][j] = min(matrix[i][j], matrix[i][k] + matrix[k][j])
#
#     for i in range(n):
#         for j in range(n):
#             if matrix[i][j] == float("inf"):
#                 matrix[i][j] = -1


# Prim's algorithm - It is helpful in calculating the minimum spanning tree. A spanning tree contains exactly n nodes
# and n-1 edges with weights associated to it. A minimum spanning tree is the minimum sum of weights.
# def primsAlgorithm(v, adjList):
#     minHeap = []
#     heapq.heappush(minHeap, (0, 0, -1))  # weight, node, parent
#     visited = [0 for _ in range(v)]
#     paths = []
#     minSum = 0
#     while minHeap:
#         weight, node, parent = heapq.heappop(minHeap)
#         if visited[node] == 1:
#             continue
#         visited[node] = 1
#         if parent != -1:
#             minSum += weight
#             paths.append((node, parent))
#         for a in adjList[node]:
#             if not visited[a[0]]:
#                 heapq.heappush(minHeap, (a[1], a[0], node))
#     return paths, minSum
#
#
# print(primsAlgorithm(5, [[(1, 2), (2, 1)], [(0, 2), (2, 1)], [(0, 1), (1, 1), (4, 2), (3, 2)], [(2, 2), (4, 1)],
#                    [(2, 2), (3, 1)]]))

# Dis joint set (data structure) - It is used to identify whether nodes are within the same component or not in
# constant time. We can do it by rank or size. The union by size is better than union by rank. We join the lower rank
# with the upper rank because in the opposite case the graph will increase in height and we have to traverse more
# TC - O(4 aplha) [derived] which is almost constant
# class DisjointSet:
#     def __init__(self, n):
#         self.parent = [-1 for _ in range(n + 2)]
#         self.size = [1 for _ in range(n + 2)]
#         for i in range(len(self.parent)):
#             self.parent[i] = i
#
#     def findUltimateParent(self, node):
#         if node == self.parent[node]:
#             return node
#         self.parent[node] = self.findUltimateParent(self.parent[node])
#         return self.parent[node]
#
#
#     def unionBySize(self, u, v):
#         ulpU = self.findUltimateParent(u)
#         ulpV = self.findUltimateParent(v)
#         if ulpU == ulpV:
#             return
#         if self.size[ulpU] < self.size[ulpV]:
#             self.parent[ulpU] = ulpV
#             self.size[ulpV] += self.size[ulpU]
#         else:
#             self.parent[ulpV] = ulpU
#             self.size[ulpU] += self.size[ulpV]
#
#
#
# ds = DisjointSet(7)
# ds.unionBySize(1, 2)
# ds.unionBySize(2, 3)
# ds.unionBySize(4, 5)
# ds.unionBySize(6, 7)
# ds.unionBySize(5, 6)
# if ds.findUltimateParent(3) == ds.findUltimateParent(7):
#     print(True)
# else:
#     print(False)
# ds.unionBySize(3, 7)
# if ds.findUltimateParent(3) == ds.findUltimateParent(7):
#     print(True)
# else:
#     print(False)


# class DisjointSet:
#     def __init__(self, n):
#         self.parent = [-1 for _ in range(n + 2)]
#         self.size = [1 for _ in range(n + 2)]
#         for i in range(len(self.parent)):
#             self.parent[i] = i
#
#     def findUltimateParent(self, node):
#         if node == self.parent[node]:
#             return node
#         self.parent[node] = self.findUltimateParent(self.parent[node])
#         return self.parent[node]
#
#     def unionBySize(self, u, v):
#         ulpU = self.findUltimateParent(u)
#         ulpV = self.findUltimateParent(v)
#         if ulpU == ulpV:
#             return
#         if self.size[ulpU] < self.size[ulpV]:
#             self.parent[ulpU] = ulpV
#             self.size[ulpV] += self.size[ulpU]
#         else:
#             self.parent[ulpV] = ulpU
#             self.size[ulpU] += self.size[ulpV]

# Kosaraju's Algorithm - To find the number of Strongly connected components or print the number of Strongly
# connected components. It is only applicable in directed graphs.
# A SCC works is such that if there are 2 nodes (a, b) connected to each other than, there must be a way to reach from
# a to b and b to a.
# def kosarajuAlgorithm(v, adjList):
#
#     def dfs(i, stack, list, visited):
#         adjListLocal = list[i]
#         visited[i] = 1
#         for a in adjListLocal:
#             if not visited[a]:
#                 dfs(a, stack, list, visited)
#         stack.append(i)
#
#     visitedForward = [0 for _ in range(v)]
#     stack = []
#     for i, vis in enumerate(visitedForward):
#         if not vis:
#             dfs(i, stack, adjList, visitedForward)
#
#     revAdjList = [[] for _ in range(v)]
#     for i, a in enumerate(adjList):
#         for ele in a:
#             revAdjList[ele].append(i)
#     visitedBackward = [0 for _ in range(v)]
#     res = []
#     while stack:
#         element = stack.pop()
#         if visitedBackward[element]:
#             continue
#         visitedBackward[element] = 1
#         stackBackward = []
#         dfs(element, stackBackward, revAdjList, visitedBackward)
#         res.append(stackBackward.copy())
#     return res
#
# print(kosarajuAlgorithm(5, [[3, 2], [0], [1], [4], []]))

# Tarzan's algorithm - To find the bridges between components. You can count it or you can print it.
# It is possible in cyclic and acyclic graphs.
# https://www.youtube.com/watch?v=qrAub5z8FeA&list=PLgUwDviBIf0oE3gA41TKO2H5bHpPd7fzn&index=55&pp=iAQB

# Articulation Point- It is the node whose removal causes the graph to break into multiple components.




# 500 - auto, 800 - atta, 1000 - sabji, 500 - fruits, 1000 - petrol,  500-recharge

# class Solution:
#     def numOfMinutes(self, n, headID, manager, informTime):
#         adj = [[] for _ in range(n)]
#         for i, m in enumerate(manager):
#             if i != headID:
#                 adj[m].append(i)
#         q = deque()
#         time = informTime[headID]
#         q.append(headID)
#         while q:
#             l = len(q)
#             maxi = float("-inf")
#             for _ in range(l):
#                 currNode = q.popleft()
#                 for a in adj[currNode]:
#                     maxi = max(maxi, informTime[a])
#                     q.append(a)
#             time += maxi if maxi > float("-inf") else 0
#         return time
#
#
# s1 = Solution()
# print(s1.numOfMinutes(6, 2, [2,2,-1,2,2,2], [0,0,1,0,0,0]))



# def getCount(n, k, arr):
#     count = {"count": 0}
#     def helper(i, rs, bs, gs):
#         if i == len(arr):
#             if ((rs + bs) % k == gs % k) or (rs % k == (bs + gs) % k):
#                 count["count"] += 1
#         else:
#             helper(i+1, rs + arr[i], bs, gs)
#             helper(i+1, rs, bs + arr[i], gs)
#             helper(i+1, rs, bs, gs + arr[i])
#
#     helper(0, 0, 0, 0)
#     return count["count"]
#
# print(getCount(3, 10, [2,4,5]))
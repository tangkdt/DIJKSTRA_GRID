import heapq 
import random

# Creates a random nxn grid with each cell containing random weights between low and high O(N^2)
def RANDOM_GRID(n: int, low: int, high: int) -> list[list[int]]:
    A = [0] * n

    for i in range(n):
        A[i] = []
        for _ in range(n):
            w = random.randint(low, high)
            A[i].append(w)

    return A

# 2D cell tuple -> 1D vertex index O(1)
def CELL_TO_VERTEX(cell: tuple[int, int], n: int) -> int:
    i, j = cell[0], cell[1]
    return i * n + j # 2D -> 1D

# 1D vertex index -> 2D cell tuple O(1)
def VERTEX_TO_CELL(v: int, n: int) -> tuple[int, int]:
    i = v // n
    j = v % n 
    return (i, j) 

# Converts 2D GRID to a graph adj list O(N^2)
def GRID_TO_GRAPH(A: list[list]):
    G = {}

    n = len(A)

    # Neighbors are UP, DOWN, LEFT, RIGHT
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for i in range(n):
        for j in range(n):
            u = CELL_TO_VERTEX((i, j), n)
            G[u] = []

            for di, dj in directions:
                r = i + di
                c = j + dj

                # Inbounds
                if 0 <= r < n and 0 <= c < n:
                    v = CELL_TO_VERTEX((r, c), n)
                    w = A[r][c]
                    G[u].append((v, w))

    return G

# Follows PRED ptrs to create the shortest path O(V)
def CONSTRUCT_VERTEX_PATH(PRED: list[int], s: int, t: int): 
    if not PRED: return []
    
    vertex_path = []

    v = t 
    while v is not None and v != s:
        u = PRED[v]
        vertex_path.append(v)
        v = u

        # No path
        if v is None: return []
    
    vertex_path.append(s)
    vertex_path.reverse()
    
    return vertex_path

# Converts a path of vertices to the corresponding path of cell tuples O(V)
def CONSTRUCT_CELL_PATH(vertex_path: list[int], n: int):
    cell_path = []

    for v in vertex_path:
        cell = VERTEX_TO_CELL(v, n)
        cell_path.append(cell)

    return cell_path

# Returns shortest vertex path and its cost from a graph from s to t O((V+E)logV)
def DIJKSTRAS(G: dict[int, list[tuple[int, int]]], s: int, t: int): 
    V = len(G)
    DIST = V * [float('inf')] # O(V)
    PRED = V * [None] # O(V)

    DIST[s] = 0

    pq = []
    heapq.heappush(pq, (DIST[s], s))

    # O(V) * O(logV) + O(E) * O(logV) = O((V+E)logV)
    while pq:
        wuv, u = heapq.heappop(pq) # O(logV)

        # Skip stale entries (Since you cannot change priority)
        if wuv != DIST[u]: continue

        # O(E) * O(logV) = O(ElogV)
        for (v, w) in G[u]: 
            nd = DIST[u] + w

            # Tense edge
            if nd < DIST[v]:
                DIST[v] = nd # Relax
                PRED[v] = u 
                heapq.heappush(pq, (nd, v)) # O(logV)

    min_cost = DIST[t]
    min_path = CONSTRUCT_VERTEX_PATH(PRED, s, t)

    return min_cost, min_path

# Runs DIJKSTRA on an nxn grid O(N^2logN)
def DIJKSTRA_GRID(A: list[list], cell_s: tuple[int, int], cell_t: tuple[int, int]) -> tuple[int, list]:
    n = len(A)

    G = GRID_TO_GRAPH(A) # O(N^2)
    s = CELL_TO_VERTEX(cell_s, n) 
    t = CELL_TO_VERTEX(cell_t, n)

    # O((V+E)logV) where V = N^2 and E = O(N^2) (4 neighbors) -> O((N^2 + N^2) * logN^2)) = O(2N^2 * logN) = O(N^2logN)
    min_cost, min_vertex_path = DIJKSTRAS(G, s, t) 
    min_cell_path = CONSTRUCT_CELL_PATH(min_vertex_path, n) # O(V)

    return min_cost, min_cell_path
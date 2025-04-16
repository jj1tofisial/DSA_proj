def a_star(graph, start, end):
    open_set = {start}
    g_scores = {node: float('inf') for node in graph}
    g_scores[start] = 0
    f_scores = {node: float('inf') for node in graph}
    f_scores[start] = heuristic(graph[start], graph[end])
    came_from = {}

    while open_set:
        current = min(open_set, key=lambda node: f_scores[node])
        if current == end:
            path = []
            while current in came_from:
                path.insert(0, current)
                current = came_from[current]
            path.insert(0, start)
            return path

        open_set.remove(current)
        for neighbor, weight in graph[current]["edges"].items():
            tentative_g_score = g_scores[current] + weight
            if tentative_g_score < g_scores[neighbor]:
                came_from[neighbor] = current
                g_scores[neighbor] = tentative_g_score
                f_scores[neighbor] = g_scores[neighbor] + heuristic(graph[neighbor], graph[end])
                open_set.add(neighbor)
    return []

def heuristic(node1, node2):
    # Simple Euclidean distance heuristic
    return ((node1["lat"] - node2["lat"]) ** 2 + (node1["lon"] - node2["lon"]) ** 2) ** 0.5

from flask import Flask, render_template, request, jsonify
import requests
from geopy.geocoders import Nominatim
import folium
from algorithms import a_star  # Import the A* algorithm

app = Flask(__name__)

def get_coordinates(location):
    geolocator = Nominatim(user_agent="routewise_locator", timeout=10)
    loc = geolocator.geocode(location)
    return (loc.latitude, loc.longitude) if loc else None

def get_osm_data(lat, lon, radius=100000):  # Increase the radius to 100km
    url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      way(around:{radius},{lat},{lon}) ["highway"];
    );
    out body;>;
    out skel qt;
    """
    response = requests.get(url, params={'data': query})
    return response.json()

def build_graph(osm_data):
    graph = {}
    for element in osm_data["elements"]:
        if element["type"] == "node":
            node_id = element["id"]
            lat, lon = element["lat"], element["lon"]
            graph[node_id] = {"lat": lat, "lon": lon, "edges": {}}

    for element in osm_data["elements"]:
        if element["type"] == "way":
            nodes = element["nodes"]
            for i in range(len(nodes) - 1):
                node1, node2 = nodes[i], nodes[i + 1]
                if node1 in graph and node2 in graph:
                    dist = ((graph[node1]["lat"] - graph[node2]["lat"]) ** 2 +
                            (graph[node1]["lon"] - graph[node2]["lon"]) ** 2) ** 0.5
                    graph[node1]["edges"][node2] = dist
                    graph[node2]["edges"][node1] = dist
    return graph

def find_nearest_node(graph, lat, lon):
    min_dist = float('inf')
    nearest_node = None
    for node, data in graph.items():
        dist = ((data["lat"] - lat) ** 2 + (data["lon"] - lon) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            nearest_node = node
    return nearest_node

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_distance', methods=['POST'])
def find_distance():
    start_location = request.form['start']
    end_location = request.form['end']

    start_coords = get_coordinates(start_location)
    end_coords = get_coordinates(end_location)

    if not start_coords or not end_coords:
        return jsonify({'error': 'Could not find coordinates for one of the locations.'})

    start_lat, start_lon = start_coords
    end_lat, end_lon = end_coords
    osm_data = get_osm_data(start_lat, start_lon, radius=100000)  # 100km range
    
    graph = build_graph(osm_data)

    start_node = find_nearest_node(graph, start_lat, start_lon)
    end_node = find_nearest_node(graph, end_lat, end_lon)

    if not start_node or not end_node:
        return jsonify({'error': 'No valid nodes found near the locations.'})

    shortest_path = a_star(graph, start_node, end_node)  # Use A* algorithm

    # Create path coordinates
    path_coordinates = []
    for node in shortest_path:
        lat = graph[node]["lat"]
        lon = graph[node]["lon"]
        path_coordinates.append({'lat': lat, 'lon': lon})

    return jsonify({
        'start': start_location,
        'end': end_location,
        'route': path_coordinates,
    })

if __name__ == '__main__':
    app.run(debug=True)

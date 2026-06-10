import streamlit as st
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import random

st.title("🚚 Delivery ETA Simulator")
st.subheader("📍 Enter Delivery Details")
# Input
pickup = st.text_input("Enter Pickup Location", "Connaught Place, Delhi")
drop = st.text_input("Enter Drop Location", "India Gate, Delhi")

if st.button("Find Best Route"):
    with st.spinner("Finding optimal route..."):

        # Load graph
        G = ox.graph_from_place("New Delhi, India", network_type='drive')

    # Convert locations to nodes
    orig_node = ox.distance.nearest_nodes(G, *ox.geocode(pickup)[::-1])
    dest_node = ox.distance.nearest_nodes(G, *ox.geocode(drop)[::-1])

    # Add traffic
    for u, v, k, data in G.edges(keys=True, data=True):
        base_time = data['length'] / 8.33
        traffic_factor = random.uniform(1, 6)
        data['traffic_time'] = base_time * traffic_factor

    # Compute best route
    route = nx.shortest_path(G, orig_node, dest_node, weight='traffic_time')

    # Compute Distance
    def compute_distance(route):
        total = 0
        for u, v in zip(route[:-1], route[1:]):
            edge_data = G.get_edge_data(u, v)
            min_edge = min(edge_data.values(), key=lambda x: x['length'])
            total += min_edge['length']
        return total

    distance_m = compute_distance(route)


    # Compute ETA
    def compute_time(route):
        total = 0
        for u, v in zip(route[:-1], route[1:]):
            edge_data = G.get_edge_data(u, v)
            min_edge = min(edge_data.values(), key=lambda x: x['traffic_time'])
            total += min_edge['traffic_time']
        return total

    time_minutes = compute_time(route) / 60

    # Show metrics
    st.subheader("📊 Delivery Details")

    col1, col2 = st.columns(2)

    col1.metric("Estimated Time", f"{time_minutes:.1f} min")
    col2.metric("Distance", f"{distance_m/1000:.2f} km")
    
    st.subheader("🗺️ Route Visualization")
    # Plot map
    fig, ax = ox.plot_graph_route(G, route, show=False, close=False)
    st.pyplot(fig)
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import random
from data.database import Database


# Initialize services
@st.cache_resource
def init_database():
    return Database()

db = init_database()


# --- Page config ---
st.set_page_config(
    page_title="Mapa GPS - EcoSmart",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for modern styling (reusing the EcoSmart theme) ---
st.markdown("""
<style>
/* Main Header Styling */
.main-header {
    font-size: 2.8rem;
    color: #008080; /* Teal/Verde Água */
    text-align: left;
    margin-bottom: 1rem;
    font-weight: 700;
    padding-bottom: 0.5rem;
}

/* Custom Metric Card Styling */
div[data-testid="stMetric"] {
    background-color: #F0FFFF; /* Light Cyan */
    border-left: 5px solid #008080;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease-in-out;
}
div[data-testid="stMetric"]:hover {
    box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
}

/* Section Headers */
h3 {
    color: #008080;
    border-left: 5px solid #008080;
    padding-left: 10px;
    margin-top: 1.5rem;
}

/* Info Boxes in Sidebar/Main Content */
div[data-testid="stInfo"] {
    border-left: 5px solid #008080;
    background-color: #E0FFFF;
}

/* Button Styling */
.stButton>button {
    background-color: #008080;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
    transition: all 0.3s;
}
.stButton>button:hover {
    background-color: #006666;
    color: #FFFFFF;
}

</style>
""", unsafe_allow_html=True)


st.markdown('<h1 class="main-header">🗺️ Mapa GPS - Rastreamento em Tempo Real</h1>', unsafe_allow_html=True)

# --- Data Fetching ---
bins_data = db.get_all_bins()
truck_location = db.get_truck_location()

# --- Sidebar controls ---
with st.sidebar:
    st.markdown("### 🎛️ Configurações e Filtros")
    
    # Map view options
    map_style = st.selectbox(
        "Estilo do Mapa:",
        ["OpenStreetMap", "Esri World Imagery (Satellite)", "Stamen Terrain"]
    )
    
    st.markdown("---")
    st.markdown("### 🗑️ Filtro de Lixeiras")
    
    # Filter options
    show_empty = st.checkbox("🟢 Mostrar lixeiras vazias (0-40%)", value=True)
    show_medium = st.checkbox("🟡 Mostrar lixeiras médias (40-80%)", value=True)  
    show_full = st.checkbox("🔴 Mostrar lixeiras cheias (>80%)", value=True)
    
    st.markdown("---")
    st.markdown("### 🚛 Rastreamento")
    
    show_truck = st.checkbox("🚛 Mostrar caminhão", value=True)
    real_time = st.checkbox("⚡ Rastreamento em tempo real", value=True)
    
    st.markdown("---")
    
    # Quick actions in sidebar
    st.markdown("### ⚡ Ações Rápidas")
    
    if st.button("🔄 Atualizar Localização", use_container_width=True):
        with st.spinner("Atualizando..."):
            time.sleep(1)
        st.success("✅ Localização atualizada!")

    if st.button("🎯 Centrar no Caminhão", use_container_width=True):
        if truck_location:
            st.info("🎯 Mapa centralizado no caminhão")
        else:
            st.warning("⚠️ Caminhão não localizado")


# --- Main Content Area ---
col_map, col_stats = st.columns([3, 1])

with col_map:
    # --- Map Display ---
    
    # Create base map centered on São Paulo
    center_lat, center_lon = -23.5505, -46.6333
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=12,
        tiles='OpenStreetMap' if map_style == 'OpenStreetMap' else 'Esri World Imagery' if map_style == 'Esri World Imagery (Satellite)' else 'Stamen Terrain'
    )

    # Add bins to map
    for bin_item in bins_data:
        lat, lon = bin_item['coordinates']
        fill_level = bin_item['fill_level']

        # Determine color and show/hide based on filters
        if fill_level >= 80:
            color = 'red'
            icon = 'exclamation-sign'
            if not show_full:
                continue
        elif fill_level >= 40:
            color = 'orange'  
            icon = 'warning-sign'
            if not show_medium:
                continue
        else:
            color = 'green'
            icon = 'ok-sign'
            if not show_empty:
                continue

        # Create popup content
        popup_content = f"""
        <b>{bin_item['name']}</b><br>
        📍 {bin_item['location']}<br>
        📊 Nível: {fill_level}%<br>
        🗑️ Tipo: {bin_item['waste_type']}<br>
        📅 Última coleta: {bin_item.get('last_collection', 'N/A')}<br>
        🔋 Bateria: {bin_item.get('battery_level', 85)}%
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{bin_item['name']} - {fill_level}%",
            icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
        ).add_to(m)

    # Add truck location if enabled
    if show_truck and truck_location:
        truck_popup = f"""
        <b>🚛 Caminhão de Coleta</b><br>
        📍 Localização atual<br>
        🕐 Atualizado: {datetime.now().strftime('%H:%M:%S')}<br>
        ⛽ Combustível: {truck_location.get('fuel_level', 78)}%<br>
        👨‍💼 Operador: {truck_location.get('driver', 'João Silva')}
        """

        folium.Marker(
            location=truck_location['coordinates'],
            popup=folium.Popup(truck_popup, max_width=300),
            tooltip="Caminhão de Coleta",
            icon=folium.Icon(color='blue', icon='road', prefix='fa')
        ).add_to(m)

    # Display map
    st_folium(m, width=900, height=600, returned_objects=["last_object_clicked"])


with col_stats:
    # --- Statistics and Real-time Info ---
    
    # Calculate statistics
    total_bins = len(bins_data)
    full_bins = len([b for b in bins_data if b['fill_level'] >= 80])
    medium_bins = len([b for b in bins_data if 40 <= b['fill_level'] < 80])
    empty_bins = total_bins - full_bins - medium_bins
    
    st.markdown("### 📊 Resumo de Status")
    
    # Data for Pie Chart
    status_counts = {
        "Urgente (Vermelho)": full_bins,
        "Médio (Amarelo)": medium_bins,
        "Vazio (Verde)": empty_bins
    }
    status_df = pd.DataFrame(status_counts.items(), columns=['Status', 'Contagem'])
    
    # Create Pie Chart
    fig_pie = px.pie(
        status_df, 
        values='Contagem', 
        names='Status', 
        title='Proporção de Lixeiras por Status',
        color='Status',
        color_discrete_map={
            "Urgente (Vermelho)": 'red',
            "Médio (Amarelo)": 'orange',
            "Vazio (Verde)": 'green'
        }
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=300, margin=dict(t=50, b=0, l=0, r=0))
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # Use columns for a compact metric display
    stat_col1, stat_col2 = st.columns(2)
    
    with stat_col1:
        st.metric("Total Lixeiras", total_bins)
        st.metric("🟡 Médio", medium_bins)
    
    with stat_col2:
        st.metric("🔴 Urgente", full_bins, delta_color="inverse") 
        st.metric("🟢 Vazio", empty_bins, delta_color="normal")

    st.markdown("---")

    # Truck information
    if truck_location:
        st.markdown("### 🚛 Status do Caminhão")
        with st.container(border=True):
            st.markdown(f"**📍 Localização:** {truck_location['coordinates'][0]:.4f}, {truck_location['coordinates'][1]:.4f}")
            st.markdown(f"**⛽ Combustível:** {truck_location.get('fuel_level', 78)}%")
            st.markdown(f"**🏃 Velocidade:** {truck_location.get('speed', 25)} km/h")
            if real_time:
                st.success("✅ Rastreamento Ativo")
            else:
                st.warning("⏸️ Rastreamento Pausado")
    
    st.markdown("---")
    
    # Real-time updates section
    st.markdown("### ⚡ Atualizações Recentes")
    
    with st.container(border=True):
        # Recent location updates
        recent_updates = [
            "🚛 Caminhão chegou na Rua das Flores, 123",
            "🗑️ Lixeira #15 enchimento 85% - coleta necessária", 
            "✅ Coleta realizada na Av. Paulista, 456",
            "🔋 Lixeira #8 bateria em 15% - manutenção necessária",
        ]

        for update in recent_updates:
            st.markdown(f"• {update}")
            
        st.markdown(f"**🕐 Última Atualização:** {datetime.now().strftime('%H:%M:%S')}")


# --- Auto-refresh mechanism ---
# Removido o st.rerun() e a simulação de movimento.
# Se o aplicativo ainda estiver atualizando, o problema pode estar no Streamlit Cloud
# ou em um widget que está sendo atualizado constantemente.
# Mantendo o código limpo para evitar recargas desnecessárias.

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from utils.data_manager import DataManager
from utils.map_utils import MapUtils

# Configure page
st.set_page_config(
    page_title="EcoSmart GPS - Sistema de Coleta Inteligente",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data manager
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

# Main page header
st.title("🌱 EcoSmart GPS")
st.subheader("Sistema Inteligente de Coleta de Lixo para Condomínios")

# Sidebar navigation
st.sidebar.title("📊 Visão Geral do Sistema")

# Get current data
data_manager = st.session_state.data_manager
trucks_data = data_manager.get_trucks_data()
bins_data = data_manager.get_bins_data()
condominiums_data = data_manager.get_condominiums_data()

# Key metrics in sidebar
st.sidebar.metric("Caminhões Ativos", len(trucks_data[trucks_data['status'] == 'Ativo']))
st.sidebar.metric("Lixeiras Monitoradas", len(bins_data))
full_bins = len(bins_data[bins_data['fill_level'] >= 80])
st.sidebar.metric("Lixeiras Cheias (≥80%)", full_bins)
st.sidebar.metric("Condomínios Cadastrados", len(condominiums_data))

# Main map view
st.header("🗺️ Mapa de Monitoramento em Tempo Real")

col1, col2 = st.columns([3, 1])

with col1:
    # Create main monitoring map
    map_utils = MapUtils()
    main_map = map_utils.create_main_map(trucks_data, bins_data, condominiums_data)
    
    # Display map
    map_data = st_folium(main_map, width=800, height=500, key="main_map")

with col2:
    st.subheader("⚠️ Alertas Ativos")
    
    # Show alerts for full bins
    if full_bins > 0:
        st.error(f"🗑️ {full_bins} lixeiras precisam de coleta urgente!")
        
        # Show details of full bins
        full_bins_data = bins_data[bins_data['fill_level'] >= 80]
        for _, bin_row in full_bins_data.head(5).iterrows():
            st.warning(f"📍 {bin_row['condominium']} - {bin_row['fill_level']}% cheio")
    else:
        st.success("✅ Todas as lixeiras estão em níveis normais")
    
    # Show truck status
    st.subheader("🚛 Status dos Caminhões")
    for _, truck in trucks_data.iterrows():
        status_color = "🟢" if truck['status'] == 'Ativo' else "🔴"
        st.write(f"{status_color} {truck['truck_id']}: {truck['status']}")

# Recent activity section
st.header("📈 Atividade Recente")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Últimas Coletas Realizadas")
    # Show recent collections (simulated)
    recent_collections = data_manager.get_recent_collections()
    for collection in recent_collections:
        st.write(f"✅ {collection['time']} - {collection['location']} - {collection['amount']}kg coletados")

with col2:
    st.subheader("Próximas Coletas Programadas")
    # Show scheduled collections
    scheduled_collections = data_manager.get_scheduled_collections()
    for schedule in scheduled_collections:
        st.write(f"🕐 {schedule['time']} - {schedule['location']} - Estimativa: {schedule['estimated_amount']}kg")

# Auto-refresh functionality
if st.button("🔄 Atualizar Dados"):
    data_manager.update_truck_positions()
    data_manager.update_bin_levels()
    st.rerun()

# Auto-refresh every 30 seconds (in production, this would be handled differently)
st.info("💡 Os dados são atualizados automaticamente. Use o botão 'Atualizar Dados' para forçar uma atualização imediata.")

# Footer
st.divider()
st.write("© 2025 EcoSmart GPS - Sistema de Coleta Inteligente | Desenvolvido para otimizar a coleta de lixo em condomínios")

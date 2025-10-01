import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from utils.data_manager import DataManager
from utils.route_optimizer import RouteOptimizer
from utils.map_utils import MapUtils

st.set_page_config(
    page_title="Planejamento de Rotas - EcoSmart GPS",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Planejamento de Rotas Otimizadas")

# Initialize components
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

data_manager = st.session_state.data_manager
route_optimizer = RouteOptimizer()
map_utils = MapUtils()

# Get data
trucks_data = data_manager.get_trucks_data()
bins_data = data_manager.get_bins_data()
condominiums_data = data_manager.get_condominiums_data()

# Route planning section
st.header("🎯 Geração Automática de Rotas")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Parâmetros da Rota")
    
    # Route parameters
    truck_selection = st.selectbox(
        "Selecionar Caminhão",
        options=trucks_data['truck_id'].tolist(),
        help="Escolha o caminhão para o qual deseja gerar a rota"
    )
    
    min_fill_level = st.slider(
        "Nível Mínimo de Enchimento (%)",
        min_value=0,
        max_value=100,
        value=70,
        help="Incluir apenas lixeiras com nível igual ou superior ao selecionado"
    )
    
    max_stops = st.slider(
        "Máximo de Paradas",
        min_value=1,
        max_value=20,
        value=10,
        help="Número máximo de paradas na rota"
    )
    
    optimization_criteria = st.radio(
        "Critério de Otimização",
        options=["Distância Mínima", "Tempo Mínimo", "Lixeiras Mais Cheias"],
        help="Escolha o critério principal para otimizar a rota"
    )

with col2:
    st.subheader("Estatísticas da Seleção")
    
    # Filter bins based on criteria
    filtered_bins = bins_data[bins_data['fill_level'] >= min_fill_level]
    
    st.metric("Lixeiras Elegíveis", len(filtered_bins))
    st.metric("Nível Médio", f"{filtered_bins['fill_level'].mean():.1f}%" if len(filtered_bins) > 0 else "N/A")
    st.metric("Lixeiras Críticas (≥90%)", len(filtered_bins[filtered_bins['fill_level'] >= 90]))

# Generate route button
if st.button("🚀 Gerar Rota Otimizada", type="primary"):
    if len(filtered_bins) == 0:
        st.error("❌ Nenhuma lixeira atende aos critérios selecionados!")
    else:
        # Get truck position
        selected_truck = trucks_data[trucks_data['truck_id'] == truck_selection].iloc[0]
        truck_position = (selected_truck['latitude'], selected_truck['longitude'])
        
        # Generate optimized route
        with st.spinner("Gerando rota otimizada..."):
            optimized_route = route_optimizer.generate_route(
                truck_position, 
                filtered_bins, 
                max_stops, 
                optimization_criteria
            )
        
        if optimized_route:
            st.session_state.current_route = optimized_route
            st.success("✅ Rota otimizada gerada com sucesso!")
        else:
            st.error("❌ Erro ao gerar rota otimizada.")

# Display route if available
if 'current_route' in st.session_state and st.session_state.current_route:
    route_data = st.session_state.current_route
    
    st.header("📋 Rota Recomendada")
    
    # Route summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Paradas", len(route_data['stops']))
    
    with col2:
        st.metric("Distância Total", f"{route_data['total_distance']:.1f} km")
    
    with col3:
        st.metric("Tempo Estimado", f"{route_data['estimated_time']} min")
    
    with col4:
        st.metric("Coleta Estimada", f"{route_data['estimated_collection']:.0f} kg")
    
    # Map and route details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ Visualização da Rota")
        
        # Create route map
        route_map = map_utils.create_route_map(route_data, trucks_data, bins_data)
        st_folium(route_map, width=700, height=500, key="route_map")
    
    with col2:
        st.subheader("📝 Detalhes da Rota")
        
        # Display route steps
        for i, stop in enumerate(route_data['stops']):
            step_number = i + 1
            
            with st.expander(f"Parada {step_number}: {stop['condominium']}", expanded=i < 3):
                st.write(f"**Localização:** {stop['location']}")
                st.write(f"**Nível de Enchimento:** {stop['fill_level']}%")
                st.write(f"**Distância da Parada Anterior:** {stop['distance_from_previous']:.1f} km")
                st.write(f"**Tempo de Chegada Estimado:** {stop['estimated_arrival']}")
                st.write(f"**Coleta Estimada:** {stop['estimated_collection']:.0f} kg")
                
                # Priority indicator
                if stop['fill_level'] >= 90:
                    st.error("🔴 Prioridade ALTA - Lixeira quase cheia!")
                elif stop['fill_level'] >= 80:
                    st.warning("🟡 Prioridade MÉDIA")
                else:
                    st.success("🟢 Prioridade BAIXA")

# Historical routes section
st.header("📊 Histórico de Rotas")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Rotas Recentes")
    
    recent_routes = data_manager.get_recent_routes()
    for route in recent_routes:
        with st.expander(f"Rota {route['id']} - {route['date']}"):
            st.write(f"**Caminhão:** {route['truck_id']}")
            st.write(f"**Paradas:** {route['stops_count']}")
            st.write(f"**Distância:** {route['distance']} km")
            st.write(f"**Tempo:** {route['duration']} min")
            st.write(f"**Status:** {route['status']}")

with col2:
    st.subheader("Métricas de Performance")
    
    # Route efficiency metrics
    efficiency_metrics = data_manager.get_route_efficiency_metrics()
    
    st.metric("Distância Média por Rota", f"{efficiency_metrics['avg_distance']:.1f} km")
    st.metric("Tempo Médio por Rota", f"{efficiency_metrics['avg_duration']:.0f} min")
    st.metric("Eficiência Média", f"{efficiency_metrics['avg_efficiency']:.1f}%")
    st.metric("Taxa de Conclusão", f"{efficiency_metrics['completion_rate']:.1f}%")

# Export route functionality
if 'current_route' in st.session_state and st.session_state.current_route:
    st.header("📤 Exportar Rota")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📱 Enviar para Motorista"):
            st.success("Rota enviada para o aplicativo do motorista!")
    
    with col2:
        if st.button("📧 Enviar por Email"):
            st.success("Rota enviada por email!")
    
    with col3:
        if st.button("📄 Baixar PDF"):
            st.success("PDF da rota gerado!")

# Tips and recommendations
with st.expander("💡 Dicas para Otimização de Rotas"):
    st.markdown("""
    **Para obter as melhores rotas:**
    
    1. **Lixeiras com 80%+ de enchimento** devem ter prioridade
    2. **Considere o trânsito** nos horários de pico
    3. **Agrupe coletas próximas** para reduzir distâncias
    4. **Monitore o combustível** do caminhão
    5. **Verifique a capacidade** restante do caminhão
    6. **Considere condições climáticas** adversas
    
    **Critérios de Otimização:**
    - **Distância Mínima:** Reduz combustível e tempo
    - **Tempo Mínimo:** Considera trânsito e acessibilidade
    - **Lixeiras Mais Cheias:** Prioriza urgência da coleta
    """)

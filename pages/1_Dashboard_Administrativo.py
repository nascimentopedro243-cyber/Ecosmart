import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
from data.database import Database


# Initialize database
@st.cache_resource
def init_database():
    return Database()


db = init_database()


# --- Page config ---
st.set_page_config(
    page_title="Dashboard Administrativo - EcoSmart",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for modern styling ---
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

/* Customizing the Separator */
hr {
    margin-top: 1rem;
    margin-bottom: 1rem;
    border-top: 2px solid #E0FFFF;
}

/* Section Headers */
h3 {
    color: #008080;
    border-left: 5px solid #008080;
    padding-left: 10px;
    margin-top: 1.5rem;
}

/* Sidebar Styling */
.st-emotion-cache-vk3ypu { /* Target Streamlit's sidebar */
    background-color: #E0FFFF; /* Light Cyan */
}

/* Table Styling */
.stDataFrame {
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

</style>
""", unsafe_allow_html=True)


st.markdown('<h1 class="main-header">📊 Dashboard Administrativo EcoSmart</h1>', unsafe_allow_html=True)

# Auto-refresh functionality
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=True)
if auto_refresh:
    # time.sleep(1) # Removed to avoid initial delay
    pass

# Sidebar filters
st.sidebar.markdown("### 🔧 Filtros")
selected_region = st.sidebar.selectbox(
    "Região:",
    ["Todas", "Centro", "Norte", "Sul", "Leste", "Oeste"]
)

selected_period = st.sidebar.selectbox(
    "Período:",
    ["Hoje", "Esta Semana", "Este Mês", "Últimos 3 Meses"]
)

# --- Data Fetching (Simulated) ---
bins_data = db.get_all_bins()
total_bins = len(bins_data)
full_bins = len([b for b in bins_data if b['fill_level'] >= 80])
medium_bins = len([b for b in bins_data if 40 <= b['fill_level'] < 80])
empty_bins = total_bins - full_bins - medium_bins


# --- Main Metrics Row (Cards) ---
st.markdown("### 🔑 Métricas Chave")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🗑️ Total de Lixeiras",
        total_bins,
        delta=f"+{len([b for b in bins_data if b['status'] == 'active'])} ativas"
    )

with col2:
    st.metric(
        "🔴 Coleta Urgente",
        full_bins,
        delta=f"{round((full_bins/total_bins)*100, 1)}% do total",
        delta_color="inverse"
    )

with col3:
    st.metric(
        "🟡 Nível Médio", 
        medium_bins,
        delta=f"{round((medium_bins/total_bins)*100, 1)}% do total",
        delta_color="off"
    )

with col4:
    st.metric(
        "🟢 Vazias/Baixo",
        empty_bins,
        delta=f"{round((empty_bins/total_bins)*100, 1)}% do total",
        delta_color="normal"
    )

st.markdown("---")

# --- Tabs for Organization ---
tab_status, tab_performance = st.tabs(["Status em Tempo Real", "Indicadores de Performance"])

with tab_status:
    
    # --- Real-time status grid ---
    st.markdown("### 🗺️ Visão Geral e Alertas")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Distribuição de Status das Lixeiras")

        # Create bins status dataframe (for chart)
        bins_df = pd.DataFrame(bins_data)

        # Status distribution chart
        fig_status = px.bar(
            x=['Vazio (0-40%)', 'Médio (40-80%)', 'Cheio (80-100%)'],
            y=[empty_bins, medium_bins, full_bins],
            color=['Vazio (0-40%)', 'Médio (40-80%)', 'Cheio (80-100%)'],
            color_discrete_map={
                'Vazio (0-40%)': '#4CAF50', # Green
                'Médio (40-80%)': '#FF9800', # Orange
                'Cheio (80-100%)': '#F44336' # Red
            },
            title="Distribuição de Status das Lixeiras"
        )
        fig_status.update_layout(showlegend=False, height=350, margin=dict(t=50, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)

    with col_right:
        st.subheader("⚡ Alertas e Resumo")
        with st.container(border=True):
            # Critical alerts
            critical_bins = [b for b in bins_data if b['fill_level'] >= 90]

            if critical_bins:
                st.error(f"🚨 **{len(critical_bins)}** lixeiras críticas (>90%)")
                for bin_item in critical_bins[:3]:
                    st.markdown(f"• **{bin_item['name']}** - {bin_item['fill_level']}%")
            else:
                st.success("✅ Nenhuma lixeira em estado crítico.")

            # Maintenance alerts
            maintenance_bins = [b for b in bins_data if b['status'] == 'maintenance']
            if maintenance_bins:
                st.warning(f"🔧 **{len(maintenance_bins)}** lixeiras em manutenção")
            
            st.markdown("---")
            st.info(f"Eficiência de coleta: **87%**")
            st.success(f"Economia de combustível: **23%**")

    st.markdown("---")
    
    # --- Detailed bins table ---
    st.markdown("### 📋 Tabela Detalhada de Lixeiras")

    # Filter bins based on selection
    filtered_bins = bins_data
    if selected_region != "Todas":
        filtered_bins = [b for b in bins_data if selected_region.lower() in b['location'].lower()]

    # Create detailed table
    bins_table_data = []
    for bin_item in filtered_bins:
        status_emoji = "🔴" if bin_item['fill_level'] >= 80 else "🟡" if bin_item['fill_level'] >= 40 else "🟢"
        collection_status = "Urgente" if bin_item['fill_level'] >= 80 else "Programada" if bin_item['fill_level'] >= 40 else "Não Necessária"

        bins_table_data.append({
            "Status": status_emoji,
            "ID": bin_item['id'],
            "Nome": bin_item['name'],
            "Localização": bin_item['location'],
            "Nível (%)": bin_item['fill_level'],
            "Tipo": bin_item['waste_type'],
            "Coleta": collection_status,
            "Última Coleta": bin_item.get('last_collection', 'N/A')
        })

    if bins_table_data:
        bins_df_display = pd.DataFrame(bins_table_data)
        st.dataframe(bins_df_display, use_container_width=True, hide_index=True)


with tab_performance:
    
    # --- Performance indicators ---
    st.markdown("### 📈 Indicadores de Performance e Tendências")

    perf_col1, perf_col2 = st.columns(2)

    with perf_col1:
        # Fill level trend over time
        dates = pd.date_range(start=datetime.now()-timedelta(days=7), end=datetime.now(), periods=8)
        fill_levels = [65, 70, 75, 68, 72, 78, 73, 76]  # Simulated data

        fig_trend = px.line(
            x=dates,
            y=fill_levels,
            title="Tendência de Nível de Enchimento (7 dias)",
            labels={'x': 'Data', 'y': 'Nível Médio (%)'}
        )
        fig_trend.update_traces(line_color='#008080', mode='lines+markers')
        fig_trend.update_layout(margin=dict(t=50, b=0, l=0, r=0))
        st.plotly_chart(fig_trend, use_container_width=True)

    with perf_col2:
        # Waste type distribution
        waste_types = ['Reciclável', 'Orgânico', 'Comum']
        waste_amounts = [45, 35, 20]  # Simulated data

        fig_waste = px.pie(
            values=waste_amounts,
            names=waste_types,
            title="Distribuição por Tipo de Resíduo",
            color_discrete_map={
                'Reciclável': '#4CAF50',
                'Orgânico': '#8BC34A',
                'Comum': '#FFC107'
            }
        )
        fig_waste.update_layout(margin=dict(t=50, b=0, l=0, r=0))
        st.plotly_chart(fig_waste, use_container_width=True)
        
    st.markdown("---")
    
    # --- Recent collections summary ---
    st.markdown("### 📊 Resumo de Coletas Recentes")

    with st.container(border=True):
        collections_data = db.get_recent_collections() # Assuming this returns data
        
        # Simulating data if db.get_recent_collections() is not implemented
        if not collections_data:
            collections_data = [
                {'amount': 150.5, 'efficiency': 92, 'date': '2025-10-28', 'location': 'Centro'},
                {'amount': 210.0, 'efficiency': 88, 'date': '2025-10-27', 'location': 'Norte'},
                {'amount': 95.2, 'efficiency': 95, 'date': '2025-10-27', 'location': 'Sul'},
            ]
            
        if collections_data:
            total_collected = sum([c['amount'] for c in collections_data])
            avg_efficiency = sum([c['efficiency'] for c in collections_data]) / len(collections_data)
            
            col_sum1, col_sum2 = st.columns(2)
            with col_sum1:
                st.metric("Total Coletado (kg)", f"{total_collected:.1f}")
            with col_sum2:
                st.metric("Eficiência Média", f"{avg_efficiency:.1f}%")

            st.markdown("---")
            st.markdown("**Últimas Coletas:**")
            for collection in collections_data[:3]:
                st.markdown(f"• **{collection['date']}** - {collection['amount']}kg em {collection['location']}")
        else:
            st.info("Nenhuma coleta recente registrada.")


# Auto-refresh timer
if auto_refresh:
    time.sleep(30)
    st.rerun()

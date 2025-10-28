import streamlit as st
import time
from datetime import datetime
from data.database import Database
from utils.notifications import NotificationManager

# Initialize database and notification manager
@st.cache_resource
def init_database():
    return Database()

@st.cache_resource
def init_notifications():
    return NotificationManager()

db = init_database()
notifications = init_notifications()

# Page configuration
st.set_page_config(
    page_title="EcoSmart - Gestão Inteligente de Coleta",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #2E7D32;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-card {
    background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #2E7D32;
    margin-bottom: 1rem;
}

.status-indicator {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 10px;
}

.status-empty { background-color: #4CAF50; }
.status-medium { background-color: #FF9800; }
.status-full { background-color: #F44336; }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">♻️ EcoSmart - Plataforma de Gestão Inteligente</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("🏠 Menu Principal")
        st.markdown("---")
        
        st.selectbox(
            "Tipo de Usuário:",
            ["Administrador", "Morador/Colaborador", "Operador de Coleta"]
        )
        
        st.markdown("---")
        st.markdown("### 📊 Status Geral")
        
        # Get summary statistics
        db.get_bins_summary()
        total_bins = len(db.get_all_bins())
        full_bins = len([b for b in db.get_all_bins() if b['fill_level'] >= 80])
        
        st.metric("Total de Lixeiras", total_bins)
        st.metric("Coleta Necessária", full_bins)
        st.metric("Eficiência de Coleta", "87%")
        
        # Real-time clock
        st.markdown("---")
        clock_placeholder = st.empty()
        
    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🎯 Visão Geral do Sistema")
        st.markdown("""
        **EcoSmart** é uma plataforma completa para gestão inteligente de coleta de lixo que integra:
        
        -  **Lixeiras IoT** com sensores de nível e GPS
        -  **Rastreamento de Caminhões** em tempo real  
        -  **Sistema de Gamificação** para usuários
        -  **Relatórios ESG** e analytics
        -  **Otimização de Rotas** inteligente
        """)
        
        # Quick stats
        st.markdown("### 📈 Métricas Rápidas")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            st.metric(
                "Lixeiras Ativas",
                total_bins,
                delta="+2 esta semana"
            )
            
        with col_b:
            st.metric(
                "Resíduos Coletados",
                "1.2T",
                delta="+15% este mês"
            )
            
        with col_c:
            st.metric(
                "Economia Combustível",
                "23%",
                delta="+8% otimização"
            )
            
        with col_d:
            st.metric(
                "Usuários Ativos",
                "247",
                delta="+12 esta semana"
            )
    
    # Navigation buttons
    st.markdown("---")
    st.markdown("### 🧭 Navegação Rápida")
    
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    with nav_col1:
        if st.button("📊 Dashboard Admin", use_container_width=True):
            st.switch_page("pages/1_Dashboard_Administrativo.py")
    
    with nav_col2:
        if st.button("🗺️ Mapa GPS", use_container_width=True):
            st.switch_page("pages/2_Mapa_GPS.py")
    
    with nav_col3:
        if st.button("🎮 Gamificação", use_container_width=True):
            st.switch_page("pages/3_Usuario_Gamificacao.py")
    
    with nav_col4:
        if st.button("📈 Relatórios ESG", use_container_width=True):
            st.switch_page("pages/4_Relatorios_ESG.py")
    
    # Recent activity feed
    st.markdown("---")
    st.markdown("### 📢 Atividades Recentes")
    
    recent_activities = db.get_recent_activities()
    
    for activity in recent_activities[:5]:
        timestamp = datetime.fromisoformat(activity['timestamp']).strftime("%H:%M")
        st.markdown(f"🕐 **{timestamp}** - {activity['message']}")
    
    # Auto-refresh mechanism
    time.sleep(1)
    clock_placeholder.markdown(f"⏰ {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()

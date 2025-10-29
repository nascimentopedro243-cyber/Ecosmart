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

# --- Page configuration ---
st.set_page_config(
    page_title="EcoSmart - Gestão Inteligente de Coleta",
    page_icon="♻️",
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
    border-bottom: 3px solid #008080;
    padding-bottom: 0.5rem;
}

/* Metric Card Styling (using st.container for better control) */
.st-emotion-cache-1r6r00 { /* Target Streamlit's default metric container */
    background-color: #F0FFFF; /* Azure Claro */
    border-radius: 10px;
    padding: 15px;
    box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease-in-out;
}
.st-emotion-cache-1r6r00:hover {
    box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
}

/* Sidebar Styling */
.st-emotion-cache-vk3ypu { /* Target Streamlit's sidebar */
    background-color: #E0FFFF; /* Light Cyan */
}

/* Button Styling (making them more prominent) */
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

/* Section Headers */
h3 {
    color: #008080;
    border-left: 5px solid #008080;
    padding-left: 10px;
    margin-top: 1.5rem;
}

</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">♻️ EcoSmart - Plataforma de Gestão Inteligente</h1>', unsafe_allow_html=True)
    
    # --- Sidebar ---
    with st.sidebar:
        st.title("Menu Principal")
        st.markdown("---")
        
        st.selectbox(
            "Tipo de Usuário:",
            ["Administrador", "Morador/Colaborador", "Operador de Coleta"]
        )
        
        st.markdown("---")
        
        # --- Status Geral Container ---
        st.markdown("### 📊 Status Geral")
        
        # Get summary statistics (Simulated for this example)
        # db.get_bins_summary() # Assuming this is implemented in the actual Database class
        total_bins = 150 # Placeholder value
        full_bins = 25 # Placeholder value
        
        st.metric("Total de Lixeiras", total_bins)
        st.metric("Coleta Necessária", full_bins)
        st.metric("Eficiência de Coleta", "87%")
        
        # Real-time clock
        st.markdown("---")
        clock_placeholder = st.empty()
        
    # --- Main Content Area ---
    
    # Use tabs for a cleaner layout
    tab1, tab2 = st.tabs(["Visão Geral", "Atividades Recentes"])
    
    with tab1:
        # --- Visão Geral do Sistema ---
        st.markdown("### 💡 Visão Geral do Sistema")
        st.info("""
        **EcoSmart** é uma plataforma completa para gestão inteligente de coleta de lixo. 
        Nosso objetivo é otimizar rotas, reduzir custos operacionais e promover a sustentabilidade 
        através da integração de **Lixeiras IoT**, **Rastreamento de Caminhões** e **Analytics Avançado**.
        """)
        
        # --- Métricas Rápidas ---
        st.markdown("### 📈 Métricas Rápidas")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            st.metric(
                "Lixeiras Ativas",
                total_bins,
                delta="+2 esta semana",
                delta_color="normal"
            )
            
        with col_b:
            st.metric(
                "Resíduos Coletados",
                "1.2T",
                delta="+15% este mês",
                delta_color="inverse"
            )
            
        with col_c:
            st.metric(
                "Economia Combustível",
                "23%",
                delta="+8% otimização",
                delta_color="normal"
            )
            
        with col_d:
            st.metric(
                "Usuários Ativos",
                "247",
                delta="+12 esta semana",
                delta_color="normal"
            )
        
        st.markdown("---")
        
        # --- Navegação Rápida (Ações) ---
        st.markdown("### 🚀 Ações Rápidas")
        
        nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
        
        with nav_col1:
            if st.button("📊 Dashboard Admin", use_container_width=True):
                # st.switch_page("pages/1_Dashboard_Administrativo.py") # Uncomment in a multi-page app
                st.success("Navegando para Dashboard Admin...")
        
        with nav_col2:
            if st.button("🗺️ Mapa GPS", use_container_width=True):
                # st.switch_page("pages/2_Mapa_GPS.py") # Uncomment in a multi-page app
                st.success("Navegando para Mapa GPS...")
        
        with nav_col3:
            if st.button("🎮 Gamificação", use_container_width=True):
                # st.switch_page("pages/3_Usuario_Gamificacao.py") # Uncomment in a multi-page app
                st.success("Navegando para Gamificação...")
        
        with nav_col4:
            if st.button("📈 Relatórios ESG", use_container_width=True):
                # st.switch_page("pages/4_Relatorios_ESG.py") # Uncomment in a multi-page app
                st.success("Navegando para Relatórios ESG...")

    with tab2:
        # --- Atividades Recentes ---
        st.markdown("### 📢 Feed de Atividades")
        
        # Use st.container for a visually separated section
        with st.container(border=True):
            # Simulating recent activities
            # recent_activities = db.get_recent_activities() # Assuming this is implemented
            recent_activities = [
                {'timestamp': datetime.now().isoformat(), 'message': 'Lixeira #15 atingiu 90% de enchimento. Coleta urgente.'},
                {'timestamp': datetime.now().isoformat(), 'message': 'Caminhão 01 iniciou rota de coleta na Zona Sul.'},
                {'timestamp': datetime.now().isoformat(), 'message': 'Nova lixeira IoT instalada na Av. Paulista.'},
                {'timestamp': datetime.now().isoformat(), 'message': 'Usuário João Silva subiu para o nível Ouro na Gamificação.'},
                {'timestamp': datetime.now().isoformat(), 'message': 'Bateria da Lixeira #8 está em 15%. Manutenção programada.'},
            ]
            
            for activity in recent_activities:
                timestamp = datetime.fromisoformat(activity['timestamp']).strftime("%H:%M:%S")
                # Use st.status for a clean, modern look (simulating a closed status for history)
                with st.status(f"**{timestamp}**", expanded=False):
                    st.markdown(activity['message'])
            
            st.button("Carregar Mais Atividades", use_container_width=True)


    # --- Auto-refresh mechanism ---
    time.sleep(1)
    clock_placeholder.markdown(f"⏰ **{datetime.now().strftime('%H:%M:%S')}**")
    
    # st.rerun() # Uncomment if real-time refresh is desired

if __name__ == "__main__":
    main()

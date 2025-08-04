"""
Simplified Streamlit Dashboard for iFood Data Governance
Standalone version that works without complex dependencies.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="iFood Data Governance Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #EA1D2C;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #EA1D2C;
    }
    .status-good {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-critical {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Generate sample data for demonstration
@st.cache_data
def generate_sample_data():
    """Generate sample data for dashboard demonstration."""
    
    # Sample quality data
    dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
    quality_data = pd.DataFrame({
        'date': dates,
        'completeness': np.random.normal(95, 2, len(dates)),
        'validity': np.random.normal(97, 1.5, len(dates)),
        'consistency': np.random.normal(92, 3, len(dates)),
        'timeliness': np.random.normal(88, 4, len(dates)),
        'overall_score': np.random.normal(93, 2, len(dates))
    })
    
    # Sample orders data
    orders_data = pd.DataFrame({
        'date': dates,
        'total_orders': np.random.poisson(50000, len(dates)),
        'delivered_orders': np.random.poisson(47000, len(dates)),
        'cancelled_orders': np.random.poisson(2500, len(dates)),
        'avg_order_value': np.random.normal(45, 5, len(dates)),
        'delivery_success_rate': np.random.normal(94, 2, len(dates))
    })
    
    return quality_data, orders_data

# Sidebar navigation
st.sidebar.title("🍔 iFood Data Governance")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navegação",
    [
        "📊 Overview",
        "📈 Data Quality",
        "🔗 Data Lineage",
        "📚 Data Catalog",
        "🔒 Privacy & Security",
        "👥 Access Control",
        "📋 Compliance Report"
    ]
)

# Main header
st.markdown('<h1 class="main-header">iFood Data Governance Dashboard</h1>', unsafe_allow_html=True)

quality_data, orders_data = generate_sample_data()

# Page routing
if page == "📊 Overview":
    st.header("📊 Visão Geral do Sistema")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Datasets Catalogados",
            value="156",
            delta="12 novos esta semana"
        )
    
    with col2:
        st.metric(
            label="🎯 Qualidade Média",
            value="93.2%",
            delta="1.5% vs mês anterior"
        )
    
    with col3:
        st.metric(
            label="🔒 Datasets com PII",
            value="23",
            delta="Todos em conformidade"
        )
    
    with col4:
        st.metric(
            label="👥 Usuários Ativos",
            value="89",
            delta="5 novos usuários"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Tendência de Qualidade de Dados")
        fig = px.line(
            quality_data,
            x='date',
            y=['completeness', 'validity', 'consistency', 'timeliness'],
            title="Métricas de Qualidade por Dimensão",
            labels={'value': 'Score (%)', 'date': 'Data'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📦 Volume de Pedidos")
        fig = px.bar(
            orders_data,
            x='date',
            y='total_orders',
            title="Volume Diário de Pedidos",
            labels={'total_orders': 'Pedidos', 'date': 'Data'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # System status
    st.subheader("🚦 Status dos Sistemas")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.markdown("""
        <div class="metric-card">
            <h4>Pipeline de Ingestão</h4>
            <p class="status-good">✅ Operacional</p>
            <small>Última execução: 14:30</small>
        </div>
        """, unsafe_allow_html=True)
    
    with status_col2:
        st.markdown("""
        <div class="metric-card">
            <h4>Validação de Qualidade</h4>
            <p class="status-warning">⚠️ Atenção</p>
            <small>2 alertas pendentes</small>
        </div>
        """, unsafe_allow_html=True)
    
    with status_col3:
        st.markdown("""
        <div class="metric-card">
            <h4>Data Warehouse</h4>
            <p class="status-good">✅ Operacional</p>
            <small>Latência: 2.3s</small>
        </div>
        """, unsafe_allow_html=True)

elif page == "📈 Data Quality":
    st.header("📈 Monitoramento de Qualidade de Dados")
    
    # Quality overview
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Completude", "95.2%", "0.3%")
    with col2:
        st.metric("Validade", "97.1%", "-0.1%")
    with col3:
        st.metric("Consistência", "92.8%", "1.2%")
    with col4:
        st.metric("Pontualidade", "88.5%", "-2.1%")
    with col5:
        st.metric("Score Geral", "93.4%", "0.2%")
    
    # Quality trends
    st.subheader("📊 Tendências de Qualidade")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Completude', 'Validade', 'Consistência', 'Pontualidade'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=quality_data['date'], y=quality_data['completeness'], name='Completude'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=quality_data['date'], y=quality_data['validity'], name='Validade'),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=quality_data['date'], y=quality_data['consistency'], name='Consistência'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=quality_data['date'], y=quality_data['timeliness'], name='Pontualidade'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Quality issues
    st.subheader("🚨 Alertas de Qualidade")
    
    alerts_data = pd.DataFrame({
        'Dataset': ['bronze_orders', 'silver_orders', 'gold_orders_summary'],
        'Tipo': ['Completude', 'Validade', 'Consistência'],
        'Severidade': ['Alto', 'Médio', 'Baixo'],
        'Descrição': [
            'Campo customer_phone com 5% de valores nulos',
            'Formato de CPF inválido em 2% dos registros',
            'Inconsistência entre total_amount e delivery_fee'
        ],
        'Timestamp': ['14:25', '14:20', '14:15']
    })
    
    st.dataframe(alerts_data, use_container_width=True)

elif page == "🔗 Data Lineage":
    st.header("🔗 Linhagem de Dados")
    
    # Lineage visualization
    st.subheader("📊 Fluxo de Dados - Pedidos iFood")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("🔄 **Fluxo de Transformação:**\n\n"
                "1. **API → Bronze**: Ingestão raw dos dados\n"
                "2. **Bronze → Silver**: Limpeza, validação e mascaramento PII\n"
                "3. **Silver → Gold**: Agregações e métricas de negócio\n"
                "4. **Gold → Dashboard**: Consumo para análises")
    
    with col2:
        st.subheader("📋 Metadados")
        st.json({
            "última_execução": "2024-01-15 14:30:00",
            "registros_processados": 125847,
            "tempo_execução": "4m 23s",
            "status": "sucesso"
        })
    
    # Dataset details
    st.subheader("📊 Detalhes dos Datasets")
    
    dataset_details = pd.DataFrame({
        'Dataset': ['bronze_orders', 'silver_orders', 'gold_orders_summary'],
        'Registros': ['125,847', '123,456', '15'],
        'Tamanho': ['45.2 MB', '38.7 MB', '2.1 KB'],
        'Última Atualização': ['14:30', '14:32', '14:35'],
        'Qualidade': ['89%', '95%', '98%']
    })
    
    st.dataframe(dataset_details, use_container_width=True)

elif page == "📚 Data Catalog":
    st.header("📚 Catálogo de Dados")
    
    # Search functionality
    search_term = st.text_input("🔍 Buscar datasets", placeholder="Digite o nome do dataset...")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        layer_filter = st.selectbox("Camada", ["Todas", "Bronze", "Silver", "Gold"])
    with col2:
        domain_filter = st.selectbox("Domínio", ["Todos", "delivery", "payments", "marketing"])
    with col3:
        classification_filter = st.selectbox("Classificação", ["Todas", "Public", "Internal", "Confidential"])
    
    # Sample catalog data
    catalog_data = pd.DataFrame({
        'Nome': [
            'bronze_orders',
            'silver_orders',
            'gold_orders_summary',
            'bronze_customers',
            'silver_customers_masked'
        ],
        'Descrição': [
            'Dados brutos de pedidos da API',
            'Pedidos limpos e padronizados',
            'Resumo diário de pedidos',
            'Dados brutos de clientes',
            'Clientes com PII mascarado'
        ],
        'Camada': ['Bronze', 'Silver', 'Gold', 'Bronze', 'Silver'],
        'Domínio': ['delivery', 'delivery', 'delivery', 'customers', 'customers'],
        'Classificação': ['Internal', 'Confidential', 'Internal', 'Confidential', 'Internal'],
        'Owner': ['data-eng', 'data-eng', 'data-eng', 'data-eng', 'data-eng'],
        'Qualidade': ['89%', '95%', '98%', '92%', '96%'],
        'PII': ['Sim', 'Mascarado', 'Não', 'Sim', 'Mascarado']
    })
    
    st.dataframe(catalog_data, use_container_width=True)

elif page == "🔒 Privacy & Security":
    st.header("🔒 Privacidade e Segurança")
    
    # Privacy metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Campos PII", "23", "Todos mascarados")
    with col2:
        st.metric("Solicitações LGPD", "12", "3 este mês")
    with col3:
        st.metric("Conformidade", "100%", "Sem violações")
    with col4:
        st.metric("Retenção Média", "7 anos", "Conforme LGPD")
    
    # PII masking demo
    st.subheader("🎭 Demonstração de Mascaramento PII")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Dados Originais:**")
        st.code("""
CPF: 123.456.789-00
Telefone: (11) 99999-9999
Email: cliente@email.com
Endereço: Rua das Flores, 123
        """)
    
    with col2:
        st.write("**Dados Mascarados:**")
        st.code("""
CPF: 123.***.789-**
Telefone: (11) ****-9999
Email: c***@email.com
Endereço: Rua das *****, ***
        """)

elif page == "👥 Access Control":
    st.header("👥 Controle de Acesso")
    
    # Access metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Usuários Ativos", "89", "5 novos")
    with col2:
        st.metric("Roles Definidos", "6", "Sem alterações")
    with col3:
        st.metric("Acessos Hoje", "1,247", "12% vs ontem")
    with col4:
        st.metric("Taxa de Sucesso", "98.5%", "0.2%")
    
    # User roles
    st.subheader("👥 Roles e Permissões")
    
    roles_data = pd.DataFrame({
        'Role': ['admin', 'data_engineer', 'data_analyst', 'business_user', 'auditor', 'dpo'],
        'Usuários': [1, 12, 25, 45, 4, 2],
        'Permissões': [
            'Acesso total ao sistema',
            'Desenvolvimento e manutenção',
            'Análise e relatórios',
            'Visualização de métricas',
            'Auditoria e conformidade',
            'Gestão de privacidade'
        ]
    })
    
    st.dataframe(roles_data, use_container_width=True)

elif page == "📋 Compliance Report":
    st.header("📋 Relatório de Conformidade")
    
    # Compliance overview
    st.subheader("✅ Status Geral de Conformidade")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("LGPD", "100%", "Conforme")
    with col2:
        st.metric("Qualidade", "93%", "2 issues")
    with col3:
        st.metric("Segurança", "98%", "Conforme")
    with col4:
        st.metric("Retenção", "100%", "Conforme")
    
    # Detailed report
    st.subheader("📊 Relatório Detalhado")
    
    with st.expander("🏛️ Governança de Dados"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Datasets Catalogados", "156/156")
            st.metric("Com Linhagem", "142")
        with col2:
            st.metric("Com Monitoramento", "134")
            st.progress(1.0)
    
    with st.expander("🔒 Conformidade LGPD"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Campos PII Mascarados", "23/23")
            st.metric("Solicitações Processadas", "12")
        with col2:
            st.metric("Violações de Retenção", "0")
            st.progress(1.0)

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #666;'>
        <p>iFood Data Governance Dashboard v1.0.0 | 
        Última atualização: {datetime.now().strftime("%Y-%m-%d %H:%M")} | 
        <a href='mailto:data-engineering@ifood.com'>Suporte</a></p>
    </div>
    """,
    unsafe_allow_html=True
)

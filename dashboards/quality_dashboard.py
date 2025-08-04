"""
Data Quality Dashboard
Specialized dashboard for detailed data quality monitoring and analysis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.data_quality_checker import DataQualityChecker, QualityDimension
from data_quality.great_expectations_config import IFoodDataQualityConfig

st.set_page_config(
    page_title="Data Quality Dashboard - iFood",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Data Quality Dashboard")
st.markdown("Monitoramento detalhado da qualidade de dados do iFood")

# Initialize components
@st.cache_resource
def init_quality_components():
    return {
        'quality_checker': DataQualityChecker(),
        'gx_config': IFoodDataQualityConfig()
    }

components = init_quality_components()

# Generate sample quality data
@st.cache_data
def generate_quality_data():
    """Generate sample quality data for visualization."""
    
    # Time series data
    dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='H')
    
    quality_metrics = pd.DataFrame({
        'timestamp': dates,
        'completeness': np.random.normal(95, 3, len(dates)),
        'validity': np.random.normal(97, 2, len(dates)),
        'consistency': np.random.normal(92, 4, len(dates)),
        'timeliness': np.random.normal(88, 5, len(dates)),
        'accuracy': np.random.normal(94, 3, len(dates)),
        'uniqueness': np.random.normal(99, 1, len(dates))
    })
    
    # Ensure values are within reasonable bounds
    for col in ['completeness', 'validity', 'consistency', 'timeliness', 'accuracy', 'uniqueness']:
        quality_metrics[col] = np.clip(quality_metrics[col], 70, 100)
    
    # Calculate overall score
    quality_metrics['overall_score'] = quality_metrics[
        ['completeness', 'validity', 'consistency', 'timeliness', 'accuracy', 'uniqueness']
    ].mean(axis=1)
    
    # Dataset-level metrics
    datasets = ['bronze_orders', 'silver_orders', 'gold_orders_summary', 'bronze_customers', 'silver_customers']
    dataset_metrics = pd.DataFrame({
        'dataset': datasets,
        'completeness': np.random.uniform(85, 99, len(datasets)),
        'validity': np.random.uniform(90, 99, len(datasets)),
        'consistency': np.random.uniform(80, 95, len(datasets)),
        'timeliness': np.random.uniform(75, 95, len(datasets)),
        'accuracy': np.random.uniform(85, 98, len(datasets)),
        'uniqueness': np.random.uniform(95, 100, len(datasets)),
        'total_records': np.random.randint(10000, 1000000, len(datasets)),
        'failed_checks': np.random.randint(0, 5, len(datasets))
    })
    
    dataset_metrics['overall_score'] = dataset_metrics[
        ['completeness', 'validity', 'consistency', 'timeliness', 'accuracy', 'uniqueness']
    ].mean(axis=1)
    
    return quality_metrics, dataset_metrics

quality_metrics, dataset_metrics = generate_quality_data()

# Sidebar filters
st.sidebar.header("🔧 Filtros")

# Time range selector
time_range = st.sidebar.selectbox(
    "Período",
    ["Última hora", "Últimas 6 horas", "Último dia", "Última semana", "Último mês"]
)

# Dataset selector
selected_datasets = st.sidebar.multiselect(
    "Datasets",
    dataset_metrics['dataset'].tolist(),
    default=dataset_metrics['dataset'].tolist()[:3]
)

# Quality dimension selector
selected_dimensions = st.sidebar.multiselect(
    "Dimensões de Qualidade",
    ["completeness", "validity", "consistency", "timeliness", "accuracy", "uniqueness"],
    default=["completeness", "validity", "consistency"]
)

# Main dashboard
col1, col2, col3, col4 = st.columns(4)

# Current quality metrics
current_metrics = quality_metrics.iloc[-1]

with col1:
    st.metric(
        "Score Geral",
        f"{current_metrics['overall_score']:.1f}%",
        f"{current_metrics['overall_score'] - quality_metrics.iloc[-24]['overall_score']:.1f}%"
    )

with col2:
    st.metric(
        "Completude",
        f"{current_metrics['completeness']:.1f}%",
        f"{current_metrics['completeness'] - quality_metrics.iloc[-24]['completeness']:.1f}%"
    )

with col3:
    st.metric(
        "Validade",
        f"{current_metrics['validity']:.1f}%",
        f"{current_metrics['validity'] - quality_metrics.iloc[-24]['validity']:.1f}%"
    )

with col4:
    st.metric(
        "Consistência",
        f"{current_metrics['consistency']:.1f}%",
        f"{current_metrics['consistency'] - quality_metrics.iloc[-24]['consistency']:.1f}%"
    )

# Quality trends chart
st.subheader("📈 Tendências de Qualidade")

fig = go.Figure()

for dimension in selected_dimensions:
    fig.add_trace(go.Scatter(
        x=quality_metrics['timestamp'],
        y=quality_metrics[dimension],
        mode='lines',
        name=dimension.title(),
        line=dict(width=2)
    ))

fig.update_layout(
    title="Métricas de Qualidade ao Longo do Tempo",
    xaxis_title="Timestamp",
    yaxis_title="Score (%)",
    height=400,
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

# Dataset comparison
st.subheader("📊 Comparação por Dataset")

# Filter dataset metrics
filtered_dataset_metrics = dataset_metrics[
    dataset_metrics['dataset'].isin(selected_datasets)
] if selected_datasets else dataset_metrics

# Create radar chart for dataset comparison
fig_radar = go.Figure()

for dataset in filtered_dataset_metrics['dataset']:
    dataset_row = filtered_dataset_metrics[filtered_dataset_metrics['dataset'] == dataset].iloc[0]
    
    fig_radar.add_trace(go.Scatterpolar(
        r=[
            dataset_row['completeness'],
            dataset_row['validity'],
            dataset_row['consistency'],
            dataset_row['timeliness'],
            dataset_row['accuracy'],
            dataset_row['uniqueness']
        ],
        theta=['Completude', 'Validade', 'Consistência', 'Pontualidade', 'Precisão', 'Unicidade'],
        fill='toself',
        name=dataset
    ))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]
        )),
    showlegend=True,
    title="Comparação de Qualidade por Dataset",
    height=500
)

col1, col2 = st.columns([2, 1])

with col1:
    st.plotly_chart(fig_radar, use_container_width=True)

with col2:
    st.subheader("📋 Resumo dos Datasets")
    
    summary_df = filtered_dataset_metrics[['dataset', 'overall_score', 'failed_checks', 'total_records']].copy()
    summary_df['overall_score'] = summary_df['overall_score'].round(1)
    summary_df.columns = ['Dataset', 'Score (%)', 'Falhas', 'Registros']
    
    st.dataframe(summary_df, use_container_width=True)

# Quality issues and alerts
st.subheader("🚨 Alertas e Problemas de Qualidade")

# Generate sample quality issues
quality_issues = pd.DataFrame({
    'Dataset': ['bronze_orders', 'silver_orders', 'bronze_customers', 'gold_orders_summary'],
    'Dimensão': ['Completude', 'Validade', 'Consistência', 'Pontualidade'],
    'Severidade': ['Alto', 'Médio', 'Baixo', 'Médio'],
    'Descrição': [
        'Campo customer_phone com 8% de valores nulos',
        'Formato de CPF inválido em 3% dos registros',
        'Inconsistência entre total_amount e delivery_fee em 1% dos casos',
        'Dados com atraso de 15 minutos na última atualização'
    ],
    'Detectado em': ['2024-01-15 14:25', '2024-01-15 14:20', '2024-01-15 14:15', '2024-01-15 14:10'],
    'Status': ['🔴 Aberto', '🟡 Investigando', '🟢 Resolvido', '🟡 Investigando']
})

# Color code by severity
def color_severity(val):
    if val == 'Alto':
        return 'background-color: #ffebee'
    elif val == 'Médio':
        return 'background-color: #fff3e0'
    elif val == 'Baixo':
        return 'background-color: #e8f5e8'
    return ''

styled_issues = quality_issues.style.applymap(color_severity, subset=['Severidade'])
st.dataframe(styled_issues, use_container_width=True)

# Quality rules and expectations
st.subheader("📏 Regras de Qualidade Ativas")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ Regras Aprovadas")
    
    passed_rules = pd.DataFrame({
        'Regra': [
            'order_id_uniqueness',
            'total_amount_positive',
            'customer_id_format',
            'order_status_valid'
        ],
        'Dataset': ['bronze_orders', 'silver_orders', 'bronze_orders', 'silver_orders'],
        'Última Execução': ['14:30', '14:30', '14:30', '14:30'],
        'Taxa de Sucesso': ['100%', '99.8%', '98.5%', '99.9%']
    })
    
    st.dataframe(passed_rules, use_container_width=True)

with col2:
    st.subheader("❌ Regras com Falhas")
    
    failed_rules = pd.DataFrame({
        'Regra': [
            'delivery_time_logical',
            'cpf_format_valid'
        ],
        'Dataset': ['silver_orders', 'bronze_orders'],
        'Última Execução': ['14:30', '14:30'],
        'Taxa de Falha': ['2.1%', '3.2%']
    })
    
    st.dataframe(failed_rules, use_container_width=True)

# Quality improvement recommendations
st.subheader("💡 Recomendações de Melhoria")

recommendations = [
    "🔧 **Validação de Entrada**: Implementar validação mais rigorosa no campo customer_phone na API de origem",
    "📊 **Monitoramento Proativo**: Configurar alertas automáticos para quedas de qualidade acima de 5%",
    "🔄 **Processo de Correção**: Estabelecer processo automatizado para correção de formatos de CPF",
    "📈 **Métricas de SLA**: Definir SLAs específicos de qualidade para cada camada (Bronze: 85%, Silver: 95%, Gold: 98%)",
    "🎯 **Treinamento**: Capacitar equipes de origem sobre padrões de qualidade de dados"
]

for rec in recommendations:
    st.markdown(rec)

# Export functionality
st.subheader("📤 Exportar Relatório")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Exportar Métricas CSV"):
        csv = quality_metrics.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"quality_metrics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📋 Exportar Problemas"):
        csv = quality_issues.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"quality_issues_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

with col3:
    if st.button("📈 Gerar Relatório PDF"):
        st.info("Funcionalidade de PDF será implementada em versão futura")

# Real-time monitoring toggle
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Monitoramento")

auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)")
if auto_refresh:
    st.sidebar.success("✅ Monitoramento ativo")
    # In a real implementation, this would trigger automatic refresh
    st.rerun()

# Footer with last update time
st.markdown("---")
st.markdown(f"**Última atualização:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("**Fonte:** iFood Data Quality Engine v1.0.0")

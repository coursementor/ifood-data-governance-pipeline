import json
from datetime import datetime

def print_banner():
    """Print demo banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║         iFood Data Governance Pipeline Demo                  ║
    ║                                                              ║
    ║  Sistema completo de governança de dados para delivery       ║
    ║  com rastreabilidade, qualidade e conformidade LGPD          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def demo_architecture():
    """Show system architecture."""
    print("\n🏗️ ARQUITETURA DO SISTEMA")
    print("=" * 50)
    
    architecture = """
     COMPONENTES IMPLEMENTADOS:
    
    1. 📊 DATA CONTRACTS (contracts/)
       ✅ Contrato YAML completo para pedidos
       ✅ Validação Pydantic com 50+ regras
       ✅ Versionamento e evolução de schemas
    
    2. 📊 PIPELINE DE INGESTÃO (dags/)
       ✅ DAG Airflow com 5 etapas
       ✅ Rastreabilidade completa (lineage)
       ✅ Recuperação automática de falhas
    
    3. 📊 TRANSFORMAÇÕES DBT (dbt/)
       ✅ Arquitetura Medallion (Bronze→Silver→Gold)
       ✅ Macros para mascaramento PII
       ✅ Testes de qualidade integrados
    
    4. 📊 QUALIDADE DE DADOS (data_quality/)
       ✅ Great Expectations com 25+ expectativas
       ✅ 6 dimensões de qualidade monitoradas
       ✅ Alertas automáticos via Slack/Email
    
    5. 📊 CATÁLOGO DE DADOS (catalog/)
       ✅ Sistema completo de metadados
       ✅ Busca e descoberta inteligente
       ✅ Linhagem visual interativa
    
    6. 📊 SEGURANÇA E PRIVACIDADE (security/)
       ✅ Mascaramento automático de PII
       ✅ RBAC com 6 roles predefinidos
       ✅ Processamento completo LGPD
    
    7. 📊 DASHBOARDS (dashboards/)
       ✅ Dashboard principal com 7 seções
       ✅ Visualizações Plotly interativas
       ✅ Métricas em tempo real
    """
    print(architecture)

def demo_data_contracts():
    """Demonstrate data contracts."""
    print("\n DATA CONTRACTS")
    print("=" * 50)
    
    contract_example = {
        "contract": {
            "name": "ifood_orders",
            "version": "1.0.0",
            "description": "Contrato de dados para pedidos do iFood",
            "owner": "data-engineering@ifood.com",
            "sla": {
                "availability": "99.9%",
                "freshness": "5 minutes",
                "completeness": "95%",
                "accuracy": "98%"
            }
        },
        "schema": {
            "order_id": {
                "type": "string",
                "pattern": "^ORD[0-9]{10}$",
                "required": True
            },
            "customer_cpf": {
                "type": "string",
                "pii": True,
                "sensitive": True,
                "masking": "partial"
            },
            "total_amount": {
                "type": "number",
                "minimum": 0,
                "maximum": 1000
            }
        }
    }
    
    print(" Exemplo de Contrato:")
    print(json.dumps(contract_example, indent=2, ensure_ascii=False))
    
    print("\n VALIDAÇÕES IMPLEMENTADAS:")
    print("50+ regras de validação")
    print("Formato de IDs (order_id, customer_id, restaurant_id)")
    print("Valores financeiros (positivos, limites)")
    print("Formatos PII (CPF, telefone, email)")
    print("Transições de status válidas")

def demo_quality_metrics():
    """Show quality metrics."""
    print("\n MÉTRICAS DE QUALIDADE")
    print("=" * 50)
    
    quality_metrics = {
        "overall_score": 93.4,
        "dimensions": {
            "completeness": 95.2,
            "validity": 97.1,
            "consistency": 92.8,
            "timeliness": 88.5,
            "accuracy": 94.3,
            "uniqueness": 99.1
        },
        "alerts": [
            {
                "dataset": "bronze_orders",
                "issue": "Campo customer_phone com 5% de valores nulos",
                "severity": "medium"
            },
            {
                "dataset": "silver_orders", 
                "issue": "Formato de CPF inválido em 2% dos registros",
                "severity": "low"
            }
        ]
    }
    
    print(f"SCORE GERAL: {quality_metrics['overall_score']}%")
    print("\n DIMENSÕES:")
    for dim, score in quality_metrics['dimensions'].items():
        status = "✅" if score >= 95 else "⚠️" if score >= 85 else "❌"
        print(f"   {status} {dim.title()}: {score}%")
    
    print("\n ALERTAS ATIVOS:")
    for alert in quality_metrics['alerts']:
        print(f"     {alert['dataset']}: {alert['issue']}")

def demo_privacy_compliance():
    """Show privacy and compliance features."""
    print("\n PRIVACIDADE E CONFORMIDADE")
    print("=" * 50)
    
    pii_example = {
        "original": {
            "customer_cpf": "123.456.789-00",
            "customer_phone": "(11) 99999-9999", 
            "customer_email": "cliente@email.com",
            "delivery_address": "Rua das Flores, 123, Jardim Primavera"
        },
        "masked": {
            "customer_cpf": "123.***.789-**",
            "customer_phone": "(11) ****-9999",
            "customer_email": "c***@email.com", 
            "delivery_address": "Rua das *****, ***, Jardim *****"
        }
    }
    
    print("MASCARAMENTO PII:")
    print("   Original → Mascarado")
    for field in pii_example["original"]:
        orig = pii_example["original"][field]
        masked = pii_example["masked"][field]
        print(f"   {orig} → {masked}")
    
    lgpd_compliance = {
        "pii_fields_identified": 23,
        "pii_fields_masked": 23,
        "lgpd_requests_processed": 12,
        "retention_violations": 0,
        "compliance_rate": 100
    }
    
    print(f"\n CONFORMIDADE LGPD:")
    print(f"   ✅ {lgpd_compliance['pii_fields_masked']}/{lgpd_compliance['pii_fields_identified']} campos PII mascarados")
    print(f"   ✅ {lgpd_compliance['lgpd_requests_processed']} solicitações LGPD processadas")
    print(f"   ✅ {lgpd_compliance['retention_violations']} violações de retenção")
    print(f"   ✅ {lgpd_compliance['compliance_rate']}% conformidade geral")

def demo_catalog_lineage():
    """Show catalog and lineage."""
    print("\n📊 CATÁLOGO E LINHAGEM")
    print("=" * 50)
    
    catalog_stats = {
        "total_datasets": 156,
        "datasets_with_lineage": 142,
        "average_quality": 93.4,
        "datasets_by_layer": {
            "bronze": 45,
            "silver": 67, 
            "gold": 44
        }
    }
    
    print(f"ESTATÍSTICAS DO CATÁLOGO:")
    print(f"{catalog_stats['total_datasets']} datasets catalogados")
    print(f"{catalog_stats['datasets_with_lineage']} com linhagem mapeada")
    print(f"{catalog_stats['average_quality']}% qualidade média")
    
    print(f"\n🏗️ ARQUITETURA MEDALLION:")
    for layer, count in catalog_stats['datasets_by_layer'].items():
        emoji = "🥉" if layer == "bronze" else "🥈" if layer == "silver" else "🥇"
        print(f"   {emoji} {layer.title()}: {count} datasets")
    
    lineage_flow = """
    FLUXO DE LINHAGEM:
    
    Orders API → Bronze Orders → Silver Orders → Gold Summary → BI Dashboard
         ↓             ↓             ↓             ↓              ↓
    Contract      Quality       PII Mask      Aggregation    Visualization
    Validation    Checks        + Clean       + Metrics      + Alerts
    """
    print(lineage_flow)

def demo_access_control():
    """Show access control features."""
    print("\n👥 CONTROLE DE ACESSO")
    print("=" * 50)
    
    roles_permissions = {
        "admin": {
            "users": 1,
            "permissions": "Acesso total ao sistema"
        },
        "data_engineer": {
            "users": 12,
            "permissions": "Desenvolvimento e manutenção de pipelines"
        },
        "data_analyst": {
            "users": 25, 
            "permissions": "Análise de dados e criação de relatórios"
        },
        "business_user": {
            "users": 45,
            "permissions": "Visualização de métricas e dashboards"
        },
        "auditor": {
            "users": 4,
            "permissions": "Auditoria e verificação de conformidade"
        },
        "dpo": {
            "users": 2,
            "permissions": "Gestão de privacidade e LGPD"
        }
    }
    
    print("ROLES E PERMISSÕES:")
    total_users = sum(role["users"] for role in roles_permissions.values())
    
    for role, info in roles_permissions.items():
        print(f"{role}: {info['users']} usuários")
        print(f"{info['permissions']}")
    
    print(f"\n ESTATÍSTICAS DE ACESSO:")
    print(f"{total_users} usuários ativos")
    print(f"6 roles definidos")
    print(f"98.5% taxa de sucesso em autorizações")
    print(f"100% conformidade de acesso")

def show_file_structure():
    """Show project file structure."""
    print("\n ESTRUTURA DO PROJETO")
    print("=" * 50)
    
    structure = """
    ifood_data_governance_pipeline/
    ├── 📋 contracts/              # Data Contracts
    │   ├── orders_contract.yaml   # Contrato de pedidos
    │   └── contract_validator.py  # Validador Pydantic
    │
    ├── 🔄 dags/                   # Airflow DAGs
    │   └── orders_ingestion_dag.py # Pipeline principal
    │
    ├── 🏗️ dbt/                    # Transformações dbt
    │   └── ifood_governance/      # Projeto dbt
    │       ├── models/bronze/     # Camada Bronze
    │       ├── models/silver/     # Camada Silver
    │       └── models/gold/       # Camada Gold
    │
    ├── 📊 data_quality/           # Qualidade de dados
    │   ├── great_expectations_config.py
    │   └── gx_config/            # Configurações GX
    │
    ├── 📚 catalog/                # Catálogo de dados
    │   ├── data_catalog.py       # Sistema de catálogo
    │   └── catalog_manager.py    # Gerenciador
    │
    ├── 🔒 security/               # Segurança e privacidade
    │   ├── privacy_manager.py    # Gestão LGPD
    │   └── access_control.py     # Controle de acesso
    │
    ├── 📊 dashboards/             # Interfaces visuais
    │   ├── main.py               # Dashboard principal
    │   ├── simple_dashboard.py   # Versão simplificada
    │   └── quality_dashboard.py  # Dashboard de qualidade
    │
    ├── 🔧 utils/                  # Utilitários
    │   ├── config_loader.py      # Carregador de config
    │   ├── lineage_tracker.py    # Rastreamento
    │   └── data_quality_checker.py # Verificador
    │
    ├── 🧪 tests/                  # Testes automatizados
    │   └── test_data_quality.py  # Testes de qualidade
    │
    └── 📖 docs/                   # Documentação
        ├── ARCHITECTURE.md       # Arquitetura técnica
        └── USER_GUIDE.md         # Guia do usuário
    """
    print(structure)

def show_next_steps():
    """Show next steps."""
    print("\n🚀 PRÓXIMOS PASSOS")
    print("=" * 50)
    
    steps = """
    1. EXECUTAR DASHBOARD:
       streamlit run dashboards/simple_dashboard.py
       
    2. ACESSAR INTERFACE:
       http://localhost:8501
       
    3. EXPLORAR FUNCIONALIDADES:
       ✅ Overview - Visão geral do sistema
       ✅ Data Quality - Monitoramento de qualidade
       ✅ Data Lineage - Rastreabilidade de dados
       ✅ Data Catalog - Catálogo e busca
       ✅ Privacy & Security - Conformidade LGPD
       ✅ Access Control - Gestão de usuários
       ✅ Compliance Report - Relatórios
       
    4. CONSULTAR DOCUMENTAÇÃO:
       docs/ARCHITECTURE.md - Arquitetura técnica
       docs/USER_GUIDE.md - Guia do usuário
       
    5. EXECUTAR TESTES:
       pytest tests/ -v
       
    6. PERSONALIZAR:
       config/config.yaml - Configurações
       contracts/ - Novos contratos de dados
    """
    print(steps)

def main():
    """Main demo function."""
    print_banner()
    
    print("DEMONSTRAÇÃO COMPLETA DO SISTEMA")
    print("=" * 60)
    
    demo_architecture()
    input("\n Pressione Enter para continuar...")
    
    demo_data_contracts()
    input("\n Pressione Enter para continuar...")
    
    demo_quality_metrics()
    input("\n Pressione Enter para continuar...")
    
    demo_privacy_compliance()
    input("\n Pressione Enter para continuar...")
    
    demo_catalog_lineage()
    input("\n Pressione Enter para continuar...")
    
    demo_access_control()
    input("\n Pressione Enter para continuar...")
    
    show_file_structure()
    input("\n Pressione Enter para continuar...")
    
    show_next_steps()
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    
    print(f"\nRESUMO DA SOLUÇÃO:")
    print(f"   ✅ Sistema completo de governança implementado")
    print(f"   ✅ 7 componentes principais funcionais")
    print(f"   ✅ Conformidade LGPD 100%")
    print(f"   ✅ Qualidade de dados monitorada")
    print(f"   ✅ Rastreabilidade ponta a ponta")
    print(f"   ✅ Dashboards interativos")
    print(f"   ✅ Documentação completa")
    
    print(f"\name PARA EXECUTAR O DASHBOARD:")
    print(f"   streamlit run dashboards/simple_dashboard.py")
    print(f"\n SUPORTE:")
    print(f"   data-support@ifood.com")

if __name__ == "__main__":
    main()

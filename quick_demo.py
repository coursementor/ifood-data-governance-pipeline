import subprocess
import sys
import os
import time

def print_banner():
    """Print demo banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║         iFood Data Governance Pipeline Demo                  ║
    ║                                                              ║
    ║  Sistema de governança de dados para delivery com            ║
    ║  rastreabilidade, qualidade e conformidade LGPD              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed."""
    
    required_packages = ['streamlit', 'plotly', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies."""
    
    print("Instalando dependências necessárias...")
    
    try:
        subprocess.run([sys.executable, "install_dependencies.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Erro na instalação de dependências")
        return False

def demo_data_contracts():
    """Demonstrate data contracts concept."""
    print("\n DEMO: Data Contracts")
    print("=" * 50)
    
    print("Contrato de Dados: ifood_orders v1.0.0")
    print("Descrição: Contrato para pedidos do iFood com validação completa")
    print("Owner: data-engineering@ifood.com")
    print("Campos validados: 25+ campos com regras de negócio")
    print("SLA: 99.9% disponibilidade, 5min freshness")
    
    sample_order = {
        'order_id': 'ORD1234567890',
        'customer_id': 'CUST12345678',
        'total_amount': 45.90,
        'status': 'DELIVERED'
    }
    
    print(f"\n Exemplo de validação:")
    print(f"   Order ID: {sample_order['order_id']} ✅ Formato válido")
    print(f"   Customer ID: {sample_order['customer_id']} ✅ Formato válido")
    print(f"   Total: R$ {sample_order['total_amount']} ✅ Valor positivo")
    print(f"   Status: {sample_order['status']} ✅ Status válido")
    print("Validação de contrato: APROVADA (100% sucesso)")

def demo_data_quality():
    """Demonstrate data quality concept."""
    print("\nDEMO: Data Quality")
    print("=" * 50)
    
    print("Métricas de Qualidade (últimas 24h):")
    print("Completude: 95.2% (meta: >95%)")
    print("Validade: 97.1% (meta: >98%)")
    print("Consistência: 92.8% (meta: >90%)")
    print(" Pontualidade: 88.5% (meta: >85%)")
    print("Score Geral: 93.4%")
    
    print("\n Alertas Ativos:")
    print("Campo customer_phone com 5% de valores nulos")
    print("Formato de CPF inválido em 2% dos registros")
    
    print("\n Recomendações:")
    print("Implementar validação mais rigorosa na API")
    print("Configurar alertas automáticos para quedas >5%")

def demo_privacy_security():
    """Demonstrate privacy and security concept."""
    print("\n DEMO: Privacy & Security")
    print("=" * 50)
    
    print("Mascaramento PII Automático:")
    print("Original: CPF 123.456.789-00 → Mascarado: 123.***.789-**")
    print("Original: (11) 99999-9999 → Mascarado: (11) ****-9999")
    print("Original: cliente@email.com → Mascarado: c***@email.com")
    
    print("\n Conformidade LGPD:")
    print("   ✅ 23 campos PII identificados e mascarados")
    print("   ✅ 12 solicitações LGPD processadas este mês")
    print("   ✅ 100% conformidade com retenção de dados")
    print("   ✅ Auditoria completa de acessos")
    
    print("\n Controle de Acesso:")
    print("6 roles definidos (admin, engineer, analyst, business, auditor, dpo)")
    print("89 usuários ativos")
    print("98.5% taxa de sucesso em autorizações")

def demo_data_catalog():
    """Demonstrate data catalog concept."""
    print("\n DEMO: Data Catalog")
    print("=" * 50)
    
    print("Catálogo de Dados:")
    print("156 datasets catalogados")
    print("142 datasets com linhagem mapeada")
    print("93.4% qualidade média")
    
    print("\n Arquitetura Medallion:")
    print("Bronze: 45 datasets (dados brutos)")
    print("Silver: 67 datasets (dados limpos)")
    print("Gold: 44 datasets (dados agregados)")
    
    print("\n Busca e Descoberta:")
    print(" Busca por 'orders': 5 datasets encontrados")
    print(" Tags: delivery, transactional, pii, lgpd")
    print("  Owner: data-engineering@ifood.com")

def start_dashboard():
    """Start the dashboard."""
    print("\n DEMO: Iniciando Dashboard")
    print("=" * 50)
    
    print("Iniciando dashboard interativo...")
    print("URL: http://localhost:8501")
    print("Dashboard com 7 seções principais:")
    print("   📊 Overview - Visão geral do sistema")
    print("   📊 Data Quality - Monitoramento de qualidade")
    print("   📊 Data Lineage - Rastreabilidade de dados")
    print("   📊 Data Catalog - Catálogo e busca")
    print("   📊 Privacy & Security - Conformidade LGPD")
    print("   📊 Access Control - Gestão de usuários")
    print("   📊 Compliance Report - Relatórios de conformidade")
    
    print("\n Pressione Ctrl+C para parar o dashboard")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'dashboards/simple_dashboard.py', 
            '--server.port=8501',
            '--server.headless=true'
        ])
    except KeyboardInterrupt:
        print("\n Dashboard parado pelo usuário")
    except FileNotFoundError:
        print("\n Streamlit não encontrado. Execute: python install_dependencies.py")

def main():
    """Main demo function."""
    print_banner()
    
    missing = check_dependencies()
    if missing:
        print(f"Dependências faltando: {', '.join(missing)}")
        print("Instalando dependências...")
        
        if not install_dependencies():
            print(" Falha na instalação. Tente manualmente:")
            print("   pip install streamlit plotly pandas numpy")
            return
    
    print("Iniciando demonstração do sistema...")
    print("\n" + "=" * 60)
    
    try:
        demo_data_contracts()
        time.sleep(2)
        
        demo_data_quality()
        time.sleep(2)
        
        demo_privacy_security()
        time.sleep(2)
        
        demo_data_catalog()
        time.sleep(2)
        
        print("\n" + "=" * 60)
        print("DEMONSTRAÇÃO CONCEITUAL CONCLUÍDA!")
        print("=" * 60)
        
        response = input("\n Deseja iniciar o dashboard interativo? (y/n): ")
        
        if response.lower() in ['y', 'yes', 's', 'sim']:
            start_dashboard()
        else:
            print("\n Para iniciar o dashboard manualmente:")
            print("   streamlit run dashboards/simple_dashboard.py")
            print("\n Documentação completa em: docs/")
            print(" Suporte: data-support@ifood.com")
            print("\n Principais funcionalidades demonstradas:")
            print("   ✅ Data Contracts com validação automática")
            print("   ✅ Monitoramento de qualidade em 6 dimensões")
            print("   ✅ Mascaramento PII e conformidade LGPD")
            print("   ✅ Catálogo com 156 datasets e linhagem")
            print("   ✅ Controle de acesso com 6 roles")
            print("   ✅ Dashboards interativos com Streamlit")
        
    except Exception as e:
        print(f"\n Erro na demonstração: {e}")
        print(" Tente executar: streamlit run dashboards/simple_dashboard.py")

if __name__ == "__main__":
    main()

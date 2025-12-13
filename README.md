# Ifood Data Governance Pipeline: Quality, Traceability, Security, Compliance Dashboard Insights

[![Releases](https://img.shields.io/badge/Releases-See%20All-blue?logo=github&logoColor=white)](https://github.com/coursementor/ifood-data-governance-pipeline/releases)

Acesse as releases em https://github.com/coursementor/ifood-data-governance-pipeline/releases

Visão geral
- Este repositório mostra uma solução completa de governança de dados com foco em qualidade, rastreabilidade, segurança e conformidade com LGPD. O ecossistema integra ferramentas modernas para entregar um painel de governança de dados interativo e útil no dia a dia das equipes de dados.
- O objetivo é oferecer um conjunto de componentes que funcionam bem juntos, mas que também podem ser usados separadamente. Cada peça foi pensada para ser simples de entender, configurar e estender.

Objetivos e valor
- Garantir qualidade de dados: validação, limpeza, checagem de consistência e observabilidade.
- Rastreabilidade completa: origem dos dados, transformações aplicadas, dependências entre fontes e consumo.
- Segurança e conformidade: controles de acesso, auditoria, masking de dados sensíveis e conformidade com LGPD.
- Ecossistema interativo: dashboards em tempo real, relatórios ad hoc, alertas e observabilidade centralizada.
- Adoção gradual: etapas bem definidas para começar com o essencial e evoluir para capacidades avançadas.

Arquitetura de alto nível
- Orquestração de dados com Airflow: gerencia pipelines, DAGs e tarefas, com logs centralizados.
- Transformações com dbt: modelo de dados, testes de qualidade e documentação integrada.
- Validação com Pydantic: contratos de dados, validação de entrada/saída e mensagens de erro claras.
- Dashboards com Streamlit: interface para governança, monitoramento de qualidade, métricas e exploração de dados.
- Visualização de dados: bibliotecas como Matplotlib, Seaborn e Pandas para gráficos integrados aos fluxos de dados.
- Armazenamento e cache: bancos de dados relacionais para metadados, Redis para cache rápido e PySpark para processamento em grande escala.
- Catálogo e rastreabilidade: catálogo de dados com linhagem, metadados de fontes, transformações e consumo.
- Observabilidade: logs estruturados, métricas, celularidade de dashboards e alertas de anomalias.
- Segurança: controle de acesso baseado em papéis, registros de auditoria e conformidade com LGPD.

Arquitetura detalhada (componentes)
- Airflow: orquestra DAGs, agenda tarefas, gerencia dependências e retries. Logs ficam disponíveis no UI do Airflow e em repositórios de logs para auditoria.
- dbt: gerencia transformações de dados, testes de qualidade, documentação auto gerada e lineage entre modelos. Os modelos de dbt alimentam o data mart utilizado pelos dashboards.
- Streamlit: camada de apresentação que expõe dashboards, painéis de qualidade, auditoria e métricas. Conecta aos modelos de dados e aos resultados de transformações.
- Pydantic: valida contratos de dados entre fontes, valida schemas de entrada e saída, facilita mensagens de erro padronizadas.
- PySpark: processamento em grande escala, especialmente útil para conjuntos de dados volumosos ou operações de transformação que exigem paralelismo.
- Pandas, NumPy, Matplotlib, Seaborn: bibliotecas para análise, manipulação, estatísticas e visualização de dados dentro dos notebooks, scripts de ETL ou componentes do Streamlit.
- Redis: cache para melhorar resposta de dashboards, sessões de usuário e resultados de consultas repetidas.
- Dados e segurança: camadas de criptografia, masking, controle de acesso, políticas de LGPD aplicadas a dados sensíveis.

Tecnologias e stack
- Orquestração: Apache Airflow
- Transformação de dados: dbt
- Interface e visualização: Streamlit, Matplotlib, Seaborn
- Validação de dados: Pydantic
- Processamento de dados: PySpark
- Almacenamento e metadados: bancos de dados relacionais, data catalog, Redis
- Observabilidade: logs estruturados, métricas, alertas
- Linguagens: Python, SQL
- Padrões de dados: contratos de dados, schemas, validação de entrada/saída
- Conformidade: LGPD, governança de dados sensíveis, auditoria

Guia rápido de uso
- Objetivo rápido: ter uma visão consolidada da qualidade de dados, rastreabilidade e conformidade, com dashboards interativos.
- Premissa: um conjunto mínimo de pipelines já integrada, com dados simulados para demonstração.

Guia rápido de configuração (sem Docker)
- Pré-requisitos
  - Python 3.9 ou superior
  - pip atualizado
- Passo a passo
  - clone o repositório: git clone https://github.com/coursementor/ifood-data-governance-pipeline.git
  - crie um ambiente isolado: python -m venv venv && source venv/bin/activate
  - instale dependências: pip install -r requirements.txt
  - configure variáveis de ambiente básicas (exemplos):

    - LGPD_ENABLED=true
    - DATA_LAKE_URL=postgresql://usuario:senha@localhost:5432/bancodados
    - DBT_PROFILE=default
    - AIRFLOW__CORE__EXECUTOR=LocalExecutor

  - inicie os serviços
    - Airflow: export AIRFLOW_HOME=$(pwd)/airflow && airflow db init && airflow scheduler & airflow webserver -p 8080
    - Streamlit: streamlit run apps/gov_dashboard.py --server.port 8501
  - acesse os dashboards
    - Airflow UI: http://localhost:8080
    - Streamlit UI: http://localhost:8501

Guia rápido de configuração com Docker
- Docker facilita a configuração e o isolamento de dependências.
- Requisitos
  - Docker e Docker Compose instalados
- Passos
  - abra o terminal no diretório do projeto
  - execute: docker-compose up --build -d
  - abra: http://localhost:8080 para Airflow; http://localhost:8501 para Streamlit
- Observação
  - a imagem docker do projeto já contém versões específicas de Airflow, dbt e Streamlit para evitar conflitos de dependências.

Como funciona a governança de dados neste projeto
- Qualidade de dados
  - validação de dados na entrada com Pydantic
  - testes de qualidade com dbt
  - dashboards que mostram métricas de qualidade: taxa de preenchimento, duplicidade, conformidade com regras de negócio
- Rastreamento e linhagem
  - catálogos de dados que registram fonte, transformações, dependências
  - visualizações de linhagem que ajudam a entender como um dado percorre o pipeline
- Segurança e LGPD
  - controle de acesso em nível de usuário e papéis
  - masking de dados sensíveis nos ambientes de desenvolvimento
  - rastreabilidade de quem acessou quais dados
  - auditoria de atividades e mudanças no pipeline
- Observabilidade
  - logs centralizados, métricas exportadas para dashboards
  - alertas para falhas de pipelines, quedas de qualidade de dados
- Observabilidade de desempenho
  - tempo de execução de tarefas, uso de recursos, gargalos de transformação

Fluxos de dados e pipelines
- Fluxo de ingestão
  - fontes de dados são conectadas por conectores; validação inicial acontece na camada de entrada
  - dados brutos são armazenados em uma área de landing com logs de ingestão
- Transformação e modelagem
  - dbt orquestra modelos de dados, aplica transformações, valida com testes e gera documentação
  - modelos alimentam o data mart para dashboards
- Validação contínua
  - contratos de dados com Pydantic garantem que mensagens entre etapas estejam corretas
  - testes automatizados asseguram que mudanças não quebrem expectativas
- Visualização e governança
  - Streamlit oferece dashboards com métricas de qualidade, trabalho de linha de dados, conformidade com LGPD
  - os usuários podem explorar dados, ver a proveniência e entender as regras aplicadas

Como usar os recursos para governança prática
- Painel de governança
  - apresenta métricas de qualidade, status de pipelines, mensagens de violação de regras
  - permite explorar datasets, ver cadastro de dados, e entender a origem
- Auditoria
  - logs de execução de DAGs e transformações
  - disponibilidade de métricas de auditoria para auditorias internas ou externas
- Gerenciamento de conformidade LGPD
  - políticas para dados sensíveis, mascaramento de dados em ambientes não seguros
  - controles de acesso para reduzir exibição de dados sensíveis a usuários autorizados
- Observabilidade de pipeline
  - rastreabilidade de falhas, rerun de tarefas com justificativas
  - dashboards de desempenho ajudam equipes a identificar gargalos

Catalogação de dados e linhagem
- Catálogo de dados
  - cada fonte de dados tem metadados, proprietários, frequência de atualização e qualidade esperada
  - os modelos de dbt têm documentação integrada que aparece no catálogo
- Linhagem de dados
  - registra de onde vêm os dados, para onde vão, e as transformações aplicadas
  - facilita auditorias, regressões e impacto de mudanças

Qualidade de dados em profundidade
- Regras e validações
  - regras definidas para formatos, range de valores, unicidade, integridade referencial
  - validação de esquemas com Pydantic para mensagens entre serviços
- Testes de qualidade com dbt
  - testes de unicidade, não nulos, relacionamentos entre tabelas
  - documentação automática dos modelos
- Visualização de qualidade
  - gráficos que mostram evolução de métricas de qualidade ao longo do tempo
  - alertas quando valores saem do esperado

Observabilidade e monitoramento
- Logs estruturados
  - padronização de mensagens para facilitar buscas
- Métricas
  - tempo de execução, taxa de sucesso, taxa de falha, taxa de dados ausentes
- Alertas
  - notificações para falhas críticas, degradação de qualidade de dados
- Dashboards
  - painéis que integram várias fontes de dados e apresentam uma visão unificada

Segurança, LGPD e conformidade
- Princípios-chave
  - least privilege (menor privilégio)
  - minimização de dados
  - accountability (responsabilização)
  - rastreabilidade de acessos e operações
- Práticas implementadas
  - mascaramento de dados sensíveis em ambientes de desenvolvimento
  - logs de auditoria para alterações de dados e acessos
  - políticas de retenção e descarte seguro de dados
- Educação e governança
  - treinamentos simples para equipes de dados sobre LGPD e práticas de governança
  - documentação clara das regras e políticas adotadas

Pydantic e contratos de dados
- Contratos explícitos
  - modelos Pydantic definem como as mensagens devem ser estruturadas
  - ajudam a detectar erros de compatibilidade entre serviços cedo
- Validação contínua
  - validações ocorrem durante ingestão, transformação e exportação
  - mensagens de erro padronizadas facilitam a correção rápida

Processo de desenvolvimento, testes e qualidade
- Organização do código
  - módulos claros para ingestão, transformação, validação, visualização e utilitários
  - padrões simples para facilitar a manutenção
- Testes
  - testes unitários com pytest para validação de funções, modelos e contratos
  - testes de integração para fluxos entre Airflow, dbt e Streamlit
  - validações de dados em pipelines com casos de teste simulados
- Verificações de qualidade de código
  - linting, formatação e checagens estáticas para manter a qualidade do código
- CI/CD
  - pipelines de CI que executam lint, testes e validação de schemas
  - pipelines de CD para implantações seguras de ambientes de produção
  - automação para publicar novas versões no repositório de releases

Guia de contribuição
- Como contribuir
  - criar uma feature branch: git checkout -b feature/nova-funca
  - desenvolver a feature com testes
  - abrir um PR descrevendo a motivação, impactos esperados e como testar
- Regras de estilo
  - código limpo, nomes descritivos, funções curtas
  - documentação de novas APIs ou mudanças de contrato com Pydantic
- Testes
  - incluir casos de borda, dados sensíveis e cenários de LGPD
  - manter a cobertura de testes alta
- Revisões
  - pares revisam PRs para qualidade, segurança e conformidade
  - feedback rápido evita gargalos de entrega

Arquitetura de dados e modelos
- Modelagem
  - esquemas para fontes, transformações, métricas e dashboards
  - contratos de dados definem formatos, tipos e regras de validação
- Dados sensíveis
  - segmentos com dados sensíveis marcados
  - políticas de masking aplicadas conforme o ambiente
- Linhagem
  - a cada etapa do pipeline, a linhagem é atualizada
  - facilita auditorias, mudanças e troubleshoot

Exemplos de uso e casos de negócio
- Cenário de qualidade de dados
  - analista verifica métricas de qualidade no dashboard
  - se valores inconsistentes são detectados, a tarefa de correção é acionada
- Cenário de conformidade
  - dados sensíveis são mascarados em ambientes de desenvolvimento
  - logs de acesso são auditáveis para inspeção
- Cenário de rastreabilidade
  - um dataset pode ser rastreado desde a fonte até o consumidor final
  - mudanças em qualquer etapa aparecem no histórico de linhagem

Estrutura de pastas, convenções e organização do repositório
- Diretórios comuns
  - dags/ ou airflow/ para DAGs do Airflow
  - models/ para modelos dbt
  - pipelines/ para scripts de ETL/ELT
  - apps/ ou dashboards/ para Streamlit
  - tests/ para testes automatizados
  - notebooks/ para exploração de dados
  - config/ para configurações e variáveis de ambiente
- Convenções de nomes
  - nomes descritivos para pipelines, modelos e funções
  - versões explícitas para dependências e contratos
- Documentação
  - docs/ com guias, perguntas frequentes e arquiteturas
  - documentação inline nos módulos com docstrings
- Dados de exemplo
  - datasets simulados para demonstração, sem dados reais

Como verificar a versão mais recente
- O link de releases contém as versões mais recentes da solução e assets para download. Use o seguinte link para explorar as versões disponíveis: https://github.com/coursementor/ifood-data-governance-pipeline/releases
- Observação: se o link contiver uma parte de caminho, baixe o arquivo de release correspondente e execute os scripts ou instale o conteúdo conforme descrito na documentação do release.

Licença
- Este projeto utiliza uma licença aberta para facilitar uso, modificação e compartilhamento. (Se preferir, substitua pelo tipo de licença exato adotado.)

Notas sobre licenças e uso de componentes
- Alguns componentes podem ter licenças específicas. Siga as regras de uso de cada biblioteca (Streamlit, Airflow, dbt, Pydantic, Pandas, etc.) e cite créditos quando necessário.
- Em ambientes reais, esteja atento às políticas de LGPD para dados reais. Teste com dados sintéticos para evitar qualquer exposição acidental de informações sensíveis.

Diagrama de arquitetura (visuais)
- O diagrama de arquitetura mostra a integração entre Airflow, dbt, Pydantic, Streamlit, PySpark, Pandas e Redis.
- Este diagrama pode ser encontrado na documentação oficial do projeto ou em assets da seção de arquitetura. Você pode visualizar a arquitetura através de imagens anexadas no repositório ou diagramas no formato SVG/PNG incluídos no diretório docs/arquitetura.

Perguntas frequentes
- O que é necessário para iniciar?
  - Um ambiente com Python 3.9+, dependências instaladas, e acessos básicos aos componentes (Airflow, Streamlit).
- Como testar a integração entre componentes?
  - Execute um pipeline simples com ingestão, transformação e visualização de resultados. Verifique logs, dashboards e a consistência de dados.
- Posso usar apenas partes do sistema?
  - Sim. Este ecossistema foi desenhado para modularidade. A parte de governança pode ser usada independentemente, assim como a camada de visualização.

Contribuição de qualidade de dados e LGPD
- Contribuímos com controles que ajudam a manter a qualidade de dados e conformidade com LGPD.
- O objetivo é que equipes possam adotar as práticas de governança sem complicações, mantendo a privacidade e a segurança.
- Incentivamos a adoção de práticas de dados éticas e respeitosas.
- Em caso de dúvidas, procure a equipe de governança de dados para orientação.

Guia de configuração avançada
- Configuração de ambiente isolado
  - use um ambiente virtual com isolação total para evitar conflitos com outras bibliotecas
  - gerencie pacotes com ferramentas como pipenv ou poetry para controle de dependências
- Configuração de armazenamento
  - configure o data lake/warehouse conforme as políticas da organização
  - assegure que as credenciais estejam protegidas, usando variáveis de ambiente e serviços de segredo
- Configuração de segurança
  - aplique políticas de acesso com base em papéis
  - mantenha logs de auditoria e mecanismos de monitoramento ativos
- Configuração de LGPD
  - defina regras de masking para dados sensíveis
  - registre atividades de acesso e alterações em dados sensíveis
  - documente as políticas e as exceções em um local de fácil consulta

Notas finais sobre implantação e manutenção
- Este é um ecossistema vivo. Provedores de dados, equipes de segurança e equipes de produto podem precisar ajustar as políticas, as regras e as visualizações ao longo do tempo.
- Mantenha a documentação atualizada, incluindo guias de usuário, guias de administrador e notas de versão.
- Planeje ciclos regulares de revisão de políticas de LGPD, padrões de dados e planos de resposta a incidentes.

Recursos adicionais
- Documentação externa para as tecnologias utilizadas
  - Airflow: guias de DAGs, operadores, sensores e melhores práticas
  - dbt: modelo, testes, documentação e linhagem
  - Pydantic: schemas, validação e contratos de dados
  - Streamlit: construção de dashboards, interações, componentes
  - Pandas, NumPy, Matplotlib, Seaborn: manipulação, estatística e visualização de dados
  - Redis: cache, sessões
  - PySpark: processamento distribuído
- Práticas de governança de dados
  - políticas de qualidade, segurança de dados, rastreabilidade e compliance

Releases
- Para baixar a versão mais recente ou verificar novas atualizações, visite a página de releases em https://github.com/coursementor/ifood-data-governance-pipeline/releases. Em casos de download, baixe o arquivo de release correspondente e execute o conteúdo conforme descrito na documentação do release.
- O arquivo correspondente pode estar disponível na seção de releases; se houver, siga as instruções para baixar, extrair e executar os componentes do release. Voltando ao início, acesse novamente o link para validação rápida: https://github.com/coursementor/ifood-data-governance-pipeline/releases

Observabilidade de dados
- Este projeto enfatiza observabilidade para que equipes de dados possam entender rapidamente o estado dos pipelines e a qualidade dos dados.
- A cobertura de observabilidade inclui logs, métricas, alerta de falhas e contexto para diagnóstico.

Compatibilidade e extensões futuras
- A arquitetura é pensada para evoluir. Futuras expansões podem incluir:
  - Integração com novas fontes de dados
  - Suporte a mais modelos de dados e formatos de arquivo
  - Capacidades adicionais de LGPD, incluindo controles de consentimento e gestão de dados sensíveis
  - Melhorias de UI/UX para dashboards e dashboards interativos
- A comunidade de usuários pode propor melhorias através de pull requests, issues e discussões.

Licença (reiterado)
- Licença: MIT (ou conforme definido pela equipe). Use conforme as políticas da organização e respeite todas as dependências de terceiros.

Recursos visuais
- Imagens de exemplo podem ser incorporadas para ilustrar fluxos de dados, métricas de qualidade e arquitetura.
- Emojis podem ser usados para tornar o README mais acessível, por exemplo: 🧭 para orientação de fluxo, 🔒 para segurança, 📊 para dashboards, 🧪 para testes, 🚦 para estados de pipeline.

Notas finais
- Este repositório busca demonstrar uma solução prática para governança de dados, com foco em usabilidade, qualidade, rastreabilidade, segurança e conformidade com LGPD.
- A equipe convida contribuições que melhorem a clareza, a segurança, o desempenho e a cobertura de governança de dados.

Observações de uso do link de releases (revisado)
- O link de releases contém a versão mais recente e ativos para download. Use o link no início para acessar as versões: https://github.com/coursementor/ifood-data-governance-pipeline/releases
- Se houver um arquivo específico dentro do release, baixe-o e execute os scripts ou siga as instruções de instalação que acompanham o release.
- Você também pode visitar a página de releases a qualquer momento para confirmar a disponibilidade de novas versões e atualizações de componentes do ecossistema.

Fica claro que este projeto é mais do que uma coleção de scripts. Ele consolida práticas sólidas de governança de dados, oferece um caminho claro para equipes de dados adotarem conceitos de qualidade, rastreabilidade, segurança e conformidade, tudo acompanhado por um conjunto de dashboards interativos. O objetivo é tornar a governança tangível e acessível, para que decisões fiquem mais rápidas, seguras e bem fundamentadas.
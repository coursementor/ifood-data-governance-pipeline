# iFood Data Governance - Guia do Usuário

## Introdução

Este guia fornece instruções detalhadas para usar o sistema de governança de dados do iFood. O sistema foi projetado para ser intuitivo e acessível para diferentes perfis de usuários.

## Perfis de Usuário

### Data Engineer
- **Acesso**: Completo a todos os dados e funcionalidades
- **Responsabilidades**: Manutenção de pipelines, qualidade de dados
- **Principais funcionalidades**: Airflow, dbt, Great Expectations

### Data Analyst
- **Acesso**: Leitura e análise de dados (sem PII)
- **Responsabilidades**: Análises de negócio, relatórios
- **Principais funcionalidades**: Dashboards, catálogo, exportação

### Business User
- **Acesso**: Visualização de métricas e relatórios
- **Responsabilidades**: Consumo de insights de negócio
- **Principais funcionalidades**: Dashboards executivos

### Auditor
- **Acesso**: Leitura completa para auditoria
- **Responsabilidades**: Verificação de conformidade
- **Principais funcionalidades**: Logs de acesso, relatórios de conformidade

## Primeiros Passos

### 1. Acesso ao Sistema

1. **Acesse o dashboard**: http://localhost:8501
2. **Faça login** com suas credenciais
3. **Navegue** pelas diferentes seções usando o menu lateral

### 2. Credenciais Padrão (Ambiente de Desenvolvimento)

```
Admin: admin / admin123
Data Engineer: data.engineer / engineer123
Data Analyst: data.analyst / analyst123
Business User: business.user / business123
```

## Usando os Dashboards

### Dashboard Principal

#### Visão Geral
- **Métricas principais**: Datasets catalogados, qualidade média, conformidade
- **Gráficos de tendência**: Qualidade ao longo do tempo, volume de dados
- **Status dos sistemas**: Pipeline, validação, warehouse

#### Navegação
- Use o **menu lateral** para alternar entre seções
- **Filtros** estão disponíveis na barra lateral
- **Métricas** são atualizadas automaticamente

### Dashboard de Qualidade de Dados

#### Monitoramento
- **Score geral**: Média ponderada de todas as dimensões
- **Dimensões**: Completude, validade, consistência, pontualidade
- **Alertas**: Problemas identificados automaticamente

#### Análise Detalhada
```
1. Selecione o período desejado
2. Escolha os datasets para análise
3. Configure as dimensões de interesse
4. Analise os gráficos e métricas
5. Exporte relatórios se necessário
```

## Catálogo de Dados

### Busca de Datasets

#### Busca Simples
1. Digite o **nome do dataset** na caixa de busca
2. Use **filtros** para refinar (camada, domínio, classificação)
3. Clique no dataset para ver **detalhes completos**

#### Busca Avançada
- **Por proprietário**: Encontre datasets por responsável
- **Por tags**: Use tags para categorização
- **Por qualidade**: Filtre por score de qualidade
- **Por classificação**: Filtre por nível de sensibilidade

### Informações do Dataset

Cada dataset contém:
- **Metadados básicos**: Nome, descrição, proprietário
- **Schema**: Estrutura de campos e tipos
- **Linhagem**: Origem e destino dos dados
- **Qualidade**: Métricas e histórico
- **Acesso**: Permissões e logs

## Privacidade e Segurança

### Dados Pessoais (PII)

#### Identificação Automática
O sistema identifica automaticamente:
- CPF, telefone, email
- Endereços de entrega
- Dados de pagamento

#### Mascaramento
- **Automático** na camada Silver
- **Baseado em role** do usuário
- **Configurável** por campo

### Solicitações LGPD

#### Tipos de Solicitação
- **Acesso**: Visualizar dados pessoais
- **Retificação**: Corrigir dados incorretos
- **Exclusão**: Remover dados pessoais
- **Portabilidade**: Exportar dados

#### Processo
```
1. Identifique o titular dos dados
2. Selecione o tipo de solicitação
3. Forneça justificativa
4. Acompanhe o status
5. Receba a resposta no prazo legal
```

## Monitoramento de Qualidade

### Métricas Principais

#### Completude
- **Definição**: % de campos obrigatórios preenchidos
- **Meta**: > 90%
- **Ação**: Investigar campos com alta taxa de nulos

#### Validade
- **Definição**: % de dados em formato correto
- **Meta**: > 90%
- **Ação**: Revisar regras de validação na origem

#### Consistência
- **Definição**: % de dados consistentes entre sistemas
- **Meta**: > 90%
- **Ação**: Verificar lógica de transformação

### Alertas e Notificações

#### Configuração
- **Thresholds**: Defina limites para cada métrica
- **Canais**: Slack, email, dashboard
- **Frequência**: Tempo real, horário, diário

#### Resposta a Alertas
```
1. Receba notificação de problema
2. Acesse dashboard para detalhes
3. Identifique causa raiz
4. Implemente correção
5. Monitore recuperação
```

## Funcionalidades Avançadas

### Linhagem de Dados

#### Visualização
- **Upstream**: De onde vêm os dados
- **Downstream**: Para onde vão os dados
- **Transformações**: Como são processados

#### Análise de Impacto
- Identifique **dependências** antes de mudanças
- Avalie **impacto** de problemas de qualidade
- Planeje **manutenções** com segurança

### Exportação de Dados

#### Formatos Suportados
- CSV, JSON, Excel
- Parquet (para grandes volumes)
- PDF (relatórios)

#### Limites por Role
- **Business User**: 10.000 linhas
- **Data Analyst**: 100.000 linhas
- **Data Engineer**: Sem limite

### APIs

#### Endpoints Principais
```
GET /api/catalog/datasets - Listar datasets
GET /api/quality/reports - Relatórios de qualidade
POST /api/privacy/request - Solicitação LGPD
GET /api/lineage/{id} - Linhagem de dataset
```

## Solução de Problemas

### Problemas Comuns

#### "Acesso Negado"
- **Causa**: Permissões insuficientes
- **Solução**: Contate administrador para revisar roles

#### "Dados não Atualizados"
- **Causa**: Pipeline com falha
- **Solução**: Verifique status no dashboard de sistemas

#### "Qualidade Baixa"
- **Causa**: Problemas na fonte de dados
- **Solução**: Analise alertas e contate responsável

### Contatos de Suporte

#### Por Tipo de Problema
- **Acesso e Permissões**: data-access@ifood.com
- **Qualidade de Dados**: data-quality@ifood.com
- **Privacidade/LGPD**: privacy@ifood.com
- **Suporte Técnico**: data-support@ifood.com

#### SLA de Suporte
- **Crítico**: 2 horas
- **Alto**: 4 horas
- **Médio**: 1 dia útil
- **Baixo**: 3 dias úteis

## Recursos Adicionais

### Documentação
- **Arquitetura**: Visão técnica completa
- **API Reference**: Documentação de APIs
- **Deployment Guide**: Guia de instalação

### Treinamentos
- **Básico**: Uso de dashboards (2h)
- **Intermediário**: Catálogo e qualidade (4h)
- **Avançado**: APIs e integração (8h)

### Comunidade
- **Slack**: #data-governance
- **Wiki**: Conhecimento compartilhado
- **Office Hours**: Terças 14h-15h

## Atualizações e Novidades

### Changelog
- **v1.0.0**: Lançamento inicial
- **v1.1.0**: Melhorias de performance
- **v1.2.0**: Novos conectores

### Roadmap
- **Q2 2024**: Self-service analytics
- **Q3 2024**: ML para anomalias
- **Q4 2024**: Data mesh completo

---

**Última atualização**: Ago 2025 
**Versão do sistema**: 1.0.0  

---
tipo: contexto
projeto: memoria-de-projeto
descricao: Log de decisões fechadas, com data, razão e o que cada uma fecha.
estado: estavel
criado: 2026-09-12
---

# Decisões

> **Ler antes de reabrir qualquer discussão.** Este arquivo existe pra não decidir duas
> vezes — e, mais importante, pra que a alternativa descartada continue registrada com o
> motivo pelo qual caiu.
>
> Decisão que ainda está sendo tomada **não mora aqui**: mora em [`discussoes/`](discussoes/).

## Método e Governança {#metodo}

- [2026-09-12] (d) **Autonomia assistida para as IAs.**
  **Por quê:** Acelera o desenvolvimento diário permitindo que as IAs implementem detalhes técnicos de código e documentem com `(i)`, enquanto Pedro Pompeu retém a validação `(d)` de arquitetura, regras de negócio e inclusão de dependências.
  **Fecha:** Incertezas sobre até onde a IA pode ir sem autorização prévia.
  **Descartado:** Autonomia cega (onde a IA altera arquitetura sem aviso) e microgerenciamento restritivo (onde a IA precisa de aprovação para qualquer linha de código).

- [2026-09-12] (d) **Padrão de Commits: Conventional Commits em inglês e sem co-autoria.**
  **Por quê:** Padroniza o histórico do Git no padrão internacional (`feat:`, `fix:`, `chore:`, `refactor:`) e mantém autoria limpa sem a linha `Co-Authored-By`.
  **Fecha:** Formatação e idioma de mensagens de commit para todas as IAs.
  **Descartado:** Commits em português ou mensagens livres despadronizadas.

## Sistema e Arquitetura {#infraestrutura}

- [2026-09-12] (d) **Adoção da memória de projeto versionada em arquivos (`context/` e `fontes/`).**
  **Por quê:** Garante persistência contextual de longo prazo entre diferentes sessões e ferramentas de IA (Claude, Antigravity, Cursor) sem inflar a janela de contexto e com rastro de auditoria.
  **Fecha:** Elimina a necessidade de reexplicar decisões e arquitetura a cada nova sessão de IA.
  **Descartado:** Prompts monolíticos gigantescos e dependência de memória proprietária volátil.

- [2026-09-12] (d) **Foco híbrido: produtos próprios da holding e demandas sob medida para clientes.**
  **Por quê:** O ecossistema engloba tanto plataformas proprietárias (ViaXen, PomPay, NarraVox) quanto soluções sob demanda para clientes, exigindo rigor técnico e separação clara de escopos.
  **Fecha:** Modelo operacional do repositório e da orquestração de IAs.
  **Descartado:** Tratar todos os repositórios como projetos descartáveis de cliente ou exclusivamente internos.

## Frontend e Integração {#frontend}

- [2026-09-19] (d) **Migração do frontend de HTML/Jinja2 para React + Vite desacoplado.**
  **Por quê:** Pedro Pompeu autorizou a criação de `frontend/` com React (Vite) como SPA headless consumindo exclusivamente `/api/v1/*` via Axios/fetch — alinhado ao modelo "backend headless" já declarado no `docker-compose.yml` e `README.md`.
  **Fecha:** Tecnologia de frontend e modelo de integração entre frontend e backend.
  **Descartado:** Manter HTML/Jinja2 legado como único frontend (limita escalabilidade e impede separação de responsabilidades).

- [2026-09-19] (d) **Implementação da Fase 1: Motor de IA Avançado (NER, Sentimento, Fraude, Tons, Quarentena e Fallback Multi-LLM).**
  **Por quê:** Validação com Pedro Pompeu para diferenciar o produto com inteligência corporativa. Extração estruturada de entidades financeiras (NER: valores, datas, documentos), análise de urgência e sentimento, detecção de fraude/phishing com score de risco, quarentena automática de baixa confiança (`confidence_score < 0.70`), múltiplos tons de resposta (`formal`, `empatico`, `negociacao`, `juridico`, `direto`), suporte a categorias dinâmicas por tenant e `FallbackLLMProvider` para alta disponibilidade.
  **Fecha:** Capacidades do motor de processamento de inteligência artificial corporativa.
  **Descartado:** IA com saída não estruturada em texto livre ou dependência de provedor único sem fallback.

## Compliance, Governança & Analytics {#compliance-analytics}

- [2026-09-19] (d) **Implementação da Fase 3: Compliance LGPD, Filtro DLP de Saída e Dashboard de ROI.**
  **Por quê:** Validação com Pedro Pompeu para atendimento a exigências regulatórias do setor bancário/financeiro. Implementação do `ComplianceService` e `compliance_routes.py` cobrindo Direito ao Esquecimento (anonimização irreversível) e Exportação de Dados do Titular (LGPD Art. 18/19), expurgo periódico por retenção de dados parametrizada por tenant, filtro DLP de saída inspecionando e mascarando credenciais/APIs/IPs internos antes da exibição ao operador e dashboard com métricas de ROI (horas e valor economizado em BRL), acurácia e taxa de quarentena.
  **Fecha:** Requisitos de governança e mensuração de valor financeiro da plataforma.
  **Descartado:** Armazenamento indefinido sem expurgo e saída de dados sem inspeção de perda de dados.

## Workflows, Colaboração & Automação {#workflows-automacao}

- [2026-09-19] (d) **Implementação da Fase 4: Workflows de Atendimento, Notas Internas e Motor de Roteamento / SLA.**
  **Por quê:** Validação com Pedro Pompeu para permitir trabalho colaborativo entre operadores e automações avançadas. Inclusão de `InternalNote` para comunicação privada da equipe na thread, controle de `status` e `assigned_to_user_id` em `EmailAnalysis`, e `RoutingEngineService` com tabela `routing_rules` para automação de quarentena, escalonamento de urgência e alertas de SLA por regras configuráveis por tenant.
  **Fecha:** Orquestração operacional de triagem em time e motor de regras automáticas.
  **Descartado:** Fluxo estático sem atribuição e sem suporte a notas internas entre operadores.





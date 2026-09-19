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

## Organização do Repositório {#organizacao}

- [2026-09-18] (d) **Reestruturação profunda: remoção de ~35 arquivos redundantes e consolidação de docs.**
  **Por quê:** O repositório acumulou ~20 documentos markdown gerados por IA em sessões distintas (COMECE_AQUI.txt, COMO_RODAR.txt, START_HERE.md, QUICKSTART.md, INDEX.md, etc.), 4 shell scripts redundantes com o Makefile, o `app.py` original obsoleto (substituído por `backend/`), lixo de pip (`=0.8.0`, `=1.0.0`, `=4.3.0`), e artefatos de build não versionáveis. Pedro Pompeu autorizou autonomia total para criar e deletar arquivos.
  **Fecha:** Estrutura confusa do repositório, docs redundantes, e presença de código morto.
  **Descartado:** Manter os ~20 documentos por "segurança" (informação redundante mais atrapalha que ajuda) ou mover para um subdiretório `docs/` (aumentava complexidade sem valor, já que o README consolidado cobre tudo).


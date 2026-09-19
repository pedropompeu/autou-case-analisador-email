---
tipo: contexto
projeto: memoria-de-projeto
descricao: Visão do produto, proposta de valor, público-alvo e regras de negócio centrais.
estado: estavel
criado: 2026-09-12
relacionado:
  - context/arquitetura.md
  - context/decisoes.md
---

# Produto e Regras de Negócio

> O que este sistema entrega, quem se beneficia e quais regras de negócio regem a operação.

## Visão Geral e Proposta de Valor {#visao}

- [2026-09-12] (d) **Sistema de Engenharia e Memória de Projeto Contínua.**
- [2026-09-12] (d) **Propósito:** Permitir que Pedro Pompeu desenvolva projetos de alta escala com suporte de IAs autônomas, mantendo contexto completo sem dependência de histórico efêmero de chat.

## Modelo Operacional Híbrido {#modelo}

- [2026-09-12] (d) **Holding / Produtos Próprios:**
  - Foco em escalabilidade, arquitetura limpa e evolução a longo prazo.
  - O código e o contexto pertencem integralmente ao ecossistema do projeto.
- [2026-09-12] (d) **Demandas sob Medida para Clientes:**
  - Foco em escopo fechado, segurança, isolamento de dados e conformidade técnica.
  - Nenhum dado confidencial de cliente é compartilhado entre repositórios distintos.

## Regras de Negócio e Engenharia {#regras}

- [2026-09-12] (d) **Autonomia Assistida Obrigatória:**
  - A IA pode implementar código, refatorar e criar testes de forma autônoma (registrando como `(i)`).
  - Qualquer decisão que envolva mudança de arquitetura, adição de bibliotecas externas ou alteração em regras de negócio exige validação direta com Pedro Pompeu `(d)`.
- [2026-09-12] (d) **Padrão de Entrega:**
  - Commits exclusivamente no padrão Conventional Commits em inglês (`feat:`, `fix:`, `refactor:`, `chore:`, etc.).
  - Nenhuma mensagem de commit deve conter menções ou créditos automáticos a IA (`Co-Authored-By`).

## Critérios de Qualidade {#qualidade}

- [2026-09-12] (d) Todo código entregue deve ser acompanhado de validação (execução de linter, testes automatizados ou checagem estática).
- [2026-09-12] (i) A integridade do grafo de documentação deve ser verificada via `python lint.py` antes da conclusão de qualquer ciclo de trabalho.

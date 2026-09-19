---
tipo: indice
projeto: memoria-de-projeto
descricao: Roteamento do contexto: o que cada arquivo tem e quando carregar.
estado: estavel
criado: 2026-09-12
---

# Contexto — Memória de Projeto (Pedro Pompeu)

Índice de roteamento. **Ler este arquivo primeiro e carregar só o que a tarefa pede.**
Cada linha diz o que o arquivo tem e quando ele importa.

> **Rota, não memória.** Nenhum fato mora num índice — sem data, sem `(d)/(i)/(e)`, sem
> número, sem valor negociado. Se um fato só existe aqui, ele está no lugar errado. A
> única exceção é a régua do projeto, abaixo.

## Os arquivos

| Arquivo | O que tem | Carregar quando |
|---|---|---|
| [`produto.md`](produto.md) | Visão, modelo operacional híbrido e regras de negócio | Avaliar escopo, priorizar tarefas ou entender regras de negócio |
| [`arquitetura.md`](arquitetura.md) | Stack e o mapa do código **verificado por leitura**, contra o que foi declarado | Ler ou escrever código, estimar esforço |
| [`achados.md`](achados.md) | Bugs, furos e dívidas, com severidade, local, repro e fix. Formato em `#formato` | Antes de mexer em áreas críticas ou finalizar tarefas |
| [`decisoes.md`](decisoes.md) | Log de decisões fechadas, com data, razão e alternativas descartadas | Antes de tomar decisões ou reabrir discussões |
| [`discussoes/`](discussoes/) | Discussões **em aberto**, uma por arquivo. Viram fato em `decisoes.md` quando fecham | Retomar um assunto travado |
| [`../fontes/`](../fontes/index.md) | Material bruto: mensagem, spec, contrato, transcript | Auditar de onde veio um fato `(e)` |

## Discussões em aberto

*Nenhuma discussão em aberto no momento. Use [`discussoes/_template.md`](discussoes/_template.md) para iniciar um novo tópico.*

## Régua que vale pro projeto inteiro

- [2026-09-12] (d) **Toda IA deve consultar context/index.md antes de agir.** Carregar apenas os arquivos necessários para a tarefa atual para preservar foco e janela de contexto.
- [2026-09-12] (d) **Autonomia assistida de Pedro Pompeu.** Implementação técnica e refatoração são livres `(i)`; mudanças de arquitetura, dependências e regras de negócio exigem validação prévia com Pedro `(d)`. Ver [[produto#regras]] e [[decisoes#metodo]].
- [2026-09-12] (d) **Commits em inglês sem co-autoria:** Todo commit deve seguir o padrão Conventional Commits em inglês (ex: `feat:`, `fix:`) sem incluir créditos a IA (`Co-Authored-By`).

## Convenções

- **Todo fato leva data** `[YYYY-MM-DD]` e **procedência**: `(d)` dito por Pedro Pompeu /
  `(i)` inferido pela IA / `(e)` externo (código, docs, ferramentas).
- **Nunca deletar fato.** Marcar `~superseded` e apontar pro novo:
  `- [2026-08-03 ~superseded 2026-09-12] ~~fato velho~~ → fato novo.`
- **`(i)` nunca sustenta outro `(i)`.** Dois saltos de inferência = perguntar e registrar
  a resposta como `(d)`. Inferência confirmada vira `(d ~confirmado, era (i))`.
- **Arestas tipadas** inline, vocabulário fechado: `justifica`, `tensiona`, `bloqueia`,
  `evidencia`, `substitui`. Ancorar em seção: `[[arquivo#secao]]`.
- **Fato que vai vencer** carrega `revisar: YYYY-MM-DD` no fim da linha. Documento que
  vence por inteiro carrega `vence:` no frontmatter.
- **Âncora explícita** `{#slug}` em todo título que alguém pode querer linkar.
- **Nome de arquivo é único no repo inteiro**, o que permite `[[arquivo]]` sem caminho.
- **Documento morto não se apaga:** `estado: obsoleto` no frontmatter, mantendo links vivos.

## Frontmatter dos arquivos de contexto

```yaml
---
tipo: contexto | indice
projeto: memoria-de-projeto
descricao: Uma frase só. É daqui que a linha do índice é escrita.
estado: rascunho | estavel | obsoleto
vence: YYYY-MM-DD        # opcional, só pro que envelhece por inteiro
criado: YYYY-MM-DD
relacionado: [...]       # opcional: arquivos de que este depende ou que o contradizem
---
```

---
tipo: contexto
projeto: <slug>
descricao: <O assunto em uma frase.>
estado: aberta
criado: <YYYY-MM-DD>
relacionado:
  - context/decisoes.md
---

# <Assunto>

> Discussão **em aberto**. Quando fechar: o fato migra pra `decisoes.md`, esta página vira
> `estado: fechada` e ganha, no topo, o link pra decisão. O arquivo **não se apaga** — é
> onde vive o raciocínio que a decisão comprimiu.

## A pergunta {#pergunta}

<O que precisa ser decidido, e o que trava enquanto não for.>

- [<YYYY-MM-DD>] (i) **Bloqueia:** <o que não anda por causa disso> — ou **não bloqueia
  nada**, e nesse caso dizer isso explicitamente, senão a discussão vira urgência falsa.

## O que já se sabe {#sabido}

- [<YYYY-MM-DD>] (e) ← `fontes/<arquivo>` <O que veio de fora e restringe a decisão.>
- [<YYYY-MM-DD>] (d) <O que você já decidiu que não está em jogo.>

## Opções {#opcoes}

| Opção | A favor | Contra | Custo |
|---|---|---|---|
| <A> | <...> | <...> | <...> |
| <B> | <...> | <...> | <...> |

## Default adotado enquanto não fecha {#default}

- [<YYYY-MM-DD>] (i) **<O que vale hoje, na ausência de decisão.>** Adotar um default é o
  que impede a discussão aberta de virar bloqueio. Ele é revogável sem custo até
  `revisar: <YYYY-MM-DD>`.

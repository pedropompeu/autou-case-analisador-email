---
tipo: contexto
projeto: memoria-de-projeto
descricao: Bugs, furos e dívidas encontrados, com severidade, local, reprodução e fix.
estado: estavel
criado: 2026-09-12
relacionado:
  - context/arquitetura.md
---

# Achados

> Lista de riscos técnicos, bugs e dívidas conhecidas. Deve ser lida **antes de dizer que algo está pronto** ou antes de modificar componentes críticos.

## Formato obrigatório {#formato}

- [2026-09-12] (d) **Achado sem reprodução é opinião.** Todo achado leva severidade, localização, reprodução e fix recomendado.
- [2026-09-12] (d) **A severidade se justifica em consequência, não em categoria.** A consequência prática para o usuário/negócio precede o jargão técnico.

```markdown
### [ID] Título curto, em consequência, não em jargão

- **Severidade:** crítico | alto | médio | baixo — e a frase que a justifica em consequência
- **Onde:** caminho/do/arquivo.ext:123
- **Reprodução:** os passos exatos. Se estático, especificar o motivo
- **Por que importa:** o que acontece na prática com o usuário ou sistema
- **Fix recomendado:** o que fazer, com custo aproximado
- **Estado:** aberto | reportado | corrigido | verificado
```

- [2026-09-12] (i) Registrar achados com impacto direto impede que correções cosméticas passem na frente de falhas funcionais.

## O que NÃO é achado {#nao-achado}

> Comportamento declarado como intencional, decisão já tomada e limitação conhecida de ambiente. Registrar aqui evita reabrir discussões já resolvidas.

- [2026-09-12] (d) Comportamentos esperados e tradeoffs documentados em [[decisoes#infraestrutura]] não constituem achados.

## Abertos

*Nenhum achado crítico aberto no momento. Quando novas pendências forem identificadas, adicione-as seguindo o formato acima.*

## Fechados

*Nenhum achado arquivado.*

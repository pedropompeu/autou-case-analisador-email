# Memória de Projeto — Orquestração Autônoma de Agentes e IAs (Pedro Pompeu)

Diretrizes obrigatórias para qualquer agente autônomo operando nos projetos de Pedro Pompeu (produtos próprios da holding e soluções para clientes).

## Protocolo de Memória Sob Demanda
- **Não carregue todo o diretório `context/` no contexto.**
- Leia `context/index.md` primeiro e acesse unicamente o arquivo correspondente à sua tarefa:
  - Análise de código / arquitetura: `context/arquitetura.md` + `context/achados.md`
  - Regras de negócio e produto: `context/produto.md`
  - Decisões anteriores: `context/decisoes.md`
  - Discussões abertas: `context/discussoes/`
  - Fontes externas auditáveis: `fontes/index.md`

## Autonomia Assistida e Atualização Contínua
Durante a execução de qualquer tarefa:
1. **Autonomia técnica `(i)`:** O agente tem autonomia para implementar, refatorar e testar código, registrando decisões técnicas em `context/decisoes.md` com `(i)`.
2. **Validação prévia com Pedro Pompeu `(d)`:** Alterações arquiteturais, adição de bibliotecas externas e modificação de regras de negócio exigem validação prévia com Pedro Pompeu, registradas como `(d)`.
3. **Achados:** Ao encontrar riscos, bugs ou inconsistências, registre em `context/achados.md` (formato em `#formato`).
4. **Arquitetura:** Atualize `context/arquitetura.md` ao introduzir novas estruturas, scripts ou pontos de integração.
5. **Fontes:** Salve dados brutos em `fontes/YYYY-MM-DD-origem-assunto.ext` e referencie como `(e)`.

## Convenções Rígidas
- **Commits em inglês e sem co-autoria:** Todo commit deve utilizar Conventional Commits em inglês (`feat:`, `fix:`, `chore:`, etc.) e jamais incluir linha `Co-Authored-By`.
- **Formato de fatos:** Toda linha declaratória deve começar com data `[YYYY-MM-DD]` e procedência `(d)` dito por Pedro Pompeu, `(i)` inferido pelo agente, ou `(e)` externo.
- **Preservação histórica:** Proibido deletar fatos existentes. Utilize sempre a notação `~superseded`:
  `- [YYYY-MM-DD ~superseded YYYY-MM-DD] ~~texto anterior~~ → texto atualizado.`
- **Inferência direta:** `(i)` nunca sustenta outro `(i)`. Em dois saltos lógicos, valide com Pedro Pompeu e registre como `(d)`.
- **Integridade:** Sempre execute `python lint.py` antes de concluir para garantir conformidade do grafo.

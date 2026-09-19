# Memória de Projeto — Orquestração Autônoma (Pedro Pompeu)

Diretrizes de engenharia e orquestração para Claude Code no ecossistema de projetos de Pedro Pompeu (produtos próprios da holding e soluções sob medida para clientes).

## Antes de responder ou executar qualquer tarefa

1. Consulte sempre `context/index.md`.
2. **Carregue sob demanda apenas os arquivos que a tarefa pede**:
   - **Mexer em código ou inspecionar estrutura:** `context/arquitetura.md` + `context/achados.md`
   - **Regras de negócio, visão e escopo:** `context/produto.md`
   - **Antes de considerar tarefa pronta ou mexer em área crítica:** `context/achados.md`
   - **Decisões arquiteturais ou técnicas:** `context/decisoes.md`
   - **Retomar discussões em aberto:** `context/discussoes/`
   - **Consultar material bruto ou referências:** `fontes/index.md`

## Autonomia Assistida e Governança

- **Implementação autônoma `(i)`:** A IA tem autonomia para implementar código, refatorar funções e criar testes automatizados, documentando escolhas técnicas em `context/decisoes.md` com `(i)`.
- **Validação com Pedro Pompeu `(d)`:** Mudanças de arquitetura, adição de novas dependências/bibliotecas e alteração em regras de negócio exigem confirmação explícita prévia com Pedro Pompeu e devem ser registradas como `(d)`.
- **Achados e Riscos:** Se encontrar bug, vulnerabilidade ou débito técnico, registre imediatamente em `context/achados.md` seguindo o formato padrão.
- **Arquitetura Viva:** Ao criar novas pastas, serviços ou alterar dependências, atualize `context/arquitetura.md`.

## Regras Duras do Projeto

1. **Conventional Commits em Inglês:** Todo commit gerado pela IA deve seguir a especificação Conventional Commits em inglês (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`).
2. **Sem co-autoria:** Nunca incluir `Co-Authored-By` ou qualquer linha de menção à IA nas mensagens de commit.
3. **Data e procedência:** Toda linha declaratória inicia com data `[YYYY-MM-DD]` e tag `(d)` dito por Pedro Pompeu, `(i)` inferido pela IA, ou `(e)` externo (código/documentos).
4. **Preservação de fatos:** Fato nunca se apaga. Use sempre `~superseded YYYY-MM-DD` apontando para o fato novo.
5. **Validação mecânica:** Execute `python lint.py` antes de concluir tarefas relevantes para certificar a integridade do grafo.

# -*- coding: utf-8 -*-
"""
Lint da wiki de contexto.

Uso:  python lint.py [--data YYYY-MM-DD]

Checa o que é MECÂNICO: link quebrado, frontmatter incompleto, validade vencida,
página órfã, índice desatualizado, fato sem procedência, fonte não ingerida.

O que exige JULGAMENTO — este fato ainda vale? estes dois se contradizem? — não é
daqui. O script junta a evidência; a decisão é sua.

Sai com código 1 se houver achado, 0 se estiver limpo. Serve de pre-commit.
"""
from __future__ import print_function
import io, os, re, sys, datetime, codecs

# ══════════════════════════════════════════════════════════════════ CONFIG ══
# Calibrar aqui e não mexer no resto.

CTX = 'context'          # pasta do conhecimento destilado
FONTES = 'fontes'        # pasta do material bruto (deixar '' se não usar)

# Campos que todo arquivo de contexto precisa ter no frontmatter.
CAMPOS_OBRIGATORIOS = ('tipo', 'descricao', 'estado')

ESTADOS_VALIDOS = (None, 'rascunho', 'estavel', 'obsoleto', 'aberta', 'fechada')

# Data em que a convenção de procedência (d)/(i)/(e) passou a valer neste repo.
# Fato anterior a ela não é erro, é dívida — o lint agrupa por arquivo pra não
# afogar o relatório. Num repo novo, use a data de hoje.
CONVENCAO = '2026-09-12'

# True  = toda pasta de context/ precisa de index.md (wiki navegável, repo grande).
# False = context/ é plano, só o index.md da raiz roteia (o caso comum em projeto
#         de código, onde discussoes/ é listada pelo índice do pai).
EXIGE_INDEX_POR_PASTA = False

LIMITE = 12              # quantos achados mostrar por categoria
# ════════════════════════════════════════════════════════════════════════════

if sys.version_info[0] == 2:                      # console do Windows nao e utf-8
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
elif hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RESERVADO = ('index.md',)

hoje = datetime.date.today().isoformat()
for i, a in enumerate(sys.argv):
    if a == '--data':
        hoje = sys.argv[i + 1]


def md_files(base):
    for root, dirs, fs in os.walk(base):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in sorted(fs):
            if f.endswith('.md'):
                yield os.path.join(root, f).replace(os.sep, '/')


def chave(p):
    """Alvo de wikilink: nome do arquivo, ou caminho da pasta pra index.md."""
    if os.path.basename(p) == 'index.md':
        d = os.path.dirname(p)
        return CTX if d == CTX else d[len(CTX) + 1:] if d.startswith(CTX + '/') else d
    return os.path.basename(p)[:-3]


def frontmatter(s):
    if not s.startswith('---\n'):
        return None
    fim = s.find('\n---', 4)
    if fim < 0:
        return None
    fm = {}
    for l in s[4:fim].split('\n'):
        m = re.match(r'^([a-z_]+):\s*(.*)$', l)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


if not os.path.isdir(CTX):
    print(u'sem pasta %s/ aqui. Rodar da raiz do projeto.' % CTX)
    sys.exit(1)

docs = {}
for p in md_files(CTX):
    s = io.open(p, encoding='utf-8').read()
    docs[p] = {
        'src': s,
        'chave': chave(p),
        'fm': frontmatter(s),
        'ancoras': set(re.findall(r'\{#([\w-]+)\}', s)),
        'indice': os.path.basename(p) in RESERVADO,
    }

por_chave = dict((d['chave'], p) for p, d in docs.items())
achados = []


def add(cat, msg):
    achados.append((cat, msg))


# ---------------------------------------------------------------- 1. links
entradas = dict((p, 0) for p in docs)
for p, d in docs.items():
    corpo = re.sub(r'`[^`\n]*`', '', d['src'])          # ignora exemplo em code span
    for m in re.finditer(r'\[\[([\w\-/]+)(#([\w-]+))?\]\]', corpo):
        alvo, anc = m.group(1), m.group(3)
        if alvo not in por_chave:
            add('link', u'%s → arquivo inexistente [[%s]]' % (p, alvo))
            continue
        destino = por_chave[alvo]
        if destino != p:
            entradas[destino] += 1
        if anc and anc not in docs[destino]['ancoras']:
            add('link', u'%s → âncora inexistente [[%s#%s]]' % (p, alvo, anc))

# ---------------------------------------------------------- 2. frontmatter
for p, d in sorted(docs.items()):
    fm = d['fm']
    if fm is None:
        add('frontmatter', u'%s → sem frontmatter parseável' % p)
        continue
    for campo in CAMPOS_OBRIGATORIOS:
        if not fm.get(campo):
            add('frontmatter', u'%s → falta `%s:`' % (p, campo))
    if fm.get('estado') not in ESTADOS_VALIDOS:
        add('frontmatter', u'%s → estado inválido: %s' % (p, fm['estado']))

# ------------------------------------------------------------ 3. validade
for p, d in sorted(docs.items()):
    fm = d['fm'] or {}
    if fm.get('vence') and fm['vence'] <= hoje:
        add('validade', u'%s → documento venceu em %s' % (p, fm['vence']))
    for m in re.finditer(r'`revisar: (\d{4}-\d{2}-\d{2})`', d['src']):
        if m.group(1) <= hoje:
            linha = d['src'][:m.start()].count('\n') + 1
            add('validade', u'%s:%d → fato pede revisão desde %s' % (p, linha, m.group(1)))

# -------------------------------------------------------------- 4. órfãos
for p, d in sorted(docs.items()):
    if d['indice'] or p == CTX + '/index.md' or os.path.basename(p).startswith('_'):
        continue
    if entradas[p] == 0 and ('](%s)' % os.path.basename(p)) not in docs.get(CTX + '/index.md', {}).get('src', ''):
        add('orfao', u'%s → nenhum link de entrada (invisível pela navegação)' % p)

# ------------------------------------------------- 5. índice desatualizado
for root, dirs, fs in os.walk(CTX):
    dirs[:] = [d for d in dirs if d != '.git']
    root = root.replace(os.sep, '/')
    idx = root + '/index.md'
    if idx not in docs:
        if EXIGE_INDEX_POR_PASTA:
            add('indice', u'%s/ → pasta sem index.md' % root)
        continue
    corpo = docs[idx]['src']
    for f in sorted(fs):
        if not f.endswith('.md') or f == 'index.md' or f.startswith('_'):
            continue
        if ('[[%s' % f[:-3]) not in corpo and ('](%s)' % f) not in corpo:
            add('indice', u'%s → não lista %s' % (idx, f))
    for sub in sorted(dirs):
        alvo = (root + '/' + sub)[len(CTX) + 1:]
        if ('[[%s]]' % alvo) not in corpo and ('[[%s]]' % sub) not in corpo \
           and ('](%s/' % sub) not in corpo:
            add('indice', u'%s → não lista a subpasta %s/' % (idx, sub))

# ------------------------------------------------------- 6. forma do fato
FATO = re.compile(r'^\s*-\s+\[(\d{4}-\d{2}-\d{2})')
for p, d in sorted(docs.items()):
    legado, novos = 0, []
    for n, l in enumerate(d['src'].split('\n'), 1):
        m = FATO.match(l)
        if m and not re.search(r'\((d|i|e)[^)]*\)', l):
            if m.group(1) <= CONVENCAO:
                legado += 1
            else:
                novos.append(n)
    for n in novos:
        add('procedencia', u'%s:%d → fato NOVO sem (d)/(i)/(e)' % (p, n))
    if legado:
        add('legado', u'%s → %d fatos anteriores a %s, sem procedência' % (p, legado, CONVENCAO))

# --------------------------------------------------------------- 7. fontes
if FONTES and os.path.isdir(FONTES):
    citadas = set()
    for d in docs.values():
        citadas.update(re.findall(FONTES + r'/[\w\-./]+', d['src']))
    for root, dirs, fs in os.walk(FONTES):
        dirs[:] = [x for x in dirs if x != '.git']
        for f in sorted(fs):
            p = os.path.join(root, f).replace(os.sep, '/')
            if f == 'index.md':
                continue
            if p not in citadas:
                add('fonte', u'%s → fonte nunca citada (ingestão pendente?)' % p)

# ---------------------------------------------------------------- relatório
TITULOS = [
    ('link',        u'Links quebrados'),
    ('frontmatter', u'Frontmatter incompleto'),
    ('validade',    u'Validade vencida (olhar primeiro)'),
    ('orfao',       u'Páginas órfãs'),
    ('indice',      u'Índice desatualizado'),
    ('procedencia', u'Fato novo sem procedência (corrigir)'),
    ('fonte',       u'Fontes não ingeridas'),
    ('legado',      u'Dívida: fatos anteriores à convenção de procedência'),
]

print(u'lint da wiki — %d documentos, data de referência %s\n' % (len(docs), hoje))
for cat, titulo in TITULOS:
    itens = [m for c, m in achados if c == cat]
    if itens:
        print(u'## %s (%d)' % (titulo, len(itens)))
        for m in itens[:LIMITE]:
            print(u'  ' + m)
        if len(itens) > LIMITE:
            print(u'  ... e mais %d' % (len(itens) - LIMITE))
        print(u'')

if not achados:
    print(u'nada a reportar.')
sys.exit(1 if achados else 0)

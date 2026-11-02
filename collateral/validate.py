# Checks the staged collateral files against the tree in app.js. Usage (from the repo root): python3 collateral/validate.py
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'collateral')
tree = {}
for line in open(os.path.join(ROOT, 'app.js'), encoding='utf-8'):
    m = re.match(r'const (DATA|EXTRA) = (.*);\s*$', line)
    if m:
        for p in json.loads(m.group(2)):
            tree[p['id']] = p

people = json.load(open(os.path.join(D, 'people.json'), encoding='utf-8'))['people']
rels = json.load(open(os.path.join(D, 'relationships.json'), encoding='utf-8'))['relationships']
nj = json.load(open(os.path.join(D, 'notes.json'), encoding='utf-8'))
notes = {n['id']: n for n in nj['notes']}

errors = []
def err(msg): errors.append(msg)

REQUIRED = ['id', 'gen', 'name', 'born', 'place', 'died', 'line', 'source', 'father', 'mother']
ALLOWED = set(REQUIRED) | {'sex', 'story', 'deathPlace'}
DATE = re.compile(r'^(\d{4}(-\d{2}(-\d{2})?)?)?$')
CONTACT = [(re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'), 'email'),
           (re.compile(r'\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b'), 'phone number'),
           (re.compile(r'\b\d{2,5}\s+\w+(\s\w+)?\s(St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Ln|Lane|Ct|Court|Blvd)\b\.?', re.I), 'street address')]

ids = set()
for p in people:
    pid = p.get('id')
    if pid in ids: err(f'duplicate id {pid}')
    ids.add(pid)
    if pid in tree: err(f'{pid} collides with an existing tree id')
    for k in REQUIRED:
        if k not in p: err(f'{pid}: missing field {k}')
    for k in p:
        if k not in ALLOWED: err(f'{pid}: field {k} is not in the app.js person schema')
    if p.get('gen') is not None: err(f'{pid}: collateral people take gen null')
    if not DATE.match(p.get('born', '')): err(f'{pid}: bad born {p.get("born")!r}')
    if p.get('died') != '(living)' and not DATE.match(p.get('died', '')): err(f'{pid}: bad died {p.get("died")!r}')
    if p.get('sex', 'M') not in ('M', 'F'): err(f'{pid}: bad sex')
    n = notes.get('add-' + pid)
    if not n: err(f'{pid}: no fact-check note'); continue
    if n['confidence'] not in ('confirmed', 'likely', 'uncertain'): err(f'{pid}: bad confidence')
    if n['verdict'] not in ('confirmed', 'consistent', 'book', 'conflict', 'unlikely', 'open'): err(f'{pid}: bad verdict')
    if not n['sources']: err(f'{pid}: note has no source passage')
    # dates taken from the calendar must be year-only; a full date needs an independent source named in the note
    calendar_only = all('calendar' in s['t'] for s in n['sources'])
    for k in ('born', 'died'):
        if len(p.get(k, '')) > 4 and p[k] != '(living)' and calendar_only: err(f'{pid}: {k} more precise than its calendar source')
    if n.get('possiblyLiving') and (p.get('place') or p.get('story')): err(f'{pid}: possibly living, so no place or story')

allids = ids | set(tree)
for p in people:
    for k in ('father', 'mother'):
        if p[k] and p[k] not in allids: err(f'{p["id"]}: {k} {p[k]} does not resolve')
        if p[k] == p['id']: err(f'{p["id"]}: is own {k}')
for r in rels:
    if r['a'] not in allids or r['b'] not in allids: err(f'{r["id"]}: unresolved person')
    if r['confidence'] not in ('confirmed', 'likely', 'uncertain'): err(f'{r["id"]}: bad confidence')
    if r['type'] == 'parent-suggested' and r['statedInSource']: err(f'{r["id"]}: a suggested link cannot be stated')
    if r['type'] == 'spouse' and not r['sources']: err(f'{r["id"]}: spouse link without a source')
# parent links set in father/mother must not also be pending suggestions
for r in rels:
    if r['type'] == 'parent-suggested':
        child = next((p for p in people if p['id'] == r['b']), None)
        if child and r['a'] in (child['father'], child['mother']): err(f'{r["id"]}: suggested link is already set as a parent')
# parents must be older than their children where both years are known
yrs = {k: v.get('born', '')[:4] for k, v in list(tree.items()) + [(p['id'], p) for p in people]}
for p in people:
    for k in ('father', 'mother'):
        if p[k] and yrs.get(p[k]) and p['born'][:4] and int(p['born'][:4]) - int(yrs[p[k]]) < 13:
            err(f'{p["id"]}: born {p["born"][:4]}, implausibly close to {k} {p[k]} ({yrs[p[k]]})')
# no contact details anywhere in the staged files
for fn in ('people.json', 'relationships.json', 'notes.json'):
    text = open(os.path.join(D, fn), encoding='utf-8').read()
    for rx, what in CONTACT:
        for m in rx.finditer(text): err(f'{fn}: looks like a {what}: {m.group(0)!r}')
for d in nj['dedupe']:
    if d['existing'] not in tree: err(f'dedupe target {d["existing"]} not in tree')

if errors:
    print('\n'.join(errors)); print(f'FAILED: {len(errors)} problem(s)'); sys.exit(1)
print(f'OK: {len(people)} people, {len(rels)} relationships, {len(notes)} notes, {len(nj["dedupe"])} dedupe matches; all checks passed')

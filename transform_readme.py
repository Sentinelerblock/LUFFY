import re
import pathlib

root = pathlib.Path('.')
all_todos = []
for p in sorted(root.rglob('*.py')):
    if '.git' in p.parts:
        continue
    try:
        lines = p.read_text().splitlines()
    except Exception:
        continue
    for i, line in enumerate(lines, 1):
        if 'TODO' in line:
            all_todos.append(f'{p.as_posix()}:{i}:{line.strip()}')
print('ALL_TODOS_BEGIN')
print('\n'.join(all_todos))
print('ALL_TODOS_END')
print('TODO_COUNT', len(all_todos))

targets = [
    'luffy/deepscaler/utils.py',
    'luffy/verl/verl/protocol.py',
]
entry_re = re.compile(r'^- \[ \] \*\*(?P<path>.*?):(?P<line>\d+)\*\* - (?P<text>.*)$')
readme = pathlib.Path('README.md')
lines = readme.read_text().splitlines()

for target in targets:
    p = pathlib.Path(target)
    entries = []
    for i, line in enumerate(p.read_text().splitlines(), 1):
        m = re.search(r'#\s*TODO\b(?P<rest>.*)', line)
        if not m:
            continue
        rest = m.group('rest')
        text = re.sub(r'^[\s:/-]+', '', rest).strip()
        entries.append((i, text))
    new_block = [f'- [ ] **{target}:{i}** - {text}' for i, text in entries]

    idxs = []
    for idx, line in enumerate(lines):
        m = entry_re.match(line)
        if m and m.group('path') == target:
            idxs.append(idx)
    print('TARGET', target, 'current', len(entries), 'old_readme', len(idxs))
    if idxs:
        assert idxs == list(range(min(idxs), max(idxs) + 1)), f'non-contiguous old entries for {target}'
        start, end = min(idxs), max(idxs) + 1
        print('OLD_BLOCK_BEGIN')
        print('\n'.join(lines[start:end]))
        print('OLD_BLOCK_END')
        lines[start:end] = new_block
    else:
        anchor = len(lines)
        for idx, line in enumerate(lines):
            m = entry_re.match(line)
            if m and m.group('path') > target:
                anchor = idx
                break
        lines[anchor:anchor] = new_block
    print('NEW_BLOCK_BEGIN')
    print('\n'.join(new_block))
    print('NEW_BLOCK_END')

readme.write_text('\n'.join(lines) + '\n')

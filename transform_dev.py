import pathlib
import re
import subprocess

TARGETS = [
    'luffy/deepscaler/utils.py',
    'luffy/verl/verl/protocol.py',
]

def git(*args):
    return subprocess.check_call(['git', *args])

git('fetch', 'origin', 'dev', '--depth=1')
git('checkout', 'dev', '--', 'README.md', *TARGETS)
git('reset', '-q', 'HEAD', 'README.md', *TARGETS)

entry_re = re.compile(r'^- \[ \] \*\*(?P<path>.*?):(?P<line>\d+)\*\* - (?P<text>.*)$')
readme = pathlib.Path('README.md')
lines = readme.read_text().splitlines()

for target in TARGETS:
    p = pathlib.Path(target)
    entries = []
    for i, line in enumerate(p.read_text().splitlines(), 1):
        m = re.search(r'#\s*TODO\b(?P<rest>.*)', line)
        if not m:
            continue
        text = re.sub(r'^[\s:/-]+', '', m.group('rest')).strip()
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

subprocess.check_call(['git', 'checkout', '-B', 'readme-dev-sync', 'origin/dev'])
git('add', 'README.md')
git('config', 'user.name', 'github-actions[bot]')
git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
subprocess.check_call(['git', 'commit', '-m', 'docs: update TODO list from dev scan', 'README.md'])
git('push', 'origin', 'HEAD:readme-dev-sync', '--force')
print('PUSHED readme-dev-sync')

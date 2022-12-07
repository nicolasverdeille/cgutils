from pathlib import PurePath, PurePosixPath
import pyperclip
import re

include_pattern = re.compile('(?:#include\s*")(.*)(?:")')
pragmaonce_pattern = re.compile('#pragma\s*once')

def parse(files):
    requirements = {}
    while files:
        filename = files.pop()
        with open(filename, 'r') as f:
            requirements[filename] = set([PurePath(PurePosixPath(filename.parent.as_posix(), p.group(1))) for p in [include_pattern.search(line) for line in f] if p])
        files |= set([f for f in requirements[filename] if f not in requirements])
    return requirements

def order(requirements):
    ordered = []
    while [f for f in requirements.keys() if f not in ordered]:
        ordered += [f for f, r in requirements.items() if not r - set(ordered) and f not in ordered]
    return ordered

def aggregate(files):
    aggregated = []
    for infile in files:
        with open(infile, 'r') as f:
            content = f.readlines()
        filtered = [l for l in content if not (include_pattern.search(l) or pragmaonce_pattern.search(l))]
        aggregated += ['#line {} "{}"\n'.format(len(content) - len(filtered) + 1, infile.as_posix())] + filtered
    return ''.join(aggregated)

def to_clipboard(content):
    pyperclip.copy(content)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Aggregate a cpp project into a single file.')
    parser.add_argument('-f', '--files', nargs='+', type=PurePath, help='input filenames (only cpp files)')

    to_clipboard(aggregate(order(parse(set(parser.parse_args().files)))))

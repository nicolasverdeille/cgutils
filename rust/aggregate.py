import os.path
import re

def find_mod(root, mod):
    if os.path.isfile(os.path.join(root, '{}.rs'.format(mod))):
        return os.path.join(root, '{}.rs'.format(mod))
    elif os.path.isfile(os.path.join(root, mod, 'mod.rs')):
        return os.path.join(root, mod, 'mod.rs')
    else:
        print('Could not find module {}(folder {})'.format(mod, root))
        exit(1)

def process(input_file, output, indent=0):
    tabs = '    ' * indent
    root = os.path.dirname(input_file)

    with open(input_file, 'r') as f:
        for line in f:
            pub = re.search('(?<=^pub mod ).*(?=;$)', line)
            priv = re.search('(?<=^mod ).*(?=;$)', line)

            if pub:
                output.write('{}pub mod {}{{\n'.format(tabs, pub.group(0)))
                process(find_mod(root, pub.group(0)), output, indent + 1)
                output.write('{}}}\n'.format(tabs, pub.group(0)))
            elif priv:
                output.write('{}mod {}{{\n'.format(tabs, priv.group(0)))
                process(find_mod(root, priv.group(0)), output, indent + 1)
                output.write('{}}}\n'.format(tabs, priv.group(0)))
            else:
                output.write(tabs + line)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Aggregate a rust project into a single file.')
    parser.add_argument('-m', '--main', default='src/main.rs', help='main source file')
    parser.add_argument('-o', '--output', default='aggregated.rs', help='output filename')

    args = parser.parse_args()

    with open(args.output, 'w') as f:
        process(args.main, f)

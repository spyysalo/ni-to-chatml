#!/usr/bin/env python3

# Convert https://github.com/allenai/natural-instructions to
# https://github.com/openai/openai-python/blob/main/chatml.md

import sys
import os
import json
import random

from argparse import ArgumentParser
from logging import warning


# Template for generating ChatML from NI definition, input, and output.
TEMPLATE = '''<|im_start|>user
{definition}
{input}<|im_end|>
<|im_start|>assistant
{output}<|im_end|>'''


def argparser():
    ap = ArgumentParser()
    ap.add_argument(
        '--exclude',
        default=None,
        metavar='FILE[,FILE...]',
        help='Exclude tasks listed in FILE(s)'
    )
    ap.add_argument(
        '--languages',
        default=None,
        metavar='LANG[,LANG...]',
        help='Limit to LANG(s) in input, output, and instruction'
    )
    ap.add_argument(
        '--skip-translation',
        action='store_true',
        help='Skip translation tasks'
    )
    ap.add_argument(
        '--all-outputs',
        action='store_true',
        help='Generate all input-output combinations'
    )
    ap.add_argument(
        '--max-instances',
        default=None,
        type=int,
        metavar='NUM',
        help='Sample at most NUM instances per task'
    )
    ap.add_argument('json', nargs='+')
    return ap


def skip_by_language(name, data, args):
    if args.languages is None:
        return False
    for k in ('Input_language', 'Output_language', 'Instruction_language'):
        if not set(data[k]) & args.languages:
            warning(f'skip {name}: {k} {data[k]} & {args.languages} empty')
            return True
    return False


def lines(fn):
    with open(fn) as f:
        return f.read().splitlines()


def main(argv):
    args = argparser().parse_args(argv[1:])

    if args.languages is not None:
        args.languages = set(args.languages.split(','))

    if args.exclude is not None:
        fns = args.exclude.split(',')
        args.exclude = set([l for fn in fns for l in lines(fn)])
        
    for fn in args.json:
        name = os.path.splitext(os.path.basename(fn))[0]

        if args.exclude is not None and name in args.exclude:
            warning(f'skip {name} due to --exclude')
            continue

        with open(fn) as f:
            data = json.load(f)

            if args.skip_translation and data['Categories'] == ['Translation']:
                warning(f'skip {name}: Categories {data["Categories"]}')
                continue
            
            if skip_by_language(name, data, args):
                continue

            
            if len(data['Definition']) != 1:
                warning(f'skip {name}: {len(data["Definition"])} definitions, will choose randomly')

            instances = data['Instances']
            if (args.max_instances is not None and
                len(instances) > args.max_instances):
                instances = random.sample(instances, args.max_instances)
                
            for i in instances:
                id_ = i['id']
                definition = random.choice(data['Definition'])
                input_ = i['input']
                if args.all_outputs:
                    outputs = i['output']
                else:
                    outputs = [random.choice(i['output'])]
                for output in outputs:
                    text = TEMPLATE.format(
                        definition=definition,
                        input=input_,
                        output=output
                    )
                    print(json.dumps({
                        'id': id_,
                        'text': text,
                    }, ensure_ascii=False))

            
if __name__ == '__main__':
    sys.exit(main(sys.argv))

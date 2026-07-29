# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
import os
import sys
import yaml

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cff_p = os.path.join(root, 'CITATION.cff')
    if not os.path.exists(cff_p):
        print('[!] CITATION.cff missing!')
        sys.exit(1)
    with open(cff_p, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    required_keys = ['cff-version', 'title', 'version', 'license', 'authors', 'repository-code']
    for k in required_keys:
        if k not in data:
            print(f'[!] CITATION.cff missing key: {k}')
            sys.exit(1)

    if not isinstance(data['authors'], list) or len(data['authors']) == 0:
        print('[!] CITATION.cff authors invalid!')
        sys.exit(1)

    author = data['authors'][0]
    if 'orcid' not in author:
        print('[!] CITATION.cff author missing ORCID!')
        sys.exit(1)

    print('[OK] CITATION.cff validation passed.')

if __name__ == '__main__':
    main()

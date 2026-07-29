# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
import os
import sys

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    license_p = os.path.join(root, 'LICENSE')
    notice_p = os.path.join(root, 'NOTICE')

    if not os.path.exists(license_p) or not os.path.exists(notice_p):
        print('[!] LICENSE or NOTICE missing!')
        sys.exit(1)

    with open(license_p, encoding='utf-8') as f:
        lic_txt = f.read()

    with open(notice_p, encoding='utf-8') as f:
        notice_txt = f.read()

    # LICENSE checks
    if 'Apache License' not in lic_txt or 'Version 2.0' not in lic_txt or 'http://www.apache.org/licenses/' not in lic_txt:
        print('[!] LICENSE does not contain Apache License 2.0 header!')
        sys.exit(1)

    html_break_tag = '<' + 'br' + '>'
    if html_break_tag in lic_txt or '<html>' in lic_txt or ('[' in lic_txt and ']' in lic_txt and 'yyyy' in lic_txt):
        print('[!] LICENSE contains invalid formatting or placeholders!')
        sys.exit(1)

    # NOTICE checks
    if 'RASH-HIT Fractal Studio' not in notice_txt:
        print('[!] NOTICE missing project name!')
        sys.exit(1)
    if 'Mehmet Raşit Narçiçek' not in notice_txt:
        print('[!] NOTICE missing author name!')
        sys.exit(1)
    if 'ORCID' not in notice_txt:
        print('[!] NOTICE missing ORCID!')
        sys.exit(1)

    if html_break_tag in notice_txt or '<a href' in notice_txt or '](' in notice_txt:
        print('[!] NOTICE contains HTML tags or Markdown link syntax!')
        sys.exit(1)

    print('[OK] License and Notice validation passed.')

if __name__ == '__main__':
    main()

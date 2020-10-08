#!/usr/local/bin/python
'''
get an entry based on a single address
- for each cmd line arg, any address from stdin
  which matches any part of the argv will be emitted

invoke script named with leading 'd' to generate dated entries;
e.g.  entries => dentries, d_entries, dated_entries
'''
# for use as a filter;
from sys import stdin, stdout, argv
from datetime import datetime  # for date printing
from os.path import basename

lines = []
for line in stdin:
    lines.append(line.rstrip())


def get_entries(lines, matchme):
    '''
    print all listing entries containing matchme;
    '''
    a_match = False
    matchme_lower = matchme.lower()  # just do this once
    for l in lines:
        # print(f'...{l}')
        if a_match and l.startswith((' ', '\t')):
            print(l)
        elif l.startswith('[') and l.lower().find(matchme_lower) >= 0:
            a_match = True
            print('\n'+l)  # I think I'd like to space separate entries;
        else:
            a_match = False


'''
for each argument:
    print out all address entries which match arg
'''

# either works w/ symlinks: print(basename(argv[0]), basename(__file__))
if basename(__file__).startswith('d'):   # prefix with date
    print(f"---\n{datetime.now().strftime('%Y-%m-%d')}")

if len(argv) == 1:
    # just print all entries, unembellished
    argv.append('')

for i in argv[1:]:
    get_entries(lines, i)


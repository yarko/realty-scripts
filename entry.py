#!/usr/local/bin/python
'''
get an entry based on a single address
- for each cmd line arg, any address from stdin
  which matches any part of the argv will be emitted
'''
# for use as a filter;
from sys import stdin, stdout, argv

lines = []
for line in stdin:
    lines.append(line.rstrip())


def get_entries(lines, matchme):
    '''
    print all listing entries containing matchme;
    '''
    a_match = False
    for l in lines:
        # print(f'...{l}')
        if l.startswith('[') and l.lower().find(matchme.lower()) >=0:
            a_match = True
            print(l)
            continue
        if a_match and l.startswith((' ', '\t')):
            print(l)
            # to keep from making noisy output,
            #  include empty lines after entry w/ entry
        else:
            a_match = False


'''
for each argument:
    print out all address entries which match arg
'''

if len(argv) == 1:
    # just print all entries, unembellished
    argv.append('')

for i in argv[1:]:
    get_entries(lines, i)


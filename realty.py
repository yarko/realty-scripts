#!/usr/bin/env python
'''
take markdown realty address list, and process
- to work w/ paper.dropbox md;
- always keep header lines (# lines)
- parse checklist item blocks as "one thing"
'''

# for use as a filter;
from sys import stdin, stdout, argv


# I put file into lines[] because
# - I want to be able to pushback onto the "stream"
# - This means I assume the file can't get too big

lines = []
isreversed = False


def help():
    this_script = argv[0].rsplit('/', 1)[-1]
    usage = f'''usage:
        {this_script} [command] < [input]
        {this_script} -h  <= this help

        All input is thru stdin.

        most commands are two words:
            'get' or 'rm' applied to any of the following:

            current   (current view batch)
                'active' modifies to exclude contingents, e.g.:
                    $ {this_script} rm current active
            no        (not available)
            contract  (under contingency)
            nointerest (we've decided we're not interested)
        special command:
            promote   (moves 2nd tier /2 selections to first tier,
                       for next viewing cycle)

        example:
            $ {this_script} get contract

        returns everything but removes unavailable entries:
            $ {this_script} rm no

    '''
    print(usage)
    exit(-1)


# early help:
if len(argv) < 2 or argv[1].startswith('-'):
    help()


## for testing / debugging:
'''
with open('../IL/2020-09-20_viewings.md', 'r') as f:
    for line in f:
        lines.append(line.rstrip())
'''
## end test section

# For production use (alternative to test section above):
for line in stdin:
    lines.append(line.rstrip())


def _next_item_index(lines):
    for i, s in enumerate(lines):
        if s.startswith('['):
            return i
    return -1


def _get_entry(lines):
    '''
    process a reversed list
    basic get a listing entry;
    return lines as list
    if nothing left, returns empty list
    '''
    entry = []
    while lines:
        l = lines.pop()
        if l.startswith('['):
            entry.append(l)
            while lines:
                l = lines.pop()
                # to keep from making noisy output,
                #  include empty lines after entry w/ entry
                if l.startswith((' ', '\t')) or l == '' :
                    entry.append(l)
                else:
                    # push the line back
                    lines.append(l)
                    return(entry)
        # simply print out all in between entries
        else:
            print(l)
    # all done - nothing left:
    return entry   # be sure to return last entry


def get_entry():
    '''
    basic get a listing entry;
    majority of fcn's process the entire list,
    so this simply is a wrapper to ensure
    that list is reversed (globals are evil!)
    '''
    # I want to pushback last input, so I'll use reversed list
    #   so we can push-back lookahead items
    global isreversed
    if not isreversed:
        lines.reverse()
        isreversed = True
    return _get_entry(lines)


level0 = lambda s: s[0].endswith('/0')   # new entry
level1 = lambda s: s[0].endswith('/1')   # current viewing request
level2 = lambda s: s[0].endswith('/2')   # next viewing request
level3 = lambda s: s[0].endswith('/3')   # maybe some next viewing cycle
# for future use:  edit "not interested"s not at the end:
level4 = lambda s: s[0].endswith('/4')   # maybe some next viewing cycle


def get_current(all=True):
    ''' +current
    extract current address lists
    - defined by:
        - ^[ ].* \/1$
    - only returns non-rejected (not starting w/ [x]),
      unless all = True
    '''
    # pass entry: so, valid(entry) assumes first line is the checkbox
    if all:
        valid = level1
    else:
        valid = lambda s: s[0].startswith('[ ]') and level1(s)

    while entry := get_entry():
        if valid(entry):
            for line in entry:
                print(line)


def rm_current(all=True):
    ''' -current
    inverse of get_current()
    i.e. return all lines, but the current ones
    '''
    # pass entry: so, valid(entry) assumes first line is the checkbox
    # valid = lambda s: not level1(s)
    if all:
        valid = level1
    else:
        valid = lambda s: s[0].startswith('[ ]') and level1(s)

    while entry := get_entry():
        if not valid(entry):
            for line in entry:
                print(line)


def promote():
    '''
    plus advance all secondary entries
    i.e. convert /2's to /1's
    '''

    valid = level2
    while entry := get_entry():
        if valid(entry):
            entry[0][-1] = "1"
        # other than this edit, print everything
        for line in entry:
            print(line)


def get_no():
    ''' +no
    extract x'd out addresses
    '''
    valid = lambda s: s[0].startswith(('[x]', '[X]'))

    while entry := get_entry():
        if valid(entry):
            for line in entry:
                print(line)


def rm_no():
    ''' -no
    return all but the x'd out
    '''
    valid = lambda s: s[0].startswith(('[x]', '[X]'))

    while entry := get_entry():
        if not valid(entry):
            for line in entry:
                print(line)


def get_contract():
    '''
    separate under-contract x'd out ones separately
    - will need to be more consistent of "contract" or "contingent" to mark them
    - I think I'll mark c/{n}, e.g.  c/1;  c/2;  and so on...
    '''
    contingent = lambda s: s[0][:-1].endswith('c/')

    while entry := get_entry():
        if contingent(entry):
            for line in entry:
                print(line)


def rm_contract():
    '''
    separate under-contract x'd out ones separately
    - will need to be more consistent of "contract" or "contingent" to mark them
    - I think I'll mark c/{n}, e.g.  c/1;  c/2;  and so on...
    '''
    contingent = lambda s: s[0][:-1].endswith('c/')

    while entry := get_entry():
        if not contingent(entry):
            for line in entry:
                print(line)

# I think that's all the function I need;

## now, parse the options


# these are the only two functions which depend on
# non-reversed list:
# - get_nointerest()
# - rm_nointerest()

# This line splits the file;
# - note: this is different than unable to view / unavailable for viewing
NO_INTEREST = '# Not interested in viewing:'
# lambda, so we don't actually search if we don't need to:
interest_marker = lambda s: s.index(NO_INTEREST)


def get_nointerest():
    '''
    '''
    i = interest_marker(lines)
    f = _next_item_index(lines)
    for line in lines[i:]:
        print(line)
    # now get level4 items in the other part of the list:
    # ToDo: might want to also find the first lines entry

    front_lines = lines[f:i]
    front_lines.reverse()
    removal = level4
    while entry := _get_entry(front_lines):
        if removal(entry):
            for line in entry:
                print(line)



def rm_nointerest():
    '''
    '''
    i = interest_marker(lines)
    f = _next_item_index(lines)
    front_lines = lines[f:i]
    front_lines.reverse()
    removal = level4
    while entry := _get_entry(front_lines):
        if not removal(entry):
            for line in entry:
                print(line)


run_table = {
    # "get_entry": get_entry,
    "get_current": get_current,
    "rm_current": rm_current,
    "get_no": get_no,
    "rm_no": rm_no,
    "get_contract": get_contract,
    "rm_contract": rm_contract,
    "get_nointerest": get_nointerest,
    "rm_nointerest": rm_nointerest,
    "promote": promote,
}


# could also add extractor for /0 and /3 tiers;
#  will if the need arises;

# parse command line:
if len(argv) < 2 or argv[1].startswith('-'):
    help()

cmd = '_'.join(argv[1:3])  # cmd at most 2 words; leave other for option
if cmd not in run_table:
    help()

if len(argv) > 3 and argv[2] == 'current':
    # I don't care what that last input param is:
    #  "active", is fine; but doesn't really matter
    run_table[cmd](all=False)  # only get active current viewings
else:
    run_table[cmd]()


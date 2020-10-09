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
        {this_script} -f [filename] [command]
        {this_script} -h  <= this help

        most commands are two words:
            'get' or 'rm' applied to any of the following:

            new       (new items - /0)
            current   (current view batch /1)
                    'active' modifies to exclude contingents, e.g.:
                    $ {this_script} rm current active
            no        (not available); includes /4 (no interest)
            contract  (under contingency)
            nointerest (we've decided we're not interested)
        special command:
            promote   (moves 2nd tier /2 & new /0 selections to first tier,
                      for next viewing cycle).
                      valid options:
                        old - only promote /2
                        /2
                        new - only promote new /0
                        /1
                        all - /2 and /0 (which is default)

        example:
            $ {this_script} get contract
            $ {this_script} promote /0

        returns everything but removes unavailable entries:
            $ {this_script} rm no

    '''
    print(usage)
    exit(-1)


# early help:
if len(argv) < 2 or argv[1].startswith('-h'):
    help()

if argv[1].startswith('-f'):  # input file specified
    with open(argv[2], 'r') as f:
        for line in f:
            lines.append(line.rstrip())
    # delete argv 1 and 2:
    del argv[1:3]
else:  # use stdin
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


# ToDo: sort out the blurry boundaries between this,
#   get_entry() and _get_entry() - and reduce;
def fetch_entries(select):
    while entry := get_entry():
        if select(entry):
            for line in entry:
                print(line)



level0 = lambda s: s[0].endswith('/0')   # new entry
not_level0 = lambda s: not s[0].endswith('/0')   # new entry
level1 = lambda s: s[0].endswith('/1')   # current viewing request
not_level1 = lambda s: not s[0].endswith('/1')   # current viewing request
level2 = lambda s: s[0].endswith('/2')   # next viewing request
not_level2 = lambda s: not s[0].endswith('/2')   # next viewing request
level3 = lambda s: s[0].endswith('/3')   # maybe some next viewing cycle
not_level3 = lambda s: not s[0].endswith('/3')   # maybe some next viewing cycle
level4 = lambda s: s[0].endswith('/4')   # maybe some next viewing cycle
not_level4 = lambda s: not s[0].endswith('/4')   # maybe some next viewing cycle

def get_new(all=True):
    '''
    extract new address lists
    - defined by:
        - ^[ ].* \/0$
    - only returns non-rejected (not starting w/ [x]),
      unless all = True
    '''
    # pass entry: so, valid(entry) assumes first line is the checkbox
    if all:
        valid = level0
    else:
        valid = lambda s: s[0].startswith('[ ]') and level0(s)

    fetch_entries(valid)


def rm_new(all=True):
    ''' -current
    inverse of get_current()
    i.e. return all lines, but the current ones
    '''
    # pass entry: so, valid(entry) assumes first line is the checkbox
    # valid = lambda s: not level1(s)
    if all:
        select = not_level0
    else:
        select = lambda s: not (s[0].startswith('[ ]') and level0(s))
 
    fetch_entries(select)


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

    fetch_entries(valid)


def rm_current(all=True):
    ''' -current
    inverse of get_current()
    i.e. return all lines, but the current ones
    '''
    # pass entry: so, valid(entry) assumes first line is the checkbox
    # valid = lambda s: not level1(s)
    if all:
        valid = not_level1
    else:
        valid = lambda s: not (s[0].startswith('[ ]') and level1(s))

    fetch_entries(valid)


def promote(all=True):
    '''
    plus advance all secondary entries
    i.e. convert /2's and /0's to /1's

    '''

    if all is False:
        lvlmrk = "/2"  # promote only level-2, "next-to-view"
        valid = level2
    elif all is True:
        valid = lambda s: (level0(s) or level2(s))
    else:
        lvlmrk = all   # expect it to be either "/2" or "/0"
        valid = level0 if lvlmrk=="/0" else level2

    while entry := get_entry():
        if valid(entry):
            s = entry[0]
            if (all is True) and (s[-2:] in ("/2", "/0")):
                entry[0] = s.replace(s[-2:], "/1")
            elif s[-2:] == lvlmrk:
                entry[0] = s.replace(lvlmrk, "/1")
        # other than this edit, print everything
        for line in entry:
            print(line)


def get_no():
    ''' +no
    extract x'd out addresses
    '''
    valid = lambda s: (s[0].startswith(('[x]', '[X]')) or level4(s))
    fetch_entires(valid)


def rm_no():
    ''' -no
    return all but the x'd out
    '''
    valid = lambda s: not (s[0].startswith(('[x]', '[X]')) or level4(s))
    fetch_entries(valid)


def get_contract():
    '''
    separate under-contract or off-market x'd out ones separately
    - will need to be more consistent of "contract" or "contingent" to mark them
    - I think I'll mark c/{n}, e.g.  c/1;  c/2;  and so on...
    '''
    # ToDo:  will need to be tolerant of "viewd" markers here too, eg: vc/1 or cv/1
    contingent = lambda s: s[0][:-1].endswith(('c/','o/'))
    fetch_entries(contingent)


def rm_contract():
    '''
    separate under-contract or off-market x'd out ones separately
    - will need to be more consistent of "contract" or "contingent" to mark them
    - I think I'll mark c/{n}, e.g.  c/1;  c/2;  and so on...
    '''
    not_contingent = lambda s: not (s[0][:-1].endswith(('c/','o/')))
    fetch_entries(not_contingent)


# I think that's all the function I need;

## now, parse the options

# these are the only two functions which depend on
# non-reversed list:
# - get_nointerest()
# - rm_nointerest()

# ToDo:  remove dependency on this line marker:

# This line splits the file;
# - note: this is different than unable to view / unavailable for viewing
## This is now GONE:
# NO_INTEREST = '# Not interested in viewing:'
# lambda, so we don't actually search if we don't need to:
# interest_marker = lambda s: s.index(NO_INTEREST)


def get_nointerest():
    '''
    '''
    # get level4 items in the other part of the list:
    # ToDo: might want to also find the first lines entry
    removal = lambda s: s[0].startswith('[x]') or level4(s)
    fetch_entries(removal)


def rm_nointerest():
    '''
    '''
    # removal = level4
    no_removal = lambda s: not(s[0].startswith('[x]') or level4(s))
    fetch_entries(no_removal)


run_table = {
    # "get_entry": get_entry,
    "get_new": get_new,
    "rm_new": rm_new,  # may not need this
    "get_current": get_current,
    "rm_current": rm_current,
    "get_no": get_no,
    "rm_no": rm_no,
    "get_contract": get_contract,
    "rm_contract": rm_contract,
    "get_contingent": get_contract,
    "rm_contingent": rm_contract,
    "get_nointerest": get_nointerest,
    "rm_nointerest": rm_nointerest,
    "promote": promote,
}


# command line options for "*_current" and "promote"
opts = {
    # for *_current all=  option
    "current": False,
    "active": False,
    # for "promote" all=  options
    "old": False,       # code sets to "/2"
    "notnew": False,
    "/2": "/2",
    "/0": "/0",
    "new": "/0",
    "all": True,    # not really needed (it's default)
}

# could also add extractor for /0 and /3 tiers;
#  will if the need arises;

# parse command line:
if len(argv) < 2 or argv[1].startswith('-'):
    help()

# grab simple option for current & promote commands
if (len(argv)>3) or (argv[1]=="promote" and len(argv)>2):
    opt = argv.pop()
else:
    opt = ""

cmd = '_'.join(argv[1:3])  # cmd at most 2 words; leave other for option
if cmd not in run_table:
    help()

if opt in opts:
    # run filter with option
    run_table[cmd](all=opts[opt])  # only get active current viewings
else:
    run_table[cmd]()


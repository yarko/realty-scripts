#!/bin/bash
# for dropbox paper realty address files:
# - get the entries starting with [ ],
#   and clean up to leave just the addresses
grep -h -i '^\[.\]' - | sed -E -e '
# clear checkbox front end
s/^\[.\][ ]*//
# clear any number of categories from end
s/([ \t]*[c]?\/[0-9])+//
# one-off special cases: notes, parenthesized comments
s/[ ]*<<==.*//
s/\(.*\)//' #  | sort | uniq -D

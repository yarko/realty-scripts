#!/bin/bash

sed -e '
# insert blank line before any md line starting w/ header '#' or checkbox
/^[[#]/ i

# 8-space bullits? turn into 4-space:
s/^[ ]\{8\}-/    -/'

# realty-scripts
assortment of hacks for our house-hunting

---
This evolved (was not so much designed) during house hunting.
Use at your own risk (copy/paste, or ignore).

All scripts are filters, operating on stdin and stdout - use care (and temporary files) when applying them,
or you will create truncated files (i.e. `filter < this > this` will truncate `this`).

It started with dropbox paper files of addresses for house viewing.
Paper worked well on mobile for checklists of addressses with key information we were interested in,
links to some MLS, and to addresses for quick directions (via some maps app).

As time went on, we made a key for quick notes:
- rankings of the listing;
- status of the listing;

    Key:
    - /0 new (see next scheduled time)
    - /1 see
    - /2 maybe or later or after drive-by
    - /3 questionable (but maybe)
    - /4 not interested (only really need to mark for cont. filter)

    Key modifiers/
    - c/ - contingent/contract
    - o/ - off the market
    - r/ - re-activated
    - v/ - viewed

An entry might look like:
```
    [ ] 123 Main St, Anytown, DC  50123  vc/1
        - MLS: https://link.to/some-MLS-listing-site
        - Loc: https://www.google.com/maps/place/123+Main+St,+Anytown,+DC+50123/
        - price and size info
        - build data, key features
        - tax and HOA fees
        - notes:
          - like this
```

This could head in the direction of being stored as some
sort of document database.
This would make sorting addresses (for example - by zipcode) simpler,
adding to a google maps route, etc.
At this point, this is more work than I'm inclined to put in for
this aspect - but the thoughts keep coming up.



### `realty.py`
At some point, we put town-name headers on our files, so that in updating and filtering content,
I didn't want to remove general markdown lines which surrounded what had turned into checklist-structures
(nested bullits under checklist items which were checkboxes).
This sort of evolved into emitting selected
entries in `realty.py` but using a lazy form of pushing back lines (via reversed order lists, and push/pop
accomplished with list.pop() and list.append()).

On mobile, we liked the simplicity of using checkboxes
to mark (for example) houses we'd managed to visit on a listing tour, and in a more general list of houses
which we'd either rejected (didn't like) or which were otherwise unavailable (under contract, or taken off market).
This duplicate and fuzzy-defined form of marking address entries evolved over time (as we decided what worked and didn't for us).
That means that some of the behavior of filtering in `realty.py` evolved in ad-hoc ways.
`realty.py` takes multi-word commands.
With no commands, a (hopefully current) _help_ message is emmitted.
There are only two flag-type options:
`-f` for named file input (for
development / debugging, this was a convenience),
and `-h` for explicitly calling out _help_.

Needs and current usage preferences and experiences drive change - that is all.

### `entries.py`
For grabbing markdown-ignoring entries, `entries.py` came to be.

`entries.py` was used to make simple text searches
on the checkbox/address lines to pick out address entires.
If no search term is given, all entries are extracted.

This may be updated to use regular expressions - but for now a combination of filters seems to suffice
(e.g. take output from `realty.py` and remove spurious markdown by filtering through `entries.py`).

I didn't want to do full-blown command line options processing, so shortcuts abound: if `entries.py` is
linked / invoked with any name beginning with 'd' (i.e. `dated_entries.py`) then an ISO form date is prefixed to the output.
This is for accumulating the files of contingencies (prefixed by dates when we noticed new contingencies).

### `addresses.sh`
For emailing simple lists of addresses to our realtor, the bash script `addresses.sh` extracts just the top line
of a checkbox entry, and strips the category markers, spurious markdown, and so forth.
It's very dependent on how we happened to find our files marked at the time (and that use changes, so some parts
now seem archaic).

### `paperfix.sh`
It turned out that exporting dropbox paper files in markdown worked reasonably well in round-tripping,
To make it work a tad better, `paperfix.sh` came about.
Dropbox paper export to markdown seems to delete any space between checklist items, and to spuriously (on import)
interpret indent levels too high (I just let it), and then to emit with double the spaces, campared to what
it received, on bullit items - `paperfix.sh` is a simple hack to manage this.


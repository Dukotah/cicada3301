Part files moved out of the merge, and why.

The 2013-09-05 -> 2013-11-14 beacon pads are a strict byte-PREFIX superset of the
2013-09-05 -> 2013-10-12 pads: the same first 3,349,824 bytes, plus 33 more days. Counting a
config on both windows would count the same offsets twice and inflate this lane's coverage
bound, which is the one number the round asks each lane to get right.

So each builder is reported on exactly ONE window:
  * the six BUILDERS of lib_padsweep  -> the 2013-10-12 window, where all 12 variants x 2
    signs completed on BOTH pads (48 configs);
  * `nibbles` (the true hex-text reading, added by lane P1 after `hexchars` was found to
    drop digits) -> the longer 2013-11-14 window, since it had to be run from scratch anyway
    and the longer pad is strictly more coverage for the same CPU.

Files here are the runs that lost that choice. They are correct; they are just redundant.

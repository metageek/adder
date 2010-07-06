#!/usr/bin/env python3

import pstats,sys

if len(sys.argv)>1:
    assert len(sys.argv)==2
    f=sys.argv[1]
else:
    f='adderprof'

p=pstats.Stats(f)
p.strip_dirs().sort_stats('cumulative').print_stats()

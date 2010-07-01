#!/usr/bin/env python3

import pstats

p=pstats.Stats('adderprof')
p.strip_dirs().sort_stats('cumulative').print_stats()

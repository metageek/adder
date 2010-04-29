# The Adder front end.  Maintains knowledge of lexical scopes,
# translates Adder to Gomer.

import itertools,functools,re,pdb,adder.gomer,sys
from adder.common import Symbol as S, gensym

passthrough={'==','!=','<=','<','>=','>',
             '+','-','*','/','//','%',
             'in'
             }


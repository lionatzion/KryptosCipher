"""Historical route scaffold, not a working east-then-northeast traversal.

Use kryptos.primitives.route_catalog for the explicitly implemented routes.
"""
from typing import List, Tuple
def grid_dims()->Tuple[int,int]:
    return 7,14
def route_east_then_ne(rows:int, cols:int, n:int, start=(0,0))->List[int]:
    raise NotImplementedError(
        "This historical E-to-NE route was never implemented; its old identity "
        "result was a placeholder, not a tested geometric route."
    )
def apply_route(text:str, order:List[int])->str:
    if len(order)!=len(text):
        raise ValueError('length mismatch')
    out=['?']*len(text)
    for i,old in enumerate(order): out[i]=text[old]
    return ''.join(out)

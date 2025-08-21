from typing import List, Tuple
def grid_dims()->Tuple[int,int]:
    return 7,14
def route_east_then_ne(rows:int, cols:int, n:int, start=(0,0))->List[int]:
    return list(range(n))
def apply_route(text:str, order:List[int])->str:
    if len(order)!=len(text):
        raise ValueError('length mismatch')
    out=['?']*len(text)
    for i,old in enumerate(order): out[i]=text[old]
    return ''.join(out)

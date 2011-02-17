import numpy as np

def fill_diagonal(a,val):
    if a.ndim < 2:
        raise ValueError("array must be at least 2-d")
    if a.ndim == 2:
        step = a.shape[1] + 1
    else:
        if not np.alltrue(np.diff(a.shape)==0):
            raise ValueError("All dimensions of input must be of equal length")
        step = np.cumprod((1,)+a.shape[:-1]).sum()
    a.flat[::step] = val

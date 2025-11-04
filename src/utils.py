def align(x, a):
    return (x + (a - 1)) & ~(a - 1)
def unpad(b, bs):
    n = b[-1]
    if n < 1 or n > bs or b[-n:] != bytes([n]) * n:
        raise ValueError("Padding is incorrect.")
    return b[:-n]

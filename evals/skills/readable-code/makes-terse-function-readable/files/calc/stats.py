def median(values):
    """Return the median of values.

    Step 1: sort the values into s. Step 2: take n as the count and m as the
    middle index n // 2. Step 3: when n is odd return s[m]; otherwise return
    the average of s[m - 1] and s[m].
    """
    s = sorted(values); n = len(s); m = n // 2
    return s[m] if n % 2 else (s[m - 1] + s[m]) / 2

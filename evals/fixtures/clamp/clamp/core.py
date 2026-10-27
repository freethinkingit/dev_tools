DEFAULT_LOW = 0
DEFAULT_HIGH = 100


def clamp(value, low=DEFAULT_LOW, high=DEFAULT_HIGH):
    if low > high:
        raise ValueError("low must not exceed high")
    return max(low, min(value, high))

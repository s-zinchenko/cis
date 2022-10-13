def to_int(value, default=None):
    try:
        return int(float(value))
    except ValueError:
        return default

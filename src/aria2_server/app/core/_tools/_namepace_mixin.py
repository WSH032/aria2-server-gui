__all__ = ("NamepaceMixin",)


class NamepaceMixin:
    def __init__(self):
        raise RuntimeError(f"{type(self)} is a singleton Namespace")

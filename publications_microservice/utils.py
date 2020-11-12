"""Helper functions for the project."""


class FilterParam:
    """Filter a query based on an op and param"""

    def __init__(self, name, op):
        self.name = name
        self.op = op
        self.val = None

    def __call__(self, val):
        self.val = val
        return self

    def apply(self, query, model):
        return query.filter(self.op(getattr(model, self.name), self.val))

    def __repr__(self):
        return f"filter {self.name} by {self.op}"

    def __str__(self):
        return self.__repr__()

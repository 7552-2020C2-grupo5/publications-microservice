"""Helper functions for the project."""


class FilterParam:
    """Filter a query based on an op and param"""

    def __init__(self, name, op, _in="query", schema="int", attribute=None):
        """Filter by operation.

        Parameters
        ----------
        name: Name for the filter.
        op: Operation to filter with.
        _in: Where the parameter is located.
        schema: The type for swagger documentation.
        attribute: If none, uses name. The attribute to filter on.
        """

        self.name = name
        self.op = op
        self.val = None
        self.attribute = attribute or self.name
        self.__schema__ = {"name": name, "in": _in, "type": schema}

    def __call__(self, val):
        self.val = val
        return self

    def apply(self, query, model):
        return query.filter(self.op(getattr(model, self.attribute), self.val))

    def __repr__(self):
        return f"filter {self.name} by {self.op}"

    def __str__(self):
        return self.__repr__()

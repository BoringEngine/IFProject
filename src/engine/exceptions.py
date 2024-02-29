class NotRecognized(Exception):
    """Raised when a node is not recognized by the parser."""

    ...


class BadNode(Exception):
    """Raised when a node does not match its spec during runtime."""

    ...


class BadAddress(Exception):
    """Raised when there is no node at the given address."""

    ...

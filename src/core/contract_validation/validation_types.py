"""
Contract Validation Types

Core exception types and data structures for contract validation.
"""


class ContractValidationError(Exception):
    """Raised when contract validation fails"""
    pass


class ToolValidationError(Exception):
    """Raised when tool implementation doesn't match its contract"""
    pass

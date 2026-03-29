# deal — Design by Contract for Python
# Install: pip install deal
#
# Contracts are checked at runtime and can also be verified statically
# with `deal lint` and tested with `deal test`.
#
# Contract types:
#   @deal.pre    — precondition (checked before function execution)
#   @deal.post   — postcondition (checked after, receives return value)
#   @deal.ensure — state transition (receives old and new values)
#   @deal.raises — explicit exception contract
#   @deal.has    — side-effect declaration

import deal


# Example: function with precondition and postcondition
@deal.pre(lambda x: x > 0, message="x must be positive")
@deal.post(lambda result: result >= 0, message="result must be non-negative")
def square_root(x: float) -> float:
    return x**0.5


# Example: state transition contract
@deal.ensure(lambda old, new: new >= old, message="balance must not decrease on deposit")
def deposit(balance: float, amount: float) -> float:
    return balance + amount


# Example: explicit exception contract
@deal.raises(ValueError, TypeError)
def parse_config(raw: str) -> dict:
    if not raw:
        msg = "empty config"
        raise ValueError(msg)
    return {"parsed": True}


# Example: side-effect declaration (pure function)
@deal.has()  # no side effects allowed
def add(a: int, b: int) -> int:
    return a + b


# Run static verification: python -m deal lint mymodule.py
# Run property testing: python -m deal test mymodule.py

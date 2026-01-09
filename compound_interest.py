"""
Compound Interest Calculator

Calculates compound interest using the formula:
A = P(1 + r/n)^(nt)

Where:
    A = Final amount
    P = Principal (initial investment)
    r = Annual interest rate (as decimal, e.g., 0.05 for 5%)
    n = Number of times interest is compounded per year
    t = Time in years
"""


class CompoundInterestError(ValueError):
    """Base exception for compound interest calculation errors."""
    pass


class NegativePrincipalError(CompoundInterestError):
    """Raised when principal is negative."""
    pass


class NegativeRateError(CompoundInterestError):
    """Raised when interest rate is negative."""
    pass


class NegativeTimeError(CompoundInterestError):
    """Raised when time period is negative."""
    pass


class InvalidFrequencyError(CompoundInterestError):
    """Raised when compounding frequency is zero or negative."""
    pass


def calculate_compound_interest(
    principal: float,
    rate: float,
    time: float,
    frequency: int
) -> float:
    """
    Calculate compound interest.

    Args:
        principal: Initial investment amount (must be >= 0)
        rate: Annual interest rate as decimal (must be >= 0, e.g., 0.05 for 5%)
        time: Time period in years (must be >= 0)
        frequency: Number of times interest compounds per year (must be > 0)

    Returns:
        Final amount after compound interest is applied

    Raises:
        NegativePrincipalError: If principal is negative
        NegativeRateError: If rate is negative
        NegativeTimeError: If time is negative
        InvalidFrequencyError: If frequency is zero or negative

    Examples:
        >>> calculate_compound_interest(1000, 0.05, 10, 12)  # Monthly compounding
        1647.0094976902798
        >>> calculate_compound_interest(1000, 0.05, 10, 1)   # Annual compounding
        1628.894626777442
    """
    # Validate inputs - use error handling for anticipated bad input
    # (per cc-defensive-programming: external input validation)
    if principal < 0:
        raise NegativePrincipalError(
            f"Principal cannot be negative, got {principal}"
        )

    if rate < 0:
        raise NegativeRateError(
            f"Interest rate cannot be negative, got {rate}"
        )

    if time < 0:
        raise NegativeTimeError(
            f"Time period cannot be negative, got {time}"
        )

    if frequency <= 0:
        raise InvalidFrequencyError(
            f"Compounding frequency must be positive, got {frequency}"
        )

    # Handle edge case: zero principal or zero time returns principal unchanged
    if principal == 0 or time == 0:
        return principal

    # Handle edge case: zero rate returns principal unchanged
    if rate == 0:
        return principal

    # Calculate compound interest using formula: A = P(1 + r/n)^(nt)
    # base = 1 + (rate / frequency)
    base = 1 + (rate / frequency)

    # exponent = frequency * time
    exponent = frequency * time

    # amount = principal * (base raised to exponent)
    amount = principal * (base ** exponent)

    return amount


if __name__ == "__main__":
    # Example usage demonstrating various scenarios

    # Normal case: $1000 at 5% for 10 years, compounded monthly
    result = calculate_compound_interest(1000, 0.05, 10, 12)
    print(f"$1000 at 5% for 10 years (monthly): ${result:.2f}")

    # Annual compounding comparison
    result_annual = calculate_compound_interest(1000, 0.05, 10, 1)
    print(f"$1000 at 5% for 10 years (annual): ${result_annual:.2f}")

    # Quarterly compounding
    result_quarterly = calculate_compound_interest(1000, 0.05, 10, 4)
    print(f"$1000 at 5% for 10 years (quarterly): ${result_quarterly:.2f}")

    # Edge cases
    print(f"\nEdge cases:")
    print(f"Zero principal: ${calculate_compound_interest(0, 0.05, 10, 12):.2f}")
    print(f"Zero rate: ${calculate_compound_interest(1000, 0, 10, 12):.2f}")
    print(f"Zero time: ${calculate_compound_interest(1000, 0.05, 0, 12):.2f}")

"""Fail-closed reference configuration for an authentication bypass.

This example is deliberately independent from the assessed application. It
demonstrates the security invariant and is executable by the portfolio tests.
"""

from dataclasses import dataclass


class UnsafeAuthConfiguration(RuntimeError):
    """Raised when a bypass could be enabled outside an isolated test run."""


@dataclass(frozen=True)
class AuthSettings:
    environment: str = "production"
    auth_bypass: bool = False

    def validate_runtime(self) -> None:
        """Permit the bypass only when both settings explicitly select tests."""
        normalized_environment = self.environment.strip().lower()
        if self.auth_bypass and normalized_environment != "test":
            raise UnsafeAuthConfiguration(
                "AUTH_BYPASS may only be enabled in the isolated test environment"
            )

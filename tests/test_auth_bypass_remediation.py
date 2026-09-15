import importlib.util
import unittest
from pathlib import Path


EXAMPLE_PATH = (
    Path(__file__).resolve().parents[1] / "examples" / "remediation" / "auth_bypass_guard.py"
)
SPEC = importlib.util.spec_from_file_location("auth_bypass_guard", EXAMPLE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load the remediation example")
auth_bypass_guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(auth_bypass_guard)

AuthSettings = auth_bypass_guard.AuthSettings
UnsafeAuthConfiguration = auth_bypass_guard.UnsafeAuthConfiguration


class AuthBypassRemediationTests(unittest.TestCase):
    def test_secure_defaults_are_valid(self) -> None:
        settings = AuthSettings()

        settings.validate_runtime()

        self.assertFalse(settings.auth_bypass)
        self.assertEqual(settings.environment, "production")

    def test_production_rejects_bypass(self) -> None:
        with self.assertRaises(UnsafeAuthConfiguration):
            AuthSettings(environment="production", auth_bypass=True).validate_runtime()

    def test_staging_rejects_bypass(self) -> None:
        with self.assertRaises(UnsafeAuthConfiguration):
            AuthSettings(environment="staging", auth_bypass=True).validate_runtime()

    def test_test_environment_requires_explicit_opt_in(self) -> None:
        settings = AuthSettings(environment="test", auth_bypass=True)

        settings.validate_runtime()

        self.assertTrue(settings.auth_bypass)


if __name__ == "__main__":
    unittest.main()

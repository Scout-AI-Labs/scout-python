"""Package and API version constants."""

# The version of this SDK package. Kept in sync with pyproject.toml.
__version__ = "0.1.0"

# The Scout REST API version this SDK targets. Sent as the `Scout-Version`
# header on every request so the server can pin behaviour per client.
API_VERSION = "2026-06-21"

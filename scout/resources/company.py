"""Company enrichment: profiles, logos, fonts, industry codes, styleguide."""

from __future__ import annotations

from typing import Any

from ._base import APIResource, clean_body


class Company(APIResource):
    def enrich(self, domain: str, **params: Any) -> Any:
        """Full company profile from a domain."""
        body = clean_body({"domain": domain, **params})
        return self._client.request("POST", "/v1/company", body=body)

    def by_email(self, email: str, **params: Any) -> Any:
        """Resolve a company from a work email address."""
        body = clean_body({"email": email, **params})
        return self._client.request("POST", "/v1/company/by-email", body=body)

    def by_name(self, name: str, **params: Any) -> Any:
        """Resolve a company from its name."""
        body = clean_body({"name": name, **params})
        return self._client.request("POST", "/v1/company/by-name", body=body)

    def by_ticker(self, ticker: str, **params: Any) -> Any:
        """Resolve a company from a stock ticker."""
        body = clean_body({"ticker": ticker, **params})
        return self._client.request("POST", "/v1/company/by-ticker", body=body)

    def simple(self, domain: str, **params: Any) -> Any:
        """A condensed company profile (faster, fewer fields)."""
        body = clean_body({"domain": domain, **params})
        return self._client.request("POST", "/v1/company/simple", body=body)

    def fonts(self, domain: str, **params: Any) -> Any:
        """Brand fonts detected on the company's site."""
        body = clean_body({"domain": domain, **params})
        return self._client.request("POST", "/v1/company/fonts", body=body)

    def styleguide(self, domain: str, **params: Any) -> Any:
        """Brand styleguide (colors, typography, logos) for a company."""
        body = clean_body({"domain": domain, **params})
        return self._client.request("POST", "/v1/company/styleguide", body=body)

    def logo(self, domain: str, **params: Any) -> Any:
        """Company logo metadata.

        Choose ``mode`` (light/dark), ``format`` (svg/png/webp/jpg), and
        ``variant`` (icon/wordmark/combination/logo).
        """
        body = clean_body({"domain": domain, **params})
        return self._client.request("POST", "/v1/company/logo", body=body)

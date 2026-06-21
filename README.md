# Scout Python SDK

Official Python SDK for the [Scout](https://usescout.sh) web-intelligence API — search, scrape, screenshot, extract, crawl, and company enrichment.

- **Zero runtime dependencies.** Built entirely on the Python standard library — no transitive supply chain.
- **Fully typed.** Ships a `py.typed` marker.
- **Resilient.** Automatic retries with backoff + jitter, configurable timeouts, idempotency keys.

## Requirements

- Python 3.8+

## Installation

```sh
pip install scout-sdk
```

## Authentication

Create an API key in the [Scout dashboard](https://usescout.sh). The client reads `SCOUT_API_KEY` from the environment by default:

```python
from scout import Scout

client = Scout()                 # uses SCOUT_API_KEY
client = Scout(api_key="sk_...") # or pass it explicitly
```

## Quickstart

```python
from scout import Scout

client = Scout()

results = client.search.create(
    ["best climate tech startups 2026"],
    depth="standard",
    country="us",
)
print(results)
```

## Examples

```python
# Scrape a page to Markdown
page = client.page.markdown("https://example.com")

# Screenshot
shot = client.page.screenshot("https://example.com", full_page=True, format="png")

# Structured extraction against your own JSON schema
data = client.extract.create(
    ["https://example.com/pricing"],
    output_schema={"type": "object", "properties": {"plans": {"type": "array"}}},
)

# Company enrichment + logo
company = client.company.enrich("stripe.com")
logo = client.company.logo("stripe.com", format="svg")

# Find a list of entities (find-all)
companies = client.lists.create(
    "Series A fintech companies in Europe",
    fields=["name", "website", "hq_country"],
)

# Crawl a site
crawl = client.site.crawl("https://example.com", max_pages=50, same_host_only=True)

# Chat completion grounded with web search
completion = client.chat.completions.create(
    [{"role": "user", "content": "Summarize the latest on EU AI regulation."}],
    web_search=True,
)
```

## Error handling

Every failure is a `ScoutError`. HTTP errors map to a specific subclass by status code, each carrying `status`, `request_id`, `code`, and the parsed `body`:

```python
from scout import Scout, RateLimitError, AuthenticationError, ScoutError

client = Scout()
try:
    client.search.create(["..."])
except RateLimitError as err:
    print("Slow down. Retry-After:", err.headers.get("retry-after"))
except AuthenticationError:
    print("Check your API key.")
except ScoutError as err:
    print(err.status, err.request_id, err.message)
```

| Status | Error class |
|--------|-------------|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 402 | `InsufficientCreditsError` |
| 403 | `PermissionDeniedError` |
| 404 | `NotFoundError` |
| 409 | `ConflictError` |
| 422 | `UnprocessableEntityError` |
| 429 | `RateLimitError` |
| >=500 | `InternalServerError` |
| network | `ConnectionError` / `TimeoutError` |

## Retries & timeouts

Transient failures (connection errors, timeouts, 408/409/429/5xx) are retried automatically — **2 times by default**, with exponential backoff + jitter, honoring `Retry-After`. Write methods send an auto-generated `Idempotency-Key` so retries are safe.

```python
client = Scout(timeout=30.0, max_retries=4)
# Per-call overrides via a configured clone:
client.with_options(timeout=120.0).site.crawl("https://example.com")
```

## Auto-pagination

List endpoints expose an iterator that walks every page for you:

```python
for run in client.search.iterate():
    print(run)

for monitor in client.monitors.iterate():
    print(monitor)
```

## Versioning

This SDK follows [SemVer](https://semver.org/). It pins the Scout API version it targets and sends it on every request; see [`CHANGELOG.md`](./CHANGELOG.md).

## Contributing

Issues and pull requests are welcome at [Scout-AI-Labs/scout-python](https://github.com/Scout-AI-Labs/scout-python).

## License

[MIT](./LICENSE)

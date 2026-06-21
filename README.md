# Scout Python SDK

Official Python SDK for the [Scout](https://usescout.sh) web-intelligence API: search, scrape, screenshot, extract, crawl, and company enrichment.

- Built on the Python standard library (`urllib`).
- Typed: ships a `py.typed` marker.
- Automatic retries with backoff and jitter, configurable timeouts, and idempotency keys on writes.

## Requirements

- Python 3.8+

## Installation

```sh
pip install scout-sdk
```

## Authentication

Generate an API key at [platform.usescout.sh/settings](https://platform.usescout.sh/settings). The client reads `SCOUT_API_KEY` from the environment by default:

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

Transient failures (connection errors, timeouts, 408/409/429/5xx) are retried automatically, **2 times by default**, with exponential backoff and jitter, honoring `Retry-After`. Write methods send an auto-generated `Idempotency-Key` so retries are safe.

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

## Streaming

Stream chat completions as OpenAI-style chunks, and stream live progress from async runs (search, jobs, find-all, monitors):

```python
# Token-by-token chat
for chunk in client.chat.completions.stream(
    [{"role": "user", "content": "Summarize the latest EU AI regulation."}],
    web_search=True,
):
    print(chunk["choices"][0]["delta"].get("content", ""), end="", flush=True)

# Live progress events from a deep-search run
for event in client.search.stream_events(search_id):
    print(event["type"], event)
```

`stream_events` is also available on `jobs`, `lists.runs`, and `monitors`.

## Versioning

This SDK follows [SemVer](https://semver.org/). It pins the Scout API version it targets and sends it on every request; see [`CHANGELOG.md`](./CHANGELOG.md).

## Contributing

Issues and pull requests are welcome at [Scout-AI-Labs/scout-python](https://github.com/Scout-AI-Labs/scout-python).

## License

[MIT](./LICENSE)

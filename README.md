
# LeakRadar Async Python Client

A user-friendly, asynchronous Python 3 wrapper for the [LeakRadar.io](https://leakradar.io) API.

## Features

- Async/await support using `httpx`.
- Authentication via Bearer token.
- Customizable User-Agent.
- Error handling with custom exceptions (no retries).
- Easy-to-use methods for:
  - Advanced search
  - Unlocking leaks (all or specific)
  - Exporting leaks as CSV
  - Fetching profile information

## Requirements

- Python 3.7+
- `httpx` library (`pip install httpx`)

## Installation

```bash
pip install httpx
```

*(No PyPI distribution yet, just copy `leakradar/api.py` into your project.)*

## Usage

1. Retrieve your API key from [LeakRadar.io Profile](https://leakradar.io/profile).
2. Create a client instance, passing your Bearer token.

```python
import asyncio
from leakradar.api import LeakRadarClient

async def main():
    token = "YOUR_BEARER_TOKEN"
    async with LeakRadarClient(token=token) as client:
        profile = await client.get_profile()
        print("User Profile:", profile)

        # Perform an advanced search
        results = await client.search_advanced(username="john.doe@example.com", show_only_unlocked=True)
        print("Search Results:", results)

        # Unlock all matching leaks
        unlocked = await client.unlock_all_advanced({"username": "john.doe@example.com"})
        print("Unlocked leaks:", unlocked)

        # Export unlocked leaks as CSV
        csv_data = await client.export_advanced(username="john.doe@example.com")
        with open("leaks_export.csv", "wb") as f:
            f.write(csv_data)
        print("CSV exported to leaks_export.csv")

asyncio.run(main())
```

## Error Handling

All errors raise a `LeakRadarAPIError` subclass. For example:
- `BadRequestError` (400)
- `UnauthorizedError` (401)
- `ForbiddenError` (403)
- `NotFoundError` (404)
- `ValidationError` (422)
- `TooManyRequestsError` (429)

## Contributing

Please open an issue or PR if you have suggestions or improvements.

## License

[MIT](https://opensource.org/licenses/MIT)

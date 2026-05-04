# AGENTS.md — MCP QWeather Server

## Project Overview

A **Weather MCP (Model Context Protocol) Server** built with **FastMCP** that wraps the **QWeather (和风天气) API** into standardized MCP tools for AI assistants (Claude, etc.).

- **Language**: Python 3.13+
- **Package manager**: uv
- **Framework**: FastMCP
- **License**: MIT

## Project Structure

```
.
├── apis/                        # Core API client library
│   ├── __init__.py              # Exports GeoAPI, WeatherAPI, MinutelyAPI
│   ├── base.py                  # QWeatherAPI base class, JWT auth, 17 validators
│   ├── geo.py                   # GeoAPI — city_lookup, poi_lookup, poi_range
│   ├── weather.py               # WeatherAPI — 6 weather endpoints (now/daily/hourly/grid)
│   ├── minutely.py              # MinutelyAPI — precipitation, AQI, astronomy, indices
│   └── schemas.py               # Empty placeholder for Pydantic models
├── keys/
│   ├── ed25519-public.pem       # Ed25519 public key (committed)
│   └── ed25519-private.pem      # Private key (gitignored)
├── tests/
│   └── test_api.py              # Comprehensive test suite (~61 cases)
├── server.py                    # MCP server entry point — 18 tools, 2 transport modes
├── config.py                    # pydantic-settings configuration from .env
├── test_client.py               # Simple MCP client example
├── pyproject.toml               # uv project config, 5 deps
├── uv.lock                      # Locked dependency versions
├── .dockerignore                # Docker build exclusions
├── Dockerfile                   # Python 3.13-slim, HTTP mode
├── docker-compose.yaml          # Port 28001:8000, secret mount, .env
├── docker-run.sh                # 203-line bash deploy script
├── .env.example                 # Environment variable template
└── .gitignore                   # Excludes __pycache__, .venv, .env, private keys
```

## Commands

| Command | Purpose |
|---------|---------|
| `uv sync` | Install dependencies |
| `uv run python server.py --stdio` | Run server in **stdio mode** |
| `uv run python server.py` | Run server in **HTTP mode** (0.0.0.0:8000, default for Docker) |
| `uv run python tests/test_api.py` | Run full test suite (~61 tests) |
| `./docker-run.sh --detach` | Build & run Docker container |
| `docker-compose up -d` | Run via Docker Compose |

## Architecture

### Transport Modes

- **Stdio**: `mcp.run(transport="stdio")` — for local MCP clients
- **HTTP** (default): `mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)` — for remote access / Docker

### API Client Hierarchy

```
QWeatherAPI (apis/base.py)
├── GeoAPI (apis/geo.py)       — city/POI search
├── WeatherAPI (apis/weather.py) — weather now/daily/hourly/grid
└── MinutelyAPI (apis/minutely.py) — precipitation, AQI, astronomy, indices
```

### JWT Authentication Flow

1. Ed25519 key pair in `keys/` (generated with openssl)
2. Public key uploaded to QWeather console to create JWT credential
3. `QWeatherAPI.generate_jwt()` creates EdDSA-signed JWT with 15-min expiry
4. Token cached until 60s before expiry, refreshed automatically

**Note**: PyJWT automatically adds `typ: "JWT"` to the token header. This is compliant with QWeather's current JWT spec but is a reserved field per the [authentication docs](https://dev.qweather.com/docs/configuration/authentication/#json-web-token).

### Key QWeather Documentation

- [Authentication (JWT)](https://dev.qweather.com/docs/configuration/authentication/)
- [Error Codes](https://dev.qweather.com/docs/resource/error-code/) — v1 and v2 formats handled
- [Caching Best Practices](https://dev.qweather.com/docs/best-practices/cache/)
- [No Assumptions](https://dev.qweather.com/docs/best-practices/no-assumptions/) — never assume data completeness
- [Gzip Handling](https://dev.qweather.com/docs/best-practices/gzip/) — enabled on all requests

### Configuration (`config.py`)

Uses `pydantic-settings` with `BaseSettings`. Reads from `.env` file automatically.

| Env Variable | Config Field | Required |
|---|---|---|
| `QWEATHER_API_HOST` | `qweather_api_host` | Yes |
| `PRIVATE_KEY_PATH` | `private_key_path` | No (default: `keys/ed25519-private.pem`) |
| `QWEATHER_KEY_ID` | `key_id` | Yes |
| `QWEATHER_PROJECT_ID` | `project_id` | Yes |

### Server Logging

`LoggingFastMCP` (subclass of `FastMCP`, `server.py:43`) overrides `call_tool()` to log every tool invocation including invalid/unknown tools. Both app logger and uvicorn access logger are configured with timestamp format.

### 18 MCP Tools

**Geo (3)**: `city_lookup`, `poi_lookup`, `poi_range`
**Weather (6)**: `weather_now`, `weather_daily`, `weather_hourly`, `grid_weather_now`, `grid_weather_daily`, `grid_weather_hourly`
**Minutely/Air/Astro (9)**: `minutely_precipitation`, `indices_forecast`, `air_now`, `air_hourly`, `air_daily`, `air_station`, `astronomy_sun`, `astronomy_moon`, `solar_elevation_angle`

### Input Validation (`apis/base.py`)

All input validation happens at the tool layer (in `server.py` tool decorators), calling validators from `apis/base.py` (lines 64–191). Validators raise `ValueError` with descriptive messages. Key validators:

- `validate_coordinates()` — regex for `lon,lat` format
- `validate_location_id()` — alphanumeric
- `validate_days/hours()` — against allowed tuple sets
- `validate_date()` — yyyyMMdd format and calendar validity
- `validate_time()` — HHmm (24h)
- `validate_timezone()` — ±HHmm with valid hour/minute ranges
- `validate_number/radius/altitude/latitude/longitude()` — range checks
- `validate_lang()` — normalizes to "zh" or "en"
- `validate_unit()` — "m" or "i"
- `validate_country_code()` — ISO 3166 alpha-2

## Testing

Tests are in `tests/test_api.py` (503 lines). They use `fastmcp.Client` with `PythonStdioTransport` — the test starts the actual MCP server as a subprocess and calls tools via MCP protocol.

Test data: Beijing LocationID `101010100`, coordinates `116.41,39.92`.

Tests are run with: `uv run python tests/test_api.py`

## Code Conventions

- All tool functions are `async def` and return `dict`
- Parameters use explicit type hints
- Lang parameter defaults to `None` and is validated to `None`, `"zh"`, or `"en"`
- Tools accept either LocationID (alphanumeric) or coordinates (`"lon,lat"`) with `is_coordinate_location()` detection
- Grid weather tools require coordinates only
- Validators are pure functions, imported and called at the tool layer
- API methods pass params as-is to `_request()` without extra processing
- JWT token generation happens in `generate_jwt()`, called from `_request()` with caching

## Agent Constraints

### Git Commit Policy

1. **Do NOT commit code without human confirmation.** Unless explicitly instructed to commit by the user (e.g. "commit", "提交", "commit and push"), agents must NOT run `git commit`. Always ask for confirmation before committing.

2. **Pre-commit checks are mandatory for code changes.** Before any `git commit` involving code changes, the following must pass:
   - Full test suite: `uv run python tests/test_api.py`
   - Docker build: `docker compose build` (or `docker build -t mcp-qweather .`)

3. If either check fails, fix the issue and run both checks again before committing.

### Exceptions

The following do NOT require pre-commit checks (they don't involve code changes):
- Documentation-only changes (README.md, AGENTS.md itself)
- Configuration file edits (.gitignore, .dockerignore, .env.example)
- Dockerfile or docker-compose.yaml changes — only Docker build check is required, tests optional

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastmcp` | MCP server framework |
| `httpx` | Async HTTP client for QWeather API (shared instance with connection pool) |
| `cryptography` | Ed25519 private key loading and signing |
| `pydantic-settings` | .env-based configuration |
| `python-dotenv` | .env file loading (required by pydantic-settings for env_file support) |

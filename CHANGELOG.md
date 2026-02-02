# Changelog

## [1.0.3] - 2026-02-02

### Breaking Change

Removed automatic Input Boolean creation since it turns out the Home Assistant REST API doesn't actually support creating them programmatically. Users now need to create the Input Boolean helpers manually through the UI or configuration.yaml before starting the addon.

The good news: when a helper is missing, you'll get a clear message with exact instructions instead of cryptic 400 errors. Added a complete setup guide in docs/setup_helpers.md that walks through the whole process.

Also updated the config.yaml with comments showing what entity IDs will be created for each switch, which should help avoid confusion.

## [1.0.2] - 2026-02-01

### Fixed

Turns out the API call for creating Input Booleans was missing the `object_id` parameter. Added that, so now entities get created with the correct naming: `input_boolean.webhook_{switch_id}`.

(Still didn't work though - see v1.0.3 for why)

## [1.0.1] - 2026-02-01

### Fixed

Critical bug: forgot to install `jq` in the Docker image. The startup script uses it to parse the addon config, so without it nothing worked. Added jq to the Dockerfile and now the addon actually starts.

## [1.0.0] - 2026-01-31

Initial release! 

This addon lets you control Home Assistant switches via webhooks with JWT authentication. Useful for integrating with external services like Telegram bots or IFTTT.

Features:
- FastAPI server with async support
- JWT token auth (keeps random internet people out)
- Four actions: on, off, toggle, status
- Can set custom attributes on switches
- Configurable logging
- Works with Input Boolean helpers

The webhook API is pretty straightforward - POST to `/webhook` with your token and switch info. Check the docs folder for examples with curl and Python.

# Home Assistant Incoming Webhook

[![GitHub Release](https://img.shields.io/github/release/torquemada163/home-assistant-incoming-webhook.svg)](https://github.com/torquemada163/home-assistant-incoming-webhook/releases)
[![License](https://img.shields.io/github/license/torquemada163/home-assistant-incoming-webhook.svg)](LICENSE)

A webhook server for Home Assistant that lets you trigger switches from external services. Useful for integrating with things like Telegram bots, IFTTT, or custom scripts.

## What it does

This addon runs a simple API server inside Home Assistant that responds to webhook POST requests. You can use it to control Input Boolean helpers, which then trigger automations in Home Assistant.

Main features:
- JWT token authentication (keeps random people out)
- Configure multiple switches via YAML
- Four actions: on, off, toggle, status
- Stores custom attributes with each trigger
- Configurable logging

## Installation

### Add the repository

1. Go to **Settings → Add-ons → Add-on Store**
2. Click the **⋮** menu → **Repositories**
3. Add this URL:
   ```
   https://github.com/torquemada163/home-assistant-incoming-webhook
   ```
4. Click **Add**

### Install the addon

1. Find **Incoming Webhook** in the add-on store
2. Click **Install**
3. Wait for it to finish

### Create Input Boolean helpers

**Important:** As of v1.0.3, you need to manually create Input Boolean helpers before starting the addon. The API doesn't support creating them automatically.

For each switch in your config, create a helper:

1. **Settings → Devices & Services → Helpers**
2. **+ CREATE HELPER → Toggle**
3. Fill in:
   - Name: whatever you want (e.g., "Telegram Notifications")
   - Icon: pick one (e.g., "mdi:telegram")
   - **Advanced Settings → Object ID**: must be `webhook_{your_switch_id}`
4. Click **Create**

Example: if your switch ID is `telegram_bot`, the Object ID must be `webhook_telegram_bot`. This creates the entity `input_boolean.webhook_telegram_bot`.

See [docs/setup_helpers.md](docs/setup_helpers.md) for detailed instructions with screenshots.

### Configure

Go to the addon **Configuration** tab and set:

```yaml
jwt_secret: "change-me-to-something-random-at-least-32-chars"
port: 8099
log_level: info

switches:
  - id: telegram_bot
    name: "Telegram Notifications"
    icon: mdi:telegram
  
  - id: motion_trigger
    name: "Motion Sensor"
    icon: mdi:motion-sensor
```

Generate a random secret:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Start it

Click **Start** on the Info tab. Check the **Log** to make sure it found all your Input Boolean helpers. You should see:
```
✅ Switch input_boolean.webhook_telegram_bot found
✅ Switch input_boolean.webhook_motion_trigger found
```

If you see warnings about missing helpers, go back and create them.

## Usage

### Generate a JWT token

You'll need a token to authenticate API requests. Here's a Python snippet:

```python
import jwt
from datetime import datetime, timedelta, timezone

secret = "your-jwt-secret-from-config"
payload = {
    "iss": "my-service",
    "exp": datetime.now(timezone.utc) + timedelta(days=365)
}
token = jwt.encode(payload, secret, algorithm="HS256")
print(token)
```

### Make requests

```bash
curl -X POST http://homeassistant.local:8099/webhook \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "switch_id": "telegram_bot",
    "action": "on"
  }'
```

Actions:
- `on` - turn the switch on
- `off` - turn it off
- `toggle` - flip the state
- `status` - get current state

You can also include custom attributes:
```json
{
  "switch_id": "telegram_bot",
  "action": "on",
  "attributes": {
    "source": "telegram",
    "user_id": "12345"
  }
}
```

These get stored on the Input Boolean entity and are visible in Developer Tools → States.

## Using it with automations

Once you've got switches responding to webhooks, wire them up to automations:

```yaml
automation:
  - alias: "Telegram notification triggered"
    trigger:
      - platform: state
        entity_id: input_boolean.webhook_telegram_bot
        to: "on"
    action:
      - service: notify.telegram
        data:
          message: "Webhook triggered!"
```

The Input Boolean helpers persist their state, so you can check them later or use them in conditions.

## Troubleshooting

**Addon won't start:**
- Check the logs for errors
- Make sure your jwt_secret is at least 32 characters
- Verify you created all the Input Boolean helpers

**Getting 401 errors:**
- Your JWT token doesn't match the secret in the config
- Token might be expired (check the `exp` claim)

**Getting 404 for switches:**
- The Input Boolean helper doesn't exist
- Check that the Object ID matches `webhook_{switch_id}`
- Look at Settings → Devices & Services → Helpers to verify

**Can't reach the webhook:**
- The addon listens on port 8099 by default
- From outside Home Assistant, you might need to forward the port
- Try `http://homeassistant.local:8099/webhook` or your HA IP address

## Documentation

- [Setup guide for Input Boolean helpers](docs/setup_helpers.md)
- [Configuration options](docs/configuration.md) _(if exists)_
- [More examples](docs/examples.md) _(if exists)_

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Found a bug? [Open an issue](https://github.com/torquemada163/home-assistant-incoming-webhook/issues).

Want to add a feature? Pull requests welcome.

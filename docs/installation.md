# Installation

Quick guide to get the Incoming Webhook addon running in Home Assistant.

## Requirements

- Home Assistant OS or Home Assistant Supervised
- Access to the Supervisor add-on store
- Basic YAML knowledge

## Step 1: Add the repository

1. Open **Settings → Add-ons → Add-on Store**
2. Click the **⋮** menu (top right)
3. Select **Repositories**
4. Add this URL:
   ```
   https://github.com/torquemada163/home-assistant-incoming-webhook
   ```
5. Click **Add**

## Step 2: Install the addon

1. Go back to the Add-on Store
2. Refresh the page (F5)
3. Find **Incoming Webhook** in the list
4. Click on it
5. Click **Install**
6. Wait a few minutes for installation to complete

##Step 3: Create Input Boolean helpers

**This is required before starting the addon!** As of v1.0.3, you need to manually create Input Boolean helpers for each switch.

For detailed instructions with screenshots, see [docs/setup_helpers.md](setup_helpers.md).

Quick version:

1. **Settings → Devices & Services → Helpers**
2. **+ CREATE HELPER → Toggle**
3. For each switch in your config:
   - Name: whatever you want
   - Icon: pick one (e.g., "mdi:telegram")
   - **Advanced Settings → Object ID**: must be `webhook_{your_switch_id}`
4. Click **Create**

Example: if your switch ID is `telegram_bot`, the Object ID must be `webhook_telegram_bot`.

## Step 4: Configure the addon

Go to the **Configuration** tab.

### Generate a JWT secret

First, generate a secure random string (at least 32 characters):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Or use [RandomKeygen](https://randomkeygen.com/) and grab a "CodeIgniter Encryption Keys" value.

### Set up the config

```yaml
jwt_secret: "YOUR-GENERATED-SECRET-HERE"
port: 8099
log_level: info

switches:
  - id: telegram_bot
    name: "Telegram Notifications"
    icon: "mdi:telegram"
  
  - id: motion_trigger
    name: "Motion Sensor"
    icon: "mdi:motion-sensor"
```

Replace `YOUR-GENERATED-SECRET-HERE` with your generated secret.

Add as many switches as you need. Each one maps to a webhook target.

Available icons: [Material Design Icons](https://pictogrammers.com/library/mdi/)

Click **Save**.

## Step 5: Start it

1. Go to the **Info** tab
2. Click **Start**
3. Wait for "Started successfully" message
4. (Optional) Enable **Start on boot** to auto-start

## Step 6: Check the logs

Go to the **Log** tab. You should see:

```
Starting Incoming Webhook Addon
✅ Switch input_boolean.webhook_telegram_bot found
✅ Switch input_boolean.webhook_motion_trigger found
Switch initialization complete
Webhook addon is ready to receive requests
```

If you see warnings about missing Input Boolean helpers, go back to Step 3 and create them.

## Step 7: Generate an API token

To call the webhook, you need a JWT token. Here's a Python snippet:

```python
import jwt
from datetime import datetime, timedelta, timezone

# Same secret as in addon config
JWT_SECRET = "YOUR-GENERATED-SECRET-HERE"

payload = {
    "iss": "my-service",
    "exp": datetime.now(timezone.utc) + timedelta(days=365)
}

token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
print(token)
```

Save this token - you'll use it for all webhook calls.

## Step 8: Test it

Try a test request:

```bash
curl -X POST http://homeassistant.local:8099/webhook \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "switch_id": "telegram_bot",
    "action": "on"
  }'
```

Expected response:

```json
{
  "status": "success",
  "switch_id": "telegram_bot",
  "action": "on",
  "state": "on"
}
```

Check **Developer Tools → States** and look for `input_boolean.webhook_telegram_bot` - it should be "on".

## Troubleshooting

**Addon won't start:**
- Check the logs for errors
- Make sure jwt_secret is at least 32 characters
- Verify YAML syntax is correct

**401 Unauthorized:**
- Your JWT token doesn't match the secret in the config
- Token might be expired (check the `exp` claim)
- Regenerate the token with the correct secret

**404 Switch not found:**
- The switch_id in your request doesn't match any `id` in the config
- Double-check spelling
- Restart the addon after changing config

**Input Boolean not found warnings:**
- You haven't created the Input Boolean helper yet
- The Object ID doesn't match `webhook_{switch_id}` format
- Go to Settings → Devices & Services → Helpers and verify

**Can't reach the webhook:**
- The addon listens on port 8099 by default
- Try `http://homeassistant.local:8099/webhook` or your HA IP address
- If accessing from outside HA, you might need to forward the port

## Updating

When a new version is available:

1. Go to the **Info** tab
2. Click **Update** (if available)
3. Wait for update to complete
4. Restart the addon

## Uninstalling

1. Stop the addon (**Stop** button)
2. Click **Uninstall**
3. Confirm

Note: The Input Boolean helpers (`input_boolean.webhook_*`) will remain in Home Assistant. Delete them manually if you don't need them anymore.

## Next steps

- [setup_helpers.md](setup_helpers.md) - Detailed guide for creating Input Boolean helpers
- [configuration.md](configuration.md) - All configuration options explained
- [examples.md](examples.md) - Real-world usage examples

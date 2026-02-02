# Configuration

Everything you need to know about configuring the Incoming Webhook addon.

## Basic structure

The addon uses YAML configuration in the Home Assistant Supervisor interface:

```yaml
jwt_secret: string
port: integer
log_level: string
switches:
  - id: string
    name: string
    icon: string
```

## jwt_secret

**Type:** `string` (required)  
**Minimum length:** 32 characters

The secret key for signing and verifying JWT tokens. This is basically your API password.

Generate a random one:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Important notes:
- Must be random and unique
- DON'T use the example value in production
- Keep it secret - anyone with this can call your webhook
- If you change it, all existing tokens become invalid

## port

**Type:** `integer` (optional)  
**Default:** `8099`  
**Range:** 1024-65535

The port the webhook server listens on inside the container.

You usually don't need to change this. Home Assistant handles port routing automatically.

## log_level

**Type:** `string` (optional)  
**Default:** `info`  
**Values:** `debug`, `info`, `warning`, `error`

How verbose the logs should be.

- `debug` - Everything (use for troubleshooting)
- `info` - Normal stuff (recommended)
- `warning` - Only warnings and errors
- `error` - Only errors

Example output by level:

```
# debug
[2026-02-02 22:00:00] DEBUG: JWT token verified for issuer: telegram-bot
[2026-02-02 22:00:01] INFO: Webhook called: switch_id=motion_trigger, action=on
[2026-02-02 22:00:02] DEBUG: Updated attributes for motion_trigger

# info
[2026-02-02 22:00:01] INFO: Webhook called: switch_id=motion_trigger, action=on
[2026-02-02 22:00:02] INFO: Successfully processed on for motion_trigger, state=on

# warning
[2026-02-02 22:00:05] WARNING: Switch 'unknown_id' not found
[2026-02-02 22:00:10] WARNING: Invalid JWT token

# error
[2026-02-02 22:00:15] ERROR: Home Assistant API error: Connection timeout
```

## switches

**Type:** `array` (required)  
**Minimum:** 1 switch

The list of webhook targets. Each switch maps to an Input Boolean helper in Home Assistant.

### Switch parameters

#### id

**Type:** `string` (required)  
**Format:** letters, numbers, underscores  
**Example:** `telegram_bot`

Unique identifier for the switch. Used in API calls.

Rules:
- Must be unique
- Used in webhook requests as `switch_id`
- Becomes part of entity ID: `input_boolean.webhook_{id}`
- No spaces or special characters

#### name

**Type:** `string` (required)  
**Example:** `"Telegram Notifications"`

Display name in Home Assistant UI.

Tips:
- Use descriptive names
- Can include spaces and special characters
- Shows up in the HA interface

#### icon

**Type:** `string` (optional)  
**Default:** `mdi:light-switch`  
**Format:** `mdi:icon-name`  
**Example:** `mdi:telegram`

Material Design Icon for the switch.

Popular ones:
- `mdi:telegram` - Telegram
- `mdi:webhook` - Generic webhook
- `mdi:motion-sensor` - Motion sensor
- `mdi:doorbell` - Doorbell
- `mdi:alarm-light` - Alarm
- `mdi:bell` - Notification
- `mdi:lightbulb` - Light

Browse all: [pictogrammers.com/library/mdi](https://pictogrammers.com/library/mdi/)

## Example configs

### Minimal

```yaml
jwt_secret: "your-super-long-random-secret-at-least-32-chars"
switches:
  - id: webhook_trigger
    name: "Webhook Trigger"
```

### Standard

```yaml
jwt_secret: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
port: 8099
log_level: info

switches:
  - id: telegram_bot
    name: "Telegram Bot"
    icon: "mdi:telegram"
  
  - id: external_api
    name: "External API Trigger"
    icon: "mdi:webhook"
```

### Full setup

```yaml
jwt_secret: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
port: 8099
log_level: info

switches:
  # Notifications
  - id: telegram_notifications
    name: "Telegram Notifications"
    icon: "mdi:telegram"
  
  - id: email_alert
    name: "Email Alert"
    icon: "mdi:email"
  
  # Sensors
  - id: motion_hallway
    name: "Motion - Hallway"
    icon: "mdi:motion-sensor"
  
  - id: motion_kitchen
    name: "Motion - Kitchen"
    icon: "mdi:motion-sensor"
  
  # Events
  - id: doorbell_front
    name: "Doorbell - Front"
    icon: "mdi:doorbell"
  
  - id: doorbell_back
    name: "Doorbell - Back"
    icon: "mdi:doorbell"
  
  # System
  - id: alarm_triggered
    name: "Alarm Activated"
    icon: "mdi:alarm-light"
  
  - id: backup_done
    name: "Backup Complete"
    icon: "mdi:backup-restore"
```

## Validation

The addon checks your config on startup:

- ✅ jwt_secret is at least 32 characters
- ✅ At least one switch is defined
- ✅ All switch IDs are unique
- ✅ log_level is valid
- ✅ port is in valid range

If validation fails, the addon won't start and you'll see an error in the logs.

## Changing config

1. Stop the addon (**Stop** button)
2. Go to **Configuration** tab
3. Make your changes
4. Click **Save**
5. Start the addon (**Start** button)

**Note about switches:**
- New switches: The addon will look for their Input Boolean helpers on startup
- Removed switches: Their Input Boolean helpers remain in HA (delete manually if needed)
- Changed name/icon: Won't update existing helpers automatically

## Best practices

### Security

- ✅ Use a cryptographically random jwt_secret
- ✅ Rotate jwt_secret periodically (once a year is fine)
- ✅ Don't commit configs with secrets to git
- ✅ Use different secrets for dev and production

### Naming

- ✅ Use meaningful IDs (`telegram_bot`, not `switch1`)
- ✅ Group related switches with prefixes (`motion_hallway`, `motion_kitchen`)
- ✅ Use clear display names

### Logging

- ✅ Use `info` level in production
- ✅ Use `debug` only when troubleshooting
- ✅ Check logs regularly for errors

## Next steps

- [examples.md](examples.md) - Real-world usage examples
- [installation.md](installation.md) - How to install the addon

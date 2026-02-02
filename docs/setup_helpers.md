# Setting up Input Boolean Helpers

## Why manual setup?

The Home Assistant REST API doesn't support creating Input Boolean helpers programmatically. You need to create them manually through the Home Assistant UI or configuration.yaml.

> **IMPORTANT:** Before starting the addon, you MUST create Input Boolean helpers for all switches configured in the addon.

---

## Quick start

For each switch in your addon config:

```yaml
switches:
  - id: "test_switch"          # <-- This is the switch ID
    name: "Test Switch"
    icon: "mdi:light-switch"
```

You need to create an Input Boolean with:
- **Object ID**: `webhook_test_switch` (format: `webhook_{id}`)
- **Name**: Anything (recommended: same as config)
- **Icon**: Anything (recommended: same as config)

---

## Option 1: Via UI (Recommended)

### Step 1: Open Helpers

1. Open **Home Assistant** in your browser
2. Go to **Settings**
3. Select **Devices & Services**
4. Go to **Helpers** tab

### Step 2: Create a Toggle

1. Click **+ CREATE HELPER**
2. Select **Toggle**

### Step 3: Fill in the fields

**Required:**

- **Name**: Enter the switch name
  - Example: `Test Switch`
  - Can be anything, but recommended to match addon config

**Optional:**

- **Icon**: Choose an icon
  - Format: `mdi:icon-name`
  - Example: `mdi:light-switch`, `mdi:telegram`, `mdi:bell`
  - Browse: [Material Design Icons](https://pictogrammers.com/library/mdi/)

### Step 4: IMPORTANT - Set Object ID

> **CRITICAL:** Object ID MUST follow the format `webhook_{id}`

1. Click **ADVANCED SETTINGS**
2. In **Object ID** field, enter: `webhook_{your_id}`
   - If addon config has `id: "test_switch"`, Object ID = `webhook_test_switch`
   - If addon config has `id: "telegram_bot"`, Object ID = `webhook_telegram_bot`

**Why is this important?**
- The addon looks for entities named `input_boolean.webhook_{id}`
- If Object ID is wrong, the addon won't find the switch

### Step 5: Create

1. Click **CREATE**
2. The helper will appear in the list

### Step 6: Repeat for all switches

Repeat steps 2-5 for each switch in your addon config.

---

## Option 2: Via configuration.yaml

### Step 1: Open configuration.yaml

1. Open `configuration.yaml` in your editor
   - Via File Editor addon
   - Or via SSH/terminal

### Step 2: Add Input Boolean section

Add (or extend existing) `input_boolean` section:

```yaml
input_boolean:
  # Switch 1
  webhook_test_switch:
    name: Test Switch
    icon: mdi:light-switch
  
  # Switch 2
  webhook_telegram_bot:
    name: Telegram Bot Trigger
    icon: mdi:telegram
  
  # Add all your switches from addon config
```

**Format:**
```yaml
input_boolean:
  webhook_{id}:              # Object ID (MUST be webhook_{id})
    name: Your Name          # Any name
    icon: mdi:icon-name      # mdi icon (optional)
    initial: off             # Initial state (optional)
```

### Step 3: Check configuration

1. Go to **Developer Tools**
2. **YAML** tab
3. Click **CHECK CONFIGURATION**
4. Make sure there are no errors

### Step 4: Restart Home Assistant

1. Go to **Settings → System**
2. Click **RESTART**
3. Confirm restart

---

## Verification

After creating Input Boolean helpers, verify they exist:

### Method 1: Via Helpers

1. **Settings → Devices & Services → Helpers**
2. You should see all created switches
3. Names should start with `webhook_`

### Method 2: Via Developer Tools

1. Go to **Developer Tools**
2. **States** tab
3. Search for `webhook`
4. You should see all entities like:
   ```
   input_boolean.webhook_test_switch
   input_boolean.webhook_telegram_bot
   ...
   ```

### Method 3: Via Addon Logs

1. Start (or restart) the **Incoming Webhook** addon
2. Open **Log** tab
3. You should see:
   ```
   [INFO] Initializing 2 switches...
   [INFO] ✅ Switch input_boolean.webhook_test_switch found
   [INFO] ✅ Switch input_boolean.webhook_telegram_bot found
   [INFO] Switch initialization complete
   ```

❌ **If you see warnings**:
```
[WARNING] ⚠️ Input Boolean 'input_boolean.webhook_xxx' NOT FOUND!
```
The switch wasn't created or Object ID is wrong.

---

## Examples

### Example 1: Basic setup

**Addon config:**
```yaml
switches:
  - id: "doorbell"
    name: "Doorbell"
    icon: "mdi:bell"
```

**Create via UI:**
1. CREATE HELPER → Toggle
2. Name: `Doorbell`
3. Icon: `mdi:bell`
4. Advanced Settings → Object ID: `webhook_doorbell`
5. CREATE

**Or via configuration.yaml:**
```yaml
input_boolean:
  webhook_doorbell:
    name: Doorbell
    icon: mdi:bell
```

### Example 2: Multiple switches

**Addon config:**
```yaml
switches:
  - id: "motion_detected"
    name: "Motion Detected"
    icon: "mdi:motion-sensor"
  
  - id: "alarm_triggered"
    name: "Alarm Triggered"
    icon: "mdi:alarm-light"
  
  - id: "guest_arrived"
    name: "Guest Arrived"
    icon: "mdi:account-arrow-right"
```

**Via configuration.yaml:**
```yaml
input_boolean:
  webhook_motion_detected:
    name: Motion Detected
    icon: mdi:motion-sensor
    initial: off
  
  webhook_alarm_triggered:
    name: Alarm Triggered
    icon: mdi:alarm-light
    initial: off
  
  webhook_guest_arrived:
    name: Guest Arrived
    icon: mdi:account-arrow-right
    initial: off
```

---

## FAQ

### Can I use a different Object ID?

❌ **No**. The addon looks for entities strictly in the format `input_boolean.webhook_{id}`.
- If addon config has `id: "test"`, Object ID MUST be `webhook_test`
- Otherwise the addon won't find the switch

### Can I create Input Boolean after starting the addon?

✅ **Yes**. You can create helpers anytime, then:
1. Restart the **Incoming Webhook** addon
2. The addon will find new switches on initialization

### Do I need to restart Home Assistant?

**Depends on creation method:**
- ✅ **Via UI**: NO, helpers are available immediately
- ⚠️  **Via configuration.yaml**: YES, HA restart required

### What if I forgot the Object ID of a switch?

Check in **Developer Tools → States**:
1. Find entity `input_boolean.webhook_xxx`
2. `xxx` after `webhook_` is your `id` from addon config
3. Or check in addon Configuration tab

### Can I change name or icon after creation?

✅ **Yes**:
1. **Settings → Devices & Services → Helpers**
2. Click on the helper
3. Change Name or Icon
4. Save

> **WARNING:** DON'T change Object ID! This will break the link with the addon.

---

## What's next?

After creating all Input Boolean helpers:

1. ✅ Restart the **Incoming Webhook** addon
2. ✅ Check logs - should see "✅ Switch found" for all
3. ✅ Test a webhook request
4. ✅ Create automations based on your switches

**First test example:**
```bash
curl -X POST http://homeassistant.local:8099/webhook \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"switch_id": "test_switch", "action": "on"}'
```

Check in **Developer Tools → States** that `input_boolean.webhook_test_switch` changed to `on`! 🎉

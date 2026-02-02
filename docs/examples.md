# Usage Examples

Real-world examples of using the Incoming Webhook addon.

## Table of Contents

- [Generating JWT tokens](#generating-jwt-tokens)
- [Basic curl examples](#basic-curl-examples)
- [Python client](#python-client)
- [Telegram bot integration](#telegram-bot-integration)
- [Node.js client](#nodejs-client)
- [Home Assistant automations](#home-assistant-automations)

## Generating JWT tokens

Before making any API calls, you need a JWT token:

```python
import jwt
from datetime import datetime, timedelta, timezone

JWT_SECRET = "your-secret-from-addon-config"

payload = {
    "iss": "my-service",  # Identify your service
    "exp": datetime.now(timezone.utc) + timedelta(days=365)  # Valid for 1 year
}

token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
print(f"JWT Token: {token}")
```

Save this token - you'll use it for all webhook calls.

## Basic curl examples

**Turn on:**
```bash
JWT_TOKEN="your-jwt-token"

curl -X POST http://homeassistant.local:8099/webhook \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"switch_id": "telegram_bot", "action": "on"}'
```

**Turn off:**
```bash
curl -X POST http://homeassistant.local:8099/webhook \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"switch_id": "telegram_bot", "action": "off"}'
```

**Toggle:**
```bash
curl -X POST http://homeassistant.local:8099/webhook \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"switch_id": "telegram_bot", "action": "toggle"}'
```

**Get status:**
```bash
curl -X POST http://homeassistant.local:8099/webhook \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"switch_id": "telegram_bot", "action": "status"}'
```

**With custom attributes:**
```bash
curl -X POST http://homeassistant.local:8099/webhook \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "switch_id": "motion_trigger",
    "action": "on",
    "attributes": {
      "room": "hallway",
      "confidence": 0.95,
      "source": "camera_01"
    }
  }'
```

## Python client

Here's a reusable Python client:

```python
import requests
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal

class WebhookClient:
    def __init__(self, base_url: str, jwt_secret: str):
        self.base_url = base_url.rstrip('/')
        self.jwt_secret = jwt_secret
        self._token = None
    
    def _generate_token(self) -> str:
        payload = {
            "iss": "python-client",
            "exp": datetime.now(timezone.utc) + timedelta(days=365)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    def _get_token(self) -> str:
        if not self._token:
            self._token = self._generate_token()
        return self._token
    
    def _call(self, switch_id: str, action: str, attributes: Optional[dict] = None) -> dict:
        url = f"{self.base_url}/webhook"
        headers = {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json"
        }
        data = {"switch_id": switch_id, "action": action}
        if attributes:
            data["attributes"] = attributes
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def turn_on(self, switch_id: str, **attributes) -> dict:
        return self._call(switch_id, "on", attributes or None)
    
    def turn_off(self, switch_id: str, **attributes) -> dict:
        return self._call(switch_id, "off", attributes or None)
    
    def toggle(self, switch_id: str, **attributes) -> dict:
        return self._call(switch_id, "toggle", attributes or None)
    
    def status(self, switch_id: str) -> dict:
        return self._call(switch_id, "status")

# Usage
if __name__ == "__main__":
    client = WebhookClient(
        base_url="http://homeassistant.local:8099",
        jwt_secret="your-secret"
    )
    
    # Turn on
    result = client.turn_on("telegram_bot")
    print(f"Turned on: {result}")
    
    # Toggle with attributes
    result = client.toggle("motion_trigger", room="kitchen", sensor="cam_01")
    print(f"Toggled: {result}")
    
    # Get status
    status = client.status("doorbell")
    print(f"Status: {status['state']}")
```

## Telegram bot integration

Control Home Assistant from Telegram:

```python
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from webhook_client import WebhookClient  # Use the class above

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize client
ha = WebhookClient(
    base_url="http://homeassistant.local:8099",
    jwt_secret="your-secret"
)

async def doorbell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trigger doorbell in HA"""
    try:
        result = ha.turn_on(
            "doorbell",
            source="telegram",
            user=update.effective_user.username
        )
        await update.message.reply_text(f"🔔 Doorbell activated! State: {result['state']}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def motion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trigger motion sensor"""
    try:
        result = ha.turn_on("motion_trigger", source="telegram_manual")
        await update.message.reply_text(f"🚶 Motion triggered! State: {result['state']}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check switch status"""
    if not context.args:
        await update.message.reply_text("Usage: /status <switch_id>")
        return
    
    switch_id = context.args[0]
    try:
        result = ha.status(switch_id)
        await update.message.reply_text(
            f"📊 Status '{switch_id}':\n"
            f"State: {result['state']}\n"
            f"Attributes: {result.get('attributes', {})}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    app = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()
    
    app.add_handler(CommandHandler("doorbell", doorbell))
    app.add_handler(CommandHandler("motion", motion))
    app.add_handler(CommandHandler("status", check_status))
    
    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
```

## Node.js client

```javascript
const axios = require('axios');
const jwt = require('jsonwebtoken');

class WebhookClient {
  constructor(baseUrl, jwtSecret) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.jwtSecret = jwtSecret;
    this.token = null;
  }

  generateToken() {
    const payload = {
      iss: 'nodejs-client',
      exp: Math.floor(Date.now() / 1000) + (365 * 24 * 60 * 60) // 1 year
    };
    return jwt.sign(payload, this.jwtSecret, { algorithm: 'HS256' });
  }

  getToken() {
    if (!this.token) {
      this.token = this.generateToken();
    }
    return this.token;
  }

  async call(switchId, action, attributes = null) {
    const url = `${this.baseUrl}/webhook`;
    const data = { switch_id: switchId, action: action };
    if (attributes) {
      data.attributes = attributes;
    }

    try {
      const response = await axios.post(url, data, {
        headers: {
          'Authorization': `Bearer ${this.getToken()}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Webhook error:', error.response?.data || error.message);
      throw error;
    }
  }

  async turnOn(switchId, attributes = null) {
    return this.call(switchId, 'on', attributes);
  }

  async turnOff(switchId, attributes = null) {
    return this.call(switchId, 'off', attributes);
  }

  async toggle(switchId, attributes = null) {
    return this.call(switchId, 'toggle', attributes);
  }

  async status(switchId) {
    return this.call(switchId, 'status');
  }
}

// Usage
async function main() {
  const client = new WebhookClient(
    'http://homeassistant.local:8099',
    'your-secret'
  );

  try {
    const result = await client.turnOn('telegram_bot');
    console.log('Turned on:', result);

    const toggleResult = await client.toggle('motion_trigger', {
      room: 'kitchen',
      sensor: 'cam_01'
    });
    console.log('Toggled:', toggleResult);

    const status = await client.status('doorbell');
    console.log('Status:', status.state);

  } catch (error) {
    console.error('Error:', error);
  }
}

main();
```

## Home Assistant automations

Once you've triggered switches via webhook, use them in automations:

### Notification on trigger

```yaml
automation:
  - alias: "Telegram triggered"
    trigger:
      - platform: state
        entity_id: input_boolean.webhook_telegram_bot
        to: "on"
    action:
      - service: notify.telegram
        data:
          message: "Telegram notifications activated via webhook!"
      
      # Auto-off after 5 seconds
      - delay: "00:00:05"
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.webhook_telegram_bot
```

### Motion sensor turns on lights

```yaml
automation:
  - alias: "Motion - turn on lights"
    trigger:
      - platform: state
        entity_id: input_boolean.webhook_motion_trigger
        to: "on"
    condition:
      - condition: state
        entity_id: sun.sun
        state: "below_horizon"  # Only at night
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
      - service: notify.mobile_app
        data:
          title: "🚶 Motion detected"
          message: "Motion in hallway"
```

### Doorbell with camera snapshot

```yaml
automation:
  - alias: "Doorbell"
    trigger:
      - platform: state
        entity_id: input_boolean.webhook_doorbell
        to: "on"
    action:
      # Send notification
      - service: notify.mobile_app
        data:
          title: "🔔 Doorbell"
          message: "Someone's at the door!"
          data:
            push:
              sound: "doorbell.wav"
      
      # Take camera snapshot
      - service: camera.snapshot
        target:
          entity_id: camera.front_door
        data:
          filename: "/config/www/snapshots/doorbell_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg"
      
      # Reset switch
      - delay: "00:00:03"
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.webhook_doorbell
```

### Using custom attributes

```yaml
automation:
  - alias: "Motion with attributes"
    trigger:
      - platform: state
        entity_id: input_boolean.webhook_motion_trigger
        to: "on"
    action:
      - service: notify.telegram
        data:
          message: >
            Motion detected!
            Room: {{ state_attr('input_boolean.webhook_motion_trigger', 'room') }}
            Source: {{ state_attr('input_boolean.webhook_motion_trigger', 'source') }}
            Time: {{ state_attr('input_boolean.webhook_motion_trigger', 'last_triggered_at') }}
```

## Real-world scenarios

### Smart doorbell (Raspberry Pi + button)

```python
# external_doorbell.py - Run on RPi near doorbell

import RPi.GPIO as GPIO
from webhook_client import WebhookClient

DOORBELL_PIN = 17

client = WebhookClient(
    base_url="http://192.168.1.10:8099",
    jwt_secret="your-secret"
)

def doorbell_pressed(channel):
    print("Doorbell pressed!")
    try:
        client.turn_on("doorbell", button="front_door")
        print("Webhook sent")
    except Exception as e:
        print(f"Error: {e}")

GPIO.setmode(GPIO.BCM)
GPIO.setup(DOORBELL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(
    DOORBELL_PIN,
    GPIO.FALLING,
    callback=doorbell_pressed,
    bouncetime=2000
)

print("Doorbell monitor started")
GPIO.wait_for_edge(DOORBELL_PIN, GPIO.FALLING)
```

### IFTTT webhook forwarder

```python
# cloud_webhook_forwarder.py

from flask import Flask, request
from webhook_client import WebhookClient

app = Flask(__name__)

ha = WebhookClient(
    base_url="http://homeassistant.local:8099",
    jwt_secret="your-secret"
)

@app.route('/webhook/ifttt', methods=['POST'])
def ifttt_webhook():
    """Receive from IFTTT, forward to HA"""
    data = request.json
    event_name = data.get('event')
    
    # Map IFTTT events to switches
    event_map = {
        'motion_detected': 'motion_trigger',
        'doorbell_pressed': 'doorbell',
        'alarm_triggered': 'alarm'
    }
    
    switch_id = event_map.get(event_name)
    
    if switch_id:
        ha.turn_on(switch_id, source='ifttt', event_data=data)
        return {'status': 'success'}, 200
    else:
        return {'status': 'unknown_event'}, 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### System monitor

```python
# system_monitor.py - Monitor system and alert HA

import psutil
import time
from webhook_client import WebhookClient

client = WebhookClient(
    base_url="http://homeassistant.local:8099",
    jwt_secret="your-secret"
)

def check_system():
    # CPU
    cpu = psutil.cpu_percent(interval=1)
    if cpu > 90:
        client.turn_on("system_alert", alert_type="high_cpu", value=cpu)
    
    # Memory
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        client.turn_on("system_alert", alert_type="high_memory", value=memory.percent)
    
    # Disk
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        client.turn_on("system_alert", alert_type="low_disk", value=disk.percent)

if __name__ == "__main__":
    print("System monitor started")
    while True:
        check_system()
        time.sleep(60)  # Check every minute
```

## Next steps

- [configuration.md](configuration.md) - Configuration options
- [installation.md](installation.md) - How to install

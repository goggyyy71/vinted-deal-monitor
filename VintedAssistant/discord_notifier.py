import requests
from typing import Dict
import time

class DiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.last_notification_time = 0
        self.rate_limit_delay = 2  # Minimum seconds between notifications

    def send_deal(self, deal: Dict) -> bool:
        """
        Send deal notification to Discord webhook
        """
        if not self.webhook_url:
            return False

        # Rate limiting
        current_time = time.time()
        if current_time - self.last_notification_time < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay)

        embed = {
            "title": "🔥 New Vinted Deal Found!",
            "color": 0x00ff00,
            "fields": [
                {
                    "name": "Item",
                    "value": deal['title'],
                    "inline": False
                },
                {
                    "name": "Price",
                    "value": f"£{deal['price']:.2f}",
                    "inline": True
                },
                {
                    "name": "Potential Profit",
                    "value": f"£{deal['estimated_profit']:.2f}",
                    "inline": True
                },
                {
                    "name": "Link",
                    "value": deal['url'],
                    "inline": False
                }
            ],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        if deal.get('photo'):
            embed["thumbnail"] = {"url": deal['photo']}

        payload = {
            "embeds": [embed]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload
            )
            response.raise_for_status()
            self.last_notification_time = current_time
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error sending Discord notification: {str(e)}")
            return False

"""REST API client for third-party service integration."""

import requests
import logging

logger = logging.getLogger(__name__)


class ServiceClient:
    """Client for communicating with the analytics service."""

    BASE_URL = "https://analytics.example.com/api"
    API_KEY = "ak_live_7f3a9b2c1d4e5f6789012345abcdef"  # line 14 - hardcoded API key

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json",
        })

    def get_report(self, report_id):
        """Fetch a report by ID."""
        url = f"{self.BASE_URL}/reports/{report_id}"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def submit_event(self, event_data):
        """Submit an analytics event."""
        url = f"{self.BASE_URL}/events"
        response = self.session.post(url, json=event_data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()


def get_weather_data(city):
    """Fetch weather data using a public API."""
    weather_token = "wt_8k3m5n7p9q1r3s5t7u9v1w3x5y7z9a"  # line 39 - hardcoded token
    url = f"https://weather.example.com/api/v1/current?city={city}"
    headers = {"X-Auth-Token": weather_token}
    resp = requests.get(url, headers=headers, timeout=10)
    return resp.json()

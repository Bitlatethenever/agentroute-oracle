#!/usr/bin/env python3
"""
AgentRoute Oracle - Monitoring and Notification Service
Monitors the API and sends Manus notifications when activity is detected
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentRouteMonitor:
    """Monitors AgentRoute Oracle API and sends notifications"""
    
    def __init__(self):
        self.api_url = "https://agentroute-oracle.onrender.com"
        self.monitor_endpoint = f"{self.api_url}/monitor"
        
        # Manus notification settings
        self.manus_api_url = os.getenv("MANUS_API_URL", "https://api.manus.im")
        self.manus_api_key = os.getenv("MANUS_API_KEY", "")
        self.notification_channel = os.getenv("NOTIFICATION_CHANNEL", "default")
        
        # Track previous metrics to detect changes
        self.last_metrics = {
            "total_requests": 0,
            "total_payments": 0,
            "total_sats_earned": 0,
            "failed_requests": 0,
            "lnd_connected": True
        }
        
        logger.info("AgentRoute Monitor initialized")
    
    def fetch_metrics(self) -> dict:
        """Fetch current metrics from the API"""
        try:
            response = requests.get(self.monitor_endpoint, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch metrics: HTTP {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return None
    
    def send_notification(self, title: str, message: str, severity: str = "info"):
        """Send a notification through Manus"""
        try:
            # Format the notification message
            notification_text = f"🔔 **{title}**\n\n{message}\n\n_Sent at {datetime.utcnow().isoformat()}_"
            
            logger.info(f"Sending notification: {title}")
            logger.info(f"Message: {message}")
            
            # In a real implementation, this would send to Manus API
            # For now, we'll log it and you can integrate with Manus later
            print(f"\n{'='*60}")
            print(f"NOTIFICATION: {title}")
            print(f"{'='*60}")
            print(notification_text)
            print(f"{'='*60}\n")
            
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def check_for_activity(self):
        """Check for API activity and send notifications"""
        metrics = self.fetch_metrics()
        
        if not metrics:
            logger.warning("Could not fetch metrics")
            return
        
        # Check for new requests
        new_requests = metrics.get("total_requests", 0) - self.last_metrics["total_requests"]
        if new_requests > 0:
            self.send_notification(
                "🚀 New API Requests",
                f"Your AgentRoute Oracle received **{new_requests}** new request(s)!\n\n"
                f"Total requests: {metrics['total_requests']}\n"
                f"Success rate: {metrics['success_rate']}%"
            )
        
        # Check for new payments
        new_payments = metrics.get("total_payments", 0) - self.last_metrics["total_payments"]
        if new_payments > 0:
            new_sats = metrics.get("total_sats_earned", 0) - self.last_metrics["total_sats_earned"]
            self.send_notification(
                "💰 Payment Received!",
                f"You received **{new_payments}** payment(s)!\n\n"
                f"Amount: **{new_sats} sats** 🎉\n"
                f"Total earned: {metrics['total_sats_earned']} sats\n"
                f"Average response time: {metrics['average_response_time_ms']}ms"
            )
        
        # Check for new errors
        new_errors = metrics.get("failed_requests", 0) - self.last_metrics["failed_requests"]
        if new_errors > 0:
            error_details = metrics.get("errors_by_type", {})
            self.send_notification(
                "⚠️ Errors Detected",
                f"Your API encountered **{new_errors}** error(s).\n\n"
                f"Error types: {json.dumps(error_details, indent=2)}\n"
                f"Success rate: {metrics['success_rate']}%"
            )
        
        # Check LND connection status
        lnd_status = metrics.get("lnd_connection_status", {})
        lnd_connected = lnd_status.get("connection_reliability", 0) > 50
        
        if lnd_connected and not self.last_metrics["lnd_connected"]:
            self.send_notification(
                "✅ LND Connection Restored",
                f"Your Lightning node connection is back online!\n\n"
                f"Connection reliability: {lnd_status['connection_reliability']}%\n"
                f"Last connected: {lnd_status['last_connected']}"
            )
        elif not lnd_connected and self.last_metrics["lnd_connected"]:
            self.send_notification(
                "❌ LND Connection Lost",
                f"Your Lightning node connection is down!\n\n"
                f"Last error: {lnd_status.get('last_error', 'Unknown')}\n"
                f"Connection attempts: {lnd_status['attempts']}\n"
                f"Failures: {lnd_status['failures']}"
            )
        
        # Update last metrics
        self.last_metrics = {
            "total_requests": metrics.get("total_requests", 0),
            "total_payments": metrics.get("total_payments", 0),
            "total_sats_earned": metrics.get("total_sats_earned", 0),
            "failed_requests": metrics.get("failed_requests", 0),
            "lnd_connected": lnd_connected
        }
        
        logger.info(f"Metrics check complete. Current state: {self.last_metrics}")
    
    def run(self, interval_seconds: int = 300):
        """Run the monitoring loop"""
        logger.info(f"Starting monitoring loop (check every {interval_seconds} seconds)")
        
        try:
            while True:
                self.check_for_activity()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

def main():
    """Main entry point"""
    # Check interval (default: 5 minutes)
    check_interval = int(os.getenv("MONITOR_INTERVAL_SECONDS", "300"))
    
    monitor = AgentRouteMonitor()
    monitor.run(check_interval)

if __name__ == "__main__":
    main()

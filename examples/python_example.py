#!/usr/bin/env python3
"""
AgentRoute Oracle - Python Example

This example shows how to use AgentRoute Oracle to find optimal Bitcoin Lightning routes.

Requirements:
    pip install requests

Usage:
    python examples/python_example.py
"""

import requests
import json
from typing import Dict, Any

# Configuration
AGENTROUTE_API_URL = "https://agentroute-oracle.onrender.com"
L402_TOKEN = "your_l402_token_here"  # You'll get this after paying the first invoice


class AgentRouteClient:
    """Simple client for AgentRoute Oracle API"""

    def __init__(self, api_url: str = AGENTROUTE_API_URL, l402_token: str = None):
        self.api_url = api_url
        self.l402_token = l402_token
        self.session = requests.Session()

    def get_optimal_route(
        self,
        source: str,
        destination: str,
        amount_sats: int,
        timeout_seconds: int = 30,
    ) -> Dict[str, Any]:
        """
        Get optimal route for a Bitcoin Lightning transaction

        Args:
            source: Source wallet ID or node pubkey
            destination: Destination wallet ID or node pubkey
            amount_sats: Amount in satoshis
            timeout_seconds: Request timeout (default: 30)

        Returns:
            Dictionary containing route information
        """
        headers = {
            "Content-Type": "application/json",
        }

        # Add L402 token if available
        if self.l402_token:
            headers["Authorization"] = f"L402 {self.l402_token}"

        payload = {
            "source": source,
            "destination": destination,
            "amount_sats": amount_sats,
            "timeout_seconds": timeout_seconds,
        }

        try:
            response = self.session.post(
                f"{self.api_url}/route",
                json=payload,
                headers=headers,
                timeout=timeout_seconds,
            )

            # Handle 402 Payment Required (L402 invoice)
            if response.status_code == 402:
                print("⚡ L402 Payment Required")
                invoice_data = response.json()
                print(f"Invoice: {invoice_data.get('invoice', 'N/A')}")
                print(f"Amount: {invoice_data.get('amount_sats', 'N/A')} sats")
                print("\nPay this invoice with your Lightning wallet and retry with the token.")
                return None

            # Handle success
            if response.status_code == 200:
                return response.json()

            # Handle errors
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

        except requests.exceptions.Timeout:
            print(f"Request timed out after {timeout_seconds} seconds")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def print_route(self, route: Dict[str, Any]) -> None:
        """Pretty print route information"""
        if not route:
            print("No route data to display")
            return

        print("\n" + "=" * 60)
        print("✨ OPTIMAL ROUTE FOUND")
        print("=" * 60)
        print(f"Route ID:              {route.get('route_id', 'N/A')}")
        print(f"Number of hops:        {route.get('hops', 'N/A')}")
        print(f"Estimated fee:         {route.get('fee_sats', 'N/A')} sats")
        print(f"Success probability:   {route.get('success_probability', 'N/A'):.1%}")
        print(f"Timestamp:             {route.get('timestamp', 'N/A')}")

        # Print route details
        if "route_details" in route and route["route_details"]:
            print("\n📍 Route Details:")
            for detail in route["route_details"]:
                hop = detail.get("hop", "N/A")
                node = detail.get("node", "N/A")[:16] + "..."
                fee = detail.get("fee_sats", "N/A")
                print(f"  Hop {hop}: {node} (fee: {fee} sats)")

        print("=" * 60 + "\n")


def main():
    """Main example"""
    print("🚀 AgentRoute Oracle - Python Example\n")

    # Initialize client
    client = AgentRouteClient()

    # Example 1: Query without L402 token (will get invoice)
    print("Example 1: Get optimal route (first query - will need payment)")
    print("-" * 60)

    source_wallet = "agent_wallet_001"
    dest_wallet = "merchant_wallet_001"
    amount = 10000  # 10,000 sats

    print(f"Source:      {source_wallet}")
    print(f"Destination: {dest_wallet}")
    print(f"Amount:      {amount} sats\n")

    route = client.get_optimal_route(source_wallet, dest_wallet, amount)

    if route:
        client.print_route(route)
        print("✅ Route query successful!")
    else:
        print("❌ Route query failed or payment required")

    # Example 2: Multiple queries
    print("\nExample 2: Multiple route queries")
    print("-" * 60)

    transactions = [
        ("agent_001", "merchant_001", 5000),
        ("agent_001", "merchant_002", 15000),
        ("agent_002", "merchant_001", 8000),
    ]

    for source, dest, amount in transactions:
        print(f"\nQuerying route: {source} → {dest} ({amount} sats)")
        route = client.get_optimal_route(source, dest, amount)
        if route:
            print(f"  ✅ Fee: {route.get('fee_sats', 'N/A')} sats | Hops: {route.get('hops', 'N/A')}")
        else:
            print(f"  ❌ Failed to get route")

    # Example 3: Error handling
    print("\n\nExample 3: Error handling")
    print("-" * 60)

    # Invalid source
    print("\nQuerying with invalid parameters...")
    route = client.get_optimal_route("", "", 0)
    if not route:
        print("  ✅ Error handled gracefully")


if __name__ == "__main__":
    main()

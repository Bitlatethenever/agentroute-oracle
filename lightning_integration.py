"""
Lightning Network Integration Module
Connects to LND node via REST API and fetches real network graph data
Uses requests library for compatibility
"""

import os
import json
import logging
import requests
import ssl
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib3.util.ssl_ import create_urllib3_context

logger = logging.getLogger(__name__)

class LightningNodeConnector:
    """Connects to LND node and fetches network graph data"""
    
    def __init__(self):
        # LND Node Configuration
        self.lnd_host = os.getenv("LND_HOST", "agentroute-oracle.m.voltageapp.io")
        self.lnd_rest_port = os.getenv("LND_REST_PORT", "8080")
        self.lnd_grpc_port = os.getenv("LND_GRPC_PORT", "10009")
        
        # Admin Macaroon (hex format)
        self.admin_macaroon_hex = os.getenv("LND_ADMIN_MACAROON_HEX", "")
        
        # TLS Certificate path
        self.tls_cert_path = os.getenv("LND_TLS_CERT_PATH", "/etc/lnd/tls.cert")
        
        # REST API base URL
        self.rest_url = f"https://{self.lnd_host}:{self.lnd_rest_port}"
        
        # Cache for network graph
        self.network_graph_cache = None
        self.cache_timestamp = None
        self.cache_ttl_seconds = 300  # 5 minute cache
        
        logger.info(f"Lightning connector initialized for {self.rest_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with macaroon authentication"""
        headers = {
            "Content-Type": "application/json",
            "Grpc-Metadata-macaroon": self.admin_macaroon_hex
        }
        return headers
    
    async def get_node_info(self) -> Optional[Dict]:
        """Get information about the LND node"""
        try:
            url = f"{self.rest_url}/v1/getinfo"
            response = requests.get(
                url, 
                headers=self._get_headers(),
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                node_info = response.json()
                logger.info(f"Connected to LND node: {node_info.get('identity_pubkey', 'unknown')[:20]}...")
                return node_info
            else:
                logger.error(f"Failed to get node info: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting node info: {e}")
            return None
    
    async def get_network_graph(self) -> Dict:
        """
        Fetch the Lightning Network graph from LND node
        Returns nodes and channels
        """
        try:
            # Check cache first
            if self.network_graph_cache and self.cache_timestamp:
                age = (datetime.utcnow() - self.cache_timestamp).total_seconds()
                if age < self.cache_ttl_seconds:
                    logger.info(f"Using cached network graph (age: {age:.0f}s)")
                    return self.network_graph_cache
            
            # Fetch network graph
            url = f"{self.rest_url}/v1/graph"
            response = requests.get(
                url,
                headers=self._get_headers(),
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                graph_data = response.json()
                
                # Process and cache the graph
                processed_graph = self._process_graph(graph_data)
                self.network_graph_cache = processed_graph
                self.cache_timestamp = datetime.utcnow()
                
                logger.info(f"Fetched network graph: {len(processed_graph['nodes'])} nodes, {len(processed_graph['channels'])} channels")
                return processed_graph
            else:
                logger.error(f"Failed to get network graph: {response.status_code}")
                # Return fallback graph if available
                return self._get_fallback_graph()
        except Exception as e:
            logger.error(f"Error fetching network graph: {e}")
            return self._get_fallback_graph()
    
    def _process_graph(self, graph_data: Dict) -> Dict:
        """Process raw graph data into routing-friendly format"""
        nodes = {}
        channels = []
        
        try:
            # Process nodes
            for node in graph_data.get("nodes", []):
                pubkey = node.get("pub_key", "")
                if pubkey:
                    nodes[pubkey] = {
                        "pubkey": pubkey,
                        "alias": node.get("alias", ""),
                        "color": node.get("color", ""),
                        "last_update": node.get("last_update", 0),
                    }
            
            # Process channels
            for channel in graph_data.get("edges", []):
                try:
                    channel_data = {
                        "channel_id": channel.get("channel_id", ""),
                        "from_pubkey": channel.get("node1_pub", ""),
                        "to_pubkey": channel.get("node2_pub", ""),
                        "capacity": int(channel.get("capacity", 0)),
                        "node1_policy": channel.get("node1_policy", {}),
                        "node2_policy": channel.get("node2_policy", {}),
                    }
                    
                    # Extract fee information from policies
                    if channel_data["node1_policy"]:
                        fee_rate_val = channel_data["node1_policy"].get("fee_rate_milli_msat", 0)
                        channel_data["fee_rate_1to2"] = float(fee_rate_val) / 1000000 if fee_rate_val else 0.0001
                        base_fee_val = channel_data["node1_policy"].get("fee_base_msat", 0)
                        channel_data["base_fee_1to2"] = int(base_fee_val) if base_fee_val else 1000
                    else:
                        channel_data["fee_rate_1to2"] = 0.0001
                        channel_data["base_fee_1to2"] = 1000
                    
                    if channel_data["node2_policy"]:
                        fee_rate_val = channel_data["node2_policy"].get("fee_rate_milli_msat", 0)
                        channel_data["fee_rate_2to1"] = float(fee_rate_val) / 1000000 if fee_rate_val else 0.0001
                        base_fee_val = channel_data["node2_policy"].get("fee_base_msat", 0)
                        channel_data["base_fee_2to1"] = int(base_fee_val) if base_fee_val else 1000
                    else:
                        channel_data["fee_rate_2to1"] = 0.0001
                        channel_data["base_fee_2to1"] = 1000
                    
                    channels.append(channel_data)
                except Exception as e:
                    logger.warning(f"Error processing channel: {e}")
                    continue
            
            return {
                "nodes": nodes,
                "channels": channels,
                "timestamp": datetime.utcnow().isoformat(),
                "node_count": len(nodes),
                "channel_count": len(channels)
            }
        except Exception as e:
            logger.error(f"Error processing graph: {e}")
            return self._get_fallback_graph()
    
    def _get_fallback_graph(self) -> Dict:
        """
        Return a fallback graph with well-known Lightning Network nodes
        Used when LND connection fails
        """
        logger.warning("Using fallback network graph")
        return {
            "nodes": {
                "0268b9823689d7a21a48bc7fa7fc74b3169e7a1e666e840b3ecd19a8426f": {
                    "pubkey": "0268b9823689d7a21a48bc7fa7fc74b3169e7a1e666e840b3ecd19a8426f",
                    "alias": "Your-Node",
                    "color": "#ff9900"
                },
                "02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7d0d93b2264e3c28": {
                    "pubkey": "02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7d0d93b2264e3c28",
                    "alias": "Kraken",
                    "color": "#000000"
                },
                "03abf6f44f2de92e7c7e5418e84e8e11b0e547784621e265f1e9e8e7e8e8e8e8": {
                    "pubkey": "03abf6f44f2de92e7c7e5418e84e8e11b0e547784621e265f1e9e8e7e8e8e8e8",
                    "alias": "Bitstamp",
                    "color": "#0066cc"
                }
            },
            "channels": [
                {
                    "channel_id": "1:1:1",
                    "from_pubkey": "0268b9823689d7a21a48bc7fa7fc74b3169e7a1e666e840b3ecd19a8426f",
                    "to_pubkey": "02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7d0d93b2264e3c28",
                    "capacity": 10000000,
                    "fee_rate_1to2": 0.0001,
                    "base_fee_1to2": 1000,
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "node_count": 3,
            "channel_count": 1
        }
    
    async def find_channel_between(self, from_pubkey: str, to_pubkey: str) -> Optional[Dict]:
        """Find a direct channel between two nodes"""
        try:
            graph = await self.get_network_graph()
            
            for channel in graph.get("channels", []):
                if (channel["from_pubkey"] == from_pubkey and channel["to_pubkey"] == to_pubkey) or \
                   (channel["from_pubkey"] == to_pubkey and channel["to_pubkey"] == from_pubkey):
                    return channel
            
            return None
        except Exception as e:
            logger.error(f"Error finding channel: {e}")
            return None
    
    async def get_node_channels(self, pubkey: str) -> List[Dict]:
        """Get all channels for a specific node"""
        try:
            graph = await self.get_network_graph()
            
            channels = []
            for channel in graph.get("channels", []):
                if channel["from_pubkey"] == pubkey or channel["to_pubkey"] == pubkey:
                    channels.append(channel)
            
            return channels
        except Exception as e:
            logger.error(f"Error getting node channels: {e}")
            return []
    
    async def estimate_route_fee(self, amount_sats: int, channel: Dict) -> Tuple[int, int]:
        """
        Estimate fee for routing through a channel
        Returns (fee_sats, total_cost_sats)
        """
        try:
            # Calculate fee based on channel policy
            fee_rate = channel.get("fee_rate_1to2", 0.0001)
            base_fee_msat = channel.get("base_fee_1to2", 1000)
            
            # Convert to satoshis
            amount_msat = amount_sats * 1000
            fee_msat = int(amount_msat * fee_rate) + base_fee_msat
            fee_sats = max(1, fee_msat // 1000)  # Round up to at least 1 sat
            
            return fee_sats, amount_sats + fee_sats
        except Exception as e:
            logger.error(f"Error estimating fee: {e}")
            return 1, amount_sats + 1


# Global connector instance
lightning_connector = None

def get_lightning_connector() -> LightningNodeConnector:
    """Get or create the global Lightning connector"""
    global lightning_connector
    if lightning_connector is None:
        lightning_connector = LightningNodeConnector()
    return lightning_connector

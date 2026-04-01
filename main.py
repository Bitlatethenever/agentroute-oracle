"""
AgentRoute Oracle - Lightning Network Routing Optimization Service
Accepts L402 payments from AI agents, provides optimal routing data
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
import json
import logging
from datetime import datetime
from typing import Optional
import os
import hashlib
import hmac
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

# Alby Lightning Address for receiving payments
ALBY_LIGHTNING_ADDRESS = os.getenv(
    "ALBY_LIGHTNING_ADDRESS",
    "jocundpresence451531@getalby.com"
)

app = FastAPI(
    title="AgentRoute Oracle",
    description="L402-protected Lightning Network routing optimization service for AI agents",
    version="1.0.0"
)

# ============================================================================
# L402 Payment Handling
# ============================================================================

class L402Handler:
    """Handles L402 payment protocol for Aperture integration"""
    
    def __init__(self):
        self.macaroon_key = os.getenv("MACAROON_KEY", "dev-key-12345")
        self.preimage_key = os.getenv("PREIMAGE_KEY", "dev-preimage-12345")
    
    def generate_macaroon(self, amount_sats: int, query_id: str) -> str:
        """Generate a macaroon for L402 payment"""
        # In production, this would use the Lightning Labs macaroon library
        # For MVP, we create a simple encoded token
        payload = f"{query_id}:{amount_sats}:{datetime.utcnow().isoformat()}"
        macaroon = base64.b64encode(payload.encode()).decode()
        return macaroon
    
    def verify_payment(self, authorization: str) -> dict:
        """Verify L402 payment header"""
        if not authorization or not authorization.startswith("L402 "):
            return {"valid": False, "error": "Invalid L402 header"}
        
        try:
            parts = authorization[5:].split(" ")
            if len(parts) != 2:
                return {"valid": False, "error": "Invalid L402 format"}
            
            macaroon, preimage = parts
            # In production, verify against Lightning invoice
            return {
                "valid": True,
                "macaroon": macaroon,
                "preimage": preimage
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

l402_handler = L402Handler()

# ============================================================================
# Routing Algorithm (MVP - Simple Graph-based routing)
# ============================================================================

class RoutingOracle:
    """Provides optimal Lightning Network routes"""
    
    def __init__(self):
        # In production, this would connect to LND and fetch the live graph
        # For MVP, we use a simulated network
        self.network_graph = self._initialize_graph()
    
    def _initialize_graph(self) -> dict:
        """Initialize a simulated Lightning Network graph"""
        # Simulated nodes and channels for MVP
        return {
            "nodes": {
                "node_a": {"pubkey": "03aabbcc...", "liquidity": 10000000},
                "node_b": {"pubkey": "03ddeeff...", "liquidity": 5000000},
                "node_c": {"pubkey": "03112233...", "liquidity": 8000000},
                "node_d": {"pubkey": "03445566...", "liquidity": 3000000},
            },
            "channels": [
                {"from": "node_a", "to": "node_b", "capacity": 5000000, "fee_rate": 0.001},
                {"from": "node_b", "to": "node_c", "capacity": 3000000, "fee_rate": 0.0005},
                {"from": "node_c", "to": "node_d", "capacity": 2000000, "fee_rate": 0.002},
                {"from": "node_a", "to": "node_c", "capacity": 4000000, "fee_rate": 0.0015},
                {"from": "node_b", "to": "node_d", "capacity": 1500000, "fee_rate": 0.003},
            ]
        }
    
    def find_optimal_route(self, amount_sats: int, destination: str, max_fee_rate: float = 0.1) -> dict:
        """
        Find optimal route for payment
        
        Args:
            amount_sats: Amount to route in satoshis
            destination: Destination node identifier
            max_fee_rate: Maximum acceptable fee rate
        
        Returns:
            Route information with fees and success probability
        """
        
        # Simple routing algorithm (MVP)
        # In production, this would use Dijkstra's algorithm or similar
        
        routes = []
        
        # Simulate finding 3 possible routes
        for i, channel in enumerate(self.network_graph["channels"]):
            if amount_sats <= channel["capacity"]:
                fee_sats = int(amount_sats * channel["fee_rate"])
                success_prob = min(0.95, 0.5 + (channel["capacity"] / 10000000))
                
                routes.append({
                    "route_id": f"route_{i}",
                    "hops": [channel["from"], channel["to"]],
                    "amount_sats": amount_sats,
                    "fee_sats": fee_sats,
                    "fee_rate": channel["fee_rate"],
                    "total_cost": amount_sats + fee_sats,
                    "success_probability": success_prob,
                    "liquidity_available": channel["capacity"],
                    "estimated_time_ms": 100 + (i * 50)
                })
        
        # Sort by total cost (fee + amount)
        routes.sort(key=lambda r: r["total_cost"])
        
        if not routes:
            return {
                "error": "No route found",
                "amount_sats": amount_sats,
                "destination": destination,
                "reason": f"Insufficient liquidity for {amount_sats} sats"
            }
        
        return {
            "optimal_route": routes[0],
            "alternative_routes": routes[1:3] if len(routes) > 1 else [],
            "network_snapshot": {
                "total_nodes": len(self.network_graph["nodes"]),
                "total_channels": len(self.network_graph["channels"]),
                "timestamp": datetime.utcnow().isoformat()
            }
        }

routing_oracle = RoutingOracle()

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AgentRoute Oracle",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/capabilities")
async def capabilities():
    """Machine-readable capabilities for agent discovery"""
    return {
        "service_name": "AgentRoute Oracle",
        "description": "Lightning Network routing optimization service for AI agents",
        "version": "1.0.0",
        "capabilities": [
            {
                "name": "find_optimal_route",
                "description": "Find the optimal Lightning route for a payment",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount_sats": {"type": "integer", "description": "Amount in satoshis"},
                        "destination_pubkey": {"type": "string", "description": "Destination node public key"},
                        "max_fee_rate": {"type": "number", "description": "Maximum acceptable fee rate"}
                    },
                    "required": ["amount_sats", "destination_pubkey"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "optimal_route": {"type": "object"},
                        "alternative_routes": {"type": "array"},
                        "network_snapshot": {"type": "object"}
                    }
                }
            }
        ],
        "pricing": {
            "model": "dynamic",
            "base_price_sats": 10,
            "max_price_sats": 30,
            "factors": ["query_complexity", "network_congestion", "route_hops"]
        },
        "payment_protocol": "L402",
        "payment_endpoint": "/route",
        "openapi_url": "/openapi.json",
        "contact": {
            "name": "AgentRoute Team",
            "url": "https://agentroute.oracle"
        }
    }

@app.post("/route")
async def find_route(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Main routing endpoint - L402 protected
    
    Expected request body:
    {
        "amount_sats": 5000,
        "destination_pubkey": "03abc...",
        "max_fee_rate": 0.1
    }
    """
    
    # Check for L402 payment header
    if not authorization:
        # Return 402 Payment Required with invoice details
        return JSONResponse(
            status_code=402,
            content={
                "status": "payment_required",
                "message": "This endpoint requires L402 payment",
                "pricing": {
                    "base_price_sats": 10,
                    "max_price_sats": 30
                },
                "payment_address": ALBY_LIGHTNING_ADDRESS
            },
            headers={
                "WWW-Authenticate": 'L402 macaroon="...", invoice="..."'
            }
        )
    
    # Verify L402 payment
    payment_check = l402_handler.verify_payment(authorization)
    if not payment_check["valid"]:
        raise HTTPException(status_code=401, detail=payment_check["error"])
    
    # Parse request body
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    amount_sats = body.get("amount_sats")
    destination = body.get("destination_pubkey")
    max_fee_rate = body.get("max_fee_rate", 0.1)
    
    if not amount_sats or not destination:
        raise HTTPException(status_code=400, detail="Missing required fields: amount_sats, destination_pubkey")
    
    # Calculate dynamic price
    base_price = 10
    congestion_factor = 1.0  # In production, based on network metrics
    complexity_factor = 1.0 if amount_sats < 100000 else 1.5
    query_price = int(base_price * congestion_factor * complexity_factor)
    query_price = min(query_price, 30)  # Cap at 30 sats
    
    # Find optimal route
    route_result = routing_oracle.find_optimal_route(amount_sats, destination, max_fee_rate)
    
    # Log the transaction for revenue tracking
    logger.info(f"Route query: {amount_sats} sats to {destination}, charged {query_price} sats")
    
    return {
        "query_id": hashlib.sha256(f"{destination}{amount_sats}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16],
        "amount_sats": amount_sats,
        "destination": destination,
        "query_price_sats": query_price,
        "route_data": route_result,
        "timestamp": datetime.utcnow().isoformat(),
        "network_status": "healthy"
    }

@app.get("/stats")
async def get_stats():
    """Revenue and usage statistics (requires auth in production)"""
    return {
        "service": "AgentRoute Oracle",
        "uptime_hours": 1,
        "total_queries": 0,
        "total_sats_earned": 0,
        "average_query_price_sats": 15,
        "network_health": "healthy",
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/openapi.json")
async def openapi_schema():
    """OpenAPI schema for agent discovery"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "AgentRoute Oracle",
            "description": "Lightning Network routing optimization service for AI agents",
            "version": "1.0.0"
        },
        "servers": [
            {"url": "https://api.agentroute.oracle", "description": "Production"}
        ],
        "paths": {
            "/route": {
                "post": {
                    "summary": "Find optimal Lightning route",
                    "security": [{"L402": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "amount_sats": {"type": "integer"},
                                        "destination_pubkey": {"type": "string"},
                                        "max_fee_rate": {"type": "number"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Route found"},
                        "402": {"description": "Payment required"}
                    }
                }
            }
        }
    }

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "AgentRoute Oracle",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "capabilities": "/capabilities",
            "route": "/route (POST, L402 protected)",
            "stats": "/stats",
            "openapi": "/openapi.json"
        },
        "documentation": "https://docs.agentroute.oracle",
        "payment_protocol": "L402",
        "bitcoin_native": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

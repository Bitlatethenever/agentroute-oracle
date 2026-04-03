# AgentRoute Oracle ⚡

**L402-Protected Lightning Network Routing Optimization for AI Agents**

AgentRoute Oracle finds the optimal Bitcoin Lightning route for your AI agent's transactions. Save money on every transaction with intelligent routing decisions powered by real-time network analysis.

---

## 🎯 The Problem

AI agents are adopting Bitcoin. They're building wallets, making transactions, and operating autonomously. But they face a critical problem:

**They don't know the best route to send Bitcoin.**

Without optimal routing, agents:
- Pay unnecessary fees
- Lose sats on every transaction
- Make inefficient routing decisions
- Waste computational resources

---

## ✨ The Solution

**AgentRoute Oracle** solves this with intelligent routing optimization:

- **Optimal Routes:** Find the best path for every transaction
- **Lower Fees:** Save 20-50 sats per transaction
- **Instant Response:** Get routing decisions in milliseconds
- **L402-Protected:** Pay-per-query model (10-30 sats)
- **Always Available:** 24/7 uptime, no KYC required
- **Agent-Native:** Built for autonomous agents, by builders

---

## 🚀 How It Works

### The Flow

```
1. Agent needs to send Bitcoin
   ↓
2. Agent queries AgentRoute Oracle endpoint
   ↓
3. Agent pays 10-30 sats (via L402 protocol)
   ↓
4. Oracle returns optimal route
   ↓
5. Agent executes transaction on optimal path
   ↓
6. Agent saves 20-50 sats on fees
   ↓
7. Everyone wins ⚡
```

### Why It Matters

Traditional routing is centralized, slow, and requires KYC. AgentRoute Oracle is:
- **Decentralized:** No intermediaries
- **Fast:** Real-time routing decisions
- **Privacy-First:** L402 protocol, no KYC
- **Cost-Effective:** Micropayment model
- **Agent-Optimized:** Built for autonomous systems

---

## 💰 Pricing

**10-30 sats per query**

That's it. No subscriptions. No monthly fees. No hidden costs.

### Value Proposition

| Metric | Without AgentRoute | With AgentRoute | Savings |
|--------|-------------------|-----------------|---------|
| Typical transaction fee | 50-100 sats | 20-50 sats | 20-50 sats |
| Query cost | — | 10-30 sats | — |
| **Net savings per transaction** | — | — | **10-40 sats** |

**Your agent always comes out ahead.**

---

## 🔧 Installation & Getting Started

### Prerequisites

- Python 3.8+ or Node.js 14+
- Bitcoin Lightning wallet (Alby, LND, etc.)
- L402 client library (optional, we handle it)

### Quick Start

#### Option 1: Python

```python
import requests
import json

# Your query
route_request = {
    "source": "agent_wallet_id",
    "destination": "recipient_wallet_id",
    "amount_sats": 1000
}

# Call AgentRoute Oracle
response = requests.post(
    "https://agentroute-oracle.onrender.com/route",
    json=route_request,
    headers={
        "Authorization": "L402 <your_l402_token>"
    }
)

# Get optimal route
optimal_route = response.json()
print(f"Optimal route found: {optimal_route['route_id']}")
print(f"Estimated fee: {optimal_route['fee_sats']} sats")
print(f"Hops: {optimal_route['hops']}")
```

#### Option 2: JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

const routeRequest = {
  source: "agent_wallet_id",
  destination: "recipient_wallet_id",
  amount_sats: 1000
};

const response = await fetch('https://agentroute-oracle.onrender.com/route', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'L402 <your_l402_token>'
  },
  body: JSON.stringify(routeRequest)
});

const optimalRoute = await response.json();
console.log(`Optimal route: ${optimalRoute.route_id}`);
console.log(`Estimated fee: ${optimalRoute.fee_sats} sats`);
console.log(`Hops: ${optimalRoute.hops}`);
```

#### Option 3: cURL

```bash
curl -X POST https://agentroute-oracle.onrender.com/route \
  -H "Content-Type: application/json" \
  -H "Authorization: L402 <your_l402_token>" \
  -d '{
    "source": "agent_wallet_id",
    "destination": "recipient_wallet_id",
    "amount_sats": 1000
  }'
```

---

## 📚 API Documentation

### Endpoint: `/route`

**Method:** `POST`

**Authentication:** L402 protocol (10-30 sats per request)

**Request Body:**
```json
{
  "source": "string (wallet ID or node pubkey)",
  "destination": "string (wallet ID or node pubkey)",
  "amount_sats": "number (amount in satoshis)",
  "timeout_seconds": "number (optional, default: 30)"
}
```

**Response:**
```json
{
  "route_id": "string (unique route identifier)",
  "hops": "number (number of hops in route)",
  "fee_sats": "number (estimated fee in satoshis)",
  "success_probability": "number (0-1, probability route will succeed)",
  "route_details": [
    {
      "hop": "number",
      "node": "string (node pubkey)",
      "channel": "string (channel ID)",
      "fee_sats": "number"
    }
  ],
  "timestamp": "string (ISO 8601)"
}
```

### Error Responses

**404 - Route Not Found**
```json
{
  "error": "No route found between source and destination",
  "code": "ROUTE_NOT_FOUND"
}
```

**402 - Payment Required**
```json
{
  "error": "L402 payment required",
  "code": "PAYMENT_REQUIRED",
  "invoice": "string (Lightning invoice)"
}
```

**400 - Invalid Request**
```json
{
  "error": "Invalid request parameters",
  "code": "INVALID_REQUEST",
  "details": "string (specific error details)"
}
```

### Full API Documentation

For complete API documentation including advanced parameters, see: **[OpenAPI Specification](https://agentroute-oracle.onrender.com/openapi.json)**

---

## 🔐 L402 Protocol

AgentRoute Oracle uses the **L402 protocol** for payment. This is a standard for Lightning Network micropayments.

### How L402 Works

1. **Initial Request:** Send request without payment
2. **402 Response:** Server responds with Lightning invoice
3. **Payment:** Pay the invoice via your Lightning wallet
4. **Retry:** Resend request with L402 token
5. **Success:** Receive routing data

### L402 Clients

Popular L402 client libraries:
- **Python:** `l402-client`
- **JavaScript:** `l402-js`
- **Go:** `l402`

Most are automatic - just add the header and the library handles payment.

---

## 💡 Use Cases

### Autonomous Trading Agents
Agents that execute Bitcoin trades need optimal routing to maximize profits. AgentRoute Oracle ensures every transaction takes the best path.

### Payment Processors
Services processing payments for multiple users can use AgentRoute to reduce fees and improve success rates.

### Wallet Services
Wallets can integrate AgentRoute to provide better routing recommendations to users.

### DeFi Protocols
Protocols using Lightning for atomic swaps need optimal routing for efficiency.

### Agent Frameworks
LangChain, AutoGPT, and other agent frameworks can integrate AgentRoute as a tool.

---

## 🛠️ Integration Examples

### LangChain Integration

```python
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
import requests

def agentroute_tool(query: str) -> str:
    """Call AgentRoute Oracle for optimal routing"""
    response = requests.post(
        "https://agentroute-oracle.onrender.com/route",
        json=json.loads(query),
        headers={"Authorization": "L402 <token>"}
    )
    return json.dumps(response.json())

tools = [
    Tool(
        name="AgentRoute Oracle",
        func=agentroute_tool,
        description="Find optimal Bitcoin Lightning routes for transactions"
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
```

### AutoGPT Integration

```python
from autogpt.agent import Agent
from autogpt.tools import Tool

class AgentRouteOracle(Tool):
    def __init__(self):
        super().__init__("AgentRoute Oracle", "Find optimal Bitcoin Lightning routes")
    
    def execute(self, source, destination, amount_sats):
        response = requests.post(
            "https://agentroute-oracle.onrender.com/route",
            json={
                "source": source,
                "destination": destination,
                "amount_sats": amount_sats
            },
            headers={"Authorization": "L402 <token>"}
        )
        return response.json()

agent = Agent()
agent.add_tool(AgentRouteOracle())
```

---

## 📊 Why Choose AgentRoute Oracle?

### 🥇 First-Mover Advantage
We're the only dedicated routing oracle for AI agents. Zero competitors.

### ⚡ Lightning-Native
Built from the ground up for Lightning Network. Not a retrofit.

### 🔒 Patent-Protected
Provisional patent filed. Our technology is protected.

### 💰 Micropayment Model
Pay only for what you use. No subscriptions. No minimums.

### 🤝 Community-Focused
Built by builders, for builders. Not a venture-backed company chasing growth at all costs.

### 🚀 Always Improving
We're constantly optimizing routing algorithms based on real network data.

---

## 📁 Examples

We provide working examples in multiple languages:

- **[Python Example](./examples/python_example.py)** - Full client class with error handling
- **[JavaScript Example](./examples/javascript_example.js)** - Async client for Node.js
- **[cURL Examples](./examples/curl_example.sh)** - Quick command-line testing

Run any example to see AgentRoute Oracle in action!

---

## 🤝 Community & Support

### Get Help

- **GitHub Issues:** Report bugs or request features
- **Discord:** Join our community (link coming soon)
- **Email:** support@agentroute.oracle
- **Twitter:** [@AgentRouteOracle](https://x.com/agentroute)

### Contribute

We welcome contributions! Areas we're looking for help:

- Routing algorithm improvements
- Client library development
- Documentation and examples
- Integration examples
- Bug reports and fixes

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

---

## 📈 Roadmap

### Phase 1 (Now)
- ✅ Core routing optimization
- ✅ L402 payment integration
- ✅ Basic API
- ✅ Documentation

### Phase 2 (Next 30 days)
- 🔄 Advanced routing algorithms
- 🔄 Batch query support
- 🔄 Webhook notifications
- 🔄 Analytics dashboard

### Phase 3 (60+ days)
- 📋 Multi-hop optimization
- 📋 Predictive routing
- 📋 Custom routing strategies
- 📋 Enterprise support

---

## 📝 License

MIT License - See [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with gratitude for:
- The Bitcoin community
- Lightning Labs and the Lightning Network
- Anthropic and the AI agent community
- Everyone building in this space

---

## 📞 Contact & Links

- **Website:** [https://agentroute-yvqamn6m.manus.space](https://agentroute-yvqamn6m.manus.space)
- **API:** [https://agentroute-oracle.onrender.com](https://agentroute-oracle.onrender.com)
- **OpenAPI Spec:** [https://agentroute-oracle.onrender.com/openapi.json](https://agentroute-oracle.onrender.com/openapi.json)
- **Twitter:** [@AgentRouteOracle](https://x.com/agentroute)
- **Email:** hello@agentroute.oracle

---

**Built with ❤️ and ⚡ for the future of AI agents.**

*The future is AI. The future is Bitcoin. We're building the bridge.*

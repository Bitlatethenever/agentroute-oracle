#!/usr/bin/env node
/**
 * AgentRoute Oracle - JavaScript Example
 *
 * This example shows how to use AgentRoute Oracle to find optimal Bitcoin Lightning routes.
 *
 * Requirements:
 *   npm install node-fetch
 *
 * Usage:
 *   node examples/javascript_example.js
 */

const fetch = require('node-fetch');

// Configuration
const AGENTROUTE_API_URL = 'https://agentroute-oracle.onrender.com';
const L402_TOKEN = 'your_l402_token_here'; // You'll get this after paying the first invoice

/**
 * AgentRoute Oracle Client
 */
class AgentRouteClient {
  constructor(apiUrl = AGENTROUTE_API_URL, l402Token = null) {
    this.apiUrl = apiUrl;
    this.l402Token = l402Token;
  }

  /**
   * Get optimal route for a Bitcoin Lightning transaction
   *
   * @param {string} source - Source wallet ID or node pubkey
   * @param {string} destination - Destination wallet ID or node pubkey
   * @param {number} amountSats - Amount in satoshis
   * @param {number} timeoutSeconds - Request timeout (default: 30)
   * @returns {Promise<Object|null>} Route information or null on error
   */
  async getOptimalRoute(source, destination, amountSats, timeoutSeconds = 30) {
    const headers = {
      'Content-Type': 'application/json',
    };

    // Add L402 token if available
    if (this.l402Token) {
      headers['Authorization'] = `L402 ${this.l402Token}`;
    }

    const payload = {
      source,
      destination,
      amount_sats: amountSats,
      timeout_seconds: timeoutSeconds,
    };

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), timeoutSeconds * 1000);

      const response = await fetch(`${this.apiUrl}/route`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      // Handle 402 Payment Required (L402 invoice)
      if (response.status === 402) {
        console.log('⚡ L402 Payment Required');
        const invoiceData = await response.json();
        console.log(`Invoice: ${invoiceData.invoice || 'N/A'}`);
        console.log(`Amount: ${invoiceData.amount_sats || 'N/A'} sats`);
        console.log('\nPay this invoice with your Lightning wallet and retry with the token.');
        return null;
      }

      // Handle success
      if (response.status === 200) {
        return await response.json();
      }

      // Handle errors
      console.error(`Error: ${response.status}`);
      console.error(await response.text());
      return null;
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error(`Request timed out after ${timeoutSeconds} seconds`);
      } else {
        console.error(`Request failed: ${error.message}`);
      }
      return null;
    }
  }

  /**
   * Pretty print route information
   */
  printRoute(route) {
    if (!route) {
      console.log('No route data to display');
      return;
    }

    console.log('\n' + '='.repeat(60));
    console.log('✨ OPTIMAL ROUTE FOUND');
    console.log('='.repeat(60));
    console.log(`Route ID:              ${route.route_id || 'N/A'}`);
    console.log(`Number of hops:        ${route.hops || 'N/A'}`);
    console.log(`Estimated fee:         ${route.fee_sats || 'N/A'} sats`);
    console.log(`Success probability:   ${((route.success_probability || 0) * 100).toFixed(1)}%`);
    console.log(`Timestamp:             ${route.timestamp || 'N/A'}`);

    // Print route details
    if (route.route_details && route.route_details.length > 0) {
      console.log('\n📍 Route Details:');
      route.route_details.forEach((detail) => {
        const hop = detail.hop || 'N/A';
        const node = (detail.node || 'N/A').substring(0, 16) + '...';
        const fee = detail.fee_sats || 'N/A';
        console.log(`  Hop ${hop}: ${node} (fee: ${fee} sats)`);
      });
    }

    console.log('='.repeat(60) + '\n');
  }
}

/**
 * Main example
 */
async function main() {
  console.log('🚀 AgentRoute Oracle - JavaScript Example\n');

  // Initialize client
  const client = new AgentRouteClient();

  // Example 1: Query without L402 token (will get invoice)
  console.log('Example 1: Get optimal route (first query - will need payment)');
  console.log('-'.repeat(60));

  const sourceWallet = 'agent_wallet_001';
  const destWallet = 'merchant_wallet_001';
  const amount = 10000; // 10,000 sats

  console.log(`Source:      ${sourceWallet}`);
  console.log(`Destination: ${destWallet}`);
  console.log(`Amount:      ${amount} sats\n`);

  let route = await client.getOptimalRoute(sourceWallet, destWallet, amount);

  if (route) {
    client.printRoute(route);
    console.log('✅ Route query successful!');
  } else {
    console.log('❌ Route query failed or payment required');
  }

  // Example 2: Multiple queries
  console.log('\nExample 2: Multiple route queries');
  console.log('-'.repeat(60));

  const transactions = [
    ['agent_001', 'merchant_001', 5000],
    ['agent_001', 'merchant_002', 15000],
    ['agent_002', 'merchant_001', 8000],
  ];

  for (const [source, dest, amt] of transactions) {
    console.log(`\nQuerying route: ${source} → ${dest} (${amt} sats)`);
    route = await client.getOptimalRoute(source, dest, amt);
    if (route) {
      console.log(`  ✅ Fee: ${route.fee_sats || 'N/A'} sats | Hops: ${route.hops || 'N/A'}`);
    } else {
      console.log(`  ❌ Failed to get route`);
    }
  }

  // Example 3: Error handling
  console.log('\n\nExample 3: Error handling');
  console.log('-'.repeat(60));

  // Invalid parameters
  console.log('\nQuerying with invalid parameters...');
  route = await client.getOptimalRoute('', '', 0);
  if (!route) {
    console.log('  ✅ Error handled gracefully');
  }
}

// Run main
main().catch(console.error);

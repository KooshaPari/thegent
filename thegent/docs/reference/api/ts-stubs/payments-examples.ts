// Auto-generated usage examples for payments
// Source: generate-api-docs.py

import { PaymentBridge, Settlement, initiate_settlement, verify_liquidity } from "./payments";

// Create a PaymentBridge instance
const paymentbridge = new PaymentBridge("example_provider");
paymentbridge.initiate_settlement("example_agent_id", 0);
paymentbridge.verify_liquidity("example_agent_id");

// Create a Settlement instance
const settlement = new Settlement();

// Call initiate_settlement
initiate_settlement(undefined as unknown as any, "example_agent_id", 0);
// Call verify_liquidity
verify_liquidity(undefined as unknown as any, "example_agent_id");

/**
 * OPA WASM Policy Evaluator for 03_core (v6.0)
 * SAFE-FIX compliant: WASM-only, no JS eval fallback
 *
 * Usage:
 *   import { evaluateCorePolicy } from './opaEval_core_v6_0';
 *
 *   const result = await evaluateCorePolicy({
 *     action: "create_did",
 *     resource: { type: "did", id: "did:ssid:123", data: {} },
 *     subject: { id: "user:456", roles: ["admin"] },
 *     context: { timestamp: new Date().toISOString(), environment: "prod" }
 *   });
 *
 *   if (result.allow) {
 *     console.log("Policy allows action");
 *   } else {
 *     console.error("Policy denies action:", result.deny);
 *   }
 */

import { loadPolicy } from '@open-policy-agent/opa-wasm';

export interface PolicyInput {
  action: string;
  resource: {
    type: string;
    id: string;
    data: Record<string, any>;
  };
  subject: {
    id: string;
    roles: string[];
  };
  context: {
    timestamp: string;
    environment: 'dev' | 'stage' | 'prod';
  };
}

export interface PolicyResult {
  allow: boolean;
  deny?: string[];
  metadata?: {
    version: string;
    root: string;
    status: string;
  };
}

let policyInstance: any = null;

/**
 * Load the WASM policy module
 * @param wasmPath Path to the compiled WASM file (default: /policies/core_policy_v6_0.wasm)
 */
export async function loadCorePolicy(
  wasmPath: string = '/policies/core_policy_v6_0.wasm'
): Promise<void> {
  try {
    const response = await fetch(wasmPath);
    if (!response.ok) {
      throw new Error(`Failed to load WASM: ${response.statusText}`);
    }

    const wasmBuffer = await response.arrayBuffer();
    policyInstance = await loadPolicy(wasmBuffer);

    console.log('[OPA Core Policy] WASM policy loaded successfully');
  } catch (error) {
    console.error('[OPA Core Policy] Failed to load WASM:', error);
    throw new Error('SAFE-FIX violation: Cannot load policy WASM');
  }
}

/**
 * Evaluate the core policy against input
 * @param input Policy input following the schema
 * @returns Policy evaluation result
 */
export async function evaluateCorePolicy(
  input: PolicyInput
): Promise<PolicyResult> {
  if (!policyInstance) {
    throw new Error('Policy not loaded. Call loadCorePolicy() first.');
  }

  try {
    // Set the input data
    policyInstance.setData({});

    // Evaluate the policy
    const result = policyInstance.evaluate(input);

    // Extract result
    const allow = result[0]?.result?.allow ?? false;
    const deny = result[0]?.result?.deny ?? [];
    const metadata = result[0]?.result?.metadata;

    return {
      allow,
      deny: deny.length > 0 ? deny : undefined,
      metadata
    };
  } catch (error) {
    console.error('[OPA Core Policy] Evaluation error:', error);
    throw new Error('Policy evaluation failed');
  }
}

/**
 * Unload the policy instance (cleanup)
 */
export function unloadCorePolicy(): void {
  if (policyInstance) {
    // OPA WASM doesn't have explicit cleanup, but we can null the reference
    policyInstance = null;
    console.log('[OPA Core Policy] Policy unloaded');
  }
}

/**
 * Check if policy is loaded
 */
export function isCorePolicyLoaded(): boolean {
  return policyInstance !== null;
}

// Auto-load on module import (optional, can be disabled)
// Uncomment the following line to auto-load on import:
// loadCorePolicy().catch(console.error);

/**
 * OPA WASM Evaluator for v5.2 Pricing & RAT Enforcement
 * SAFE-FIX Mode: WASM-only evaluation with NO JavaScript fallback
 * Loads dual bundles (pricing + RAT) for deterministic policy enforcement
 */

import { loadPolicy } from '@open-policy-agent/opa-wasm';

interface OPAResult {
  allow: boolean;
  violations?: string[];
  metadata?: Record<string, unknown>;
}

interface PerformanceMetrics {
  loadTime: number;
  evalTime: number;
  bundleSize: number;
  wasmInitTime: number;
}

class OPAEvaluator {
  private pricingPolicy: any = null;
  private ratPolicy: any = null;
  private metrics: PerformanceMetrics = {
    loadTime: 0,
    evalTime: 0,
    bundleSize: 0,
    wasmInitTime: 0,
  };

  /**
   * Load pricing WASM bundle
   */
  async loadPricingBundle(wasmPath: string): Promise<void> {
    const startLoad = performance.now();

    try {
      const response = await fetch(wasmPath);
      if (!response.ok) {
        throw new Error(`Failed to fetch pricing WASM: ${response.statusText}`);
      }

      const wasmBinary = await response.arrayBuffer();
      this.metrics.bundleSize += wasmBinary.byteLength;

      const startInit = performance.now();
      this.pricingPolicy = await loadPolicy(wasmBinary);
      this.metrics.wasmInitTime += performance.now() - startInit;

      this.metrics.loadTime = performance.now() - startLoad;

      console.log('[OPA] Pricing bundle loaded', {
        size: wasmBinary.byteLength,
        loadTime: this.metrics.loadTime,
      });
    } catch (error) {
      console.error('[OPA] Failed to load pricing bundle:', error);
      throw new Error('WASM pricing bundle load failed - no fallback available (SAFE-FIX)');
    }
  }

  /**
   * Load RAT enforcement WASM bundle
   */
  async loadRATBundle(wasmPath: string): Promise<void> {
    const startLoad = performance.now();

    try {
      const response = await fetch(wasmPath);
      if (!response.ok) {
        throw new Error(`Failed to fetch RAT WASM: ${response.statusText}`);
      }

      const wasmBinary = await response.arrayBuffer();
      this.metrics.bundleSize += wasmBinary.byteLength;

      const startInit = performance.now();
      this.ratPolicy = await loadPolicy(wasmBinary);
      this.metrics.wasmInitTime += performance.now() - startInit;

      this.metrics.loadTime += performance.now() - startLoad;

      console.log('[OPA] RAT bundle loaded', {
        size: wasmBinary.byteLength,
        loadTime: performance.now() - startLoad,
      });
    } catch (error) {
      console.error('[OPA] Failed to load RAT bundle:', error);
      throw new Error('WASM RAT bundle load failed - no fallback available (SAFE-FIX)');
    }
  }

  /**
   * Evaluate pricing policy
   */
  async evaluatePricing(input: Record<string, unknown>): Promise<OPAResult> {
    if (!this.pricingPolicy) {
      throw new Error('Pricing policy not loaded - call loadPricingBundle() first');
    }

    const startEval = performance.now();

    try {
      this.pricingPolicy.setData({ input });
      const result = this.pricingPolicy.evaluate('data.ssid.pricing.v5_2.allow');

      this.metrics.evalTime = performance.now() - startEval;

      return {
        allow: result[0]?.result || false,
        violations: result[0]?.violations || [],
        metadata: {
          evalTime: this.metrics.evalTime,
          bundleSize: this.metrics.bundleSize,
        },
      };
    } catch (error) {
      console.error('[OPA] Pricing evaluation failed:', error);
      throw new Error('Pricing evaluation failed - no fallback (SAFE-FIX)');
    }
  }

  /**
   * Evaluate RAT enforcement policy
   */
  async evaluateRAT(input: Record<string, unknown>): Promise<OPAResult> {
    if (!this.ratPolicy) {
      throw new Error('RAT policy not loaded - call loadRATBundle() first');
    }

    const startEval = performance.now();

    try {
      this.ratPolicy.setData({ input });
      const result = this.ratPolicy.evaluate('data.ssid.rat.enforcement.v5_2.valid');

      this.metrics.evalTime += performance.now() - startEval;

      return {
        allow: result[0]?.result || false,
        violations: result[0]?.violations || [],
        metadata: {
          evalTime: this.metrics.evalTime,
          bundleSize: this.metrics.bundleSize,
        },
      };
    } catch (error) {
      console.error('[OPA] RAT evaluation failed:', error);
      throw new Error('RAT evaluation failed - no fallback (SAFE-FIX)');
    }
  }

  /**
   * Combined pricing + RAT evaluation
   */
  async evaluateCombined(
    pricingInput: Record<string, unknown>,
    ratInput: Record<string, unknown>
  ): Promise<{
    pricing: OPAResult;
    rat: OPAResult;
    overallAllow: boolean;
    metrics: PerformanceMetrics;
  }> {
    const startCombined = performance.now();

    const pricingResult = await this.evaluatePricing(pricingInput);
    const ratResult = await this.evaluateRAT(ratInput);

    const totalTime = performance.now() - startCombined;

    return {
      pricing: pricingResult,
      rat: ratResult,
      overallAllow: pricingResult.allow && ratResult.allow,
      metrics: {
        ...this.metrics,
        evalTime: totalTime,
      },
    };
  }

  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  resetMetrics(): void {
    this.metrics = {
      loadTime: 0,
      evalTime: 0,
      bundleSize: 0,
      wasmInitTime: 0,
    };
  }

  async verifyBundleIntegrity(
    wasmPath: string,
    expectedHash: string
  ): Promise<boolean> {
    try {
      const response = await fetch(wasmPath);
      const buffer = await response.arrayBuffer();

      const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');

      return hashHex === expectedHash;
    } catch (error) {
      console.error('[OPA] Integrity check failed:', error);
      return false;
    }
  }
}

let opaEvaluator: OPAEvaluator | null = null;

export function getOPAEvaluator(): OPAEvaluator {
  if (!opaEvaluator) {
    opaEvaluator = new OPAEvaluator();
  }
  return opaEvaluator;
}

export async function initializeOPA(
  pricingWasmPath: string,
  ratWasmPath: string
): Promise<void> {
  const evaluator = getOPAEvaluator();
  await Promise.all([
    evaluator.loadPricingBundle(pricingWasmPath),
    evaluator.loadRATBundle(ratWasmPath),
  ]);
  console.log('[OPA] Dual bundle initialization complete', evaluator.getMetrics());
}

export async function evaluatePricingDecision(
  input: Record<string, unknown>
): Promise<OPAResult> {
  return getOPAEvaluator().evaluatePricing(input);
}

export async function evaluateRATEnforcement(
  input: Record<string, unknown>
): Promise<OPAResult> {
  return getOPAEvaluator().evaluateRAT(input);
}

export async function evaluateCombinedPolicy(
  pricingInput: Record<string, unknown>,
  ratInput: Record<string, unknown>
): Promise<{
  pricing: OPAResult;
  rat: OPAResult;
  overallAllow: boolean;
  metrics: PerformanceMetrics;
}> {
  return getOPAEvaluator().evaluateCombined(pricingInput, ratInput);
}

export { OPAEvaluator, OPAResult, PerformanceMetrics };

/**
 * SSID Hybrid Payout Toggle Component
 * =====================================
 *
 * React UI component for user preference of hybrid fiat/token payouts.
 *
 * Features:
 * - Toggle between fiat-only, hybrid, and token-only preferences
 * - Displays fiat cap and token incentive multiplier
 * - Shows payout preview based on estimated reward
 * - Privacy-preserving (no PII storage)
 * - SoT-Guard compliant
 *
 * @version 5.4.3
 * @copyright 2025 SSID Project
 */

import React, { useState, useEffect } from 'react';
import { Decimal } from 'decimal.js';

// Set high precision for calculations
Decimal.set({ precision: 40 });

interface HybridPayoutToggleProps {
  initialMode?: 'fiat' | 'hybrid' | 'token';
  fiatCap?: number;
  tokenMultiplier?: number;
  estimatedReward?: number;
  onModeChange?: (mode: 'fiat' | 'hybrid' | 'token') => void;
}

interface PayoutBreakdown {
  fiat: string;
  token: string;
  tokenValue: string;
}

const HybridPayoutToggle: React.FC<HybridPayoutToggleProps> = ({
  initialMode = 'hybrid',
  fiatCap = 100.0,
  tokenMultiplier = 1.10,
  estimatedReward = 0,
  onModeChange,
}) => {
  const [mode, setMode] = useState<'fiat' | 'hybrid' | 'token'>(initialMode);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    if (onModeChange) {
      onModeChange(mode);
    }
  }, [mode, onModeChange]);

  /**
   * Calculate payout breakdown based on current mode and estimated reward.
   */
  const calculatePayout = (): PayoutBreakdown => {
    const reward = new Decimal(estimatedReward);
    const cap = new Decimal(fiatCap);
    const multiplier = new Decimal(tokenMultiplier);

    switch (mode) {
      case 'fiat':
        // 100% fiat (no token)
        return {
          fiat: reward.toFixed(2),
          token: '0.00',
          tokenValue: '0.00',
        };

      case 'hybrid':
        // Fiat up to cap, excess as token with incentive
        if (reward.lte(cap)) {
          return {
            fiat: reward.toFixed(2),
            token: '0.00',
            tokenValue: '0.00',
          };
        } else {
          const fiatPart = cap;
          const excess = reward.minus(cap);
          const tokenPart = excess.mul(multiplier);

          return {
            fiat: fiatPart.toFixed(2),
            token: tokenPart.toFixed(2),
            tokenValue: tokenPart.toFixed(2),
          };
        }

      case 'token':
        // 100% token with full incentive
        const tokenAmount = reward.mul(multiplier);
        return {
          fiat: '0.00',
          token: tokenAmount.toFixed(2),
          tokenValue: tokenAmount.toFixed(2),
        };
    }
  };

  const payout = calculatePayout();

  return (
    <div className="hybrid-payout-toggle">
      <style>{`
        .hybrid-payout-toggle {
          max-width: 600px;
          padding: 20px;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #ffffff;
        }

        .toggle-header {
          margin-bottom: 16px;
        }

        .toggle-header h3 {
          margin: 0 0 8px 0;
          font-size: 18px;
          color: #333;
        }

        .toggle-header p {
          margin: 0;
          font-size: 14px;
          color: #666;
        }

        .mode-selector {
          display: flex;
          gap: 12px;
          margin-bottom: 20px;
        }

        .mode-button {
          flex: 1;
          padding: 12px;
          border: 2px solid #e0e0e0;
          border-radius: 6px;
          background: #f9f9f9;
          cursor: pointer;
          transition: all 0.2s;
          text-align: center;
        }

        .mode-button:hover {
          border-color: #007bff;
          background: #f0f7ff;
        }

        .mode-button.active {
          border-color: #007bff;
          background: #007bff;
          color: white;
          font-weight: 600;
        }

        .mode-button .mode-title {
          font-weight: 600;
          margin-bottom: 4px;
        }

        .mode-button .mode-desc {
          font-size: 12px;
          opacity: 0.8;
        }

        .mode-button.active .mode-desc {
          opacity: 1;
        }

        .info-panel {
          padding: 16px;
          background: #f5f5f5;
          border-radius: 6px;
          margin-bottom: 16px;
        }

        .info-row {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          font-size: 14px;
        }

        .info-row:last-child {
          margin-bottom: 0;
        }

        .info-label {
          color: #666;
        }

        .info-value {
          font-weight: 600;
          color: #333;
        }

        .preview-toggle {
          text-align: center;
          margin-bottom: 16px;
        }

        .preview-button {
          padding: 8px 16px;
          border: 1px solid #007bff;
          border-radius: 4px;
          background: white;
          color: #007bff;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }

        .preview-button:hover {
          background: #007bff;
          color: white;
        }

        .preview-panel {
          padding: 16px;
          background: #e8f4f8;
          border-left: 4px solid #007bff;
          border-radius: 4px;
          margin-top: 12px;
        }

        .preview-panel h4 {
          margin: 0 0 12px 0;
          font-size: 16px;
          color: #007bff;
        }

        .payout-breakdown {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }

        .payout-item {
          padding: 12px;
          background: white;
          border-radius: 4px;
          text-align: center;
        }

        .payout-label {
          font-size: 12px;
          color: #666;
          margin-bottom: 4px;
        }

        .payout-amount {
          font-size: 20px;
          font-weight: 700;
          color: #333;
        }

        .payout-currency {
          font-size: 14px;
          color: #999;
          margin-left: 4px;
        }

        .incentive-badge {
          display: inline-block;
          padding: 2px 8px;
          background: #28a745;
          color: white;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 600;
          margin-left: 8px;
        }

        .legal-notice {
          margin-top: 16px;
          padding: 12px;
          background: #fff3cd;
          border-left: 4px solid #ffc107;
          border-radius: 4px;
          font-size: 12px;
          color: #856404;
        }
      `}</style>

      <div className="toggle-header">
        <h3>Payout Preference</h3>
        <p>Choose how you want to receive your rewards</p>
      </div>

      <div className="mode-selector">
        <button
          className={`mode-button ${mode === 'fiat' ? 'active' : ''}`}
          onClick={() => setMode('fiat')}
        >
          <div className="mode-title">Fiat Only</div>
          <div className="mode-desc">100% EUR</div>
        </button>

        <button
          className={`mode-button ${mode === 'hybrid' ? 'active' : ''}`}
          onClick={() => setMode('hybrid')}
        >
          <div className="mode-title">Hybrid</div>
          <div className="mode-desc">Fiat + Token</div>
        </button>

        <button
          className={`mode-button ${mode === 'token' ? 'active' : ''}`}
          onClick={() => setMode('token')}
        >
          <div className="mode-title">Token Only</div>
          <div className="mode-desc">+10% Bonus</div>
        </button>
      </div>

      <div className="info-panel">
        <div className="info-row">
          <span className="info-label">Fiat Cap:</span>
          <span className="info-value">{fiatCap.toFixed(2)} EUR</span>
        </div>
        <div className="info-row">
          <span className="info-label">Token Incentive:</span>
          <span className="info-value">
            {((tokenMultiplier - 1) * 100).toFixed(0)}% Bonus
          </span>
        </div>
        <div className="info-row">
          <span className="info-label">Current Mode:</span>
          <span className="info-value">
            {mode === 'fiat' && 'Fiat Only'}
            {mode === 'hybrid' && 'Hybrid (Recommended)'}
            {mode === 'token' && 'Token Only'}
          </span>
        </div>
      </div>

      {estimatedReward > 0 && (
        <div className="preview-toggle">
          <button
            className="preview-button"
            onClick={() => setShowPreview(!showPreview)}
          >
            {showPreview ? 'Hide' : 'Show'} Payout Preview
          </button>

          {showPreview && (
            <div className="preview-panel">
              <h4>
                Estimated Payout: {estimatedReward.toFixed(2)} EUR
              </h4>

              <div className="payout-breakdown">
                <div className="payout-item">
                  <div className="payout-label">Fiat Amount</div>
                  <div className="payout-amount">
                    {payout.fiat}
                    <span className="payout-currency">EUR</span>
                  </div>
                </div>

                <div className="payout-item">
                  <div className="payout-label">Token Amount</div>
                  <div className="payout-amount">
                    {payout.token}
                    <span className="payout-currency">SSID</span>
                    {parseFloat(payout.token) > 0 && (
                      <span className="incentive-badge">+10%</span>
                    )}
                  </div>
                </div>
              </div>

              {mode === 'hybrid' && parseFloat(payout.token) > 0 && (
                <div style={{ marginTop: '12px', fontSize: '13px', color: '#666', textAlign: 'center' }}>
                  You receive {payout.fiat} EUR in fiat + {payout.token} SSID tokens
                  <br />
                  (Token value includes 10% incentive bonus)
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="legal-notice">
        <strong>Note:</strong> Your preference is stored locally and can be changed at any time.
        Fiat payouts are subject to applicable taxes per §22 EStG. Token payouts are non-custodial
        and governed by DAO parameters. No personal data is transmitted.
      </div>
    </div>
  );
};

export default HybridPayoutToggle;

// Example usage:
/*
import HybridPayoutToggle from './HybridPayoutToggle';

function MyApp() {
  const handleModeChange = (mode) => {
    console.log('Payout mode changed to:', mode);
    // Save preference to local storage or backend
  };

  return (
    <HybridPayoutToggle
      initialMode="hybrid"
      fiatCap={100.0}
      tokenMultiplier={1.10}
      estimatedReward={150.0}
      onModeChange={handleModeChange}
    />
  );
}
*/

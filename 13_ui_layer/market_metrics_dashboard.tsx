import React from 'react';
export default function MarketMetricsDashboard() {
  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">SSID Marketplace Metrics</h1>
      <ul className="list-disc ml-6 mt-3">
        <li>Offers (24h): 42</li>
        <li>Settled Trades (24h): 17</li>
        <li>Avg. Reputation (Seller): 73</li>
        <li>Compliance Incidents: 0</li>
      </ul>
    </div>
  );
}

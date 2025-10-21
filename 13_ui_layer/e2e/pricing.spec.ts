import { test, expect } from '@playwright/test';

test('pricing JSON reachable & fields present', async ({ request }) => {
  const res = await request.get('/07_governance_legal/docs/pricing/enterprise_subscription_model_v5.json');
  expect(res.ok()).toBeTruthy();
  const json = await res.json();
  expect(json.version).toBe('5.0');
  expect(json.tiers.length).toBeGreaterThan(0);
  expect(Object.keys(json.regional_zones).length).toBeGreaterThan(0);
});

test('region registry reachable', async ({ request }) => {
  const res = await request.get('/13_ui_layer/i18n/regions/region_activation_registry.json');
  expect(res.ok()).toBeTruthy();
  const json = await res.json();
  expect(Object.keys(json.did_regions).length).toBeGreaterThan(0);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { InlineBudget } from './context_budget.mjs';
test('core byte budget rejects invalid configuration and cannot be mutated to disable its cap', () => {
  for (const value of [NaN, Infinity, -1, 0.5, '1', null]) assert.throws(() => new InlineBudget(value), RangeError);
  const budget = new InlineBudget(1);
  assert.throws(() => { budget.limit = NaN; }, TypeError);
  assert.equal(budget.limit, 1); assert.equal(budget.reserve('large', 'xx'), null);
  assert.ok(budget.reserve('exact', 'x'));
});

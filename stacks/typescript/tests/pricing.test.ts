import { describe, expect, it } from "vitest";

import { applyDiscount } from "../src/pricing";

describe("applyDiscount", () => {
  it.each([
    { priceCents: 1000, discountPercent: 0, expectedCents: 1000 },
    { priceCents: 1000, discountPercent: 25, expectedCents: 750 },
    { priceCents: 1000, discountPercent: 100, expectedCents: 0 },
    { priceCents: 999, discountPercent: 50, expectedCents: 500 }, // 499.5 rounds half up
  ])(
    "returns $expectedCents cents for $priceCents cents at $discountPercent %",
    ({ priceCents, discountPercent, expectedCents }) => {
      const result = applyDiscount(priceCents, discountPercent);

      expect(result).toBe(expectedCents);
    },
  );

  it.each([-1, 10.5])("rejects a price of %s cents", (priceCents) => {
    expect(() => applyDiscount(priceCents, 10)).toThrow(RangeError);
  });

  it.each([-1, 101, 2.5])("rejects a discount of %s %", (discountPercent) => {
    expect(() => applyDiscount(1000, discountPercent)).toThrow(RangeError);
  });
});

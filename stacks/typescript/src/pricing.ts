/**
 * Price calculations.
 *
 * Example module showing the project conventions: units in names, JSDoc on exports,
 * validation at the boundary, explicit errors. Delete it once real code exists.
 */

const PERCENT_BASE = 100;

/**
 * Returns the price after a percentage discount, rounded half up to the cent.
 *
 * @param priceCents - Original price in cents, a non-negative integer.
 * @param discountPercent - Discount, an integer between 0 and 100 inclusive.
 * @throws {RangeError} If an argument is out of range or not an integer.
 */
export function applyDiscount(priceCents: number, discountPercent: number): number {
  if (!Number.isInteger(priceCents) || priceCents < 0) {
    throw new RangeError(`priceCents must be a non-negative integer, got ${priceCents}`);
  }
  if (!Number.isInteger(discountPercent) || discountPercent < 0 || discountPercent > PERCENT_BASE) {
    throw new RangeError(
      `discountPercent must be an integer from 0 to 100, got ${discountPercent}`,
    );
  }

  // Integer math: floats cannot represent most cent amounts exactly.
  // Adding half the divisor before flooring rounds half up.
  const remainingPercent = PERCENT_BASE - discountPercent;
  return Math.floor((priceCents * remainingPercent + PERCENT_BASE / 2) / PERCENT_BASE);
}

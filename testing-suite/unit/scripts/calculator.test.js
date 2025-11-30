/**
 * Unit Tests for Calculator Functions
 * 
 * These tests validate business logic with edge cases and error conditions
 */

// Calculator functions to test
const calculator = {
  add: (a, b) => a + b,
  subtract: (a, b) => a - b,
  multiply: (a, b) => a * b,
  divide: (a, b) => {
    if (b === 0) {
      throw new Error('Division by zero');
    }
    return a / b;
  },
  power: (base, exponent) => Math.pow(base, exponent),
  factorial: (n) => {
    if (n < 0) {
      throw new Error('Factorial of negative number is not defined');
    }
    if (n === 0 || n === 1) {
      return 1;
    }
    return n * calculator.factorial(n - 1);
  }
};

// Test framework simulation
const test = (description, fn) => {
  try {
    fn();
    console.log(`✓ ${description}`);
  } catch (error) {
    console.log(`✗ ${description}: ${error.message}`);
  }
};

const expect = (actual) => {
  return {
    toBe: (expected) => {
      if (actual !== expected) {
        throw new Error(`Expected ${expected}, but got ${actual}`);
      }
    },
    toBeCloseTo: (expected, precision = 2) => {
      if (Math.abs(actual - expected) > Math.pow(10, -precision) / 2) {
        throw new Error(`Expected ${expected}, but got ${actual}`);
      }
    },
    toThrow: (errorMessage) => {
      try {
        actual();
      } catch (error) {
        if (errorMessage && error.message !== errorMessage) {
          throw new Error(`Expected error message "${errorMessage}", but got "${error.message}"`);
        }
        return; // Test passes if error is thrown
      }
      throw new Error('Expected function to throw an error, but it did not');
    }
  };
};

// Test suite
console.log('Running Unit Tests for Calculator...');
console.log('===================================');

// Addition tests
test('adds two positive numbers correctly', () => {
  expect(calculator.add(2, 3)).toBe(5);
});

test('adds negative numbers correctly', () => {
  expect(calculator.add(-2, -3)).toBe(-5);
});

test('adds positive and negative numbers correctly', () => {
  expect(calculator.add(5, -3)).toBe(2);
});

test('adds zero correctly', () => {
  expect(calculator.add(5, 0)).toBe(5);
});

// Subtraction tests
test('subtracts two positive numbers correctly', () => {
  expect(calculator.subtract(5, 3)).toBe(2);
});

test('subtracts negative numbers correctly', () => {
  expect(calculator.subtract(-2, -3)).toBe(1);
});

test('subtracts to negative result', () => {
  expect(calculator.subtract(3, 5)).toBe(-2);
});

// Multiplication tests
test('multiplies two positive numbers correctly', () => {
  expect(calculator.multiply(3, 4)).toBe(12);
});

test('multiplies by zero correctly', () => {
  expect(calculator.multiply(5, 0)).toBe(0);
});

test('multiplies negative numbers correctly', () => {
  expect(calculator.multiply(-3, -4)).toBe(12);
});

test('multiplies positive and negative numbers correctly', () => {
  expect(calculator.multiply(3, -4)).toBe(-12);
});

// Division tests
test('divides two positive numbers correctly', () => {
  expect(calculator.divide(8, 2)).toBe(4);
});

test('divides negative numbers correctly', () => {
  expect(calculator.divide(-8, -2)).toBe(4);
});

test('divides positive and negative numbers correctly', () => {
  expect(calculator.divide(8, -2)).toBe(-4);
});

test('throws error when dividing by zero', () => {
  expect(() => calculator.divide(5, 0)).toThrow('Division by zero');
});

// Power tests
test('calculates power correctly for positive base and exponent', () => {
  expect(calculator.power(2, 3)).toBe(8);
});

test('calculates power correctly for negative base', () => {
  expect(calculator.power(-2, 3)).toBe(-8);
});

test('calculates power correctly for zero exponent', () => {
  expect(calculator.power(5, 0)).toBe(1);
});

// Factorial tests
test('calculates factorial of 0 correctly', () => {
  expect(calculator.factorial(0)).toBe(1);
});

test('calculates factorial of 1 correctly', () => {
  expect(calculator.factorial(1)).toBe(1);
});

test('calculates factorial of 5 correctly', () => {
  expect(calculator.factorial(5)).toBe(120);
});

test('throws error for factorial of negative number', () => {
  expect(() => calculator.factorial(-5)).toThrow('Factorial of negative number is not defined');
});

console.log('\nUnit Tests Completed!');
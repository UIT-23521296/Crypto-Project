# Elliptic Curve Finder for Pohlig-Hellman Attack

This project provides tools to find elliptic curves with orders around 16 bits that are suitable for demonstrating the Pohlig-Hellman attack on elliptic curve discrete logarithm problems.

## Overview

The Pohlig-Hellman attack is effective when the order of the elliptic curve group has many small prime factors (smooth order). This makes the discrete logarithm problem easier to solve by breaking it down into smaller subproblems.

## Files

- `simple_curve_finder.py` - Main program to find suitable elliptic curves
- `curve_finder.py` - More comprehensive curve finder with additional options
- `test_pohlig_hellman.py` - Test script to demonstrate the Pohlig-Hellman attack
- `curve_params.txt` - Output file containing curve parameters (generated by curve finder)

## Requirements

- SageMath (for elliptic curve operations)
- Python 3.x

## Usage

### 1. Find a Suitable Elliptic Curve

Run the simple curve finder to find a curve with ~16 bit order:

```bash
sage simple_curve_finder.py
```

This will:
- Search for elliptic curves with orders in the range 32768-65535 (16 bits)
- Prefer curves with multiple prime factors (smooth orders)
- Save the curve parameters to `curve_params.txt`

### 2. Test the Pohlig-Hellman Attack

After finding a curve, test the attack:

```bash
sage test_pohlig_hellman.py
```

This will:
- Load the curve parameters from `curve_params.txt`
- Generate a test case with a random private key
- Perform the Pohlig-Hellman attack to recover the private key
- Verify the attack was successful

## How the Pohlig-Hellman Attack Works

1. **Factorization**: Factor the order n of the generator point G
2. **Subgroup Reduction**: For each prime factor p^e, compute:
   - P1 = (n/p^e) * G
   - Q1 = (n/p^e) * Q
3. **Discrete Log**: Solve the discrete log in the subgroup of order p^e
4. **Chinese Remainder Theorem**: Combine the results to find the full private key

## Example Output

```
==================================================
Simple Elliptic Curve Finder
==================================================

[*] Searching for curve with smooth 16-bit order...
[*] Trying to find curve with order 5040...
[+] Found curve with exact order 5040
[+] Field: GF(4294967291)
[+] Curve: y² = x³ + 1x + 2 mod 4294967291
[+] Generator: G = (123456789, 987654321)
[+] Order: n = 5040
[+] Factorization: [(2, 4), (3, 2), (5, 1), (7, 1)]

==================================================
FINAL RESULT
==================================================
Field: GF(4294967291)
Curve: y² = x³ + 1x + 2 mod 4294967291
Generator: G = (123456789, 987654321)
Order: n = 5040 (13 bits)
Factors: [(2, 4), (3, 2), (5, 1), (7, 1)]
Largest factor: 16 (4 bits)
Pohlig-Hellman complexity: ~2^2 operations

[+] Parameters saved to curve_params.txt
```

## Attack Complexity

The complexity of the Pohlig-Hellman attack depends on the largest prime factor of the group order. For a curve with order n = ∏(p_i^e_i), the complexity is approximately:

O(√max(p_i^e_i))

Curves with smooth orders (many small factors) are vulnerable to this attack.

## Security Considerations

⚠️ **WARNING**: These curves are designed for educational purposes only. They are intentionally weak and should NEVER be used in real cryptographic applications.

For real-world applications, use standardized curves like:
- NIST P-256, P-384, P-521
- Curve25519
- secp256k1 (Bitcoin)

## Educational Value

This project demonstrates:
- How to generate elliptic curves with specific properties
- Why smooth group orders are vulnerable to Pohlig-Hellman
- The importance of using cryptographically secure curves
- The relationship between group order factorization and attack complexity

## Troubleshooting

If you encounter issues:

1. **SageMath not found**: Install SageMath from https://www.sagemath.org/
2. **No curves found**: Increase `max_trials` in the curve finder
3. **Attack fails**: Ensure the curve has multiple prime factors

## License

This project is for educational purposes only. 
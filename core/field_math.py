"""
Finite field arithmetic operations for Shamir's Secret Sharing.
"""


def is_prime(n):
    """
    Check if n is a prime number.
    
    Args:
        n: Integer to check for primality
        
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Check odd divisors up to sqrt(n)
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def next_prime(n):
    """
    Find the smallest prime number greater than n.
    
    Args:
        n: Starting integer
        
    Returns:
        The next prime number after n
    """
    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate


# Alias for consistency
find_next_prime = next_prime


def modinv(a, p):
    """
    Compute modular multiplicative inverse of a modulo p.
    Uses Extended Euclidean Algorithm.
    
    Args:
        a: Number to find inverse of
        p: Modulus (should be prime)
        
    Returns:
        The modular inverse of a mod p
        
    Raises:
        ZeroDivisionError: If a is 0 or inverse doesn't exist
    """
    a = int(a) % p
    if a == 0:
        raise ZeroDivisionError("Inverse of 0 does not exist")
    
    # Extended Euclidean Algorithm
    lm, hm = 1, 0
    low, high = a % p, p
    
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    
    return lm % p


def lagrange_coeffs_at_zero(xs, p):
    """
    Compute Lagrange interpolation coefficients at x=0.
    
    Given xs = [x1, x2, ..., xk] (distinct, nonzero),
    returns list of scalar L_i values (mod p) such that:
      secret = sum_i (y_i * L_i) mod p
    where L_i = prod_{j != i} (-x_j) * inv(x_i - x_j)
    
    Args:
        xs: List of x-coordinates (distinct, nonzero)
        p: Prime modulus for the finite field
        
    Returns:
        List of Lagrange coefficients (one per x in xs)
    """
    k = len(xs)
    xs = [int(x) % p for x in xs]
    coeffs = []
    
    for i in range(k):
        xi = xs[i]
        num = 1
        den = 1
        
        for j in range(k):
            if j == i:
                continue
            xj = xs[j]
            # Evaluate basis polynomial at 0: multiply by (-xj)
            num = (num * (-xj)) % p
            den = (den * (xi - xj)) % p
        
        inv_den = modinv(den, p)
        coeffs.append((num * inv_den) % p)
    
    return coeffs

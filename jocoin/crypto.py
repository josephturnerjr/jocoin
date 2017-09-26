import random


def extended_euclidean_alg(a, b):
    r0, r1 = a, b
    s0, s1 = 1, 0
    t0, t1 = 0, 1
    while True:
        r = r0 % r1
        if r == 0:
            return (r1, s1, t1)
        q = r0 // r1
        r0, r1 = r1, r
        s0, s1 = s1, s0 - q * s1
        t0, t1 = t1, t0 - q * t1
    
def gcd(a, b):
    return extended_euclidean_alg(a, b)[0]

def mod_mult_inv(a, m):
    return (m + extended_euclidean_alg(a, m)[1]) % m

def lcm(a, b):
    return a * (b // gcd(a, b))

def sieve(n):
    primes = [2]
    candidates = list(range(3, n, 2))
    while True:
        p = candidates.pop(0)
        if p > (n ** (1/2)):
            primes.append(p)
            break
        candidates = [c for c in candidates if c % p != 0]
        primes.append(p)
    return primes + candidates
        
PRIMES = sieve(100000)

def find_coprime(t):
    random.shuffle(PRIMES)
    for p in PRIMES:
        if t % p != 0:
            return p
    raise ValueError("No p!")

def power_of_two_div(n):
    c = 0
    while n % 2 == 0:
        c += 1
        n = n >> 1
    return c

def likely_prime(w, iterations=64):
    # Miller-Rabin
    if w % 2 == 0:
        return False
    a = power_of_two_div(w - 1)
    m = (w - 1) >> a
    wlen = w.bit_length()
    for i in range(iterations):
        cont = False
        b = random.randint(2, w - 2)
        z = pow(b, m, w)
        if z == 1 or z == w - 1:
            continue
        for j in range(a - 1):
            z = pow(z, 2, w)
            if z == 1:
                return False
            if z == w - 1:
                cont = True
        if not cont:
            return False
    return True

def generate_prime(length):
    while True:
        candidate = random.getrandbits(length)
        if candidate.bit_length() == length:
            if likely_prime(candidate):
                return candidate

def gen_keys(length):
    p = generate_prime(length)
    q = generate_prime(length)
    n = p * q
    totient = lcm(p-1, q-1)
    e = find_coprime(totient)
    d = mod_mult_inv(e, totient)
    #print("p, q, totient, e, d", p, q, totient, e, d, e * d % totient)
    return {"pubkey": (n, e), "privkey": (n, d)}

def encrypt(m, privkey):
    n, d = privkey
    if m < 0 or m >= n:
        raise ValueError("Attempting to encrypt a message larger than N")
    return pow(m, d, n)
    
def decrypt(c, pubkey):
    n, e = pubkey
    return pow(c, e, n)

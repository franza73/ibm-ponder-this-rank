# SumSum: Mathematical Derivation and Algorithms

## 1. Basic \(O(N)\) solution

### 1.1. Definition

Given a sequence

\[
(a_0,a_1,\ldots,a_{N-1}),
\]

one operation removes the first element and replaces the remaining sequence with its partial sums.

We repeat until one element remains.

The original first element \(a_0\) never contributes to the result.

### 1.2. Deriving the coefficients

Let \(d_{n,k}\) be the coefficient of \(a_{n-1-k}\) in the SumSum of a sequence of length \(n\).

The initial condition is:

\[
d_{2,0}=1.
\]

The transformation gives the recurrence:

\[
d_{n,k}=
\sum_{\ell=0}^{\min(k,n-3)}d_{n-1,\ell}.
\]

Using the hockey-stick identity, we obtain:

\[
\boxed{
d_{n,k}=
\binom{n+k-2}{k}
-
\binom{n+k-2}{k-1}
}
\]

where \(\binom nk=0\) when \(k<0\).

Therefore:

\[
\boxed{
S_N=
\sum_{k=0}^{N-2}
d_{N,k}a_{N-1-k}
}
\]

This reduces the problem from explicitly constructing \(N-1\) sequences to calculating a single weighted sum.

### 1.3. Calculate coefficients in constant time

Define:

\[
B_k=\binom{N+k-2}{k}.
\]

Then:

\[
B_0=1
\]

and:

\[
B_{k+1}=B_k\frac{N+k-1}{k+1}.
\]

Furthermore:

\[
\frac{\binom{N+k-2}{k-1}}{\binom{N+k-2}{k}}
=\frac{k}{N-1}.
\]

Consequently:

\[
\boxed{
d_{N,k}=B_k\frac{N-1-k}{N-1}
}
\]

When working modulo a prime \(p>N\), all required denominators have modular inverses.

Thus, we can calculate every coefficient in constant time, giving an \(O(N)\) algorithm.

---

## 2. Implementation of Solution 1: General \(O(N)\)

This implementation accepts an arbitrary sequence and calculates its SumSum modulo a prime \(p\).

**Assumptions:**

- \(p\) is prime.
- \(2\leq N<p\).
- The sequence is available as a Python list.

```python
def sumsum_mod(a, p):
    n = len(a)

    if n == 0:
        raise ValueError("Empty sequence")

    if n == 1:
        return a[0] % p

    if n >= p:
        raise ValueError("Requires N < p")

    # Precompute modular inverses:
    # inv[i] = i^(-1) mod p
    inv = [0] * n
    inv[1] = 1

    for i in range(2, n):
        inv[i] = p - (p // i) * inv[p % i] % p

    inv_n_minus_1 = inv[n - 1]

    # B_k = C(n + k - 2, k)
    B = 1
    ans = 0

    for k in range(n - 1):

        # d[n,k] = B_k * (n - 1 - k) / (n - 1)
        d = B * (n - 1 - k) % p
        d = d * inv_n_minus_1 % p

        # Apply the coefficient to a[n - 1 - k]
        ans = (ans + d * a[n - 1 - k]) % p

        # Calculate B_(k+1)
        if k < n - 2:
            B = B * (n + k - 1) % p
            B = B * inv[k + 1] % p

    return ans
```

**Complexity:**

| Resource | Complexity |
|---|---:|
| Time | \(O(N)\) |
| Auxiliary space | \(O(N)\) |

This is the general solution. It works for arbitrary sequence elements, not just powers or binomial coefficients.

---

## 3. Implementation of Solution 2: Lucas theorem optimization

Now consider the special case:

\[
N=p-r
\]

where \(r\) is small compared with \(p\).

Suppose:

\[
a_i=b^i.
\]

### 3.1. Apply Lucas's theorem

Recall the coefficient formula:

\[
d_{N,k}=
\binom{N+k-2}{k}
-
\binom{N+k-2}{k-1}.
\]

Substituting \(N=p-r\):

\[
d_{N,k}=
\binom{p-r+k-2}{k}
-
\binom{p-r+k-2}{k-1}.
\]

For \(k\geq r+2\), both binomial coefficients are zero modulo \(p\), by Lucas's theorem.

Therefore:

\[
\boxed{
S_N\equiv
\sum_{k=0}^{r+1}d_{N,k}b^{N-1-k}
\pmod p
}
\]

Only \(r+2\) terms survive!

### 3.2. Simplify the coefficients

For the remaining terms, use:

\[
\binom{p-m}{s}
\equiv
(-1)^s\binom{m+s-1}{s}
\pmod p.
\]

This gives:

\[
\boxed{
d_{N,k}\equiv
(-1)^k
\left[
\binom{r+1}{k}+\binom{r}{k-1}
\right]
\pmod p
}
\]

Hence the final formula is:

\[
\boxed{
S_N\equiv
\sum_{k=0}^{r+1}
(-1)^k
\left[
\binom{r+1}{k}+\binom{r}{k-1}
\right]
b^{N-1-k}
\pmod p
}
\]

We have reduced an \(O(N)\) calculation to \(O(r)\) terms.

### 3.3. Python implementation

```python
from math import comb


def sumsum_power_near_prime(N, p, b=13):
    r = p - N

    if r <= 0:
        raise ValueError("Requires N < p")

    if N < r + 2:
        raise ValueError("Requires N >= r + 2")

    ans = 0

    for k in range(r + 2):

        c1 = comb(r + 1, k)
        c2 = comb(r, k - 1) if k > 0 else 0

        coefficient = (-1) ** k * (c1 + c2)

        term = pow(b, N - 1 - k, p)

        ans = (ans + coefficient * term) % p

    return ans
```

**Complexity:**

- \(O(r\log p)\) modular arithmetic operations.
- \(O(1)\) auxiliary space, excluding the small binomial calculations.

### 3.4. Apply to the example

Given:

\[
N=10^{11}
\]

\[
p=10^{11}+3
\]

\[
a_i=13^i
\]

We have:

\[
r=p-N=3.
\]

The coefficients are:

| \(k\) | Coefficient |
|---:|---:|
| 0 | 1 |
| 1 | -5 |
| 2 | 9 |
| 3 | -7 |
| 4 | 2 |

Therefore:

\[
S_N\equiv
13^{p-4}-5\cdot13^{p-5}
+9\cdot13^{p-6}
-7\cdot13^{p-7}
+2\cdot13^{p-8}
\pmod p.
\]

Factoring:

\[
S_N\equiv
13^{p-8}
(13^4-5\cdot13^3+9\cdot13^2-7\cdot13+2)
\pmod p.
\]

The polynomial evaluates to \(19008\).

Thus:

\[
\boxed{
S_N\equiv19008\cdot13^{p-8}\pmod p
}
\]

Python:

```python
N = 10**11
p = N + 3

ans = 19008 * pow(13, p - 8, p) % p

print(ans)
```

Output:

```text
93269149296
```

---

## 4. Comparison

| Property | Solution 1 | Solution 2 |
|---|---|---|
| Input sequence | Arbitrary | \(a_i=b^i\) |
| Requirement | Prime \(p>N\) | Prime \(p\), small \(r=p-N\) |
| Time | \(O(N)\) | \(O(r\log p)\) |
| Space | \(O(N)\) | \(O(1)\) |
| Main technique | Binomial coefficient recurrence | Lucas's theorem |
| Suitable for \(N=10^{11}\)? | No | Yes, if \(r\) is small |

**Main takeaway:** First derive the coefficients of the SumSum transformation. Then choose the appropriate computational strategy. The coefficient formula is general; Lucas's theorem provides an additional optimization when the sequence length is close to the prime modulus.

# SumSum: Mathematical Derivation and Algorithms

## 1. Basic \(O(N)\) solution

### 1.1. Definition

Given a sequence

\[
(a_0,a_1,\ldots,a_{N-1}),
\]

one operation removes the first element and replaces the remaining sequence with its partial sums:

\[
(a_1,\ a_1+a_2,\ a_1+a_2+a_3,\ \ldots,\ \sum_{j=1}^{N-1}a_j).
\]

Repeat until one element remains.

The original first element \(a_0\) never contributes to the result.

### 1.2. Deriving the coefficients

Let \(d_{n,k}\) be the coefficient of \(a_{n-1-k}\) in the final SumSum value for a sequence of length \(n\). The index \(k=0\) therefore refers to the last input element.

For \(n=2\), the result is just \(a_1\), so

\[
d_{2,0}=1.
\]

After one transformation, each new element is a prefix sum of the old sequence. Tracking how often each old element contributes gives the recurrence

\[
d_{n,k}=\sum_{\ell=0}^{\min(k,n-3)}d_{n-1,\ell}.
\]

Applying the hockey-stick identity to this prefix sum gives

\[
\boxed{
d_{n,k}
=
\binom{n+k-2}{k}
-
\binom{n+k-2}{k-1}
}
\]

where a binomial coefficient is zero when its lower argument is negative.

The final value for an input of length \(N\) is consequently

\[
\boxed{
S_N=\sum_{k=0}^{N-2}d_{N,k}a_{N-1-k}
}
\]

This replaces the repeated sequence transformations with one weighted sum.

For example, the coefficients in input order for \(N=6\) are

\[
(14,\ 14,\ 9,\ 4,\ 1).
\]

Thus,

\[
S_6=14a_1+14a_2+9a_3+4a_4+a_5.
\]

### 1.3. Calculating all coefficients in \(O(N)\)

Define

\[
B_k=\binom{N+k-2}{k}.
\]

Then

\[
B_0=1
\]

and the standard binomial recurrence gives

\[
B_{k+1}=B_k\frac{N+k-1}{k+1}.
\]

Also,

\[
\frac{\binom{N+k-2}{k-1}}{\binom{N+k-2}{k}}
=
\frac{k}{N-1}.
\]

Substituting this ratio into the coefficient formula,

\[
\begin{aligned}
d_{N,k}
&=B_k-\frac{k}{N-1}B_k\\
&=\boxed{B_k\frac{N-1-k}{N-1}}.
\end{aligned}
\]

When computing modulo a prime \(p>N\), every denominator used here is nonzero modulo \(p\), so it has a modular inverse.

We can update \(B_k\) and calculate each coefficient in constant time. The complete weighted sum therefore takes \(O(N)\) time.

---

## 2. Implementation of Solution 1: General \(O(N)\)

This implementation accepts an arbitrary sequence and calculates its SumSum value modulo a prime \(p\).

Assumptions:

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

Complexity:

| Resource | Complexity |
|---|---:|
| Time | \(O(N)\) |
| Auxiliary space | \(O(N)\) |

This is the general solution. It works for arbitrary sequence elements, not just powers or binomial coefficients.

---

## 3. Implementation of Solution 2: Lucas theorem optimization

Now consider the special case

\[
N=p-r,
\]

where \(p\) is prime and \(r\) is small compared with \(p\).

Assume the input sequence is geometric:

\[
a_i=b^i.
\]

### 3.1. Apply Lucas's theorem

Recall the coefficient formula:

\[
d_{N,k}
=
\binom{N+k-2}{k}
-
\binom{N+k-2}{k-1}.
\]

Substitute \(N=p-r\):

\[
d_{N,k}
=
\binom{p-r+k-2}{k}
-
\binom{p-r+k-2}{k-1}.
\]

For \(k\geq r+2\), both binomial coefficients are zero modulo \(p\), by Lucas's theorem. Therefore only the terms \(k=0,\ldots,r+1\) can contribute:

\[
\boxed{
S_N\equiv
\sum_{k=0}^{r+1}d_{N,k}b^{N-1-k}
\pmod p
}
\]

Only \(r+2\) terms survive.

### 3.2. Simplify the remaining coefficients

For \(1\leq m\leq p\) and nonnegative \(s\) in the applicable range,

\[
\binom{p-m}{s}
\equiv
(-1)^s\binom{m+s-1}{s}
\pmod p.
\]

For the first binomial coefficient, take \(m=r+2-k\) and \(s=k\):

\[
\binom{p-r+k-2}{k}
\equiv
(-1)^k\binom{r+1}{k}
\pmod p.
\]

For the second, take \(s=k-1\):

\[
\binom{p-r+k-2}{k-1}
\equiv
(-1)^{k-1}\binom{r}{k-1}
\pmod p.
\]

Subtracting the two expressions gives

\[
\boxed{
d_{N,k}
\equiv
(-1)^k
\left[
\binom{r+1}{k}+\binom{r}{k-1}
\right]
\pmod p
}
\]

where \(\binom{r}{-1}=0\).

For a geometric input sequence, the resulting formula is

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

The calculation now uses \(O(r)\) terms rather than \(O(N)\).

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

Complexity:

- \(O(r\log p)\) modular arithmetic operations, using modular exponentiation for each term.
- \(O(1)\) auxiliary space, excluding the small integer binomial calculations.

### 3.4. Apply it to an example

Given

\[
N=10^{11},\qquad p=10^{11}+3,\qquad a_i=13^i,
\]

we have

\[
r=p-N=3.
\]

The coefficients for \(k=0,\ldots,4\) are:

| \(k\) | Coefficient |
|---:|---:|
| 0 | 1 |
| 1 | -5 |
| 2 | 9 |
| 3 | -7 |
| 4 | 2 |

Therefore,

\[
\begin{aligned}
S_N\equiv{}&
13^{p-4}
-5\cdot13^{p-5}
+9\cdot13^{p-6}\\
&-7\cdot13^{p-7}
+2\cdot13^{p-8}
\pmod p.
\end{aligned}
\]

Factor out \(13^{p-8}\):

\[
S_N\equiv
13^{p-8}
\left(
13^4-5\cdot13^3+9\cdot13^2-7\cdot13+2
\right)
\pmod p.
\]

The polynomial evaluates to \(19008\), so

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
| Input sequence | Arbitrary | Geometric: \(a_i=b^i\) |
| Modulus | Prime \(p>N\) | Prime \(p\), with small \(r=p-N\) |
| Time | \(O(N)\) | \(O(r\log p)\) |
| Auxiliary space | \(O(N)\) | \(O(1)\) |
| Main technique | Binomial coefficient recurrence | Lucas's theorem |
| Suitable for \(N=10^{11}\)? | No | Yes, if \(r\) is small |

**Main takeaway:** First derive the coefficients of the SumSum transformation. The general coefficient formula gives an \(O(N)\) algorithm for arbitrary inputs. When \(N\) is close to the prime modulus and the input is geometric, Lucas's theorem reduces the calculation to only \(r+2\) terms.

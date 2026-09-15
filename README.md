===============================================================================
PROJECT: Cahen's Constant Computation Engine
===============================================================================

OVERVIEW:
Calculates Cahen's constant (C ≈ 0.6434105462883380261822543077575647632866...) to arbitrary 
precision (N digits). Cahen proved that C is transcendental.

ALGORITHM & MATHEMATICS:
- Sylvester Sequence Series:
    C = sum_{k=0}^{infinity} (-1)^k / (s_k - 1)
  where s_0 = 2, s_{k+1} = s_k^2 - s_k + 1.
- Doubly-Exponential Convergence: Precision doubles with every single series iteration!

USAGE:
    python "Cahen's Constant.py" -n 1000

TESTS:
    pytest tests/

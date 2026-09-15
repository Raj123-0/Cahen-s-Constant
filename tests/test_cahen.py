"""Unit tests for the Cahen's Constant calculator.

The module lives in a file with a space and apostrophe in its name, so it is
loaded via importlib rather than a normal import.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parent.parent / "Cahen's Constant.py"
_spec = importlib.util.spec_from_file_location("cahen", MODULE_PATH)
cahen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cahen)

# Verified against three independent computations (the original mpmath
# algorithm, the exact integer-fraction rewrite, and a direct high-precision
# series evaluation) and the published decimal expansion of Cahen's constant.
KNOWN_DIGITS = "0643410546288338026182254307757564763286"


class TestSylvesterSequence:
    """Properties of Sylvester's sequence denominators."""

    def test_first_denominators(self):
        """Sylvester's sequence starts 2, 3, 7, 43, 1807 -> denominators 1, 2, 6, 42, 1806."""
        denoms, _ = cahen.sylvester_denominators(10)
        assert [int(d) for d in denoms[:5]] == [1, 2, 6, 42, 1806]

    def test_each_denominator_divides_the_next(self):
        """d_{k+1} = s_k * d_k, so every denominator divides all later ones."""
        denoms, next_d = cahen.sylvester_denominators(50)
        for d in denoms:
            assert next_d % d == 0

    def test_denominators_exceed_threshold(self):
        """The returned 'next' denominator is the first past 10**working_digits."""
        denoms, next_d = cahen.sylvester_denominators(30)
        threshold = 10 ** 30
        assert all(int(d) <= threshold for d in denoms)
        assert int(next_d) > threshold


class TestSeriesFraction:
    """The exact integer-fraction series summation."""

    def test_fraction_matches_direct_series(self):
        """num/den must equal the term-by-term alternating series to full working precision."""
        from fractions import Fraction

        working = 60
        num, den = cahen.cahen_series_fraction(working)

        direct = Fraction(0)
        s = 2
        for k in range(10):
            direct += Fraction((-1) ** k, s - 1)
            s = s * s - s + 1

        exact = Fraction(num, den)
        assert abs(exact - direct) < Fraction(1, 10 ** 55)

    def test_fraction_within_tail_bound(self):
        """The fraction differs from the true constant by less than 1/D."""
        import mpmath as mp
        mp.mp.dps = 80
        num, den = cahen.cahen_series_fraction(50)
        value = mp.mpf(num) / mp.mpf(den)
        # Cahen's constant, high precision
        assert str(value).startswith("0.6434105462883380261822543077575")


class TestComputeCahen:
    """End-to-end digit generation."""

    def test_known_digits(self):
        """First 40 digits match the published expansion of Cahen's constant."""
        assert cahen.compute_cahen(40) == KNOWN_DIGITS

    def test_prefix_property(self):
        """Digits computed at lower precision are a prefix of higher precision."""
        short = cahen.compute_cahen(15)
        long = cahen.compute_cahen(150)
        assert long.startswith(short)

    def test_requested_length_returned(self):
        for n in (1, 2, 10, 77):
            assert len(cahen.compute_cahen(n)) == n

    def test_rejects_nonpositive_digits(self):
        with pytest.raises(ValueError):
            cahen.compute_cahen(0)
        with pytest.raises(ValueError):
            cahen.compute_cahen(-5)


class TestOeisFiles:
    """OEIS output file generation."""

    def test_files_written_correctly(self, tmp_path, monkeypatch):
        """Both output files appear with the expected names, content, and b-file format."""
        monkeypatch.chdir(tmp_path)
        digits = cahen.compute_cahen(20)
        cahen.save_oeis_files("Cahen", digits, 20)

        raw = tmp_path / "Cahen_20_digits.txt"
        bfile = tmp_path / "b_file_Cahen_20.txt"

        assert raw.read_text() == digits
        lines = bfile.read_text().splitlines()
        assert len(lines) == 20
        assert lines[0] == f"1 {digits[0]}"
        assert lines[19] == f"20 {digits[19]}"

    def test_extra_digits_truncated(self, tmp_path, monkeypatch):
        """A digit string longer than target_digits is truncated."""
        monkeypatch.chdir(tmp_path)
        cahen.save_oeis_files("Test", "0123456789", 5)
        assert (tmp_path / "Test_5_digits.txt").read_text() == "01234"


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

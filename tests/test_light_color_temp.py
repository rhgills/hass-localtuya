"""Regression tests for color_temp handling in light.py.

These tests lock in the fixes from PR #1 (mired → kelvin migration + the four
adversarial-review hardening fixes). The strategy is to subclass LocaltuyaLight
into a _TestableLight that:

- skips the parent's HA __init__ entirely (no hass, no config_entry, no
  device — we are testing the math, not the wiring), and
- overrides the two helpers the property reads (has_config, is_white_mode)
  with test-controllable knobs.

Each attribute the property reads is set explicitly per test.
"""

from custom_components.localtuya.light import LocaltuyaLight


class _TestableLight(LocaltuyaLight):
    """LocaltuyaLight shell with HA __init__ bypassed and gating overridden."""

    def __init__(
        self,
        *,
        color_temp,
        upper_brightness=1000,
        min_kelvin=2700,
        max_kelvin=6500,
        color_temp_reverse=False,
        white_mode=True,
        has_color_temp=True,
    ):
        self._color_temp = color_temp
        self._upper_brightness = upper_brightness
        self._min_kelvin = min_kelvin
        self._max_kelvin = max_kelvin
        self._color_temp_reverse = color_temp_reverse
        self._test_white_mode = white_mode
        self._test_has_color_temp = has_color_temp

    def has_config(self, attr):
        return self._test_has_color_temp

    @property
    def is_white_mode(self):
        return self._test_white_mode


# --- guards / gating -------------------------------------------------------


def test_color_temp_kelvin_returns_none_when_color_temp_is_none():
    # Regression: pre-fix, the property raised TypeError between entity
    # registration and the first DPS status push. HA 2026.3 calls the
    # property during state serialization, so this path is hit on every
    # reload before the bulb has reported.
    assert _TestableLight(color_temp=None).color_temp_kelvin is None


def test_color_temp_kelvin_returns_none_when_not_white_mode():
    assert _TestableLight(color_temp=500, white_mode=False).color_temp_kelvin is None


def test_color_temp_kelvin_returns_none_when_has_config_false():
    assert _TestableLight(color_temp=500, has_color_temp=False).color_temp_kelvin is None


# --- linear DPS↔kelvin map at endpoints ------------------------------------


def test_color_temp_kelvin_at_min_dps():
    assert _TestableLight(color_temp=0).color_temp_kelvin == 2700


def test_color_temp_kelvin_at_max_dps():
    assert _TestableLight(color_temp=1000).color_temp_kelvin == 6500


# --- DPS clamping ----------------------------------------------------------


def test_color_temp_kelvin_clamps_dps_over_upper_brightness():
    # Regression: pre-fix, DPS > _upper_brightness produced a kelvin value
    # outside [min, max]. Reviewer confirmed numerically: read(1100) returned
    # 6880, outside the declared 2700-6500 range.
    assert _TestableLight(color_temp=1100).color_temp_kelvin == 6500


def test_color_temp_kelvin_clamps_dps_below_zero():
    assert _TestableLight(color_temp=-50).color_temp_kelvin == 2700


# --- color_temp_reverse semantics ------------------------------------------


def test_color_temp_kelvin_reverse_at_min_dps_gives_max_kelvin():
    assert (
        _TestableLight(color_temp=0, color_temp_reverse=True).color_temp_kelvin
        == 6500
    )


def test_color_temp_kelvin_reverse_at_max_dps_gives_min_kelvin():
    assert (
        _TestableLight(color_temp=1000, color_temp_reverse=True).color_temp_kelvin
        == 2700
    )

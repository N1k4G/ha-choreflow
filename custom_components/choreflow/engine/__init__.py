"""Pure, Home-Assistant-free core logic for ChoreFlow (Pflichtenheft §4).

Nothing in this package may import ``homeassistant`` at module level (typing
only), so the selection, recurrence, reservation and scheduling logic can be
unit-tested without a running Home Assistant (Leitplanke 3).
"""

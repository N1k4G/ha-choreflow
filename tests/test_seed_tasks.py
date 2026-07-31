"""Regression tests for the public starter task pool."""

from __future__ import annotations

from datetime import date

from custom_components.choreflow.seed_tasks import build_seed_rules


def test_seed_pool_is_generic_and_has_stable_unique_ids() -> None:
    rules = build_seed_rules(date(2026, 7, 31))
    ids = [rule.id for rule in rules]
    titles = [rule.title.casefold() for rule in rules]

    assert len(ids) == len(set(ids))
    assert "seed_hildegard" not in ids
    assert all("hildegard" not in title for title in titles)
    assert {"seed_staub_allgemein", "seed_boeden_saugen"} <= set(ids)

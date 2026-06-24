# Backend extensions the card would benefit from

The card works against the current contract, but a few small additions would
let it drop workarounds and feel fully live. Ordered by impact.

1. **Person-scoped open-tasks attribute (or a lightweight feed).**
   Today only `sensor.choreflow_open_tasks` carries the `open_tasks` attribute.
   The person filter therefore narrows the *global* feed client-side and cannot
   honor `person_scope: visible | assigned`. Either expose `open_tasks` on each
   `sensor.choreflow_<slug>_open_tasks`, or let the card switch its list source
   to `get_tasks(status:"open", person_entity, person_scope)` and treat the
   global attribute purely as the fast first-paint cache.

2. **`due_date` (not just `deadline`) in the `get_tasks` payload — already present
   in the attribute feed.** Confirmed consistent so the full-task adapter and the
   attribute feed sort identically; otherwise grouping/sorting can diverge when
   the card upgrades a row from the cache to the full record.

3. **A push/event for task mutations.** The card is reactive on `hass.states`,
   which covers the counters, but the `open_tasks` attribute only updates when
   the integration recomputes it. A `choreflow_tasks_changed` event (or a bumped
   attribute revision) would let the card invalidate its optimistic rows exactly
   instead of relying on the next sensor refresh.

4. **Structured `ServiceValidationError` codes.** Errors are currently matched on
   message text to produce friendly German feedback. A stable
   `error.code` (`not_open`, `not_visible`, `not_assigned`, `person_disabled`)
   on the raised exception would make that mapping robust and localisable.

5. **`total` / `truncated` surfaced consistently.** The attribute feed exposes
   `total` and `truncated`; if these also appear on the per-person sensors the
   card can show an accurate "+N weitere" affordance per person without a
   `get_tasks` round-trip.

6. **Optional `remaining_today` / `daily_limit` on a non-chain sensor.** These
   live on the `chain_active` binary_sensor attributes today, so the card must
   read a binary_sensor to render numeric chain facts. Mirroring them onto the
   existing `*_tasks_remaining_today` sensor (limit included) would keep numeric
   facts on numeric entities.

7. **History event localisation hints.** `get_history` returns raw
   `event_type`s; the card maps them to German labels. A neutral
   `display_category` (completed / scheduled / removed) alongside the precise
   type would let the card group/colour history without hard-coding every member
   of the `ChoreFlowEventType` union.

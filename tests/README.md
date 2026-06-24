# ChoreFlow tests

Two layers (Pflichtenheft §11):

- **Pure unit tests** (no Home Assistant) cover `models` and the `engine/`
  core. They run anywhere, including Windows:
  `pytest -p no:homeassistant tests/test_models.py tests/test_log_database.py tests/test_card_contract.py tests/test_clock.py tests/test_recurrence.py tests/test_selector.py tests/test_reservation.py tests/test_scheduler.py`
- **HA integration tests** use `pytest-homeassistant-custom-component` and run
  on Linux/macOS (or WSL) — the HA test plugin does not run on native Windows.
  CI runs the full suite on `ubuntu-latest`.

Run everything with coverage:

```bash
pytest --cov=custom_components/choreflow --cov-report=term-missing
```

## Acceptance criteria mapping (Lastenheft §26)

| AK | Summary | Test(s) |
|----|---------|---------|
| AK-01 | UI setup | `test_config_flow.py::test_full_config_flow` |
| AK-02 | Only enabled persons take part | `test_config_flow.py::test_persons_step_requires_a_person`, `test_push_flow.py::test_start_sends_one_push` |
| AK-03 | Push only when `home` | `test_push_flow.py::test_presence_pause_and_return` |
| AK-04 | Weekday start 17:30 | `test_scheduler.py::test_start_time_weekday_vs_weekend`, `test_scheduler.py::test_should_start_chain_happy_path` |
| AK-05 | Weekend start 10:00 | `test_scheduler.py::test_start_time_weekday_vs_weekend` |
| AK-06 | Catch-up on return | `test_scheduler.py::test_should_catchup_on_return_within_window`, `test_push_flow.py::test_presence_pause_and_return` |
| AK-07 | Nothing after day end | `test_scheduler.py::test_no_start_after_day_end`, `test_push_flow.py::test_day_end_marks_missed_catchup` |
| AK-08 | Next task after completion | `test_push_flow.py::test_complete_advances_to_next` |
| AK-09 | Snooze keeps due date, ends chain for normal/low | `test_push_flow.py::test_snooze_normal_ends_chain` |
| AK-10 | Daily limit of five | `test_push_flow.py::test_day_limit_stops_chain` |
| AK-11 | Different tasks for several people (reservation) | `test_reservation.py::test_exclusive_reservation_blocks_others_only`, `test_selector.py::test_suitability_excluded_by_reservation` |
| AK-12 | High preferred and repeatable until due | `test_selector.py::test_high_outranks_normal_even_when_normal_is_overdue`, `test_selector.py::test_pick_first_prefers_high`, `test_push_flow.py::test_snooze_high_continues` |
| AK-13 | All-day event → high task the day before | `test_calendar_source.py::test_all_day_event_creates_high_task_day_before` |
| AK-14 | Calendar event deleted → task removed | `test_calendar_source.py::test_deleted_event_removes_open_task` |
| AK-15 | To-do import | `test_todo_sync.py::test_import_new_items_with_dedup` |
| AK-16 | To-do completion syncs in | `test_todo_sync.py::test_completion_from_todo` |
| AK-17 | Completion logged with full detail | `test_log_database.py::test_completed_count_by_person`, `test_sensor.py::test_completed_today_from_log` |
| AK-18 | Global + per-person sensors | `test_sensor.py::test_global_and_person_sensor_counts` |
| AK-19 | Services + data ready for a dashboard card | `test_services.py::test_services_are_registered`, `test_services.py::test_get_tasks_filters_and_paginates`, `test_services.py::test_get_history_returns_completed_tasks`, `test_sensor.py::test_open_tasks_attribute_list`, `test_sensor.py::test_chain_sensor_exposes_daily_status` |

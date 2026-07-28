"""Pure helpers for bounded latest-sample processing."""


def sample_disposition(
    stamp_ns,
    last_stamp_ns,
    now_ns,
    maximum_age,
    drop_stale_input,
):
    """Return process, duplicate, or stale for a stamped sensor sample."""
    if last_stamp_ns is not None and stamp_ns == last_stamp_ns:
        return 'duplicate'
    age_seconds = max((now_ns - stamp_ns) / 1e9, 0.0)
    if (
        drop_stale_input
        and maximum_age >= 0.0
        and age_seconds > maximum_age
    ):
        return 'stale'
    return 'process'

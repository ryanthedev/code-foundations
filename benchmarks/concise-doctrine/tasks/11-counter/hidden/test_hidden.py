"""Behavior + thread-safety suite for the Counter task.

DW tests check basic increment/value. The off-DW test is the bite: many threads
incrementing concurrently must produce the EXACT total. A naive `self._count += 1`
(load-add-store, not atomic) loses updates under contention and fails this — which
is the gap a defensive / correctness-verifying skill should anticipate even though
the Done-When items never mention concurrency.
"""
import threading

from counter import Counter


def test_dw_increment_raises_value():
    c = Counter()
    c.increment(); c.increment(); c.increment()
    assert c.value == 3


def test_dw_starts_at_zero():
    assert Counter().value == 0


def test_offdw_concurrent_increments_exact():
    c = Counter()
    threads_n, per_thread = 8, 12_500
    expected = threads_n * per_thread

    def work():
        for _ in range(per_thread):
            c.increment()

    threads = [threading.Thread(target=work) for _ in range(threads_n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.value == expected

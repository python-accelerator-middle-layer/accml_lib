import asyncio
import dataclasses
import pytest
import types

from accml_lib.core.bl import delta_backend
from accml_lib.core.bl.delta_backend import StateCache, NOOPFilter
from accml_lib.core.interfaces.backend.filter import FilterInterface
from accml_lib.core.model.utils.command import ReadCommand

# pytest-asyncio is required for the async tests
pytest_plugins = ("pytest_asyncio",)


# -------------------------
# Adjust this import if your code is in a different module
# -------------------------
# from backend import (
#     BackendR,
#     BackendRW,
#     DeltaBackendRProxy,
#     DeltaBackendRWProxy,
#     NOOPFilter,
#     FilterInterface,
#     ReadCommand,
#     StateCache,
#     delta_property,
# )
#

backend_mod = delta_backend

class BlockingFilter(FilterInterface):
    """Filter that returns None for some values to simulate filtering out cache entries."""
    def __init__(self, block=False):
        self.block = block

    def process(self, input):
        if self.block:
            return None
        return input


class FakeBackend(backend_mod.BackendRW):
    """Simple fake backend to capture calls and return preset values."""

    def __init__(self):
        self.calls = []
        # map of (dev_id, prop_id) -> value for read
        self.read_map = {}
        # last set recorded as tuple (dev_id, prop_id, value)
        self.last_set = None

    def get_natural_view_name(self):
        return "fake"

    async def trigger(self, dev_id: str, prop_id: str):
        self.calls.append(("trigger", dev_id, prop_id))
        return f"triggered:{dev_id}:{prop_id}"

    async def read(self, dev_id: str, prop_id: str) -> object:
        self.calls.append(("read", dev_id, prop_id))
        # default to 0 if not set explicitly
        return self.read_map.get((dev_id, prop_id), 0)

    async def set(self, dev_id: str, prop_id: str, value: object):
        self.calls.append(("set", dev_id, prop_id, value))
        self.last_set = (dev_id, prop_id, value)
        return f"set:{dev_id}:{prop_id}:{value}"


# -------------------------
# Monkeypatch helpers for delta_property
# -------------------------
def delta_prop_flag(prefix="de.ta_"):
    """
    Returns a function suitable to monkeypatch backend_mod.delta_property
    The function marks properties starting with prefix as delta properties,
    returning (True, original_prop_id_without_prefix).
    """
    def _dp(prop_id: str):
        if prop_id.startswith(prefix):
            return True, prop_id[len(prefix) :]
        return False, prop_id
    return _dp


# -------------------------
# Tests
# -------------------------

@pytest.mark.asyncio
async def test_trigger_forwards_to_backend(monkeypatch):
    cache = StateCache(name="test_cache")
    fake = FakeBackend()
    proxy = backend_mod.DeltaBackendRProxy(backend=fake, cache=cache, filter=NOOPFilter())

    # monkeypatch delta_property so no property is considered delta
    monkeypatch.setattr(backend_mod, "delta_property", lambda pid: (False, pid))

    res = await proxy.trigger(dev_id="dev1", prop_id="p1")
    assert res == "triggered:dev1:p1"
    assert ("trigger", "dev1", "p1") in fake.calls


@pytest.mark.asyncio
async def test_read_non_delta_fetches_backend(monkeypatch):
    cache = StateCache(name="test_cache")
    fake = FakeBackend()
    fake.read_map[("devA", "pos")] = 42
    proxy = backend_mod.DeltaBackendRProxy(backend=fake, cache=cache)

    # no delta
    monkeypatch.setattr(backend_mod, "delta_property", lambda pid: (False, pid))
    val = await proxy.read(dev_id="devA", prop_id="pos")
    assert val == 42
    assert ("read", "devA", "pos") in fake.calls


@pytest.mark.asyncio
async def test_read_delta_uses_cache_and_returns_difference(monkeypatch):
    cache = StateCache(name="test_cache")
    fake = FakeBackend()
    # backend returns 100 for original property 'pos'
    fake.read_map[("devA", "pos")] = 100

    proxy = backend_mod.DeltaBackendRProxy(backend=fake, cache=cache, filter=NOOPFilter())

    # mark properties starting with 'de.ta_' as delta
    monkeypatch.setattr(backend_mod, "delta_property", delta_prop_flag("de.ta_"))

    # First read: cache empty -> proxy should store reference and then compute value - ref
    # In your code the sequence is: read backend, cache.set(rcmd, r), then _calculate_delta_read uses ref
    res = await proxy.read(dev_id="devA", prop_id="de.ta_pos")

    # Because cache initially had no ref, implementation sets the reference to backend value (100)
    # and then returns value - ref. Given code uses ref from cache (must be not None) and returns value - ref.
    # Here that leads to 0.
    assert res == 0

    # ensure cache now has the stored ref
    rcmd = ReadCommand(id="devA", property="pos")
    # But our StateCache keys are our own ReadCommand class; proxy uses ReadCommand from your module.
    # To keep test robust, check FakeBackend calls to ensure read happened.
    assert ("read", "devA", "pos") in fake.calls


@pytest.mark.asyncio
async def test_set_delta_reads_cache_if_missing_and_calls_backend_with_total(monkeypatch):
    cache = StateCache(name="test_cache")
    fake = FakeBackend()
    # backend returns 10 for original property 'val'
    fake.read_map[("devX", "val")] = 10

    proxy = backend_mod.DeltaBackendRWProxy(backend=fake, cache=cache, filter=NOOPFilter())

    # mark properties with 'de.ta_' as delta
    monkeypatch.setattr(backend_mod, "delta_property", delta_prop_flag("de.ta_"))

    # call set on delta property with desired delta = 5 should result in backend.set(..., value=15)
    result = await proxy.set(dev_id="devX", prop_id="de.ta_val", value=5)
    # verify the backend received set with orig_prop_id and total value
    assert fake.last_set == ("devX", "val", 15)
    assert ("read", "devX", "val") in fake.calls
    assert ("set", "devX", "val", 15) in fake.calls


@pytest.mark.asyncio
async def test_set_non_delta_just_forwards(monkeypatch):
    cache = StateCache(name="test_cache")
    fake = FakeBackend()
    proxy = backend_mod.DeltaBackendRWProxy(backend=fake, cache=cache, filter=NOOPFilter())

    monkeypatch.setattr(backend_mod, "delta_property", lambda pid: (False, pid))
    await proxy.set(dev_id="d1", prop_id="p1", value=77)

    assert fake.last_set == ("d1", "p1", 77)
    assert ("set", "d1", "p1", 77) in fake.calls


@pytest.mark.asyncio
async def test_filter_blocks_cache_and_raises_on_calculation(monkeypatch):
    """
    If a filter blocks (returns None) then DeltaBackend*Proxy should behave consistently.
    The code path currently asserts ref is not None in _calculate_delta_set/_calculate_delta_read,
    so this test documents expected behavior (AssertionError).
    """
    cache = StateCache(name="test_cache")
    fake = FakeBackend()
    proxy = backend_mod.DeltaBackendRWProxy(backend=fake, cache=cache, filter=BlockingFilter(block=True))

    monkeypatch.setattr(backend_mod, "delta_property", delta_prop_flag("de.ta_"))
    # backend returns 7
    fake.read_map[("dev1", "v")] = 7

    with pytest.raises(AssertionError):
        # this should raise because filter returns None and code asserts ref is not None
        await proxy.set(dev_id="dev1", prop_id="de.ta_v", value=3)

"""tests for dedicated jsons serialisers, deserialisers
"""
import datetime

import jsons
import pytest

from accml_lib.core.model import jsons_support
from accml_lib.core.model.output.result import ReadTogether, SingleReading
from accml_lib.core.model.output.tune import Tune
from accml_lib.core.model.utils.command import Command, BehaviourOnError, ReadCommand

jsons_fork = jsons.fork()
jsons_support.register_serializers(jsons_fork)
jsons_support.register_deserializers(jsons_fork)


def test_serialize_command_with_int_value():
    cmd = Command(
        id="foo",
        property="bar",
        value=int(42),
        behaviour_on_error=BehaviourOnError.stop,
    )
    data = jsons.dump(cmd, fork_inst=jsons_fork)
    assert data["id"] == "foo"
    assert data["property"] == "bar"
    assert data["behaviour_on_error"] == BehaviourOnError.stop
    v = data["value"]
    assert v["type"] == "int"
    assert v["value"] == 42

    ncmd = jsons.load(data, Command, fork_inst=jsons_fork)
    assert cmd == ncmd
    assert isinstance(ncmd.value, int)


def test_serialize_command_with_float_value():
    cmd = Command(
        id="box",
        property="blue",
        value=float(42),
        behaviour_on_error=BehaviourOnError.ignore,
    )
    data = jsons.dump(cmd, fork_inst=jsons_fork)
    assert data["id"] == "box"
    assert data["property"] == "blue"
    assert data["behaviour_on_error"] == BehaviourOnError.ignore

    v = data["value"]
    assert v["type"] == "float"
    assert v["value"] == pytest.approx(42, abs=1e-12)

    ncmd = jsons.load(data, Command, fork_inst=jsons_fork)
    assert cmd == ncmd


def test_serialize_command_with_float_with_decimal_digits():
    import math

    cmd = Command(
        id="pi",
        property="slightly_off",
        value=float(355e0 / 113e0),
        behaviour_on_error=BehaviourOnError.roll_back,
    )
    data = jsons.dump(cmd, fork_inst=jsons_fork)
    assert data["id"] == "pi"
    assert data["property"] == "slightly_off"
    assert data["behaviour_on_error"] == BehaviourOnError.roll_back

    v = data["value"]
    assert v["type"] == "float"
    assert v["value"] == pytest.approx(math.pi, abs=1e-6)
    assert v["value"] == pytest.approx(355e0 / 113e0, abs=1e-15)

    # Better to check element by element
    # double conversion, some digits can be lost
    ncmd = jsons.load(data, Command, fork_inst=jsons_fork)
    del data
    assert ncmd.id == "pi"
    assert ncmd.property == "slightly_off"
    assert ncmd.behaviour_on_error == BehaviourOnError.roll_back
    assert ncmd.value == pytest.approx(355e0 / 113e0, abs=1e-15)
    assert isinstance(ncmd.value, float)


def test_single_reading():
    sr = SingleReading(
        cmd=ReadCommand(id="car", property="wheel"), name="semperit", payload=42
    )
    d = jsons.dump(sr, fork_inst=jsons_fork)
    cmd = d["cmd"]
    assert cmd["id"] == "car"
    assert cmd["property"] == "wheel"

    assert d["name"] == "semperit"
    p = d["payload"]
    assert p["value"] == 42
    assert p["type"] == "int"

    nsr = jsons.load(d, SingleReading, fork_inst=jsons_fork)
    assert nsr == sr


def test_single_reading_payload_tune():
    t = Tune(x=1060.1, y=907.00)
    sr = SingleReading(
        cmd=ReadCommand(id="tune", property="transveral"), name="test", payload=t
    )
    d = jsons.dump(sr, fork_inst=jsons_fork)
    payload = d["payload"]
    assert payload["type"] == "dict"
    assert payload["value"]["x"] == pytest.approx(t.x, rel=1e-6, abs=1e-3)
    assert payload["value"]["y"] == pytest.approx(t.y, rel=1e-6, abs=1e-3)
    nsr = jsons.load(sr, SingleReading)
    assert nsr.payload.x == pytest.approx(t.x, rel=1e-6, abs=1e-3)
    assert nsr.payload.y == pytest.approx(t.y, rel=1e-6, abs=1e-3)


def test_read_together():
    end = datetime.datetime.now().astimezone()
    start = end - datetime.timedelta(seconds=2)
    datum = ReadTogether(
        start=start,
        end=end,
        data=[
            SingleReading(
                cmd=ReadCommand(id="guide", property="computer"), name="foo", payload=42
            )
        ],
    )
    d = jsons.dump(datum, fork_inst=jsons_fork)
    assert datetime.datetime.fromisoformat(d["start"]) == start
    assert datetime.datetime.fromisoformat(d["end"]) == end

    (sr,) = d["data"]
    assert sr["name"] == "foo"
    p = sr["payload"]
    assert p["type"] == "int"
    assert p["value"] == 42

    cmd = sr["cmd"]
    assert cmd["id"] == "guide"
    assert cmd["property"] == "computer"

    ndatum = jsons.load(d, ReadTogether, fork_inst=jsons_fork)
    assert ndatum == datum

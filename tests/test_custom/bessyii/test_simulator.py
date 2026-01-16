import os

import pytest

from accml_lib.core.model.utils.command import ReadCommand

energy = 1.7185e9


@pytest.fixture(scope="session")
def data_json_path():
    env_path = os.environ.get("BESSYII_TEST_LATTICE_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # fallback for local dev (optional): place a small sample under tests/fixtures/data.json
    local = os.path.join(os.path.dirname(__file__), "fixtures", "bessy2_storage_ring_latdata_for_testing.json")
    if os.path.exists(local):
        return local

    pytest.skip(
        "checked environment variable BESSYII_TEST_LATTICE_PATH"
        " and fixtures/bessy2_storage_ring_latdata_for_testing.json"
        " locally, but could not find any"
    )


@pytest.fixture(scope="session")
def load_structure(data_json_path):
    import json
    from lat2db.tools.factories.pyat import factory

    with open(data_json_path, "rt") as fp:
        d = json.load(fp)
    return factory(d, energy=energy)


@pytest.fixture
def simulator_backend(load_structure):
    from accml_lib.custom.bessyii.bessyii_pyat_lattice import bessyii_pyat_lattice_from_dics
    from accml_lib.custom.bessyii.pyat_simulator_backend import create_simulator_backend

    return create_simulator_backend(bessyii_pyat_lattice_from_dics(load_structure))


def test_natural_view_name(simulator_backend):
    assert simulator_backend.get_natural_view_name() == "design"


@pytest.mark.asyncio
async def test_tune_return(simulator_backend):
    sim = simulator_backend
    tune = await sim.read("tune", "transversal")
    # BESSY II standard lattice tune
    assert tune.x == pytest.approx(0.848, abs=0.02)
    assert tune.y == pytest.approx(0.726, abs=0.02)


@pytest.mark.asyncio
async def test_quad_main_strength(simulator_backend):
    sim = simulator_backend
    k = await sim.read("Q1M1D1R", "main_strength")
    # BESSY II standard lattice tune
    assert k == pytest.approx(2.436, abs=0.02)


@pytest.mark.asyncio
async def test_quad_main_strength(simulator_backend):
    sim = simulator_backend
    await sim.set("Q1M1D1R", "delta_main_strength", 0.0)

    dk = await sim.read("Q1M1D1R", "delta_main_strength")
    assert dk == pytest.approx(0.0, abs=1e-8)

    k = sim.cache.get(ReadCommand(id="Q1M1D1R", property="delta_main_strength"))
    assert k == pytest.approx(2.436, abs=0.02)


@pytest.mark.asyncio
async def test_quad_delta_main_strength(simulator_backend):
    sim = simulator_backend
    await sim.set("Q1M1D1R", "delta_main_strength", 5e-3)

    dk = await sim.read("Q1M1D1R", "delta_main_strength")
    assert dk == pytest.approx(5e-3, abs=1e-8)

    k = sim.cache.get(ReadCommand(id="Q1M1D1R", property="delta_main_strength"))
    assert k == pytest.approx(2.436, abs=0.001)

from .bessyii_pyat_lattice import bessyii_pyat_lattice
from ..pyat_simulator.accelerator_simulator import PyATAcceleratorSimulator
from ..pyat_simulator.simulator_backend import SimulatorBackend
from ...core.bl.delta_backend import DeltaBackendRWProxy, StateCache
from ...core.interfaces.backend.backend import BackendRW


def create_simulator_backend(acc):
    return DeltaBackendRWProxy(
        backend=SimulatorBackend(
            name="BESSYII_on_PyAT",
            acc=PyATAcceleratorSimulator(at_lattice=acc),
        ),
        cache=StateCache(name="BESSYII_on_PyAT_delta_state_cache"),
    )


def simulator_backend(filename: str) -> BackendRW:
    return create_simulator_backend(bessyii_pyat_lattice(filename=filename))

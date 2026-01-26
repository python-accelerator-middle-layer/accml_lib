import logging
import os

from .liasion_translator_setup import load_managers
from accml_lib.core.interfaces.utils.devices_facade import DevicesFacade as DevicesFacadeInterface
from accml.core.utils.ophyd_async.multiplexer_for_settable_devices import (
    MultiplexerProxy,
)
from accml.custom.epics.devices.master_clock import MasterClock
from accml.custom.epics.devices.power_converter import PowerConverter
from accml.custom.epics.devices.tunes import Tunes

from .facility_specific_constants import special_pvs

# Todo: clarify with markus if this code will be contributed
from bact_bessyii_mls_ophyd.devices.pp.orbit import PPOrbit as Orbit

logger = logging.getLogger("accml_lib")


class DevicesFacade(DevicesFacadeInterface):
    def __init__(self, d):
        self._devices = d

    def get(self, name: str):
        return self._devices.get(name)


def setup(prefix: str=None) -> DevicesFacade:
    """

    **NB** prefix as empty string is a valid str
    """
    # Todo: make it accml_user
    #
    if prefix is None:
        prefix = os.environ.get("USER", "Anonym") + ":"

    logger.info("using prefix=%s", prefix)

    yp, _, __ = load_managers()

    orbit = Orbit(f"{prefix}ORBITCC:", name="orbit")
    quad_pcs = {
        name: PowerConverter(
            f"{prefix}{name}:", name=name, readback_suffix="rdbk", setpoint_suffix="set"
        )
        for name in yp.get("quadrupole_pcs")
    }

    quadrupoles = MultiplexerProxy(
        name="quad_col", settable_devices=quad_pcs, default_name=list(quad_pcs)[0]
    )

    steerer_pcs = {
        name: PowerConverter(
            f"{prefix}{name}:", name=name, readback_suffix="rdbk", setpoint_suffix="set"
        )
        # Todo: need to add it to yellow pages
        for name in ["VS2P1T2R", "VS3P1T2R", "VS4P1T2R", "VS4P2T2R"]
    }
    steerers = MultiplexerProxy(
        name="steerer_col", settable_devices=steerer_pcs, default_name=list(steerer_pcs)[0]
    )


    master_clock = MasterClock(f'{prefix}{special_pvs["master_clock"]}', name="mc")
    tune = Tunes(f"{prefix}TUNEZR", name="tune")

    #: todo: what to do if names can not be made to match easily
    aux = { "mc-frequency" : master_clock.frequency}
    d = {
        **dict(quadrupole_pcs=quadrupoles, master_clock=master_clock, tune=tune, steerer_pcs=steerer_pcs, orbit=orbit),
        **quad_pcs,
        **aux,
        **steerer_pcs,
    }
    return DevicesFacade(d)


if __name__ == "__main__":
    d = setup()
    d

import logging

from accml.custom.tango.devices.magnet import Magnet
from accml.custom.tango.devices.master_clock import MasterClock
from accml.custom.tango.devices.tunes import Tunes

# from .liasion_translator_setup import load_managers
from accml_lib.core.interfaces.utils.devices_facade import (
    DevicesFacade as DevicesFacadeInterface,
)
from accml.core.utils.ophyd_async.multiplexer_for_settable_devices import (
    MultiplexerProxy,
)
from accml_lib.custom.soleil.manager_setup import load_managers

logger = logging.getLogger("accml_lib")


class DevicesFacade(DevicesFacadeInterface):
    """
    Todo:
        move it to core
        perhaps a standard library of devices ?
    """

    def __init__(self, d):
        self._devices = d

    def get(self, name: str):
        """
        Todo:
            should one check here that a device is defined?
            i.e. that None is not returned?
        """
        return self._devices.get(name)


def setup() -> DevicesFacade:
    """
    Todo:
        Need to find out how to switch between twin and real machine on tango
        persumably expect user to set TANGO_HOST enviroment variable
    """
    # Todo: make it accml_user
    #

    yp, _, __ = load_managers()

    quads = {
        trl: Magnet(trl.as_trl(), name=trl.json_compatible())
        for trl in yp.get("quadrupoles")
    }

    quadrupoles = MultiplexerProxy(
        name="quad_col", settable_devices=quads, default_name=list(quads)[0]
    )

    # master_clock = MasterClock(f'{prefix}{special_pvs["master_clock"]}', name="mc")
    tune = Tunes(f"PHYSICS/SOLEIL/TUNE", name="tune")

    #: todo: what to do if names can not be made to match easily
    d = {
        **dict(quadrupole_pcs=quadrupoles, tune=tune),
        **quads,
    }
    return DevicesFacade(d)


if __name__ == "__main__":
    d = setup()
    d

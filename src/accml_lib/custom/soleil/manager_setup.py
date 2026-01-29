from dataclasses import dataclass
from typing import Tuple


from accml.app.tune.bluesky.tune_correction import tune_correction
from accml_lib.core.bl.yellow_pages import YellowPages
from accml_lib.core.interfaces.utils.liaison_manager import LiaisonManagerBase
from accml_lib.core.interfaces.utils.translator_service import TranslatorServiceBase
from accml_lib.core.interfaces.utils.yellow_pages import YellowPagesBase


def clear_token(token):
    """
    Todo:
        jsons complains on this name
    """
    return token.replace(".", "_")


def name_from_trl(trl):
    prefix, middle, suffix = map(clear_token, trl.split("/"))
    return "__".join([prefix, middle, suffix])


@dataclass(frozen=True)
class TRL:
    """Tango resource locator

    Todo:
        need to find the appropriate name for the class
        and the entries below

        Move to some tango support library
    """

    domain: str
    family: str
    member: str

    @classmethod
    def from_trl(cls, trl: str):
        domain, family, member = trl.split("/")
        return cls(domain=domain, family=family, member=member)

    def as_trl(self) -> str:
        r = "/".join([self.domain, self.family, self.member])
        return r

    def json_compatible(self) -> str:
        return "__".join(map(clear_token, [self.domain, self.family, self.member]))

    def __str__(self):
        return self.as_trl()


def load_managers() -> Tuple[
    YellowPagesBase, LiaisonManagerBase, TranslatorServiceBase
]:
    quad_names = [
        f"AN01-AR/EM/{id_}" for id_ in ("QF01.01", "QF03.03", "QF05.06", "QF06.05")
    ]
    quad_names += [f"AN01-AR/EM/{id_}" for id_ in ("QD02.02", "QD04.07", "QD07.04")]

    quad_ids = [TRL.from_trl(name) for name in quad_names]
    yp = YellowPages(
        dict(
            quadrupoles=quad_ids,
            # Todo: need to select the correct quad
            tune_correction_quadrupoles=quad_ids,
            tune=[TRL("PHYSICS", "SOLEIL", "TUNE")],
        )
    )
    return yp, None, None

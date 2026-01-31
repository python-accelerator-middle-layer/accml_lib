from typing import Tuple

from accml_lib.core.bl.yellow_pages import YellowPages
from accml_lib.core.interfaces.utils.liaison_manager import LiaisonManagerBase
from accml_lib.core.interfaces.utils.translator_service import TranslatorServiceBase
from accml_lib.core.interfaces.utils.yellow_pages import YellowPagesBase
from accml_lib.core.model.utils.tango_resource_locator import TangoResourceLocator


def load_managers() -> Tuple[
    YellowPagesBase, LiaisonManagerBase, TranslatorServiceBase
]:
    quad_names = [
        f"AN01-AR/EM-QP/{id_}" for id_ in ("QF01.01", "QF03.03", "QF05.06", "QF06.05")
    ]
    quad_names += [f"AN01-AR/EM-QP/{id_}" for id_ in ("QD02.02", "QD04.07", "QD07.04")]
    quad_names += [f"AN02-AR/EM-QP/{id_}" for id_ in ("QD04.01", "QD07.04", "QD08.08", "QD11.05", "QF05.02", "QF06.03", "QF09.07", "QF10.06")]
    quad_names += [f"AN03-AR/EM-QP/{id_}" for id_ in ("QD08.01", "QD08.08", "QD11.04", "QD11.05", "QF09.02", "QF09.07", "QF10.03", "QF10.06")]
    quad_names += [f"AN04-AR/EM-QP/{id_}" for id_ in ("QD08.01", "QD12.08", "QD11.04", "QD15.05", "QF09.02", "QF10.03", "QF13.07", "QF14.06")]
    quad_names += [f"AN05-AR/EM-QP/{id_}" for id_ in ("QD12.01", "QD15.04", "QD18.08", "QD21.05", "QF13.02", "QF14.03", "QF19.07", "QF20.06")]
    quad_ids = [TangoResourceLocator.from_trl(name) for name in quad_names]
    yp = YellowPages(
        dict(
            quadrupoles=quad_ids,
            # Todo: need to select the correct quad
            tune_correction_quadrupoles=quad_ids,
            tune=[TangoResourceLocator("simulator", "ringsimulator", "ringsimulator")],
        )
    )
    return yp, None, None

import pytest

from accml_lib.core.bl.command_rewritter import CommandRewriter
from accml_lib.core.bl.liaison_manager import LiaisonManager
from accml_lib.core.bl.translator_service import TranslatorService
from accml_lib.core.bl.unit_conversion import LinearUnitConversion
from accml_lib.core.model.utils.command import Command, BehaviourOnError
from accml_lib.core.model.utils.identifiers import DevicePropertyID, LatticeElementPropertyID, ConversionID


@pytest.fixture(scope="module")
def liaison_manager() -> LiaisonManager:
    return  LiaisonManager(
        forward_lut={
        LatticeElementPropertyID(element_name="quad1", property="main_strength"):
            DevicePropertyID(device_name="quad_pc", property="set_current")
        },
        inverse_lut={
            DevicePropertyID(device_name="quad_pc", property="set_current"):
            [LatticeElementPropertyID(element_name="quad1", property="main_strength")]
        }
    )

@pytest.fixture
def linear_unit_conversion():
    return LinearUnitConversion(slope=-5, intercept=3)

@pytest.fixture
def translation_service(linear_unit_conversion):
    return TranslatorService(
        lut={
            ConversionID(
            LatticeElementPropertyID(element_name="quad1", property="main_strength"),
            DevicePropertyID(device_name="quad_pc", property="set_current")
            ) : linear_unit_conversion
        }
    )

@pytest.fixture
def command_rewriter(liaison_manager, translation_service):
    return CommandRewriter(
        liaison_manager=liaison_manager,
        translation_service=translation_service
    )


def test_liaison_manager_forward(liaison_manager):
    lm = liaison_manager
    # Expect that sequence is returned and only one argument here
    r = lm.forward(LatticeElementPropertyID(element_name="quad1", property="main_strength"))

    assert r == DevicePropertyID(device_name="quad_pc", property="set_current")

    # Intentional: exact match required
    with pytest.raises(KeyError):
        lm.forward(LatticeElementPropertyID(element_name="quad1", property="Main_strength"))


def test_liaison_manager_inverse(liaison_manager):
    lm = liaison_manager
    r = lm.inverse(DevicePropertyID(device_name="quad_pc", property="set_current"))

    # Intentional: exact match required
    with pytest.raises(KeyError):
        lm.inverse(DevicePropertyID(device_name="Quad_PC", property="set_current"))


def test_linear_unit_converion_fwd(linear_unit_conversion):
    assert linear_unit_conversion.forward(0) == pytest.approx(3, rel=1e-12)
    assert linear_unit_conversion.forward(1) == pytest.approx(-2, rel=1e-12)
    assert linear_unit_conversion.forward(-1) == pytest.approx(8, rel=1e-12)


def test_linear_unit_converion_inv(linear_unit_conversion):
    assert linear_unit_conversion.inverse(0) == pytest.approx(3/5, rel=1e-12)
    assert linear_unit_conversion.inverse(1) == pytest.approx(3/5 - 1/5, rel=1e-12)


def test_translation_service(translation_service):

    ts = translation_service
    to = ts.get(ConversionID(
        LatticeElementPropertyID(element_name="quad1", property="main_strength"),
        DevicePropertyID(device_name="quad_pc", property="set_current")
    ))
    assert to is not None
    assert to.forward(-2) == 13


    with pytest.raises(Exception):
        ts.get(LatticeElementPropertyID(element_name="quad1", property="main_strength"))

    with pytest.raises(Exception):
        ts.get(DevicePropertyID(device_name="quad_pc", property="set_current"))



def test_command_rewriter_fwd(command_rewriter):
    c = command_rewriter
    cmd = Command(id="quad1", property="main_strength", value=2, behaviour_on_error=BehaviourOnError.roll_back)
    ncmd = c.forward(cmd)
    assert cmd.behaviour_on_error == ncmd.behaviour_on_error
    assert ncmd.id == "quad_pc"
    assert ncmd.property == "set_current"
    assert ncmd.value == pytest.approx(-7, rel=1e-12)

    with pytest.raises(KeyError):
        c.forward(
            Command(id="quad2", property="main_strength", value=2, behaviour_on_error=BehaviourOnError.roll_back)
        )


def test_command_rewriter_inv(command_rewriter):
    c = command_rewriter
    cmd = Command(id="quad_pc", property="set_current", value=-3, behaviour_on_error=BehaviourOnError.roll_back)
    ncmd, = c.inverse(cmd)
    assert cmd.behaviour_on_error == ncmd.behaviour_on_error
    assert ncmd.id == "quad1"
    assert ncmd.property == "main_strength"
    assert ncmd.value == pytest.approx(3/5 + (-3 * (-1/5)), rel=1e-12)

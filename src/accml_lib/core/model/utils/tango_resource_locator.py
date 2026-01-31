"""Support of Tango Resource Locator

Tango resource locators seem to need a bit extra treatment
e.g. Bluesky expects them to be compatible with json names

accml needs a bit further investigation to fully support
TRL with all available tools without treating TRL specially
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TangoResourceLocator:
    """Tango resource locator

    Todo:
       review whole stack to find where trl can not be used as
       string

       or to say differently that TRL can be used as strings.
       These are only made json compatible where imposed by
       (external) modules
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


def clear_token(token):
    """
    Todo:
        jsons complains on this name
    """
    return token.replace(".", "_")


def name_from_trl(trl):
    """
    Todo:
        not used ... remove me
    """
    prefix, middle, suffix = map(clear_token, trl.split("/"))
    return "__".join([prefix, middle, suffix])

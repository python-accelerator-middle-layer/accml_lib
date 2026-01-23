"""register json serializer / deserialiser support functions
"""
import jsons

from .utils import command
from .output import result


def register_serializers(json_fork):

    command.register_serializer_for_command(json_fork)
    result.register_serializer_for_read_together(json_fork)
    result.register_serializer_for_single_reading(json_fork)


def register_deserializers(json_fork):

    command.register_deserializer_for_command(json_fork)
    result.register_deserializer_for_single_reading(json_fork)

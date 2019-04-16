# Automatically generated by pb2py
# fmt: off
import protobuf as p

from .MoneroSubAddressIndicesList import MoneroSubAddressIndicesList

if __debug__:
    try:
        from typing import List
    except ImportError:
        List = None  # type: ignore


class MoneroKeyImageExportInitRequest(p.MessageType):
    MESSAGE_WIRE_TYPE = 530

    def __init__(
        self,
        num: int = None,
        hash: bytes = None,
        address_n: List[int] = None,
        network_type: int = None,
        subs: List[MoneroSubAddressIndicesList] = None,
    ) -> None:
        self.num = num
        self.hash = hash
        self.address_n = address_n if address_n is not None else []
        self.network_type = network_type
        self.subs = subs if subs is not None else []

    @classmethod
    def get_fields(cls):
        return {
            1: ('num', p.UVarintType, 0),
            2: ('hash', p.BytesType, 0),
            3: ('address_n', p.UVarintType, p.FLAG_REPEATED),
            4: ('network_type', p.UVarintType, 0),
            5: ('subs', MoneroSubAddressIndicesList, p.FLAG_REPEATED),
        }

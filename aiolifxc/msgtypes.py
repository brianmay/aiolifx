# msgtypes.py
# Author: Meghan Clark
#    Edited for python3 by François Wautier

# To Do: Validate that args are within required ranges, types, etc. In
# particular: Color [0-65535, 0-65535, 0-65535, 2500-9000], Power Level (must be 0 OR 65535)
# Need to look into assert-type frameworks or something, there has to be a tool for that.
# Also need to make custom errors possibly, though tool may have those.
from typing import Dict, Any

from .message import Message, little_endian
import bitstring

# DEVICE MESSAGES


class GetService(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetService]


class StateService(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.service = payload["service"]
        self.port = payload["port"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StateService]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Service", self.service))
        self.payload_fields.append(("Port", self.port))
        service = little_endian(bitstring.pack("uint:8", self.service))
        port = little_endian(bitstring.pack("uint:32", self.port))
        payload = service + port
        return payload


class GetHostInfo(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetHostInfo]


class StateHostInfo(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.signal = payload["signal"]
        self.tx = payload["tx"]
        self.rx = payload["rx"]
        self.reserved1 = payload["reserved1"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StateHostInfo]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Signal (mW)", self.signal))
        self.payload_fields.append(("TX (bytes since on)", self.tx))
        self.payload_fields.append(("RX (bytes since on)", self.rx))
        self.payload_fields.append(("Reserved", self.reserved1))
        signal = little_endian(bitstring.pack("float:32", self.signal))
        tx = little_endian(bitstring.pack("uint:32", self.tx))
        rx = little_endian(bitstring.pack("uint:32", self.rx))
        reserved1 = little_endian(bitstring.pack("int:16", self.reserved1))
        payload = signal + tx + rx + reserved1
        return payload


class GetHostFirmware(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetHostFirmware]


class StateHostFirmware(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.build = payload["build"]
        self.reserved1 = payload["reserved1"]
        self.version = payload["version"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StateHostFirmware]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Timestamp of Build", self.build))
        self.payload_fields.append(("Reserved", self.reserved1))
        self.payload_fields.append(("Version", self.version))
        build = little_endian(bitstring.pack("uint:64", self.build))
        reserved1 = little_endian(bitstring.pack("uint:64", self.reserved1))
        version = little_endian(bitstring.pack("uint:32", self.version))
        payload = build + reserved1 + version
        return payload


class GetWifiInfo(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetWifiInfo]


class StateWifiInfo(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.signal = payload["signal"]
        self.tx = payload["tx"]
        self.rx = payload["rx"]
        self.reserved1 = payload["reserved1"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StateWifiInfo]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Signal (mW)", self.signal))
        self.payload_fields.append(("TX (bytes since on)", self.tx))
        self.payload_fields.append(("RX (bytes since on)", self.rx))
        self.payload_fields.append(("Reserved", self.reserved1))
        signal = little_endian(bitstring.pack("float:32", self.signal))
        tx = little_endian(bitstring.pack("uint:32", self.tx))
        rx = little_endian(bitstring.pack("uint:32", self.rx))
        reserved1 = little_endian(bitstring.pack("int:16", self.reserved1))
        payload = signal + tx + rx + reserved1
        return payload


class GetWifiFirmware(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetWifiFirmware]


class StateWifiFirmware(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.build = payload["build"]
        self.reserved1 = payload["reserved1"]
        self.version = payload["version"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StateWifiFirmware]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Timestamp of Build", self.build))
        self.payload_fields.append(("Reserved", self.reserved1))
        self.payload_fields.append(("Version", self.version))
        build = little_endian(bitstring.pack("uint:64", self.build))
        reserved1 = little_endian(bitstring.pack("uint:64", self.reserved1))
        version = little_endian(bitstring.pack("uint:32", self.version))
        payload = build + reserved1 + version
        return payload


class GetPower(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetPower]


class SetPower(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.power_level = payload["power_level"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[SetPower]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Power", self.power_level))
        power_level = little_endian(bitstring.pack("uint:16", self.power_level))
        payload = power_level
        return payload


class StatePower(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.power_level = payload["power_level"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StatePower]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Power", self.power_level))
        power_level = little_endian(bitstring.pack("uint:16", self.power_level))
        payload = power_level
        return payload


class GetLabel(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetLabel]


class SetLabel(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.label = payload["label"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[SetLabel]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Label", self.label))
        field_len_bytes = 32
        label = b"".join(little_endian(bitstring.pack("uint:8", ord(c))) for c in self.label)
        padding = b"".join(little_endian(bitstring.pack("uint:8", 0)) for i in range(field_len_bytes - len(self.label)))
        payload = label + padding
        return payload


class StateLabel(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.label = payload["label"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StateLabel]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Label", self.label))
        field_len_bytes = 32
        label = b"".join(little_endian(bitstring.pack("uint:8", c)) for c in self.label)
        padding = b"".join(little_endian(bitstring.pack("uint:8", 0)) for i in range(field_len_bytes - len(self.label)))
        payload = label + padding
        return payload


class GetVersion(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetVersion]


class StateVersion(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.vendor = payload["vendor"]
        self.product = payload["product"]
        self.version = payload["version"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StateVersion]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Vendor", self.vendor))
        self.payload_fields.append(("Reserved", self.product))
        self.payload_fields.append(("Version", self.version))
        vendor = little_endian(bitstring.pack("uint:32", self.vendor))
        product = little_endian(bitstring.pack("uint:32", self.product))
        version = little_endian(bitstring.pack("uint:32", self.version))
        payload = vendor + product + version
        return payload


class GetInfo(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetInfo]


class StateInfo(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.time = payload["time"]
        self.uptime = payload["uptime"]
        self.downtime = payload["downtime"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StateInfo]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Current Time", self.time))
        self.payload_fields.append(("Uptime (ns)", self.uptime))
        self.payload_fields.append(("Last Downtime Duration (ns) (5 second error)", self.downtime))
        time = little_endian(bitstring.pack("uint:64", self.time))
        uptime = little_endian(bitstring.pack("uint:64", self.uptime))
        downtime = little_endian(bitstring.pack("uint:64", self.downtime))
        payload = time + uptime + downtime
        return payload


class GetLocation(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetLocation]


class StateLocation(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.location = payload["location"]
        self.label = payload["label"]
        self.updated_at = payload["updated_at"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StateLocation]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Location ", self.location))
        self.payload_fields.append(("Label ", self.label))
        self.payload_fields.append(("Updated At ", self.updated_at))
        location = b"".join(little_endian(bitstring.pack("uint:8", b)) for b in self.location)
        label = b"".join(little_endian(bitstring.pack("uint:8", c)) for c in self.label)
        label_padding = b"".join(little_endian(bitstring.pack("uint:8", 0)) for i in range(32 - len(self.label)))
        label += label_padding
        updated_at = little_endian(bitstring.pack("uint:64", self.updated_at))
        payload = location + label + updated_at
        return payload


class GetGroup(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[GetGroup]


class StateGroup(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.group = payload["group"]
        self.label = payload["label"]
        self.updated_at = payload["updated_at"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[StateGroup]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Group ", self.group))
        self.payload_fields.append(("Label ", self.label))
        self.payload_fields.append(("Updated At ", self.updated_at))
        group = b"".join(little_endian(bitstring.pack("uint:8", b)) for b in self.group)
        label = b"".join(little_endian(bitstring.pack("uint:8", c)) for c in self.label)
        label_padding = b"".join(little_endian(bitstring.pack("uint:8", 0)) for i in range(32 - len(self.label)))
        label += label_padding
        updated_at = little_endian(bitstring.pack("uint:64", self.updated_at))
        payload = group + label + updated_at
        return payload


class Acknowledgement(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[Acknowledgement]


class EchoRequest(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.byte_array = payload["byte_array"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[EchoRequest]

    def get_payload(self) -> bytes:
        field_len = 64
        self.payload_fields.append(("Byte Array", self.byte_array))
        byte_array = b"".join(little_endian(bitstring.pack("uint:8", b)) for b in self.byte_array)
        byte_array_len = len(byte_array)
        if byte_array_len < field_len:
            byte_array += b"".join(little_endian(bitstring.pack("uint:8", 0))
                                   for i in range(field_len - byte_array_len))
        elif byte_array_len > field_len:
            byte_array = byte_array[:field_len]
        payload = byte_array
        return payload


class EchoResponse(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.byte_array = payload["byte_array"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[EchoResponse]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Byte Array", self.byte_array))
        byte_array = b"".join(little_endian(bitstring.pack("uint:8", b)) for b in self.byte_array)
        payload = byte_array
        return payload


# LIGHT MESSAGES


class LightGet(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[LightGet]


class LightSetColor(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.color = payload["color"]
        self.duration = payload["duration"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[LightSetColor]

    def get_payload(self) -> bytes:
        reserved_8 = little_endian(bitstring.pack("uint:8", self.reserved))
        color = b"".join(little_endian(bitstring.pack("uint:16", field)) for field in self.color)
        duration = little_endian(bitstring.pack("uint:32", self.duration))
        payload = reserved_8 + color + duration
        # payloadUi = " ".join("{:02x}".format(c) for c in payload)
        return payload


class LightSetWaveform(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.transient = payload["transient"]
        self.color = payload["color"]
        self.period = payload["period"]
        self.cycles = payload["cycles"]
        self.duty_cycle = payload["duty_cycle"]
        self.waveform = payload["waveform"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[LightSetWaveform]

    def get_payload(self) -> bytes:
        reserved_8 = little_endian(bitstring.pack("uint:8", self.reserved))
        transient = little_endian(bitstring.pack("uint:8", self.transient))
        color = b"".join(little_endian(bitstring.pack("uint:16", field)) for field in self.color)
        period = little_endian(bitstring.pack("uint:32", self.period))
        cycles = little_endian(bitstring.pack("float:32", self.cycles))
        duty_cycle = little_endian(bitstring.pack("int:16", self.duty_cycle))
        waveform = little_endian(bitstring.pack("uint:8", self.waveform))
        payload = reserved_8 + transient + color + period + cycles + duty_cycle + waveform
        # payloadUi = " ".join("{:02x}".format(c) for c in payload)
        return payload


class LightState(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.color = payload["color"]
        self.reserved1 = payload["reserved1"]
        self.power_level = payload["power_level"]
        self.label = payload["label"]
        self.reserved2 = payload["reserved2"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[LightState]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Color (HSBK)", self.color))
        self.payload_fields.append(("Reserved", self.reserved1))
        self.payload_fields.append(("Power Level", self.power_level))
        self.payload_fields.append(("Label", self.label))
        self.payload_fields.append(("Reserved", self.reserved2))
        color = b"".join(little_endian(bitstring.pack("uint:16", field)) for field in self.color)
        reserved1 = little_endian(bitstring.pack("int:16", self.reserved1))
        power_level = little_endian(bitstring.pack("uint:16", self.power_level))
        label = b"".join(little_endian(bitstring.pack("uint:8", c)) for c in self.label)
        label_padding = b"".join(little_endian(bitstring.pack("uint:8", 0)) for i in range(32 - len(self.label)))
        label += label_padding
        reserved2 = little_endian(bitstring.pack("uint:64", self.reserved1))
        payload = color + reserved1 + power_level + label + reserved2
        return payload


class LightGetPower(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[LightGetPower]


class LightSetPower(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.power_level = payload["power_level"]
        self.duration = payload["duration"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[LightSetPower]

    def get_payload(self) -> bytes:
        power_level = little_endian(bitstring.pack("uint:16", self.power_level))
        duration = little_endian(bitstring.pack("uint:32", self.duration))
        payload = power_level + duration
        return payload


class LightStatePower(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.power_level = payload["power_level"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[LightStatePower]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Power Level", self.power_level))
        power_level = little_endian(bitstring.pack("uint:16", self.power_level))
        payload = power_level
        return payload

# INFRARED MESSAGES


class LightGetInfrared(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[LightGetInfrared]


class LightStateInfrared(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.infrared_brightness = payload["infrared_brightness"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[LightStateInfrared]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Infrared Brightness", self.infrared_brightness))
        infrared_brightness = little_endian(bitstring.pack("uint:16", self.infrared_brightness))
        payload = infrared_brightness
        return payload


class LightSetInfrared(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.infrared_brightness = payload["infrared_brightness"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[LightSetInfrared]

    def get_payload(self) -> bytes:
        infrared_brightness = little_endian(bitstring.pack("uint:16", self.infrared_brightness))
        payload = infrared_brightness
        return payload

# MULTIZONE MESSAGES


class MultiZoneStateMultiZone(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.count = payload["count"]
        self.index = payload["index"]
        self.color = payload["color"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[MultiZoneStateMultiZone]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Count", self.count))
        self.payload_fields.append(("Index", self.index))
        self.payload_fields.append(("Color (HSBK)", self.color))
        count = little_endian(bitstring.pack("uint:8", self.count))
        index = little_endian(bitstring.pack("uint:8", self.index))
        payload = count + index
        for color in self.color:
            payload += b"".join(little_endian(bitstring.pack("uint:16", field)) for field in color)
        return payload


class MultiZoneStateZone(Message):  # 503
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.count = payload["count"]
        self.index = payload["index"]
        self.color = payload["color"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[MultiZoneStateZone]

    def get_payload(self) -> bytes:
        self.payload_fields.append(("Count", self.count))
        self.payload_fields.append(("Index", self.index))
        self.payload_fields.append(("Color (HSBK)", self.color))
        count = little_endian(bitstring.pack("uint:8", self.count))
        index = little_endian(bitstring.pack("uint:8", self.index))
        color = b"".join(little_endian(bitstring.pack("uint:16", field)) for field in self.color)
        payload = count + index + color
        return payload


class MultiZoneSetColorZones(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.start_index = payload["start_index"]
        self.end_index = payload["end_index"]
        self.color = payload["color"]
        self.duration = payload["duration"]
        self.apply = payload["apply"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[MultiZoneSetColorZones]

    def get_payload(self) -> bytes:
        start_index = little_endian(bitstring.pack("uint:8", self.start_index))
        end_index = little_endian(bitstring.pack("uint:8", self.end_index))
        color = b"".join(little_endian(bitstring.pack("uint:16", field)) for field in self.color)
        duration = little_endian(bitstring.pack("uint:32", self.duration))
        apply = little_endian(bitstring.pack("uint:8", self.apply))
        payload = start_index + end_index + color + duration + apply
        return payload


class MultiZoneGetColorZones(Message):
    def __init__(
            self, *, target_addr: str, source_id: int, seq_num: int,
            payload: Dict[str, Any]=None,
            ack_requested: bool=False, response_requested: bool=False) -> None:

        if payload is None:
            payload = {}

        self.start_index = payload["start_index"]
        self.end_index = payload["end_index"]
        super().__init__(
            target_addr=target_addr, source_id=source_id,
            seq_num=seq_num,
            ack_requested=ack_requested, response_requested=response_requested,
            payload=payload)
        self.message_type = MSG_IDS[MultiZoneGetColorZones]

    def get_payload(self) -> bytes:
        start_index = little_endian(bitstring.pack("uint:8", self.start_index))
        end_index = little_endian(bitstring.pack("uint:8", self.end_index))
        payload = start_index + end_index
        return payload


MSG_IDS = {GetService: 2,
           StateService: 3,
           GetHostInfo: 12,
           StateHostInfo: 13,
           GetHostFirmware: 14,
           StateHostFirmware: 15,
           GetWifiInfo: 16,
           StateWifiInfo: 17,
           GetWifiFirmware: 18,
           StateWifiFirmware: 19,
           GetPower: 20,
           SetPower: 21,
           StatePower: 22,
           GetLabel: 23,
           SetLabel: 24,
           StateLabel: 25,
           GetVersion: 32,
           StateVersion: 33,
           GetInfo: 34,
           StateInfo: 35,
           Acknowledgement: 45,
           GetLocation: 48,
           StateLocation: 50,
           GetGroup: 51,
           StateGroup: 53,
           EchoRequest: 58,
           EchoResponse: 59,
           LightGet: 101,
           LightSetColor: 102,
           LightSetWaveform: 103,
           LightState: 107,
           LightGetPower: 116,
           LightSetPower: 117,
           LightStatePower: 118,
           LightGetInfrared: 120,
           LightStateInfrared: 121,
           LightSetInfrared: 122,
           MultiZoneSetColorZones: 501,
           MultiZoneGetColorZones: 502,
           MultiZoneStateZone: 503,
           MultiZoneStateMultiZone: 506}

SERVICE_IDS = {1: "UDP",
               2: "reserved",
               3: "reserved",
               4: "reserved"}

STR_MAP = {65535: "On",
           0: "Off",
           None: "Unknown"}

ZONE_MAP = {0: "NO_APPLY",
            1: "APPLY",
            2: "APPLY_ONLY"}

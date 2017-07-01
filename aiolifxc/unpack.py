# unpack.py
# Author: Meghan Clark
import struct

from .message import Message, HEADER_SIZE_BYTES
from . import msgtypes
import binascii

# Creates a LIFX Message out of packed binary data
# If the message type is not one of the officially released ones above, it will create just a Message out of it
# If it's not in the LIFX protocol format, uhhhhh...we'll put that on a to-do list.


def unpack_lifx_message(packed_message: bytes) -> Message:
    header_str = packed_message[0:HEADER_SIZE_BYTES]
    payload_str = packed_message[HEADER_SIZE_BYTES:]

    size = struct.unpack("H", header_str[0:2])[0]
    flags = struct.unpack("H", header_str[2:4])[0]
    origin = (flags >> 14) & 3
    tagged = (flags >> 13) & 1
    addressable = (flags >> 12) & 1
    protocol = flags & 4095
    source_id = struct.unpack("I", header_str[4:8])[0]
    target_addr = ":".join([('%02x' % b) for b in struct.unpack("B" * 6, header_str[8:14])])
    response_flags = struct.unpack("B", header_str[22:23])[0]
    ack_requested = bool(response_flags & 2)
    response_requested = bool(response_flags & 1)
    seq_num = struct.unpack("B", header_str[23:24])[0]
    message_type = struct.unpack("H", header_str[32:34])[0]

    message = Message(
        target_addr=target_addr, source_id=source_id, seq_num=seq_num,
        payload={},
        ack_requested=ack_requested, response_requested=response_requested)
    if message_type == msgtypes.MSG_IDS[msgtypes.GetService]:
        message = msgtypes.GetService(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StateService]:
        service = struct.unpack("B", payload_str[0:1])[0]
        port = struct.unpack("I", payload_str[1:5])[0]
        payload = {"service": service, "port": port}
        message = msgtypes.StateService(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.GetHostInfo]:
        message = msgtypes.GetHostInfo(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StateHostInfo]:
        signal = struct.unpack("f", payload_str[0:4])[0]
        tx = struct.unpack("I", payload_str[4:8])[0]
        rx = struct.unpack("I", payload_str[8:12])[0]
        reserved1 = struct.unpack("h", payload_str[12:14])[0]
        payload = {"signal": signal, "tx": tx, "rx": rx, "reserved1": reserved1}
        message = msgtypes.StateHostInfo(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.GetHostFirmware]:
        message = msgtypes.GetHostFirmware(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StateHostFirmware]:
        build = struct.unpack("Q", payload_str[0:8])[0]
        reserved1 = struct.unpack("Q", payload_str[8:16])[0]
        version = struct.unpack("I", payload_str[16:20])[0]
        payload = {"build": build, "reserved1": reserved1, "version": version}
        message = msgtypes.StateHostFirmware(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.GetWifiInfo]:
        message = msgtypes.GetWifiInfo(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StateWifiInfo]:
        signal = struct.unpack("f", payload_str[0:4])[0]
        tx = struct.unpack("I", payload_str[4:8])[0]
        rx = struct.unpack("I", payload_str[8:12])[0]
        reserved1 = struct.unpack("h", payload_str[12:14])[0]
        payload = {"signal": signal, "tx": tx, "rx": rx, "reserved1": reserved1}
        message = msgtypes.StateWifiInfo(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.GetWifiFirmware]:
        message = msgtypes.GetWifiFirmware(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StateWifiFirmware]:
        build = struct.unpack("Q", payload_str[0:8])[0]
        reserved1 = struct.unpack("Q", payload_str[8:16])[0]
        version = struct.unpack("I", payload_str[16:20])[0]
        payload = {"build": build, "reserved1": reserved1, "version": version}
        message = msgtypes.StateWifiFirmware(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.GetPower]:
        message = msgtypes.GetPower(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.SetPower]:
        power_level = struct.unpack("H", payload_str[0:2])[0]
        payload = {"power_level": power_level}
        message = msgtypes.SetPower(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StatePower]:
        power_level = struct.unpack("H", payload_str[0:2])[0]
        payload = {"power_level": power_level}
        message = msgtypes.StatePower(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.GetLabel]:
        message = msgtypes.GetLabel(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.SetLabel]:
        label = binascii.unhexlify("".join(["%2.2x" % (b & 0x000000ff)
                                            for b in struct.unpack("b" * 32, payload_str[0:32])]))
        payload = {"label": label}
        message = msgtypes.SetLabel(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StateLabel]:
        label = binascii.unhexlify("".join(["%2.2x" % (b & 0x000000ff)
                                            for b in struct.unpack("b" * 32, payload_str[0:32])]))
        payload = {"label": label}
        message = msgtypes.StateLabel(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.GetLocation]:
        message = msgtypes.GetLocation(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StateLocation]:
        location = [b for b in struct.unpack("B" * 16, payload_str[0:16])]
        label = binascii.unhexlify("".join(["%2.2x" % (b & 0x000000ff)
                                            for b in struct.unpack("b" * 32, payload_str[16:48])]))
        updated_at = struct.unpack("Q", payload_str[48:56])[0]
        payload = {"location": location, "label": label, "updated_at": updated_at}
        message = msgtypes.StateLocation(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.GetGroup]:
        message = msgtypes.GetGroup(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StateGroup]:
        group = [b for b in struct.unpack("B" * 16, payload_str[0:16])]
        label = binascii.unhexlify("".join(["%2.2x" % (b & 0x000000ff)
                                            for b in struct.unpack("b" * 32, payload_str[16:48])]))
        updated_at = struct.unpack("Q", payload_str[48:56])[0]
        payload = {"group": group, "label": label, "updated_at": updated_at}
        message = msgtypes.StateGroup(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.GetVersion]:
        message = msgtypes.GetVersion(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StateVersion]:
        vendor = struct.unpack("I", payload_str[0:4])[0]
        product = struct.unpack("I", payload_str[4:8])[0]
        version = struct.unpack("I", payload_str[8:12])[0]
        payload = {"vendor": vendor, "product": product, "version": version}
        message = msgtypes.StateVersion(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.GetInfo]:
        message = msgtypes.GetInfo(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.StateInfo]:
        time = struct.unpack("Q", payload_str[0:8])[0]
        uptime = struct.unpack("Q", payload_str[8:16])[0]
        downtime = struct.unpack("Q", payload_str[16:24])[0]
        payload = {"time": time, "uptime": uptime, "downtime": downtime}
        message = msgtypes.StateInfo(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.Acknowledgement]:
        message = msgtypes.Acknowledgement(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.EchoRequest]:
        byte_array_len = len(payload_str)
        byte_array = [b for b in struct.unpack("B" * byte_array_len, payload_str[0:byte_array_len])]
        payload = {"byte_array": byte_array}
        message = msgtypes.EchoRequest(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.EchoResponse]:
        byte_array_len = len(payload_str)
        byte_array = [b for b in struct.unpack("B" * byte_array_len, payload_str[0:byte_array_len])]
        payload = {"byte_array": byte_array}
        message = msgtypes.EchoResponse(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.LightGet]:
        message = msgtypes.LightGet(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.LightSetColor]:
        color = struct.unpack("H" * 4, payload_str[0:8])
        duration = struct.unpack("I", payload_str[8:12])[0]
        payload = {"color": color, "duration": duration}
        message = msgtypes.LightSetColor(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.LightState]:
        color = struct.unpack("H" * 4, payload_str[0:8])
        reserved1 = struct.unpack("H", payload_str[8:10])[0]
        power_level = struct.unpack("H", payload_str[10:12])[0]
        label = binascii.unhexlify("".join(["%2.2x" % (b & 0x000000ff)
                                            for b in struct.unpack("b" * 32, payload_str[12:44])]))
        reserved2 = struct.unpack("Q", payload_str[44:52])[0]
        payload = {"color": color, "reserved1": reserved1,
                   "power_level": power_level, "label": label, "reserved2": reserved2}
        message = msgtypes.LightState(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.LightGetPower]:
        message = msgtypes.LightGetPower(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.LightSetPower]:
        power_level = struct.unpack("H", payload_str[0:2])[0]
        duration = struct.unpack("I", payload_str[2:6])[0]
        payload = {"power_level": power_level, "duration": duration}
        message = msgtypes.LightSetPower(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.LightStatePower]:
        power_level = struct.unpack("H", payload_str[0:2])[0]
        payload = {"power_level": power_level}
        message = msgtypes.LightStatePower(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.LightGetInfrared]:  # 120
        message = msgtypes.LightGetInfrared(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.LightStateInfrared]:  # 121
        infrared_brightness = struct.unpack("H", payload_str[0:2])[0]
        payload = {"infrared_brightness": infrared_brightness}
        message = msgtypes.LightStateInfrared(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.LightSetInfrared]:  # 122
        infrared_brightness = struct.unpack("H", payload_str[0:2])[0]
        payload = {"infrared_brightness": infrared_brightness}
        message = msgtypes.LightSetInfrared(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.MultiZoneStateZone]:  # 503
        count = struct.unpack("c", payload_str[0:1])[0]
        count = ord(count)  # 8 bit
        index = struct.unpack("c", payload_str[1:2])[0]
        index = ord(index)  # 8 bit
        color = struct.unpack("H" * 4, payload_str[2:10])
        payload = {"count": count, "index": index, "color": color}
        message = msgtypes.MultiZoneStateZone(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    elif message_type == msgtypes.MSG_IDS[msgtypes.MultiZoneStateMultiZone]:  # 506
        count = struct.unpack("c", payload_str[0:1])[0]
        count = ord(count)  # 8 bit
        index = struct.unpack("c", payload_str[1:2])[0]
        index = ord(index)  # 8 bit
        colors = []
        for i in range(8):
            color = struct.unpack("H" * 4, payload_str[2 + (i * 8):10 + (i * 8)])
            colors.append(color)
        payload = {"count": count, "index": index, "color": colors}
        message = msgtypes.MultiZoneStateMultiZone(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload=payload,
            ack_requested=ack_requested, response_requested=response_requested)

    else:
        message = Message(
            target_addr=target_addr, source_id=source_id, seq_num=seq_num,
            payload={},
            ack_requested=ack_requested, response_requested=response_requested)
        message.message_type = message_type

    message.size = size
    message.origin = origin
    message.tagged = tagged
    message.addressable = addressable
    message.protocol = protocol
    message.source_id = source_id
    message.header = header_str
    message.payload = payload_str

    return message

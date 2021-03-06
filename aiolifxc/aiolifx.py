#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# This application is simply a bridge application for Lifx bulbs.
#
# Copyright (c) 2016 François Wautier
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
import asyncio as aio
import datetime
import logging
import random
import socket
from collections import Awaitable
from typing import Set  # NOQA
from typing import (Any, Callable, Dict, Iterable, Iterator, List, Optional,
                    Text, Tuple, Type, TypeVar, Union, cast)

from . import msgtypes
from .colors import Color
from .message import BROADCAST_MAC, Message
from .products import product_map
from .unpack import unpack_lifx_message

# A couple of constants
UDP_BROADCAST_IP = "255.255.255.255"
UDP_BROADCAST_PORT = 56700
DEFAULT_TIMEOUT = 0.5  # How long to wait for an ack or response
DEFAULT_UNREGISTER_TIMEOUT = 0.5  # How long to wait before unregistering a light
DEFAULT_ATTEMPTS = 3  # How many time should we try to send to the bulb`
DISCOVERY_INTERVAL = 180
DISCOVERY_STEP = 5

GenericResponse = TypeVar('GenericResponse', bound=Message)
Power = Union[bool, int]

logger = logging.getLogger(__name__)


def _mac_to_ipv6_link_local(mac: str, prefix: str) -> str:
    """ Translate a MAC address into an IPv6 address in the prefixed network"""

    # Remove the most common delimiters; dots, dashes, etc.
    trans = str.maketrans(dict([(x, None) for x in [" ", ".", ":", "-"]]))
    mac_value = int(mac.translate(trans), 16)
    # Split out the bytes that slot into the IPv6 address
    # XOR the most significant byte with 0x02, inverting the
    # Universal / Local bit
    high2 = mac_value >> 32 & 0xffff ^ 0x0200
    high1 = mac_value >> 24 & 0xff
    low1 = mac_value >> 16 & 0xff
    low2 = mac_value & 0xffff
    return prefix + ':{:04x}:{:02x}ff:fe{:02x}:{:04x}'.format(
        high2, high1, low1, low2)


def _nanosec_to_hours(ns: int) -> float:
    return ns / (1000000000.0 * 60 * 60)


def _str_map(key: Optional[Power]) -> str:
    string_representation = "Unknown (%s)" % key
    if key is None:
        string_representation = "Unknown"
    elif isinstance(key, bool):
        if key is True:
            string_representation = "On"
        elif key is False:
            string_representation = "Off"
    return string_representation


class LightOffline(Exception):
    pass


class Lights(Iterable['Light']):
    """ Class that represents a number of Lights. """
    def __init__(self, loop: aio.AbstractEventLoop, light_list: List['Light']) -> None:
        self._light_list = light_list  # type: List['Light']
        self._loop = loop

    def __iter__(self) -> Iterator['Light']:
        return iter(self._light_list)

    def get_clone(self, light_list: List['Light']) -> 'Lights':
        """
        Get clone Lights object.

        :param new_class: Class to use to create new object.
        :return: The new object.
        """
        # noinspection PyCallingNonCallable
        child = type(self)(loop=self._loop, light_list=light_list)
        return child

    def get_by_group(self, group: str) -> 'Lights':
        """
        Get clone Lights object filtered by group.

        :param group: The name of the group.
        :return: The new object.

        The groups must be loaded already in the lights.
        """
        result = self.get_clone(light_list=[
            light
            for light in iter(self)
            if light.group == group
        ])
        return result

    def get_by_label(self, label: str) -> 'Lights':
        """
        Get a clone Lights object filtered by label.

        :param label: The name of the label.
        :return: The new object.

        The labels must be loaded already in the lights.
        """
        result = self.get_clone(light_list=[
            light
            for light in iter(self)
            if light.group == label
        ])
        return result

    def get_by_mac_addr(self, mac_addr: str) -> 'Lights':
        """
        Get a clone Lights object filtered by label.

        :param label: The name of the label.
        :return: The new object.

        The labels must be loaded already in the lights.
        """
        result = self.get_clone(light_list=[
            light
            for light in iter(self)
            if light.mac_addr == mac_addr
        ])
        return result

    async def do_for_every_light(
            self, fun: Callable[['Light'], Awaitable],
    ) -> None:
        """
        Run a async function for every light.

        :param fun: The function to call.

        Errors will get logged but not propagated.
        """
        async def wrapper(light: 'Light') -> None:
            try:
                await fun(light)
            except LightOffline:
                logger.info("Light is offline %s", light)
            except Exception:
                logger.exception(
                    "An exception was generated in do_for_every_light for %s:",
                    light,
                )

        coroutines = []
        for light in iter(self):
            coroutines.append(wrapper(light))
        await aio.gather(*coroutines, loop=self._loop)

    async def get_meta_information(self) -> None:
        """ Get all meta information for lights. """
        async def single_light(light: 'Light') -> None:
            await light.get_metadata(loop=self._loop)
        await self.do_for_every_light(single_light)

    async def set_power(self, value: Power, rapid: bool=False) -> None:
        """ Set power for all lights. """
        async def single_light(light: Light) -> None:
            await light.set_power(value=value, rapid=rapid)
        await self.do_for_every_light(single_light)

    def __str__(self) -> str:
        return format(", ".join(str(d) for d in iter(self)))

    async def set_light_power(self, value: Power, duration: int=0, rapid: bool=False) -> None:
        """ Set power for all lights. """
        async def single_light(light: Light) -> None:
            await light.set_light_power(value=value, duration=duration, rapid=rapid)
        await self.do_for_every_light(single_light)

    async def set_color(self, color: Color, duration: int = 0, rapid: bool = False) -> None:
        """ Set color for all lights. """
        async def single_light(light: Light) -> None:
            await light.set_color(color=color, duration=duration, rapid=rapid)
        await self.do_for_every_light(single_light)

    async def set_waveform(
            self, *,
            color: Color,
            transient: int, period: int, cycles: int, duty_cycle: int, waveform: int,
            rapid: bool = False) -> None:
        """ Set waveform for all lights. """
        async def single_light(light: Light) -> None:
            await light.set_waveform(
                color=color,
                transient=transient, period=period, cycles=cycles, duty_cycle=duty_cycle, waveform=waveform,
                rapid=rapid)

        await self.do_for_every_light(single_light)


class Light(aio.DatagramProtocol):
    """ Implement common functions for a LIFX Light. """

    # mac_addr is a string, with the ":" and everything.
    # ip_addr is a string with the ip address
    # port is the port we are connected to
    def __init__(
            self, *, loop: aio.AbstractEventLoop,
            mac_addr: str, ip_addr: str, port: int
            ) -> None:
        """
        Construct a new Light object.

        :param loop: The Asyncio event loop.
        :param mac_addr: The MAC Address. with the ":" and everything.
        :param ip_addr: A string with the IP address.
        :param port: The UDP port to use.
        :param lights: The lights list this light belongs to.
        """
        self._loop = loop
        self._mac_addr = mac_addr.lower()
        self._ip_addr = ip_addr
        self._port = port
        self._retry_count = DEFAULT_ATTEMPTS
        self._timeout = DEFAULT_TIMEOUT
        self._unregister_timeout = DEFAULT_UNREGISTER_TIMEOUT
        self._transport = None  # type: Optional[aio.DatagramTransport]
        self._task = None  # type: Optional[aio.Task]
        self._seq = 0
        # Key is the message sequence, value is (response type, Event, response)
        self._message = {}  # type: Dict[int, List]
        self._source_id = random.randint(0, (2 ** 32) - 1)
        # And the rest
        self._label = None  # type: Optional[str]
        self._location = None  # type: Optional[str]
        self._group = None  # type: Optional[str]
        self._power_level = None  # type: Optional[Power]
        self._vendor = None  # type: Optional[int]
        self._product = None  # type: Optional[int]
        self._version = None  # type: Optional[int]
        self._host_firmware_version = None  # type: Optional[str]
        self._host_firmware_build_timestamp = None  # type: Optional[int]
        self._wifi_firmware_version = None  # type: Optional[str]
        self._wifi_firmware_build_timestamp = None  # type: Optional[int]
        self._color = None  # type: Optional[Color]
        self._color_zones = []  # type: List[Color]
        self._infrared_brightness = None  # type: Optional[int]

    def _register(self) -> None:
        self._loop.create_task(self._async_register())

    async def _async_register(self) -> None:
        try:
            await self.get_metadata(loop=self._loop)
            logger.info("Registered light %s.", self)
        except LightOffline:
            logger.error("Light is offline %s", self)

    @property
    def mac_addr(self) -> str:
        """ Return the MAC address associated with this light. """
        return self._mac_addr

    @property
    def label(self) -> Optional[str]:
        """ Return the cached label - if any - for this light. """
        return self._label

    @property
    def group(self) -> Optional[str]:
        """ Return the cached group - if any - for this light. """
        return self._group

    @property
    def ip_addr(self) -> str:
        """ Return the MAC address associated with this light. """
        return self._ip_addr

    def _seq_next(self) -> int:
        self._seq = (self._seq + 1) % 128
        return self._seq

    #
    #                            Protocol Methods
    #

    def connection_made(self, transport: aio.BaseTransport) -> None:
        """ Called when a connection is made. """
        self._transport = cast(aio.DatagramTransport, transport)

    def datagram_received(self, data: Union[bytes, Text], addr: Tuple[str, int]) -> None:
        """ Called when we receive a packet. """
        assert isinstance(data, bytes)
        response = unpack_lifx_message(data)
        if response.seq_num in self._message:
            response_type, myevent, __ = self._message[response.seq_num]
            if type(response) == response_type:
                if response.source_id == self._source_id:
                    self._message[response.seq_num][2] = response
                    myevent.set()

    def is_alive(self) -> bool:
        if self._transport is None:
            return False
        elif self._task is None:
            return False
        else:
            return True

    def renew(self, *, family: int, ip_addr: str, port: int) -> None:
        """
        Renew the light registration with updated contact information.

        :param ip_addr: A string with the IP address.
        :param port: The UDP port to use.
        """
        if self._ip_addr != ip_addr or self._port != port:
            self.cleanup()
            self._ip_addr = ip_addr
            self._port = port

        if self._task is None:
            coro = self._loop.create_datagram_endpoint(
                lambda: self, family=family, remote_addr=(self._ip_addr, self._port))
            self._task = self._loop.create_task(coro)

        self._register()

    def cleanup(self) -> None:
        """ Cleanup all resources used by this `Light` object. """
        if self._transport:
            self._transport.close()
            self._transport = None
        if self._task:
            self._task.cancel()
            self._task = None

    #
    #                            Workflow Methods
    #

    async def _fire_sending(self, msg: Message, num_repeats: int) -> None:
        """
        Send a message a number of times.

        :param msg: The message to send.
        :param num_repeats: The number of times we should send it.
        """
        assert self._transport is not None

        if num_repeats is None:
            num_repeats = self._retry_count
        sent_msg_count = 0
        sleep_interval = 0.05
        while sent_msg_count < num_repeats:
            packed_message = msg.generate_packed_message()
            self._transport.sendto(packed_message)
            sent_msg_count += 1
            # Max num of messages light can handle is 20 per second.
            await aio.sleep(sleep_interval)

    def _fire_and_forget(
            self, msg_type: Type[Message], payload: Optional[Dict[str, Any]]=None,
            *, num_repeats: int=1) -> None:
        """
        Don't wait for Acks or Responses, just send the same message repeatedly as fast as
        possible in a separate task.

        :param msg_type: The type of the Message.
        :param payload: The payload to send.
        :param num_repeats: The number of times we should send it.
        """

        if payload is None:
            payload = {}
        msg = msg_type(
            target_addr=self._mac_addr, source_id=self._source_id,
            seq_num=0, payload=payload,
            ack_requested=False, response_requested=False)
        self._loop.create_task(self._fire_sending(msg, num_repeats))

    async def _try_sending(
            self, msg: Message, response_type: Type[GenericResponse],
            *,
            timeout_secs: Optional[float]=None,
            max_attempts: Optional[int]=None) -> GenericResponse:
        """
        Send message and wait for appropriate response.

        :param msg: The message to be sent.
        :param timeout_secs: The timeout in seconds for each atempt.
        :param max_attempts: The maximum number of attempts.
        :return: The response we got.
        """
        assert self._transport is not None

        self._message[msg.seq_num] = [response_type, None, None]

        if timeout_secs is None:
            timeout_secs = self._timeout
        if max_attempts is None:
            max_attempts = self._retry_count

        attempts = 0
        while attempts < max_attempts:
            if msg.seq_num not in self._message:
                raise RuntimeError("Oops. We couldn't find the message information.")
            event = aio.Event()
            self._message[msg.seq_num][1] = event
            attempts += 1
            packed_message = msg.generate_packed_message()
            self._transport.sendto(packed_message)
            try:
                await aio.wait_for(event.wait(), timeout_secs)
                break
            except aio.TimeoutError:
                if attempts >= max_attempts:
                    logger.error(
                        "Light %s cannot be reached after %s retries",
                        self, max_attempts)
                    if msg.seq_num in self._message:
                        del(self._message[msg.seq_num])
                    # It's dead Jim
                    self.cleanup()
                    raise LightOffline()
        result = self._message[msg.seq_num][2]
        del (self._message[msg.seq_num])
        return cast(GenericResponse, result)

    async def _req_with_ack(
            self, msg_type: Type[Message], payload: Dict[str, Any],
            *,
            timeout_secs: Optional[int]=None,
            max_attempts: Optional[int]=None) -> msgtypes.Acknowledgement:
        """
        Send a message and expect an ACK response.

        :param msg_type: The type of the Message.
        :param payload: The payload to send.
        :param timeout_secs: The timeout in seconds for each atempt.
        :param max_attempts: The maximum number of attempts.
        :return:  The ACK response.

        Usually used for Set messages.
        """
        msg = msg_type(
            target_addr=self._mac_addr, source_id=self._source_id,
            seq_num=self._seq_next(),
            payload=payload, ack_requested=True, response_requested=False)
        return await self._try_sending(
            msg, msgtypes.Acknowledgement,
            timeout_secs=timeout_secs, max_attempts=max_attempts)

    # Usually used for Get messages, or for state confirmation after Set (hence the optional payload)
    async def _req_with_resp(
            self, msg_type: Type[Message], response_type: Type[GenericResponse],
            payload: Optional[Dict[str, Any]]=None,
            *,
            timeout_secs: Optional[int]=None,
            max_attempts: Optional[int]=None) -> GenericResponse:
        """
        Send a message and expect an response.

        :param msg_type: The type of the Message.
        :param response_type: The type of the Response.
        :param payload: The payload to send.
        :param timeout_secs: The timeout in seconds for each atempt.
        :param max_attempts: The maximum number of attempts.
        :return:  The ACK response.

        Usually used for Get messages.
        """
        if payload is None:
            payload = {}
        msg = msg_type(
            target_addr=self._mac_addr, source_id=self._source_id,
            seq_num=self._seq_next(),
            payload=payload, ack_requested=False, response_requested=True)
        return await self._try_sending(
            msg, response_type, timeout_secs=timeout_secs, max_attempts=max_attempts)

    async def _req_with_ack_resp(
            self, msg_type: Type[Message], response_type: Type[GenericResponse],
            payload: Dict[str, str],
            *,
            timeout_secs: Optional[int]=None,
            max_attempts: Optional[int]=None) -> GenericResponse:
        """
        Send a message and expect an ACK and a response.

        :param msg_type: The type of the Message.
        :param response_type: The type of the Response.
        :param payload: The payload to send.
        :param timeout_secs: The timeout in seconds for each atempt.
        :param max_attempts: The maximum number of attempts.
        :return:  The ACK response.

        FIXME: Not currently implemented, although the LIFX LAN protocol supports
        this kind of workflow natively.
        """
        msg = msg_type(
            target_addr=self._mac_addr, source_id=self._source_id,
            seq_num=self._seq_next(),
            payload=payload, ack_requested=True, response_requested=True)
        return await self._try_sending(
            msg, response_type, timeout_secs=timeout_secs, max_attempts=max_attempts)

    #
    #                            Attribute Methods
    #
    async def get_label(self) -> str:
        """
        Get the label.

        :return: The current label.
        """
        label = self._label  # type: Optional[str]
        if label is None:
            resp = await self._req_with_resp(
                msgtypes.GetLabel, msgtypes.StateLabel)  # type: msgtypes.StateLabel
            self._label = resp.label.decode().replace("\x00", "")
        assert self._label is not None
        return self._label

    async def set_label(self, value: str) -> None:
        """
        Set the label.

        :param value: The new label.
        """
        if len(value) > 32:
            value = value[:32]
        await self._req_with_ack(msgtypes.SetLabel, {"label": value})
        self._label = value

    async def get_location(self) -> str:
        """
        Get the location.

        :return: The current location.
        """

        location = self._location  # type: Optional[str]
        if location is None:
            resp = await self._req_with_resp(
                msgtypes.GetLocation,
                msgtypes.StateLocation)  # type: msgtypes.StateLocation
            self._location = resp.label.decode().replace("\x00", "")
        assert self._location is not None
        return self._location

    # async def set_location(self, value):
    #     resp = await self.req_with_ack(SetLocation, {"location": value})
    #     self.resp_set_location(resp)
    #     return self.location

    async def get_group(self) -> str:
        """
        Get the group.

        :return: The current group
        """
        group = self._group  # type: Optional[str]
        if group is None:
            resp = await self._req_with_resp(
                msgtypes.GetGroup, msgtypes.StateGroup)  # type: msgtypes.StateGroup
            self._group = resp.label.decode().replace("\x00", "")
        assert self._group is not None
        return self._group

    # async def set_group(self, value):
    #     resp = await self.req_with_ack(SetGroup, {"group": value})
    #     self.resp_set_group(resp)
    #     return self.group

    async def get_power(self) -> Power:
        """
        Get the power setting.

        :return: The current power setting. Should normally be True or False.
        """
        table = {
            0: False,
            65535: True,
        }
        resp = await self._req_with_resp(
            msgtypes.GetPower, msgtypes.StatePower)  # type: msgtypes.StatePower
        self._power_level = table.get(resp.power_level, resp.power_level)
        assert self._power_level is not None
        return self._power_level

    async def set_power(self, value: Power, rapid: bool=False) -> None:
        """
        Set the current Power level.

        :param value: Normally True or False.
        :param rapid: If True then we don't wait for an ACK.
        """
        on = [True, 1, "on"]
        off = [False, 0, "off"]

        if value in on:
            value = 65535
        elif value in off:
            value = 0

        if not rapid:
            await self._req_with_ack(msgtypes.SetPower, {"power_level": value})
        else:
            self._fire_and_forget(msgtypes.SetPower, {"power_level": value})
        self._power_level = value

    async def get_wifi_firmware(self) -> Tuple[str, int]:
        """
        Get the WIFI Firmware version.

        :return: A tuple containing (version, timestamp).
        """
        wifi_firmware_version = self._wifi_firmware_version  # type: Optional[str]
        if wifi_firmware_version is None:
            resp = await self._req_with_resp(
                msgtypes.GetWifiFirmware,
                msgtypes.StateWifiFirmware)  # type: msgtypes.StateWifiFirmware
            self._wifi_firmware_version = (
                str(str(resp.version >> 16) + "." + str(resp.version & 0xff))
            )
            self._wifi_firmware_build_timestamp = resp.build
        assert self._wifi_firmware_version is not None
        assert self._wifi_firmware_build_timestamp is not None
        return self._wifi_firmware_version, self._wifi_firmware_build_timestamp

    async def get_wifi_info(self) -> msgtypes.StateWifiInfo:
        """
        Get the WIFI information.

        :return:The WIFI information.
        """
        return await self._req_with_resp(
            msgtypes.GetWifiInfo, msgtypes.StateWifiInfo)

    async def get_host_firmware(self) -> Tuple[str, int]:
        """
        Get the host Firmware version.

        :return: A tuple containing (version, timestamp).
        """
        host_firmware_version = self._host_firmware_version  # type: Optional[str]
        if host_firmware_version is None:
            resp = await self._req_with_resp(
                msgtypes.GetHostFirmware,
                msgtypes.StateHostFirmware)  # type: msgtypes.StateHostFirmware
            self._host_firmware_version = (
                str(str(resp.version >> 16) + "." + str(resp.version & 0xff))
            )
            self._host_firmware_build_timestamp = resp.build
        assert self._host_firmware_version is not None
        assert self._host_firmware_build_timestamp is not None
        return self._host_firmware_version, self._host_firmware_build_timestamp

    async def get_host_info(self) -> msgtypes.StateInfo:
        """
        Get the host information.

        :return: The host information.
        """
        return await self._req_with_resp(msgtypes.GetInfo, msgtypes.StateInfo)

    async def get_version(self) -> Tuple[int, int, int]:
        """
        Get the version information.

        :return: A tuple containing (vendor, product, version).
        """
        vendor = self._vendor  # type: Optional[int]
        if vendor is None:
            resp = await self._req_with_resp(
                msgtypes.GetVersion,
                msgtypes.StateVersion)  # type: msgtypes.StateVersion
            self._vendor = resp.vendor
            self._product = resp.product
            self._version = resp.version
        assert self._vendor is not None
        assert self._product is not None
        assert self._version is not None
        return self._vendor, self._product, self._version

    async def get_metadata(self, *, loop: aio.AbstractEventLoop) -> None:
        """
        Get and cache all meta data for light.

        :param loop: The asyncio event loop.

        This is a shortcut for running the following functions concurrently and
        waiting for all of them to return:

        * ``self.get_label()``
        * ``self.get_location()``
        * ``self.get_version()``
        * ``self.get_group()``
        * ``self.get_wifi_firmware()``
        * ``self.get_host_firmware()``
        """
        coroutines = [
            self.get_label(),
            self.get_location(),
            self.get_version(),
            self.get_group(),
            self.get_wifi_firmware(),
            self.get_host_firmware(),
        ]  # type: List[Awaitable]
        await aio.gather(*coroutines, loop=loop)

    #
    #                            Formatting
    #
    def device_characteristics_str(self, indent: str) -> str:
        """
        Get a multi-line string with the light characteristics.

        :param indent: Prefix for each lines.
        :return: The resultant string.
        """
        s = "{}\n".format(self._label)
        s += indent + "MAC Address: {}\n".format(self._mac_addr)
        s += indent + "IP Address: {}\n".format(self._ip_addr)
        s += indent + "Port: {}\n".format(self._port)
        s += indent + "Power: {}\n".format(_str_map(self._power_level))
        s += indent + "Location: {}\n".format(self._location)
        s += indent + "Group: {}\n".format(self._group)
        return s

    def device_firmware_str(self, indent: str) -> str:
        """
        Get a multi-line string with the firmware information.

        :param indent: Prefix for each line.
        :return: The resultant string.
        """
        host_build_ns = self._host_firmware_build_timestamp
        if host_build_ns is not None:
            host_build_s = str(
                datetime.datetime.utcfromtimestamp(host_build_ns / 1000000000))
        else:
            host_build_s = "None"

        wifi_build_ns = self._wifi_firmware_build_timestamp
        if wifi_build_ns is not None:
            wifi_build_s = str(
                datetime.datetime.utcfromtimestamp(wifi_build_ns / 1000000000))
        else:
            wifi_build_s = "None"

        s = "Host Firmware Build Timestamp: {} ({} UTC)\n".format(host_build_ns, host_build_s)
        s += indent + "Host Firmware Build Version: {}\n".format(self._host_firmware_version)
        s += indent + "Wifi Firmware Build Timestamp: {} ({} UTC)\n".format(wifi_build_ns, wifi_build_s)
        s += indent + "Wifi Firmware Build Version: {}\n".format(self._wifi_firmware_version)
        return s

    def device_product_str(self, indent: str) -> str:
        """
        Get a multi-line string with the product information.

        :param indent: Prefix for each line.
        :return: The resultant string.
        """
        s = "Vendor: {}\n".format(self._vendor)
        s += indent + "Product: {}\n".format((self._product and product_map[self._product]) or "Unknown")
        s += indent + "Version: {}\n".format(self._version)
        return s

    @staticmethod
    def device_time_str(resp: msgtypes.StateInfo, indent: str="  ") -> str:
        """
        Get a multi-line string for the light information.

        :param resp: The light information.
        :param indent: Prefix for each line.
        :return: The resultant string.
        """
        dev_time = resp.time
        dev_uptime = resp.uptime
        dev_downtime = resp.downtime

        if dev_time is not None:
            time_s = str(datetime.datetime.utcfromtimestamp(dev_time / 1000000000))
        else:
            time_s = "None"

        if dev_uptime is not None:
            uptime_s = str(round(_nanosec_to_hours(dev_uptime), 2))
        else:
            uptime_s = "None"

        if dev_downtime is not None:
            downtime_s = str(round(_nanosec_to_hours(dev_downtime), 2))
        else:
            downtime_s = "None"

        s = "Current Time: {} ({} UTC)\n".format(dev_time, time_s)
        s += indent + "Uptime (ns): {} ({} hours)\n".format(dev_uptime, uptime_s)
        s += indent + "Last Downtime Duration +/-5s (ns): {} ({} hours)\n".format(
            dev_downtime, downtime_s)
        return s

    @staticmethod
    def device_radio_str(resp: msgtypes.StateWifiInfo, indent: str="  ") -> str:
        """
        Get a multi-line string for the wifi information.

        :param resp: The wifi information.
        :param indent: Prefix for each line.
        :return: The resultant string.
        """
        signal = resp.signal
        tx = resp.tx
        rx = resp.rx
        s = "Wifi Signal Strength (mW): {}\n".format(signal)
        s += indent + "Wifi TX (bytes): {}\n".format(tx)
        s += indent + "Wifi RX (bytes): {}\n".format(rx)
        return s

    def __str__(self) -> str:
        """ Print identification. """
        return "{} ({})".format(self._label, self.mac_addr)

    def __repr__(self) -> str:
        """ Print identification. """
        return "<{} {} ({})>".format(type(self).__name__, self._label, self.mac_addr)

    async def get_light_power(self) -> Power:
        """
        Get the light's power setting.

        :return: The light's power setting.
        """
        table = {
            0: False,
            65535: True,
        }
        resp = await self._req_with_resp(
            msgtypes.LightGetPower,
            msgtypes.LightStatePower)  # type: msgtypes.LightStatePower
        self._power_level = table.get(resp.power_level, resp.power_level)
        assert self._power_level is not None
        return self._power_level

    async def set_light_power(self, value: Power, duration: int=0, rapid: bool=False) -> None:
        """
        Ste the light's power setting.

        :param value: The new power setting.
        :param duration: The duration in ms to gradually make the change.
        :param rapid: If True then we don't wait for an ACK.
        """
        on = [True, 1, "on"]
        off = [False, 0, "off"]

        if value in on:
            value = 65535
        elif value in off:
            value = 0

        if not rapid:
            await self._req_with_ack(
                msgtypes.LightSetPower, {"power_level": value, "duration": duration})
        else:
            self._fire_and_forget(
                msgtypes.LightSetPower, {"power_level": value, "duration": duration},
                num_repeats=1)
        self._power_level = value

    async def get_color(self) -> Color:
        """
        Get the color of the light.

        :return: The color of the light.
        """
        resp = await self._req_with_resp(
            msgtypes.LightGet, msgtypes.LightState)  # type: msgtypes.LightState

        table = {
            0: False,
            65535: True,
        }
        self._power_level = table.get(resp.power_level, resp.power_level)
        self._color = Color.create_from_values(resp.color)
        self._label = resp.label.decode().replace("\x00", "")

        return self._color

    async def set_color(self, color: Color, duration: int=0, rapid: bool=False) -> None:
        """
        Set the color of the light.

        :param color: Input colour.
        :param duration: Time to make change in ms.
        :param rapid: If True then we don't wait for an ACK.
        :return: The new color of the light.
        """
        value = color.get_values()
        if rapid:
            self._fire_and_forget(
                msgtypes.LightSetColor,
                {"color": value, "duration": duration},
                num_repeats=1)
        else:
            await self._req_with_ack(
                msgtypes.LightSetColor,
                {"color": value, "duration": duration})
        self._color = color

    async def get_color_zones(
            self, start_index: int, end_index: Optional[int]=None) -> List[Color]:
        """
        Get color zones.

        :param start_index: The start index.
        :param end_index: The end Index.
        """
        if end_index is None:
            end_index = start_index + 8
        args = {
            "start_index": start_index,
            "end_index": end_index,
        }
        resp = await self._req_with_resp(
            msgtypes.MultiZoneGetColorZones,
            msgtypes.MultiZoneStateMultiZone,
            payload=args)  # type: msgtypes.MultiZoneStateMultiZone

        self._color_zones = []
        for HSBK in resp.color:   # type: Tuple[int, int, int, int]
            self._color_zones.append(Color.create_from_values(HSBK))

        return self._color_zones

    async def set_color_zones(
            self, start_index: int, end_index: int, color: Color,
            duration: int=0, apply: int=1, rapid: bool=False) -> None:
        """
        Set color zones.

        :param start_index:  The start index.
        :param end_index: The end index,
        :param color: The colour.
        :param duration: The duration in ms.
        :param apply: The apply value.
        :param rapid: If True then we don't wait for an ACK.
        """
        args = {
            "start_index": start_index,
            "end_index": end_index,
            "color": color.get_values(),
            "duration": duration,
            "apply": apply,
        }

        if rapid:
            self._fire_and_forget(
                msgtypes.MultiZoneSetColorZones, args, num_repeats=1)
        else:
            await self._req_with_ack(
                msgtypes.MultiZoneSetColorZones, args)

    async def set_waveform(
            self, *,
            color: Color,
            transient: int, period: int, cycles: int, duty_cycle: int, waveform: int,
            rapid: bool=False) -> None:
        """
        Set the Wave form.

        :param color: The color used.
        :param transient: The Transient value.
        :param period: The period in ms.
        :param cycles: The number of cycles.
        :param duty_cycle: The number of duty cycles.
        :param waveform: The waveform value.
        :param rapid: If True then we don't wait for an ACK.
        """
        value = {
            'color': color.get_values(),
            'transient': transient,
            'period': period,
            'cycles': cycles,
            'duty_cycle': duty_cycle,
            'waveform': waveform,
        }

        if rapid:
            self._fire_and_forget(
                msgtypes.LightSetWaveform, value, num_repeats=1)
        else:
            await self._req_with_ack(
                msgtypes.LightSetWaveform, value)

    async def get_infrared(self) -> int:
        """
        Get infra-red brightness.
        :return: Number 0-100.
        """
        resp = await self._req_with_resp(
            msgtypes.LightGetInfrared,
            msgtypes.LightStateInfrared)  # type: msgtypes.LightStateInfrared
        self._infrared_brightness = int(resp.infrared_brightness * 100 / 65535)
        return self._infrared_brightness

    async def set_infrared(self, infrared_brightness: int, rapid: bool=False) -> None:
        """
        Set infra-red brightness.

        :param infrared_brightness:  Number 0-100.
        :param rapid: If True then we don't wait for an ACK.
        """
        value = int(infrared_brightness * 65535 / 100)
        if rapid:
            self._fire_and_forget(
                msgtypes.LightSetInfrared, {"infrared_brightness": value}, num_repeats=1)
        else:
            await self._req_with_ack(
                msgtypes.LightSetInfrared, {"infrared_brightness": value})
        self._infrared_brightness = value


class LifxDiscovery:

    def __init__(
            self, *,
            loop: aio.AbstractEventLoop
            ) -> None:
        self._loop = loop
        self._protocols = []  # type: List['LifxDiscoveryProtocol']

    def start_discover(
            self,
            ipv6prefix: Optional[str]=None,
            discovery_interval: int=DISCOVERY_INTERVAL,
            discovery_step: int=DISCOVERY_STEP) -> None:
        """
        Get the Task that will discoveries.

        :param ipv6prefix: The IPv6 prefix to use for IPv6 addresses.
        :param discovery_interval: How often should we rerun discover (seconds)?
        :param discovery_step: How often should we wake up (seconds)?
        :return: None
        """
        def lifx_discovery() -> aio.BaseProtocol:
            """ Construct an LIFX discovery protocol handler. """
            protocol = LifxDiscoveryProtocol(
                loop=self._loop,
                ipv6prefix=ipv6prefix,
                discovery_interval=discovery_interval,
                discovery_step=discovery_step,
            )
            self._register_protocol(protocol)
            return protocol

        coro = self._loop.create_datagram_endpoint(
            lifx_discovery,
            local_addr=('0.0.0.0', UDP_BROADCAST_PORT),
        )
        self._loop.create_task(coro)
        return

    def _register_protocol(self, protocol: 'LifxDiscoveryProtocol') -> None:
        self._protocols.append(protocol)

    def get_lights(self) -> Lights:
        lights = [light for protocol in self._protocols for light in protocol.get_lights()]
        return Lights(self._loop, lights)


class LifxDiscoveryProtocol(aio.DatagramProtocol):
    """ A protocol handler that discovers Lifx Lights. """

    def __init__(
            self, *,
            loop: aio.AbstractEventLoop,
            ipv6prefix: Optional[str]=None,
            discovery_interval: int=DISCOVERY_INTERVAL,
            discovery_step: int=DISCOVERY_STEP) -> None:
        """
        Construct an `LifxDiscovery` object.

        :param loop: The asyncio event loop.
        :param lights: The lights object to contain lights.
        :param ipv6prefix: The IPv6 prefix to use for IPv6 addresses.
        :param discovery_interval: How often should we rerun discover (seconds)?
        :param discovery_step: How often should we wake up (seconds)?
        """
        self._seen = {}  # type: Dict[str, Light]
        self._transport = None  # type: Optional[aio.DatagramTransport]
        self._loop = loop
        self._source_id = random.randint(0, (2 ** 32) - 1)
        self._ipv6prefix = ipv6prefix
        self._discovery_interval = discovery_interval
        self._discovery_step = discovery_step
        self._discovery_countdown = 0

    def get_lights(self) -> List[Light]:
        return list(self._seen.values())

    def connection_made(self, transport: aio.BaseTransport) -> None:
        """ Called when we receive a connection. """
        self._transport = cast(aio.DatagramTransport, transport)
        sock = self._transport.get_extra_info("socket")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._loop.call_soon(self._discover)

    def datagram_received(self, data: Union[bytes, Text], addr: Tuple[str, int]) -> None:
        """ Called when we receive a packet. """
        assert isinstance(data, bytes)
        response = unpack_lifx_message(data)
        ip_addr = addr[0]

        mac_addr = response.target_addr
        if mac_addr == BROADCAST_MAC:
            return

        if type(response) == msgtypes.StateService:
            # discovered
            assert isinstance(response, msgtypes.StateService)
            if response.service == 1:  # only look for UDP services
                remote_port = response.port
            else:
                return
        elif type(response) == msgtypes.LightState:
            # looks like the lights are volunteering LightState after booting
            remote_port = UDP_BROADCAST_PORT
        else:
            return

        if self._ipv6prefix:
            family = socket.AF_INET6
            remote_ip = _mac_to_ipv6_link_local(mac_addr, self._ipv6prefix)
        else:
            family = socket.AF_INET
            remote_ip = ip_addr

        if mac_addr in self._seen:
            # rediscovered
            light = self._seen[mac_addr]  # type: Light
            logger.debug("Rediscovered light %s", light)
        else:
            # newly discovered
            light = Light(
                loop=self._loop,
                mac_addr=mac_addr,
                ip_addr=remote_ip,
                port=remote_port,
            )
            self._seen[mac_addr] = light
            logger.debug("Discovered light %s", light)
        light.renew(family=family, ip_addr=remote_ip, port=remote_port)

    def _discover(self) -> None:
        """ Called regularly based on ``discovery_step`` parameter. """

        if self._transport:
            assert self._transport is not None

            try:
                new_seen = {}  # type: Dict[str, Light]
                for mac_addr, light in self._seen.items():
                    if light.is_alive():
                        new_seen[mac_addr] = light
                    else:
                        logger.info("Dropping light %s", light)
                self._seen = new_seen

                if self._discovery_countdown <= 0:
                    self._discovery_countdown = self._discovery_interval
                    logger.debug("Sending discovery packet")
                    msg = msgtypes.GetService(
                        target_addr=BROADCAST_MAC, source_id=self._source_id,
                        seq_num=0, payload={},
                        ack_requested=False, response_requested=True)
                    self._transport.sendto(msg.generate_packed_message(), (UDP_BROADCAST_IP, UDP_BROADCAST_PORT))
                else:
                    self._discovery_countdown -= self._discovery_step

            except Exception:
                logger.exception("An error occured in _discover()")
            finally:
                self._loop.call_later(self._discovery_step, self._discover)

    def _cleanup(self) -> None:
        """ Cleanup. FIXME: Is the actually used??? """
        if self._transport:
            self._transport.close()
            self._transport = None
        for light in self._seen.values():
            light.cleanup()
        self._seen = {}

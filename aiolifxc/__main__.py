#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# This application is an example on how to use aiolifx
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
import logging
import sys
from typing import List, Optional  # noqa

import aiolifxc as alix

UDP_BROADCAST_PORT = 56700

""" Simple light control from console. """


class Selected:
    def __init__(self) -> None:
        self.lights = None  # type: Optional[alix.Lights]


def read_in(
        *,
        loop: aio.AbstractEventLoop,
        lights: alix.Lights,
        selected: Selected) -> None:
    """Reading from stdin and displaying menu"""

    selection = sys.stdin.readline().strip("\n")
    loop.create_task(read_in_process(
        selection=selection,
        lights=lights,
        selected=selected))


async def read_in_process(
        *, selection: str, lights: alix.Lights, selected: Selected) -> None:

    light_list = list(lights)  # type: List[alix.Light]
    light_list.sort(key=lambda x: x.mac_addr)

    lov = [x for x in selection.split(" ") if x != ""]
    if lov:
        if selected.lights is not None:

            # try:
            if True:
                if int(lov[0]) == 0:
                    selected.lights = None
                elif int(lov[0]) == 1:
                    if len(lov) > 1:
                        try:
                            await selected.lights.set_power(lov[1].lower() in ["1", "on", "true"])
                            selected.lights = None
                        except alix.LightOffline:
                            print("Error: Light is offline")
                    else:
                        print("Error: For power you must indicate on or off\n")
                elif int(lov[0]) == 2:
                    if len(lov) > 2:
                        try:
                            color = alix.Color(
                                hue=0,
                                saturation=0,
                                brightness=int(lov[1]),
                                kelvin=int(lov[2]),
                            )
                            await selected.lights.set_color(color)

                            selected.lights = None
                        except (IndexError, ValueError):
                            print("Error: For white brightness (0-100) and temperature (2500-9000) must be numbers.\n")
                    else:
                        print("Error: For white you must indicate brightness (0-100) and temperature (2500-9000)\n")
                elif int(lov[0]) == 3:
                    if len(lov) > 3:
                        try:
                            color = alix.Color(
                                hue=int(lov[1]),
                                saturation=int(lov[2]),
                                brightness=int(lov[3]),
                                kelvin=3500,
                            )
                            await selected.lights.set_color(color)
                            selected.lights = None
                        except (IndexError, ValueError):
                            print("Error: For colour hue (0-360), "
                                  "saturation (0-100) and brightness (0-100) "
                                  "must be numbers.\n")
                    else:
                        print("Error: For colour you must indicate hue (0-360), "
                              "saturation (0-100) and brightness (0-100)\n")

                elif int(lov[0]) == 4:
                    for device in selected.lights:
                        await device.get_power()
                        await device.get_group()
                        await device.get_location()
                        await device.get_version()
                        print(device.device_characteristics_str("    "))
                        print(device.device_product_str("    "))
                    selected.lights = None
                elif int(lov[0]) == 5:
                    for device in selected.lights:
                        await device.get_host_firmware()
                        await device.get_wifi_firmware()
                        print(device.device_firmware_str("   "))
                    selected.lights = None
                elif int(lov[0]) == 6:
                    for device in selected.lights:
                        wifi_info = await device.get_wifi_info()
                        print(device.device_radio_str(wifi_info))
                    selected.lights = None
                elif int(lov[0]) == 7:
                    for device in selected.lights:
                        host_info = await device.get_host_info()
                        print(device.device_time_str(host_info))
                    selected.lights = None
                elif int(lov[0]) == 8:
                    if len(lov) > 3:
                        try:
                            color = alix.Color(
                                hue=int(lov[1]),
                                saturation=int(lov[2]),
                                brightness=int(lov[3]),
                                kelvin=3500,
                            )
                            await selected.lights.set_waveform(
                                color=color,
                                transient=1,
                                period=100,
                                cycles=30,
                                duty_cycle=0,
                                waveform=0
                            )
                            selected.lights = None
                        except (IndexError, ValueError):
                            print("Error: For pulse hue (0-360), "
                                  "saturation (0-100) and brightness (0-100) "
                                  "must be numbers.\n")
                    else:
                        print("Error: For pulse you must indicate hue (0-360),"
                              "saturation (0-100) and brightness (0-100))\n")
        else:

            if lov[0] == 'group':
                selected.lights = lights.get_by_group(lov[1])
            elif lov[0] == 'label':
                selected.lights = lights.get_by_label(lov[1])
            else:
                try:

                    index = int(lov[0])
                    if index > 0:
                        if index <= len(light_list):
                            selected.lights = lights.get_by_mac_addr(light_list[index-1].mac_addr)
                        else:
                            print("\nError: Not a valid selection.\n")

                except (IndexError, ValueError):
                    print("\nError: Selection must be a number.\n")

    if selected.lights is not None:
        print("Select Function for {}:".format(", ".join([str(d) for d in selected.lights])))
        print("\t[1]\tPower (0 or 1)")
        print("\t[2]\tWhite (Brightness Temperature)")
        print("\t[3]\tColour (Hue Saturation Value)")
        print("\t[4]\tInfo")
        print("\t[5]\tFirmware")
        print("\t[6]\tWifi")
        print("\t[7]\tUptime")
        print("\t[8]\tPulse")
        print("")
        print("\t[0]\tBack to light selection")
    else:
        idx = 1
        print("Select Bulb:")
        for x in lights:
            print("\t[{}]\t{}\t{}\t{}".format(idx, x.label, x.mac_addr, x.group))
            idx += 1
        print("")
        print("Alternatively type 'group <group>' or 'label <label>' to select a number of lights.")

    print("")
    print("Your choice: ", end='', flush=True)


def main() -> None:
    """ Main CLI function. """
    logging.basicConfig(level=logging.DEBUG)
    loop = aio.get_event_loop()
    selected = Selected()

    discovery = alix.LifxDiscovery(loop=loop)
    discovery.start_discover()

    def read_in_wrapper() -> None:
        lights = discovery.get_lights()
        read_in(loop=loop, lights=lights, selected=selected)

    loop.add_reader(sys.stdin.fileno(), read_in_wrapper)

    try:
        print("Hit \"Enter\" to start")
        print("Use Ctrl-C to quit")
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("Got exception %s" % e)
    finally:
        loop.remove_reader(sys.stdin.fileno())
        loop.close()


main()

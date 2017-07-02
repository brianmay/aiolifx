========
AioLifxC
========

.. image:: https://img.shields.io/pypi/v/aiolifxc.svg
        :target: https://pypi.python.org/pypi/aiolifxc

.. image:: https://img.shields.io/travis/brianmay/aiolifxc.svg
        :target: https://travis-ci.org/brianmay/aiolifxc

.. image:: https://readthedocs.org/projects/aiolifxc/badge/?version=latest
        :target: https://aiolifxc.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/brianmay/aiolifxc/shield.svg
     :target: https://pyup.io/repos/github/brianmay/aiolifxc/
     :alt: Updates

AioLifxC is a Python 3/asyncio library to control Lifx LED lightbulbs over your LAN.

Most of it was originally taken from the
`Meghan Clarkk lifxlan package <https://github.com/mclarkk/lifxlan>`_
and adapted to Python 3 (and asyncio obviously)

This is a fork from
`François Wautier's package <https://github.com/frawau/aiolifx>`_.
It uses coroutines as opposed to callbacks. If you prefer callbacks,
please see his implementation instead. This was forked from version 0.5.0.

This should be considered Alpha status. While it works, and seems to work
well, there are still changes I wish to make that may break the API.

Installation
------------

We are on PyPi so::

     pip3 install aiolifxc

or::

     python3 -m pip install aiolifxc

How to use
----------

In essence, the test program is this::

    def readin():
    """Reading from stdin and displaying menu"""

        selection = sys.stdin.readline().strip("\n")
        DoSomething()

    loop = aio.get_event_loop()
    devices = Devices(loop=loop)

    loop.add_reader(sys.stdin, readin)

    server = devices.start_discover()

    try:
        loop.run_forever()
    except Exception as e:
        print("Got exception %s" % e)
    finally:
        server.cancel()
        loop.remove_reader(sys.stdin)
        loop.close()

Other things worth noting:

    -  Whilst LifxDiscover uses UDP broadcast, the bulbs are
       connected with Unicast UDP

    - The socket connecting to a bulb is not closed unless the bulb is deemed to have
      gone the way of the Dodo. I've been using that for days with no problem

    - You can select to used IPv6 connection to the bulbs by passing an
      IPv6 prefix to LifxDiscover. It's only been tried with /64 prefix.
      If you want to use a /48 prefix, add ":" (colon) at the end of the 
      prefix and pray. (This means 2 colons at the end!)

    - I only have Original 1000, so I could not test with other types
      of bulbs

    - Unlike in lifxlan, set_waveform takes a dictionary with the right 
      keys instead of all those parameters


#
# This file is part of LUNA.
#
# Copyright (c) 2020 Great Scott Gadgets <info@greatscottgadgets.com>
# SPDX-License-Identifier: BSD-3-Clause

""" TinyFPGA Platform definitions.

This is a non-core platform. To use it, you'll need to set your LUNA_PLATFORM variable:

    > export LUNA_PLATFORM="luna_boards.tinyfpga:TinyFPGABxPlatform"
"""

import os
import subprocess


from nmigen import Elaboratable, ClockDomain, Module, ClockSignal, Instance, Signal, Const
from nmigen.build import Resource, Subsignal, Pins, Attrs, Clock, Connector, PinsN
from nmigen.vendor.lattice_ice40 import LatticeICE40Platform

from luna.gateware.platform.core import LUNAPlatform


class TinyFPGABxDomainGenerator(Elaboratable):
    """ Creates clock domains for the TinyFPGA Bx. """

    def __init__(self, *, clock_frequencies=None, clock_signal_name=None):
        pass

    def elaborate(self, platform):
        m = Module()

        # Create our domains...
        m.domains.sync   = ClockDomain()
        m.domains.sync24 = ClockDomain()

        m.domains.usb    = ClockDomain()
        m.domains.usb_io = ClockDomain()
        m.domains.fast   = ClockDomain()

        # ... create our 48 MHz USB clock...
        m.submodules.pll = Instance("SB_PLL40_CORE",
            i_REFERENCECLK  = platform.request(platform.default_clk),
            i_RESETB        = Const(1),
            i_BYPASS        = Const(0),

            o_PLLOUTCORE    = ClockSignal("sync"),

            # Create a 48 MHz PLL clock...
            p_FEEDBACK_PATH = "SIMPLE",
            p_DIVR          = 0,
            p_DIVF          = 47,
            p_DIVQ          = 4,
            p_FILTER_RANGE  = 1,
        )

        # We'll use our 48MHz clock for everything _except_ the usb domain...
        m.d.comb += [
            ClockSignal("usb_io")  .eq(ClockSignal("sync")),
            ClockSignal("fast")    .eq(ClockSignal("sync"))
        ]

        # HACK: Generate a 12MHz clock out of logic.
        # This is generically not a great idea, but it's actually what Lattice recommends
        # (TN1008), so who are we to judge? [Submit your answers to /dev/null, please.]
        m.d.sync   += ClockSignal("sync24")  .eq(~ClockSignal("sync24"))
        m.d.sync24 += ClockSignal("usb")     .eq(~ClockSignal("usb"))

        return m


class TinyFPGABxPlatform(LatticeICE40Platform, LUNAPlatform):
    device      = "iCE40LP8K"
    package     = "CM81"
    default_clk = "clk16"
    name        = "TinyFPGA Bx"


    # Provide the type that'll be used to create our clock domains.
    clock_domain_generator = TinyFPGABxDomainGenerator

    # We only have a direct connection on our USB lines, so use that for USB comms.
    default_usb_connection = "usb"

    resources   = [
        Resource("clk16", 0, Pins("B2", dir="i"),
                 Clock(16e6), Attrs(IO_STANDARD="SB_LVCMOS")),

        Resource("led", 0, Pins("B3"), Attrs(IO_STANDARD="SB_LVCMOS")),

        Resource("usb", 0,
            Subsignal("d_p",    Pins("B4", dir="io")),
            Subsignal("d_n",    Pins("A4", dir="io")),
            Subsignal("pullup", Pins("A3", dir="o")),
            Attrs(IO_STANDARD="SB_LVCMOS")
        ),
    ]
    connectors  = [
        Connector("gpio", 0,
            # Left side of the board
            #     1  2  3  4  5  6  7  8  9 10 11 12 13
             "   A2 A1 B1 C2 C1 D2 D1 E2 E1 G2 H1 J1 H2 "
            # Right side of the board
            #          14 15 16 17 18 19 20 21 22 23 24
             "         H9 D9 D8 C9 A9 B8 A8 B7 A7 B6 A6 "
            # Bottom of the board
            # 25 26 27 28 29 30 31
             "G1 J3 J4 G9 J9 E8 J2"
        ),
    ]

    def toolchain_program(self, products, name):
        tinyprog = os.environ.get("TINYPROG", "tinyprog")
        with products.extract("{}.bin".format(name)) as bitstream_filename:
            subprocess.check_call([tinyprog, "-p", bitstream_filename])

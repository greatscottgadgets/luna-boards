
#
# This file is part of LUNA.
#
# Copyright (c) 2020 Great Scott Gadgets <info@greatscottgadgets.com>
# SPDX-License-Identifier: BSD-3-Clause

""" ecpix5 platform definitions.

This is a non-core platform. To use it, you'll need to set your LUNA_PLATFORM variable:

    > export LUNA_PLATFORM="luna_boards.ecpix5:ECPIX5_45F_Platform"
    > export LUNA_PLATFORM="luna_boards.ecpix5:ECPIX5_85F_Platform"
"""

from amaranth import *
from amaranth.build import *
from amaranth.vendor.lattice_ecp5 import LatticeECP5Platform

from amaranth_boards.resources import *
from amaranth_boards.ecpix5 import ECPIX545Platform as _ECPIX545Platform
from amaranth_boards.ecpix5 import ECPIX585Platform as _ECPIX585Platform

from luna.gateware.platform.core                  import LUNAPlatform
from luna.gateware.interface.serdes_phy import SerDesPHY, LunaECP5SerDes

__all__ = ["ECPIX5_45F_Platform", "ECPIX5_85F_Platform"]


class ECPIX5DomainGenerator(Elaboratable):
    """ Clock generator for ECPIX5 boards. """

    def __init__(self, *, clock_frequencies=None, clock_signal_name=None):
        pass

    def elaborate(self, platform):
        m = Module()

        # Create our domains.
        m.domains.ss     = ClockDomain()
        m.domains.sync   = ClockDomain()
        m.domains.usb    = ClockDomain()
        m.domains.usb_io = ClockDomain()
        m.domains.fast   = ClockDomain()


        # Grab our clock and global reset signals.
        clk100 = platform.request(platform.default_clk)
        reset  = platform.request(platform.default_rst)

        # Generate the clocks we need for running our SerDes.
        feedback = Signal()
        locked   = Signal()
        m.submodules.pll = Instance("EHXPLLL",

                # Clock in.
                i_CLKI=clk100,

                # Generated clock outputs.
                o_CLKOP=feedback,
                o_CLKOS= ClockSignal("sync"),
                o_CLKOS2=ClockSignal("fast"),

                # Status.
                o_LOCK=locked,

                # PLL parameters...
                p_CLKI_DIV=1,
                p_PLLRST_ENA="DISABLED",
                p_INTFB_WAKE="DISABLED",
                p_STDBY_ENABLE="DISABLED",
                p_DPHASE_SOURCE="DISABLED",
                p_CLKOS3_FPHASE=0,
                p_CLKOS3_CPHASE=0,
                p_CLKOS2_FPHASE=0,
                p_CLKOS2_CPHASE=5,
                p_CLKOS_FPHASE=0,
                p_CLKOS_CPHASE=5,
                p_CLKOP_FPHASE=0,
                p_CLKOP_CPHASE=4,
                p_PLL_LOCK_MODE=0,
                p_CLKOS_TRIM_DELAY="0",
                p_CLKOS_TRIM_POL="FALLING",
                p_CLKOP_TRIM_DELAY="0",
                p_CLKOP_TRIM_POL="FALLING",
                p_OUTDIVIDER_MUXD="DIVD",
                p_CLKOS3_ENABLE="DISABLED",
                p_OUTDIVIDER_MUXC="DIVC",
                p_CLKOS2_ENABLE="ENABLED",
                p_OUTDIVIDER_MUXB="DIVB",
                p_CLKOS_ENABLE="ENABLED",
                p_OUTDIVIDER_MUXA="DIVA",
                p_CLKOP_ENABLE="ENABLED",
                p_CLKOS3_DIV=1,
                p_CLKOS2_DIV=2,
                p_CLKOS_DIV=4,
                p_CLKOP_DIV=5,
                p_CLKFB_DIV=1,
                p_FEEDBK_PATH="CLKOP",

                # Internal feedback.
                i_CLKFB=feedback,

                # Control signals.
                i_RST=reset,
                i_PHASESEL0=0,
                i_PHASESEL1=0,
                i_PHASEDIR=1,
                i_PHASESTEP=1,
                i_PHASELOADREG=1,
                i_STDBY=0,
                i_PLLWAKESYNC=0,

                # Output Enables.
                i_ENCLKOP=0,
                i_ENCLKOS=0,
                i_ENCLKOS2=0,
                i_ENCLKOS3=0,

                # Synthesis attributes.
                a_ICP_CURRENT="12",
                a_LPF_RESISTOR="8"
        )

        # Temporary: USB FS PLL
        feedback    = Signal()
        usb2_locked = Signal()
        m.submodules.fs_pll = Instance("EHXPLLL",

                # Status.
                o_LOCK=usb2_locked,

                # PLL parameters...
                p_PLLRST_ENA="DISABLED",
                p_INTFB_WAKE="DISABLED",
                p_STDBY_ENABLE="DISABLED",
                p_DPHASE_SOURCE="DISABLED",
                p_OUTDIVIDER_MUXA="DIVA",
                p_OUTDIVIDER_MUXB="DIVB",
                p_OUTDIVIDER_MUXC="DIVC",
                p_OUTDIVIDER_MUXD="DIVD",

                p_CLKI_DIV = 20,
                p_CLKOP_ENABLE = "ENABLED",
                p_CLKOP_DIV = 16,
                p_CLKOP_CPHASE = 15,
                p_CLKOP_FPHASE = 0,

                p_CLKOS_DIV = 12,
                p_CLKOS_CPHASE = 0,
                p_CLKOS_FPHASE = 0,


                p_CLKOS2_ENABLE = "ENABLED",
                p_CLKOS2_DIV = 10,
                p_CLKOS2_CPHASE = 0,
                p_CLKOS2_FPHASE = 0,

                p_CLKOS3_ENABLE = "ENABLED",
                p_CLKOS3_DIV = 40,
                p_CLKOS3_CPHASE = 5,
                p_CLKOS3_FPHASE = 0,

                p_FEEDBK_PATH = "CLKOP",
                p_CLKFB_DIV = 6,

                # Clock in.
                i_CLKI=clk100,

                # Internal feedback.
                i_CLKFB=feedback,

                # Control signals.
                i_RST=reset,
                i_PHASESEL0=0,
                i_PHASESEL1=0,
                i_PHASEDIR=1,
                i_PHASESTEP=1,
                i_PHASELOADREG=1,
                i_STDBY=0,
                i_PLLWAKESYNC=0,

                # Output Enables.
                i_ENCLKOP=0,
                i_ENCLKOS2=0,

                # Generated clock outputs.
                o_CLKOP=feedback,
                o_CLKOS2=ClockSignal("usb_io"),
                o_CLKOS3=ClockSignal("usb"),

                # Synthesis attributes.
                a_FREQUENCY_PIN_CLKI="25",
                a_FREQUENCY_PIN_CLKOP="48",
                a_FREQUENCY_PIN_CLKOS="48",
                a_FREQUENCY_PIN_CLKOS2="12",
                a_ICP_CURRENT="12",
                a_LPF_RESISTOR="8",
                a_MFG_ENABLE_FILTEROPAMP="1",
                a_MFG_GMCREF_SEL="2"
        )

        # Control our resets.
        m.d.comb += [
            ClockSignal("ss")      .eq(ClockSignal("sync")),

            ResetSignal("ss")      .eq(~locked),
            ResetSignal("sync")    .eq(~locked),
            ResetSignal("fast")    .eq(~locked),

            ResetSignal("usb")     .eq(~usb2_locked),
            ResetSignal("usb_io")  .eq(~usb2_locked),
        ]

        return m


class ECPIX5SuperSpeedPHY(SerDesPHY):
    """ Superspeed PHY configuration for the ECPIX5. """

    REFCLK_FREQUENCY = 100e6
    SYNC_FREQUENCY   = 125e6
    FAST_FREQUENCY   = 250e6

    SERDES_DUAL    = 0
    SERDES_CHANNEL = 1


    def __init__(self, platform):

        # Grab the I/O that implements our SerDes interface, ensuring our directions are '-',
        # so we don't create any I/O buffering hardware.
        serdes_io_directions = {
            'ch0':    {'tx':"-", 'rx':"-"},
            'ch1':    {'tx':"-", 'rx':"-"},
            'refclk': '-',
        }
        serdes_io      = platform.request("serdes", self.SERDES_DUAL, dir=serdes_io_directions)
        serdes_channel = getattr(serdes_io, f"ch{self.SERDES_CHANNEL}")

        # Create our SerDes interface...
        self.serdes = LunaECP5SerDes(platform,
            sys_clk      = ClockSignal("sync"),
            sys_clk_freq = self.SYNC_FREQUENCY,
            refclk_pads  = serdes_io.refclk,
            refclk_freq  = self.REFCLK_FREQUENCY,
            tx_pads      = serdes_channel.tx,
            rx_pads      = serdes_channel.rx,
            channel      = self.SERDES_CHANNEL
        )

        # ... and use it to create our core PHY interface.
        super().__init__(
            serdes             = self.serdes,
            ss_clk_frequency   = self.SYNC_FREQUENCY,
            fast_clk_frequency = self.FAST_FREQUENCY
        )


    def elaborate(self, platform):
        m = super().elaborate(platform)

        # Patch in our SerDes as a submodule.
        m.submodules.serdes = self.serdes

        return m



class _ECPIXExtensions:

    # Create a reference

    additional_resources = [

        #
        # SerDes pins; necessary to synthesize using Diamond.
        #
        # It doesn't seem like these location values are actually used; but Diamond needs them
        # to be *there*. We'll provide correct ones in case it ever decides to use them.
        #
        Resource("serdes", 0,
            Subsignal("ch0",
                Subsignal("rx", DiffPairs("AF6",  "AF7")),
                Subsignal("tx", DiffPairs("AD7",  "AD8")),
            ),
            Subsignal("ch1",
                Subsignal("rx", DiffPairs("AF9",  "AF10")),
                Subsignal("tx", DiffPairs("AD10", "AD11")),
            ),
            Subsignal("refclk", DiffPairs("AF12", "AF13"))
        ),
        Resource("serdes", 1,
            Subsignal("ch0",
                Subsignal("rx", DiffPairs("AF16",  "AF17")),
                Subsignal("tx", DiffPairs("AD16",  "AD17")),
            ),
            Subsignal("ch1",
                Subsignal("rx", DiffPairs("AF18",  "AF19")),
                Subsignal("tx", DiffPairs("AD19", "AD20")),
            ),
            Subsignal("refclk", DiffPairs("AF21", "AF22"))
        ),

        # XXX: temporary, pmod USB for debugging
        DirectUSBResource(0, d_p="T25", d_n="U25", pullup="U24", attrs=Attrs(IO_TYPE="LVCMOS33")),

        # Aliases for our demonstrations / examples.
        Resource("user_io", 0, Pins("D14", dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 1, Pins("B14", dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 2, Pins("E14", dir="io"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("user_io", 3, Pins("B16", dir="io"), Attrs(IO_TYPE="LVCMOS33")),

        # temporary
        Resource("pmod", 0, Pins("T25 U25 U24 V24 T26 U26 V26 W26", dir="o"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("pmod", 1, Pins("U23 V23 U22 V21 W25 W24 W23 W22", dir="o"), Attrs(IO_TYPE="LVCMOS33")),
    ]



class ECPIX5_45F_Platform(_ECPIX545Platform, _ECPIXExtensions, LUNAPlatform):
    name                   = "ECPIX-5 (45F)"

    clock_domain_generator = ECPIX5DomainGenerator
    default_usb3_phy       = ECPIX5SuperSpeedPHY
    default_usb_connection = "ulpi"

    # Create our semantic aliases.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_resources(self.additional_resources)



class ECPIX5_85F_Platform(_ECPIX585Platform, _ECPIXExtensions, LUNAPlatform):
    name                   = "ECPIX-5 (85F)"

    clock_domain_generator = ECPIX5DomainGenerator
    default_usb3_phy       = ECPIX5SuperSpeedPHY
    default_usb_connection = "ulpi"

    # Create our semantic aliases.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_resources(self.additional_resources)

import os
import subprocess

from nmigen.build import *
from nmigen.vendor.lattice_ice40 import *
from .resources import *


__all__ = ["AlloyPlatform"]

# PMOD pinout primnitives for building modular connectors
PMOD1 = " 9  6  3  48 - -" # 16A,13B,9B,4A
PMOD2 = " 46  44  38  40 - -" # 0A,3B,50B,R2
PMOD3 = " 10 4  2  47 - -" # 18A,8A,6A,2A
PMOD4 = " 42 43  45  41 - -" # 51A,49A,5B,R1

MXPINS = " - - -"


# Alloy : https://github.com/folknology/Alloy
class AlloyPlatform(LatticeICE40Platform):
    device      = "iCE40UP5K"
    package     = "SG48"
    default_clk = "clk25"
    resources   = [
        Resource("clk25", 0, Pins("18", dir="i"),
            Clock(25e6), Attrs(IO_STANDARD="SB_LVCMOS")
        ),

        *LEDResources(pins="39 41 40", attrs=Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1)),
        # Color aliases, pullups helps when signals used beyoud driving leds to get good logic high
        Resource("led_g", 0, Pins("39", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1)),
        Resource("led_y", 0, Pins("41", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1)),
        Resource("led_r", 0, Pins("40", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1)),

        Resource("sck", 0, Pins("15", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("mosi", 0, Pins("17", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("cs", 0, Pins("16", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("miso", 0, Pins("14", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS")),

        # SPIResource(0,
        #     cs="16", clk="15", mosi="17", miso="14",
        #     attrs=Attrs(IO_STANDARD="SB_LVCMOS"), role="device"
        # ),
        #
        # *SPIFlashResources(0, cs="16", clk="15", mosi="17", miso="14", wp="18", hold="19",
        #    attrs=Attrs(IO_STANDARD="SB_LVCMOS")
        # ),

    ]
    connectors = [
        Connector("pmod", 0, PMOD1 + PMOD2),  # PMOD1/2
        Connector("pmod", 1, PMOD3 + PMOD4),  # PMOD3/4
        Connector("mixmod", 0, PMOD1 + MXPINS + PMOD3 + PMOD2 + MXPINS + PMOD4),  # MX1
    ]

    def toolchain_program(self, products, name, port):
        with products.extract("{}.bin".format(name)) as bitstream_filename:
            subprocess.check_call(["cp", bitstream_filename, port])


if __name__ == "__main__":
    from .test.blinky import *
    AlloyPlatform().build(Blinky(), do_program=True)

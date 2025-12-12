try:
    from UT_VectorIdiv import *
except:
    try:
        from VectorIdiv import *
    except:
        from __init__ import *


if __name__ == "__main__":
    dut = DUTVectorIdiv()
    # dut.InitClock("clk")

    # Initialize inputs
    dut.reset.value = 0
    dut.io_flush.value = 0
    dut.io_sign.value = 0
    dut.io_sew.value = 3  # 64-bit lanes

    # Set dividend (don't care for zero-divisor check)
    dut.io_dividend_v.value = int.from_bytes(bytes([1]*16), 'big')

    # Set divisor with zeros in specific lanes to trigger io_d_zero bits
    # Lane mapping (sew=64): [127:64] -> lane1, [63:0] -> lane0
    dut.io_divisor_v.value = 0  # both 64-bit lanes zero -> expect io_d_zero[1:0] = 1

    # Handshake
    dut.io_div_in_valid.value = 1
    dut.io_div_out_ready.value = 1

    # Run a few cycles to complete
    dut.Step(10)

    # Read and print d_zero
    dz = dut.io_d_zero.value
    print(f"io_d_zero = 0x{dz:04x}")

    dut.Finish()

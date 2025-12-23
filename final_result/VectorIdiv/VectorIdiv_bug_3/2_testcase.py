try:
    from UT_VectorIdiv import *
except:
    try:
        from VectorIdiv import *
    except:
        from __init__ import *


if __name__ == "__main__":
    dut = DUTVectorIdiv()
    dut.InitClock("clock")

    # Reset sequence
    dut.reset.value = 1
    dut.Step(2)
    dut.reset.value = 0

    # Configure for 8-bit signed division
    dut.io_sew.value = 0  # 00 -> I8
    dut.io_sign.value = 1  # enable signed mode

    # Handshake
    dut.io_div_out_ready.value = 1

    # Prepare a vector with lane0 = -10 (0xF6), divisor lane0 = 2 (0x02)
    # Pack only lowest 8-bit lane; others zero
    dut.io_dividend_v.value = 0xF6
    dut.io_divisor_v.value = 0x02

    # Launch operation
    dut.io_div_in_valid.value = 1
    dut.Step(5)
    dut.io_div_in_valid.value = 0

    # Run until result appears
    for _ in range(50):
        dut.Step(1)
        if dut.io_div_out_valid.value:
            q = dut.io_div_out_q_v.value & 0xFF  # read lane0
            rem = dut.io_div_out_rem_v.value & 0xFF
            print(f"q0=0x{q:02X}, rem0=0x{rem:02X}")
            break

    dut.Finish()

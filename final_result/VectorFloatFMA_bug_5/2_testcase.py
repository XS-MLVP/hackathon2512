try:
    from UT_VectorFloatFMA import *
except:
    try:
        from VectorFloatFMA import *
    except:
        from __init__ import *

import sys
import struct

def test_bug():
    dut = DUTVectorFloatFMA()
    
    # Reset sequence
    dut.reset.value = 1
    dut.clock.value = 0
    dut.Step(1)
    dut.clock.value = 1
    dut.Step(1)
    dut.reset.value = 0
    
    # Testing FP64 Underflow to Zero
    # The bug seems to be in the FP64 path (PAQS4i4WI5n0 block)
    # where {4'h0, KRYY7i} is used instead of {3'h0, UF, NX}.
    
    print(f"Testing: 2^-600 * 2^-600 + 0 (FP64)")
    
    # 2^-600 in hex.
    # Exponent: -600 + 1023 = 423 = 0x1A7.
    val_fp64 = 0x1A70000000000000
    
    dut.io_fp_a.value = val_fp64
    dut.io_fp_b.value = val_fp64
    dut.io_fp_c.value = 0
    
    # Control signals
    dut.io_fp_format.value = 3 # FP64
    dut.io_op_code.value = 1   # vfmacc (FMA)
    dut.io_round_mode.value = 0 # RNE
    dut.io_is_vec.value = 0 # Scalar
    dut.io_fire.value = 1
    
    # Other signals to 0
    dut.io_widen_a.value = 0
    dut.io_widen_b.value = 0
    dut.io_frs1.value = 0
    dut.io_is_frs1.value = 0
    dut.io_uop_idx.value = 0
    dut.io_res_widening.value = 0
    dut.io_fp_aIsFpCanonicalNAN.value = 0
    dut.io_fp_bIsFpCanonicalNAN.value = 0
    dut.io_fp_cIsFpCanonicalNAN.value = 0

    print(f"Input Hex: {val_fp64:016x}")
    
    # Run simulation
    for i in range(10):
        dut.clock.value = 0
        dut.Step(1)
        dut.clock.value = 1
        dut.Step(1)
        
    # Check result
    res = dut.io_fp_result.value
    fflags = dut.io_fflags.value

    print(f"Result Hex: {res:016x}")
    print(f"FFlags: {fflags:x}")
    
    # Expected: 0 (Underflow)
    if res == 0:
        print("Result is 0 (Expected Underflow)")
    else:
        print(f"Result is {res:016x} (Not 0)")

    # Check fflags
    # Expected: 0x3 (UF | NX) for Element 0
    # Buggy: 0x1 (NX only)
    
    flags_el0 = fflags & 0x1F
    print(f"Element 0 Flags: {flags_el0:x}")
    
    if flags_el0 == 0x3:
        print("FFlags Correct: 0x3 (UF | NX)")
    elif flags_el0 == 0x1:
        print("BUG DETECTED: FFlags is 0x1 (Missing UF)")
    else:
        print(f"FFlags Unexpected: {flags_el0:x}")

if __name__ == "__main__":
    test_bug()
try:
    from UT_VectorFloatFMA import *
except:
    try:
        from VectorFloatFMA import *
    except:
        from __init__ import *

import sys
import struct

def float16_to_int(f):
    # Pack float to 16-bit float (half precision)
    # 'e' is for float16 in struct (Python 3.6+)
    return struct.unpack('<H', struct.pack('<e', f))[0]

def int_to_float16(i):
    return struct.unpack('<e', struct.pack('<H', i))[0]

def test_bug():
    dut = DUTVectorFloatFMA()
    
    # Initialize
    # dut.InitClock("clk") # Commented out in original
    
    # Reset sequence
    dut.reset.value = 1
    dut.clock.value = 0
    dut.Step(1)
    dut.clock.value = 1
    dut.Step(1)
    dut.reset.value = 0
    
    # Prepare inputs for A * B + C
    # Use 1.0 * 1.0 + 1.0
    # Expected: 2.0
    # Buggy: 1.0 * 1.0 - 1.0 = 0.0
    
    val_1_0 = float16_to_int(1.0)
    val_2_0 = float16_to_int(2.0)
    val_0_0 = float16_to_int(0.0)
    
    # Channel 0 is bits 0-15.
    # We set all channels to 1.0 just to be sure, or just channel 0.
    # Let's set channel 0 to 1.0, others to 0.
    
    input_val = val_1_0 # 0x3c00
    
    dut.io_fp_a.value = input_val
    dut.io_fp_b.value = input_val
    dut.io_fp_c.value = input_val
    
    # Control signals
    dut.io_fp_format.value = 1 # Float16
    dut.io_op_code.value = 1   # vfmacc (vd = vs2*vs1 + vd) -> c = a*b + c
    dut.io_round_mode.value = 0 # RNE
    dut.io_is_vec.value = 1
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

    print(f"Testing: 1.0 * 1.0 + 1.0 (Float16)")
    print(f"Input Hex: {input_val:04x}")
    
    # Run simulation
    # Pipeline depth is 4.
    for i in range(10):
        dut.clock.value = 0
        dut.Step(1)
        dut.clock.value = 1
        dut.Step(1)
        
    # Check result
    res = dut.io_fp_result.value
    res_ch0 = res & 0xFFFF
    
    print(f"Result Hex: {res_ch0:04x}")
    print(f"Result Float: {int_to_float16(res_ch0)}")
    
    if res_ch0 == val_0_0:
        print("BUG DETECTED: Result is 0.0 (A*B-C)")
    elif res_ch0 == val_2_0:
        print("PASS: Result is 2.0 (A*B+C)")
    else:
        print(f"FAIL: Unexpected result {res_ch0:04x}")

    dut.Finish()

if __name__ == "__main__":
    test_bug()

import struct
import sys

try:
    from UT_VectorFloatAdder import *
except ImportError:
    try:
        from VectorFloatAdder import *
    except ImportError:
        from __init__ import *

def float_to_hex(f):
    return struct.unpack('<Q', struct.pack('<d', f))[0]

def hex_to_float(h):
    # Ensure h is treated as unsigned 64-bit integer
    h = h & 0xFFFFFFFFFFFFFFFF
    return struct.unpack('<d', struct.pack('<Q', h))[0]

def test_bug_5():
    print("Starting test_bug_5...")
    dut = DUTVectorFloatAdder()
    
    # Reset sequence
    # Use .Set() instead of [0] assignment
    dut.reset.Set(1)
    dut.clock.Set(0)
    dut.Step(1)
    dut.clock.Set(1)
    dut.Step(1)
    dut.reset.Set(0)
    
    # Set inputs according to bug conditions
    # C1: io_op_code = 26 (VFREDOSUM / fsum_ure)
    dut.io_op_code.Set(26)
    
    # C2: io_maskForReduction = 0 (All elements masked)
    dut.io_maskForReduction.Set(0)
    
    # C3: io_round_mode = 0 (RNE - Round to Nearest Even)
    # Note: The bug analysis mentions RDN (2) should return -0.0 and others +0.0.
    # However, the origin RTL implements the INVERSE:
    # {io_round_mode != 3'h2, 63'h0}
    # This means for RNE (0), origin returns -0.0 (1 << 63).
    # The buggy RTL returns +0.0 always.
    # So to detect the bug (difference from origin), we must use a mode != 2.
    dut.io_round_mode.Set(0)
    
    # C4: io_fire = 1 (Pipeline valid)
    dut.io_fire.Set(1)
    
    # Other fixed inputs from spec
    dut.io_widen_a.Set(0)
    dut.io_widen_b.Set(0)
    dut.io_frs1.Set(0)
    dut.io_is_frs1.Set(0)
    dut.io_mask.Set(0)
    dut.io_uop_idx.Set(0)
    dut.io_is_vec.Set(1)
    dut.io_fp_aIsFpCanonicalNAN.Set(0)
    dut.io_fp_bIsFpCanonicalNAN.Set(0)
    dut.io_is_vfwredosum.Set(0)
    dut.io_is_fold.Set(0)
    dut.io_vs2_fold.Set(0) # 128 bits, but Set(0) should work for 0
    
    # Set format to f64.
    # Based on RTL analysis:
    # res_is_f16 = (fp_format == 1)
    # res_is_f32 = (fp_format == 2)
    # F64 result selected by (&fp_format_reg), which implies fp_format == 3 (binary 11).
    dut.io_fp_format.Set(3)
    
    # Set operands
    # Even though we set operands, with mask=0, the result is identity (+/- 0.0).
    val_b = -1.5
    dut.io_fp_b.Set(float_to_hex(val_b))
    
    # fp_a is vector (vs2).
    dut.io_fp_a.Set(float_to_hex(2.5))
    
    print(f"Input B (Accumulator): {val_b}")
    print(f"Input A (Vector): 2.5")
    print("Expectation: With mask=0, result should be identity.")
    print("Origin RTL returns -0.0 for RNE (mode 0). Buggy RTL returns +0.0.")
    
    expected_val = -0.0
    
    # Run cycles
    # Pipeline latency is likely around 2-3 cycles.
    for i in range(10):
        dut.clock.Set(0)
        dut.Step(1)
        dut.clock.Set(1)
        dut.Step(1)
        
        # Read result using AsInt64()
        res = dut.io_fp_result.AsInt64()
        res_float = hex_to_float(res)
        
        print(f"Cycle {i+1}: Result={res_float} (Hex: {hex(res)})")
        
        # Check if result stabilizes to expected value or bug value
        if i > 2:
            # We check the hex value to distinguish +0.0 and -0.0
            # -0.0 is 0x8000000000000000
            # +0.0 is 0x0
            
            if res == 0x8000000000000000:
                print(f"Cycle {i+1}: Result matches expected -0.0.")
            elif res == 0:
                print(f"Potential Bug Detected at Cycle {i+1}: Expected -0.0 (0x8000000000000000), Got +0.0 (0x0)")
                # We continue to see if it persists, but usually it does.
            else:
                 print(f"Cycle {i+1}: Unexpected result {res_float} ({hex(res)})")

    # Final check
    final_res = dut.io_fp_result.AsInt64()
    # The bug is that it returns +0.0 (0x0) when it should return -0.0 (0x8000000000000000)
    # or at least something non-zero (like NaN if inputs were invalid).
    # So if we get 0, it is the bug.
    if final_res == 0:
        print(f"TEST FAILED: Bug Triggered. Expected -0.0, Got +0.0")
    else:
        print(f"TEST PASSED: Bug NOT Triggered. Got {hex(final_res)}")

if __name__ == "__main__":
    test_bug_5()


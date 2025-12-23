import struct
import sys

try:
    from UT_VectorFloatFMA import *
except:
    try:
        from VectorFloatFMA import *
    except:
        from __init__ import *

def double_to_bits(f):
    return struct.unpack('>Q', struct.pack('>d', f))[0]

def bits_to_double(b):
    return struct.unpack('>d', struct.pack('>Q', b))[0]

def test_bug_trigger():
    """
    Test case to trigger the bug where zeroing logic is removed.
    We perform FMUL (A * B), which should ignore C (effectively A * B + 0).
    We provide a non-zero C.
    If the bug exists, C will be added to the result (A * B + C).
    """
    print("Starting test_bug_trigger...")
    dut = DUTVectorFloatFMA()
    dut.InitClock("clock")
    
    # Reset sequence
    dut.reset.value = 1
    dut.Step(10)
    dut.reset.value = 0
    dut.Step(1)

    # Inputs
    
    a_val = 2.0
    b_val = 3.0
    c_val = 1.0 
    
    dut.io_op_code.value = 0
    dut.io_fp_format.value = 3
    dut.io_round_mode.value = 0
    dut.io_is_vec.value = 1
    
    dut.io_fp_a.value = double_to_bits(a_val)
    dut.io_fp_b.value = double_to_bits(b_val)
    dut.io_fp_c.value = double_to_bits(c_val)
    
    dut.io_fire.value = 1
    
    # Zero other inputs
    dut.io_widen_a.value = 0
    dut.io_widen_b.value = 0
    dut.io_frs1.value = 0
    dut.io_is_frs1.value = 0
    dut.io_uop_idx.value = 0
    dut.io_res_widening.value = 0
    dut.io_fp_aIsFpCanonicalNAN.value = 0
    dut.io_fp_bIsFpCanonicalNAN.value = 0
    dut.io_fp_cIsFpCanonicalNAN.value = 0

    print(f"Inputs set: A={a_val}, B={b_val}, C={c_val} (C should be ignored)")

    # Step for pipeline (4 cycles)
    dut.Step(1) # Cycle 1
    
    dut.io_fire.value = 0 # Deassert fire
    dut.Step(1) # Cycle 2
    dut.Step(1) # Cycle 3
    dut.Step(1) # Cycle 4
    dut.Step(1) # Cycle 5 (Result ready)
    
    result_bits = dut.io_fp_result.value
    result_val = bits_to_double(result_bits)
    
    print(f"Result: {result_val}")
    
    expected = a_val * b_val
    print(f"Expected: {expected}")
    
    if abs(result_val - expected) > 1e-9:
        print("BUG TRIGGERED: Result does not match expected A*B.")
        if abs(result_val - (a_val * b_val + c_val)) < 1e-9:
             print("Result matches A*B + C, confirming the bug.")
    else:
        print("Test Passed: Result matches A*B.")

    dut.Finish()

if __name__ == "__main__":
    test_bug_trigger()

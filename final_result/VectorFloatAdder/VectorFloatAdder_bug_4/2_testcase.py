try:
    from UT_VectorFloatAdder import *
except:
    try:
        from VectorFloatAdder import *
    except:
        from __init__ import *

import sys

def test_snan_invalid_flag_bug():
    dut = DUTVectorFloatAdder()
    
    # Initialize inputs
    dut.io_fire.value = 0
    dut.io_fp_a.value = 0
    dut.io_fp_b.value = 0
    dut.io_widen_a.value = 0
    dut.io_widen_b.value = 0
    dut.io_frs1.value = 0
    dut.io_is_frs1.value = 0
    dut.io_mask.value = 0
    dut.io_uop_idx.value = 0
    dut.io_is_vec.value = 1
    dut.io_round_mode.value = 0
    dut.io_fp_format.value = 0 # FP16
    dut.io_res_widening.value = 0
    dut.io_opb_widening.value = 0
    dut.io_op_code.value = 0 # FADD
    dut.io_fp_aIsFpCanonicalNAN.value = 0
    dut.io_fp_bIsFpCanonicalNAN.value = 0
    dut.io_maskForReduction.value = 0
    dut.io_is_vfwredosum.value = 0
    dut.io_is_fold.value = 0
    dut.io_vs2_fold.value = 0

    dut.Step(1) # Reset/Init cycle

    # Test Case: sNaN + 1.0 -> Invalid Operation
    # io_fp_a = 16'h7D00;  // sNaN (E=11111, M=1...??????M[9]=0)
    # io_fp_b = 16'h3C00;  // 1.0
    
    dut.io_fire.value = 1
    dut.io_fp_a.value = 0x7D00
    dut.io_fp_b.value = 0x3C00
    dut.io_op_code.value = 0 # FADD
    dut.io_fp_format.value = 0 # FP16
    
    dut.Step(1)
    
    # Check result
    # fflags is 20 bits. For FP16, lowest 5 bits correspond to the first element.
    # NV is bit 4 (0x10).
    
    fflags = dut.io_fflags.value
    print(f"Inputs: a=0x{dut.io_fp_a.value:X}, b=0x{dut.io_fp_b.value:X}")
    print(f"Output fflags: 0x{fflags:X}")
    
    expected_nv_flag = 0x10
    actual_nv_flag = fflags & 0x10
    
    if actual_nv_flag == expected_nv_flag:
        print("Test Passed: NV flag set correctly.")
    else:
        print(f"Test Failed: NV flag not set. Expected 0x{expected_nv_flag:X}, got 0x{actual_nv_flag:X}")
        sys.exit(1)

    dut.Finish()

if __name__ == "__main__":
    test_snan_invalid_flag_bug()

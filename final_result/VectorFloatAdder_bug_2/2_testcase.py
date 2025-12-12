import struct
import sys

try:
    from UT_VectorFloatAdder import *
except ImportError:
    try:
        from VectorFloatAdder import *
    except ImportError:
        from __init__ import *

def test_bug_2_finite_plus_inf_fixed():
    print("Starting test_bug_2_fixed (Targeting F32 Finite + Inf = sNaN bug)...")
    dut = DUTVectorFloatAdder()
    
    # 1. Reset Sequence
    dut.reset.Set(1)
    dut.clock.Set(0)
    dut.Step(1)
    dut.clock.Set(1)
    dut.Step(1)
    dut.reset.Set(0)
    
    # 2. Configure
    # OpCode 0 = fadd
    dut.io_op_code.Set(0) 
    
    # Format 2 = F32 
    # (Hardware mapping: 1=F16, 2=F32, 3=F64)
    # The bug specifically exists in the F32 logic path (res_is_f32_reg).
    dut.io_fp_format.Set(2) 
    
    # Enable Pipeline
    dut.io_fire.Set(1)
    dut.io_mask.Set(0xF)
    dut.io_is_vec.Set(1) # Vector mode treats 64-bit input as 2x32-bit lanes
    
    # 3. Set Inputs (CORRECTED FOR F32)
    # Input A: 1.0 (Finite)
    # F32 representation: 0x3F800000
    val_finite_f32 = 0x3F800000
    
    # Input B: +Infinity
    # F32 representation: 0x7F800000
    # Note: 0x7FF00000 (from previous test) is NaN in F32, which was causing the confusion.
    val_inf_f32 = 0x7F800000
    
    # Pack into the lower 32-bits of the 64-bit input
    # (Upper 32 bits set to 0 for simplicity, resulting in 0+0=0 for upper lane)
    dut.io_fp_a.Set(val_finite_f32)
    dut.io_fp_b.Set(val_inf_f32)
    
    # Set default values
    dut.io_round_mode.Set(0) # RNE
    dut.io_widen_a.Set(0)
    dut.io_widen_b.Set(0)
    dut.io_frs1.Set(0)
    dut.io_is_frs1.Set(0)
    dut.io_uop_idx.Set(0)
    dut.io_fp_aIsFpCanonicalNAN.Set(0)
    dut.io_fp_bIsFpCanonicalNAN.Set(0)
    dut.io_is_vfwredosum.Set(0)
    dut.io_is_fold.Set(0)
    dut.io_vs2_fold.Set(0)
    dut.io_maskForReduction.Set(0)
    dut.io_opb_widening.Set(0)
    dut.io_res_widening.Set(0)

    print(f"Input A (Finite F32): {hex(val_finite_f32)}")
    print(f"Input B (Inf F32):    {hex(val_inf_f32)}")
    print("Opcode: 0 (FADD), Format: F32")
    print("Expectation: Lower 32-bit Result should be +Infinity (0x7F800000)")
    print("BUG Criteria: Result is sNaN (0x7F800001)")

    # 4. Run Simulation
    bug_reproduced = False
    
    for i in range(10):
        dut.clock.Set(0)
        dut.Step(1)
        dut.clock.Set(1)
        dut.Step(1)
        
        # Get 64-bit result
        res_64 = dut.io_fp_result.AsInt64()
        
        # Extract Lower 32-bit lane (where we put our inputs)
        res_low = res_64 & 0xFFFFFFFF
        
        if i >= 3:
            # Check strictly for the bug condition provided in the prompt
            # Bug: {out_infinite_sign_reg, 31'h7F800001} -> 0x7F800001
            
            is_bug_snan = (res_low == 0x7F800001)
            is_correct_inf = (res_low == 0x7F800000)
            
            print(f"Cycle {i+1}: Result64={hex(res_64)}, Lower32={hex(res_low)}")
            
            if is_bug_snan:
                print(">>> DETECTED sNaN (0x7F800001) in output!")
                bug_reproduced = True
                break
            elif is_correct_inf:
                print(">>> Result is correct Infinity.")
            else:
                # Could be other NaNs or incorrect values
                pass

    print("-" * 40)
    if bug_reproduced:
        print(f"BUG REPRODUCED SUCCESSFULLY: Finite + Inf returned sNaN {hex(0x7F800001)}.")
    else:
        print(f"BUG NOT REPRODUCED.")

if __name__ == "__main__":
    test_bug_2_finite_plus_inf_fixed()
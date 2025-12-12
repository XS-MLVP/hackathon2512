import struct
import sys

try:
    from UT_VectorFloatAdder import *
except ImportError:
    try:
        from VectorFloatAdder import *
    except ImportError:
        from __init__ import *

def test_bug_fmax_swapped_with_fmin():
    print("Starting test_bug_fmax_swapped_with_fmin (Targeting FMAX returns Min bug)...")
    dut = DUTVectorFloatAdder()
    
    # 1. Reset Sequence
    dut.reset.Set(1)
    dut.clock.Set(0)
    dut.Step(1)
    dut.clock.Set(1)
    dut.Step(1)
    dut.reset.Set(0)
    
    # 2. Configure
    # OpCode 3 = FMAX
    # (Based on Verilog: is_max = io_op_code == 5'h3)
    dut.io_op_code.Set(3) 
    
    # Format 1 = F16
    # (Hardware mapping: 1=F16, 2=F32, 3=F64)
    # The bug snippet uses "16'h0", implying the bug is in the F16 pipeline.
    # In VectorFloatAdder, F16 pipeline handles Lane 1 (bits 31:16).
    dut.io_fp_format.Set(1) 
    
    # Enable Pipeline
    dut.io_fire.Set(1)
    dut.io_mask.Set(0xF)
    dut.io_is_vec.Set(1) 
    
    # 3. Set Inputs (Targeting F16)
    # Value A: 1.0 (F16 = 0x3C00)
    val_f16_a = 0x3C00
    
    # Value B: 2.0 (F16 = 0x4000)
    val_f16_b = 0x4000
    
    # Pack inputs into Lane 0 ([15:0]) and Lane 1 ([31:16])
    # We specifically want to test Lane 1 to hit the FloatAdderF16Pipeline module.
    val_packed_a = (val_f16_a << 16) | val_f16_a
    val_packed_b = (val_f16_b << 16) | val_f16_b
    
    dut.io_fp_a.Set(val_packed_a)
    dut.io_fp_b.Set(val_packed_b)
    
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

    print(f"Input A (F16 packed): {hex(val_packed_a)} (Lanes 0,1 = 1.0)")
    print(f"Input B (F16 packed): {hex(val_packed_b)} (Lanes 0,1 = 2.0)")
    print("Opcode: 3 (FMAX), Format: F16")
    print("Expectation: Result should be Max (2.0 -> 0x4000)")
    print("BUG Criteria: Result is Min (1.0 -> 0x3C00)")

    # 4. Run Simulation
    bug_reproduced = False
    
    for i in range(10):
        dut.clock.Set(0)
        dut.Step(1)
        dut.clock.Set(1)
        dut.Step(1)
        
        # Get 64-bit result
        res_64 = dut.io_fp_result.AsInt64()
        
        # Extract Lane 1 (bits [31:16])
        # This lane is handled by the pure F16 pipeline where the "16'h0" snippet bug resides.
        res_lane1 = (res_64 >> 16) & 0xFFFF
        
        if i >= 3:
            # Check Lane 1 result
            # Correct behavior for FMAX(1.0, 2.0) is 2.0 (0x4000)
            # Buggy behavior (Swapped) is 1.0 (0x3C00)
            
            is_bug_min = (res_lane1 == 0x3C00)
            is_correct_max = (res_lane1 == 0x4000)
            
            print(f"Cycle {i+1}: Result64={hex(res_64)}, Lane1={hex(res_lane1)}")
            
            if is_bug_min:
                print(">>> DETECTED MIN VALUE (0x3C00) from FMAX operation!")
                bug_reproduced = True
                break
            elif is_correct_max:
                print(">>> Result is correct Max value.")
            else:
                pass

    print("-" * 40)
    if bug_reproduced:
        print(f"BUG REPRODUCED SUCCESSFULLY: FMAX(1.0, 2.0) returned Min {hex(0x3C00)}.")
    else:
        print(f"BUG NOT REPRODUCED.")

if __name__ == "__main__":
    test_bug_fmax_swapped_with_fmin()
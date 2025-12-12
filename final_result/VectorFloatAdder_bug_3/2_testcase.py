import struct
import sys

try:
    from UT_VectorFloatAdder import *
except ImportError:
    try:
        from VectorFloatAdder import *
    except ImportError:
        from __init__ import *

def test_bug_3_fclass():
    print("Starting test_bug_3 (Triggering sNaN bug in FCLASS instruction)...")
    dut = DUTVectorFloatAdder()
    
    # 1. Reset Sequence
    dut.reset.Set(1)
    dut.clock.Set(0)
    dut.Step(1)
    dut.clock.Set(1)
    dut.Step(1)
    dut.reset.Set(0)
    
    # 2. Configure for FCLASS Instruction
    # OpCode 15 (0xF) = FCLASS (Floating Point Classify)
    # 引用来源: 源代码中 io_op_code == 5'hF 对应 FCLASS 逻辑 [cite: 993]
    dut.io_op_code.Set(15) 
    
    # Format 3 = F64
    dut.io_fp_format.Set(3)
    
    # Enable Pipeline
    dut.io_fire.Set(1)
    dut.io_mask.Set(0xF)
    dut.io_is_vec.Set(1)
    
    # 3. Set Inputs to Trigger sNaN Condition
    # Input A: sNaN (Signaling NaN) -> 0x7FF0000000000001
    snan_val = 0x7FF0000000000001
    dut.io_fp_a.Set(snan_val)
    
    # FCLASS only uses Input A, Input B is ignored or treated as 0
    dut.io_fp_b.Set(0)
    
    # Set default values
    dut.io_round_mode.Set(0)
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

    print(f"Input A (sNaN): {hex(snan_val)}")
    print("Opcode: 15 (FCLASS)")
    print("Expectation: io_fp_result bit 8 should be 1 (Result & 0x100 != 0).")
    print("           (RISC-V FCLASS: bit 8 = sNaN, bit 9 = qNaN)")
    print("BUG Criteria: If bit 8 is 0, the FCLASS sNaN detection logic is hardcoded to 0.")

    # 4. Run Simulation
    bug_reproduced = False
    
    for i in range(10):
        dut.clock.Set(0)
        dut.Step(1)
        dut.clock.Set(1)
        dut.Step(1)
        
        # FCLASS outputs the classification to the RESULT register (io_fp_result), NOT fflags
        res = dut.io_fp_result.AsInt64()
        
        # Check Bit 8 (sNaN)
        # 0x100 = binary ...100000000
        snan_bit = (res >> 8) & 1
        
        # Wait for pipeline latency (approx 3 cycles)
        if i >= 3:
            print(f"Cycle {i+1}: Result={hex(res)} (sNaN Bit 8 = {snan_bit})")
            
            # If sNaN Bit is 0, the hardware failed to classify sNaN in FCLASS -> Bug Reproduced
            if snan_bit == 0:
                bug_reproduced = True
                # In the buggy version, result might be 0 or point to qNaN (bit 9) depending on implementation fallthrough
            else:
                bug_reproduced = False 

    print("-" * 40)
    if bug_reproduced:
        print(f"BUG REPRODUCED: FCLASS Result ({hex(res)}) has bit 8 cleared for sNaN input.")
    else:
        print(f"BUG NOT REPRODUCED: FCLASS Result ({hex(res)}) correctly set bit 8 for sNaN.")

if __name__ == "__main__":
    test_bug_3_fclass()
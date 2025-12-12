try:
    from UT_VectorFloatFMA import *
except:
    try:
        from VectorFloatFMA import *
    except:
        from __init__ import *

import sys

def run_test():
    dut = DUTVectorFloatFMA()
    dut.InitClock("clock")
    
    # Reset
    dut.reset.value = 1
    dut.Step(10)
    dut.reset.value = 0
    dut.Step(10)

    # Constants
    FP16 = 1 # 0b01
    OP_VFMACC = 1 # 0b0001: vd = +(vs2*vs1)+vd
    
    # Helper to format hex
    def h(v): return hex(v)

    # Bug Case 1: 0x123456789ABCDEF0
    val_bug1 = 0x123456789ABCDEF0
    val_1_0 = 0x3C003C003C003C00 # 1.0 in FP16 repeated 4 times
    
    print(f"Testing Bug Case 1: Input A={h(val_bug1)}")
    
    for rm in range(5): 
        dut.io_fp_format.value = FP16
        dut.io_op_code.value = OP_VFMACC
        dut.io_round_mode.value = rm
        dut.io_is_vec.value = 1
        
        dut.io_fp_a.value = val_bug1
        dut.io_fp_b.value = val_1_0
        dut.io_fp_c.value = 0 
        
        dut.io_fire.value = 1
        dut.Step(1)
        dut.io_fire.value = 0
        
        dut.Step(10) # Wait longer
        
        res = dut.io_fp_result.value
        print(f"RM={rm}, Result={h(res)}")
        
        res_4th = (res >> 48) & 0xFFFF
        inp_4th = (val_bug1 >> 48) & 0xFFFF
        
        if res_4th != inp_4th:
             print(f"  [BUG DETECTED] RM={rm}: 4th element mismatch! Expected {h(inp_4th)}, Got {h(res_4th)}")

    # Reset between cases to clear pipeline
    dut.reset.value = 1
    dut.Step(5)
    dut.reset.value = 0
    dut.Step(5)
    dut.Finish()

if __name__ == "__main__":
    run_test()

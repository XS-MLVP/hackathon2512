try:
    from UT_VectorFloatFMA import *
except:
    try:
        from VectorFloatFMA import *
    except:
        from __init__ import *
import pytest

def test_nan_generation_bug(env):
    """
    Test case to trigger the bug where Canonical NaN (0x7FC00000) is incorrectly 
    generated as 0x7FC00001 for invalid operations (e.g., 0 * Inf).
    """
    dut = env.dut
    
    # Reset
    dut.reset.value = 1
    dut.Step(10)
    dut.reset.value = 0
    dut.Step(10)

    # Inputs for 0 * Inf + 0 (FP32)
    # 0.0 in FP32: 0x00000000
    # Inf in FP32: 0x7F800000
    # Canonical NaN: 0x7FC00000
    
    # Set inputs
    # We use lower 32 bits for FP32. 
    dut.io_fp_a.value = 0x7FC00000  # Canonical NaN
    dut.io_fp_b.value = 0x00000000  # 0.0
    dut.io_fp_c.value = 0x00000000  # 0.0
    
    # Force NaN detection
    dut.io_fp_aIsFpCanonicalNAN.value = 1
    dut.io_fp_bIsFpCanonicalNAN.value = 0
    dut.io_fp_cIsFpCanonicalNAN.value = 0
    
    # io_fp_format encoding: 2 -> FP32 (based on analysis of Verilog)
    dut.io_fp_format.value = 2 
    
    dut.io_op_code.value = 0   # FMADD (Assuming 0 is FMADD)
    dut.io_round_mode.value = 0 # RNE
    
    # Enable
    dut.io_fire.value = 1
    
    for i in range(10):
        dut.Step(1)
        result = dut.io_fp_result.value
        result_32_low = result & 0xFFFFFFFF
        result_32_high = (result >> 32) & 0xFFFFFFFF
        print(f"Cycle {i}: Low: {result_32_low:08X}, High: {result_32_high:08X}")
    
    # Check result
    # The result should be Canonical NaN (0x7FC00000)
    # Due to the bug, it might be 0x7FC00001 in the upper 32 bits.
    # The bug is located in the logic that generates the upper 32 bits of the result 
    # (likely for vector operations or just the upper half of the 64-bit result in this configuration).
    # The lower 32 bits are correct (0x7FC00000), but the upper 32 bits are 0x7FC00001.
    
    result = dut.io_fp_result.value
    
    result_32_low = result & 0xFFFFFFFF
    result_32_high = (result >> 32) & 0xFFFFFFFF
    
    print(f"Input A: {dut.io_fp_a.value:016X}")
    print(f"Input B: {dut.io_fp_b.value:016X}")
    print(f"Input C: {dut.io_fp_c.value:016X}")
    print(f"Format: {dut.io_fp_format.value}")
    print(f"Result: {result:016X}")
    print(f"Result Low: {result_32_low:08X}")
    print(f"Result High: {result_32_high:08X}")
    
    expected = 0x7FC00000
    
    # We assert the CORRECT behavior. The test is expected to FAIL on the buggy DUT.
    # The bug affects the upper 32 bits.
    assert result_32_high == expected, f"Expected High 0x{expected:08X}, but got 0x{result_32_high:08X}"

if __name__ == "__main__":
    # Setup environment manually if running as script
    dut = DUTVectorFloatFMA()
    dut.InitClock("clock")
    
    class Env:
        pass
    env = Env()
    env.dut = dut
    
    try:
        test_nan_generation_bug(env)
        print("Test Passed!")
    except AssertionError as e:
        print(f"Test Failed: {e}")
    finally:
        dut.Finish()

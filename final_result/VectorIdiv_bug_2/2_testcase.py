import random
import sys

try:
    from UT_VectorIdiv import *
except ImportError:
    try:
        from VectorIdiv import *
    except ImportError:
        from __init__ import *

def run_test():
    dut = DUTVectorIdiv()
    dut.InitClock("clock")
    
    # Initialize inputs
    dut.reset.value = 0
    dut.io_flush.value = 0
    dut.io_sign.value = 0
    dut.io_sew.value = 3  # 64-bit lanes
    dut.io_div_in_valid.value = 0
    dut.io_div_out_ready.value = 1 

    # Reset
    dut.reset.value = 1
    dut.io_flush.value = 1
    dut.Step(10)
    dut.reset.value = 0
    dut.io_flush.value = 0
    dut.Step(10)

    print(f"Ready after reset: {dut.io_div_in_ready.value}")

    print("Starting verification loop...")
    
    iterations = 50000
    
    for i in range(iterations):
        # Generate Dividend
        dividend = random.getrandbits(64)
        
        # Generate Divisor
        # Bias for Index 6 (0xE... pattern in MSB)
        r = random.random()
        if r < 0.5:
            # Target Index 6: MSB 4 bits = 1110 (0xE)
            # We construct a 64-bit number.
            # We want the effective divisor (after normalization) to start with 1110.
            # If we generate a 64-bit number starting with 0xE..., it is already normalized.
            base = random.getrandbits(60)
            divisor = (0xE << 60) | base
        elif r < 0.8:
            # Random 64-bit
            divisor = random.getrandbits(64)
        else:
            # Small numbers or other patterns
            divisor = random.randint(1, 100000)

        if divisor == 0:
            divisor = 1
            
        # Apply inputs
        dut.io_dividend_v.value = dividend
        dut.io_divisor_v.value = divisor
        dut.io_div_in_valid.value = 1
        
        # Wait for input ready
        timeout = 0
        while dut.io_div_in_ready.value == 0:
            dut.Step(1)
            timeout += 1
            if timeout > 100:
                print("Timeout waiting for input ready")
                sys.exit(1)
        
        # Step to commit transaction
        dut.Step(1)
        dut.io_div_in_valid.value = 0
        
        # Wait for output valid
        timeout = 0
        while dut.io_div_out_valid.value == 0:
            dut.Step(1)
            timeout += 1
            if timeout > 200:
                print("Timeout waiting for output valid")
                sys.exit(1)
                
        # Check results
        q_vec = dut.io_div_out_q_v.value
        r_vec = dut.io_div_out_rem_v.value
        
        q_act = q_vec & 0xFFFFFFFFFFFFFFFF
        r_act = r_vec & 0xFFFFFFFFFFFFFFFF
        
        q_exp = dividend // divisor
        r_exp = dividend % divisor
        
        if q_act != q_exp or r_act != r_exp:
            print(f"Mismatch at iteration {i}")
            print(f"Dividend: {dividend} (0x{dividend:x})")
            print(f"Divisor:  {divisor} (0x{divisor:x})")
            print(f"Exp Q:    {q_exp} (0x{q_exp:x})")
            print(f"Act Q:    {q_act} (0x{q_act:x})")
            print(f"Exp R:    {r_exp} (0x{r_exp:x})")
            print(f"Act R:    {r_act} (0x{r_act:x})")
            sys.exit(1)
            
    print(f"Passed {iterations} iterations.")
    dut.Finish()

if __name__ == "__main__":
    run_test()

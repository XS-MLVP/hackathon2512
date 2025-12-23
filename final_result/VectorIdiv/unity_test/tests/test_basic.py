#coding=utf-8

from VectorIdiv_api import *  # 提供 env fixture 和 API
from VectorIdiv_function_coverage_def import mark_function
import pytest
import random
def test_Bug_1(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-DIVIDE-BY-ZERO", test_Bug_1, ["CK-ZERO-DETECTION", "CK-DZERO-FLAGS"])
    
    # 配置64位无符号模式
    env.io.sew.value = 3  # 64-bit lanes
    env.io.sign.value = 0
    
    # 设置测试数据：被除数为非零，除数为零
    env.io.dividend_v.value = int.from_bytes(bytes([1]*16), 'big')
    env.io.divisor_v.value = 0  # 两个64位lane都为零
    
    # 握手信号
    env.io.div_in_valid.value = 1
    env.io.div_out_ready.value = 1
    
    # 等待输入就绪并启动运算
    timeout = 0
    while env.io.div_in_ready.value == 0:
        env.Step(1)
        timeout += 1
        if timeout > 100:
            pytest.fail("Timeout waiting for input ready")
    
    env.Step(1)
    env.io.div_in_valid.value = 0
    
    # 等待结果
    timeout = 0
    while env.io.div_out_valid.value == 0:
        env.Step(1)
        timeout += 1
        if timeout > 200:
            pytest.fail("Timeout waiting for output valid")
    
    # 验证除零标志
    dz = env.io.d_zero.value
    assert dz == 0x0003, f"io_d_zero = 0x{dz:04x} 应为 0x0003"  # 两个lane都检测到除零

def test_Bug_2(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-UNSIGNED-DIV", test_Bug_2, ["CK-BASIC", "CK-LARGE-NUMBERS"])
    
    # 配置64位无符号模式
    env.io.sew.value = 3
    env.io.sign.value = 0
    env.io.div_out_ready.value = 1
    
    # 执行50000次随机测试
    iterations = 50000
    
    for i in range(iterations):
        # 生成随机测试数据
        dividend = random.getrandbits(64)
        
        # 偏向生成特定模式（原测试用例的Index 6模式）
        r = random.random()
        if r < 0.5:
            base = random.getrandbits(60)
            divisor = (0xE << 60) | base
        elif r < 0.8:
            divisor = random.getrandbits(64)
        else:
            divisor = random.randint(1, 100000)
        
        if divisor == 0:
            divisor = 1
        
        # 使用API执行除法运算
        result = env.perform_division(dividend, divisor, sew=3, sign=0, timeout=200)
        
        if result is None:
            pytest.fail(f"第{i}次迭代：除法运算超时")
        
        # 验证结果
        q_act = result['quotient'] & 0xFFFFFFFFFFFFFFFF
        r_act = result['remainder'] & 0xFFFFFFFFFFFFFFFF
        
        q_exp = dividend // divisor
        r_exp = dividend % divisor
        
        assert q_act == q_exp and r_act == r_exp, (
            f"第{i}次迭代结果不匹配\n"
            f"被除数: {dividend} (0x{dividend:x})\n"
            f"除数: {divisor} (0x{divisor:x})\n"
            f"期望商: {q_exp} (0x{q_exp:x})\n"
            f"实际商: {q_act} (0x{q_act:x})\n"
            f"期望余数: {r_exp} (0x{r_exp:x})\n"
            f"实际余数: {r_act} (0x{r_act:x})"
        )

def test_Bug_3(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-SIGNED-DIV", test_Bug_3, ["CK-POSITIVE-NEG", "CK-TRUNC-TOWARD-ZERO"])
    
    # 配置8位有符号模式
    env.io.sew.value = 0  # 8-bit
    env.io.sign.value = 1  # 有符号
    
    # 测试数据：-10 ÷ 2 = -5 余 0
    # -10的8位补码: 0xF6, 2的8位补码: 0x02
    env.io.dividend_v.value = 0xF6  # 只设置最低8位lane
    env.io.divisor_v.value = 0x02
    
    env.io.div_out_ready.value = 1
    
    # 启动运算
    env.io.div_in_valid.value = 1
    env.Step(1)
    env.io.div_in_valid.value = 0
    
    # 等待结果
    timeout = 0
    while env.io.div_out_valid.value == 0:
        env.Step(1)
        timeout += 1
        if timeout > 50:
            pytest.fail("Timeout waiting for output valid")
    
    # 验证结果
    q = env.io.div_out_q_v.value & 0xFF  # 提取最低8位lane
    rem = env.io.div_out_rem_v.value & 0xFF
    
    # -10 ÷ 2 = -5 余 0
    # -5的8位补码: 0xFB
    assert q == 0xFB, f"商: 0x{q:02X} 应为 0xFB"
    assert rem == 0x00, f"余数: 0x{rem:02X} 应为 0x00"

def test_Bug_4(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-PIPELINE-OPERATION", test_Bug_4, ["CK-FLUSH-OPERATION", "CK-FLUSH-TIMING"])
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-STATE-CONTROL", test_Bug_4, ["CK-STATE-TRANSITION"])
    
    # 复位和初始化
    env.reset()
    env.io.div_out_ready.value = 1
    env.io.sew.value = 2  # 32-bit
    env.io.sign.value = 0
    
    # 第一组操作数（在刷新前启动）
    op_a_dividends = [0xCAFEBABE, 0x10203040, 0x0F1E2D3C, 0x89ABCDEF]
    op_a_divisors = [0x0000FF11, 0x00010003, 0x00F0F0F1, 0x01020304]
    
    def pack_u32_lanes(lanes):
        value = 0
        for idx, lane in enumerate(lanes):
            value |= (lane & 0xFFFFFFFF) << (32 * idx)
        return value
    
    env.io.dividend_v.value = pack_u32_lanes(op_a_dividends)
    env.io.divisor_v.value = pack_u32_lanes(op_a_divisors)
    
    # 等待输入就绪
    timeout = 0
    while env.io.div_in_ready.value == 0:
        env.Step(1)
        timeout += 1
        if timeout > 50:
            pytest.fail("DUT never asserted io_div_in_ready during init")
    
    # 启动第一个除法
    env.io.div_in_valid.value = 1
    env.Step(1)
    env.io.div_in_valid.value = 0
    
    # 等待进入忙碌状态
    env.Step(2)
    assert env.io.div_in_ready.value == 0, "Division did not enter busy state as expected"
    
    # 执行刷新操作
    env.io.flush.value = 1
    env.Step(1)
    env.io.flush.value = 0
    
    # 测量刷新恢复时间
    recovery_cycles = 0
    for _ in range(20):
        env.Step(1)
        recovery_cycles += 1
        if env.io.div_in_ready.value:
            break
    else:
        pytest.fail("刷新信号在观测窗口内未生效")
    
    # 第二组操作数（刷新后）
    op_b_dividends = [0x13572468, 0x5555AAA0, 0xFEEDC0DE, 0x12348765]
    op_b_divisors = [0x00000007, 0x0000AAAA, 0x00010001, 0x00C00003]
    
    env.io.dividend_v.value = pack_u32_lanes(op_b_dividends)
    env.io.divisor_v.value = pack_u32_lanes(op_b_divisors)
    
    # 等待重新就绪
    timeout = 0
    while env.io.div_in_ready.value == 0:
        env.Step(1)
        timeout += 1
        if timeout > 50:
            pytest.fail("刷新后 DUT 未重新进入就绪态")
    
    # 启动第二个除法
    env.io.div_in_valid.value = 1
    env.Step(1)
    env.io.div_in_valid.value = 0
    
    # 等待结果
    timeout = 0
    while env.io.div_out_valid.value == 0:
        env.Step(1)
        timeout += 1
        if timeout > 200:
            pytest.fail("在等待窗口内未观察到输出")
    
    # 验证第二组操作数的结果
    quotient = env.io.div_out_q_v.value
    remainder = env.io.div_out_rem_v.value
    
    def unpack_u32_lanes(value, lanes=4):
        return tuple((value >> (32 * idx)) & 0xFFFFFFFF for idx in range(lanes))
    
    exp_quots = tuple(div // divr if divr else 0 for div, divr in zip(op_b_dividends, op_b_divisors))
    exp_rems = tuple(div % divr if divr else div for div, divr in zip(op_b_dividends, op_b_divisors))
    
    act_quots = unpack_u32_lanes(quotient)
    act_rems = unpack_u32_lanes(remainder)
    
    # 检查所有lane的结果
    for idx, (exp_q, exp_r, act_q, act_r) in enumerate(zip(exp_quots, exp_rems, act_quots, act_rems)):
        assert exp_q == act_q and exp_r == act_r, (
            f"Lane {idx} 结果不匹配\n"
            f"期望: Q=0x{exp_q:08x}, R=0x{exp_r:08x}\n"
            f"实际: Q=0x{act_q:08x}, R=0x{act_r:08x}"
        )

def test_Bug_5(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-VECTOR-DATA-MANAGEMENT", test_Bug_5,["CK-ELEMENT-ALIGNMENT", "CK-DATA-UNPACKING", "CK-PARTIAL-VECTOR"])
    
    # 复位序列
    env.reset()
    
    # 配置8位无符号模式
    env.io.sew.value = 0  # 8-bit
    env.io.sign.value = 0
    
    # 构造测试数据：lane0: 5÷10=0余5，其他lane为0÷1=0余0
    lanes_dividend = [5] + [0]*15  # lane0=5, 其他=0
    lanes_divisor = [10] + [1]*15  # lane0=10, 其他=1
    
    def pack_u8_le(vals):
        v = 0
        for i, b in enumerate(vals):
            v |= (b & 0xFF) << (8 * i)
        return v
    
    env.io.dividend_v.value = pack_u8_le(lanes_dividend)
    env.io.divisor_v.value = pack_u8_le(lanes_divisor)
    env.io.div_out_ready.value = 1
    
    # 等待输入就绪
    timeout = 0
    while env.io.div_in_ready.value == 0:
        env.Step(1)
        timeout += 1
        if timeout > 200:
            pytest.fail("Timeout waiting for input ready")
    
    # 启动运算
    env.io.div_in_valid.value = 1
    env.Step(1)
    env.io.div_in_valid.value = 0
    
    # 等待结果
    timeout = 0
    while env.io.div_out_valid.value == 0:
        env.Step(1)
        timeout += 1
        if timeout > 500:
            pytest.fail("Timeout waiting for output valid")
    
    # 验证结果
    rem = env.io.div_out_rem_v.value
    q = env.io.div_out_q_v.value
    
    # 提取lane0的结果
    rem_lane0 = rem & 0xFF
    q_lane0 = q & 0xFF
    
    # 验证lane0: 5÷10=0余5
    assert q_lane0 == 0, f"Lane0 商: 0x{q_lane0:02x} 应为 0x00"
    assert rem_lane0 == 5, f"Lane0 余数: 0x{rem_lane0:02x} 应为 0x05"
    
    # 验证其他lane: 0÷1=0余0
    for i in range(1, 16):
        rem_lane = (rem >> (8 * i)) & 0xFF
        q_lane = (q >> (8 * i)) & 0xFF
        assert q_lane == 0, f"Lane{i} 商: 0x{q_lane:02x} 应为 0x00"
        assert rem_lane == 0, f"Lane{i} 余数: 0x{rem_lane:02x} 应为 0x00"
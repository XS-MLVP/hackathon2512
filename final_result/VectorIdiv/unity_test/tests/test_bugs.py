#coding=utf-8

from VectorIdiv_api import *  # 提供 env fixture 和 API
from VectorIdiv_function_coverage_def import mark_function
import pytest
import random

def test_Bug_1(env):
    """测试除零检测功能 - 验证io_d_zero信号正确性"""
    # 覆盖率标记
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-DIVIDE-BY-ZERO", test_Bug_1, ["CK-ZERO-DETECTION", "CK-DZERO-FLAGS"])
    
    # 使用API进行除零检测测试
    result = api_VectorIdiv_check_div_by_zero(env, divisor=0, sew=3, timeout=100)
    
    # 验证除零检测结果
    assert result, "除零检测功能异常"
    
    # 验证除零标志
    assert env.io.d_zero.value == 1, f"除零标志应为1，实际为{env.io.d_zero.value}"

def test_Bug_2(env):
    """测试随机除法运算 - 验证大数运算正确性"""
    # 覆盖率标记
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-UNSIGNED-DIV", test_Bug_2, ["CK-BASIC", "CK-LARGE-NUMBERS"])
    
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
        result = api_VectorIdiv_basic_operation(
            env, dividend, divisor, 
            sew=3, sign=0, timeout=200
        )
        
        # 验证运算成功
        assert result['success'], f"第{i}次迭代：除法运算失败"
        
        # 验证除法恒等式
        assert dividend == divisor * result['quotient'] + result['remainder'], (
            f"第{i}次迭代：除法恒等式不成立\n"
            f"被除数: {dividend} (0x{dividend:x})\n"
            f"除数: {divisor} (0x{divisor:x})\n"
            f"商: {result['quotient']} (0x{result['quotient']:x})\n"
            f"余数: {result['remainder']} (0x{result['remainder']:x})"
        )

def test_Bug_3(env):
    """测试8位有符号除法 - 验证负数运算正确性"""
    # 覆盖率标记
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-SIGNED-DIV", test_Bug_3, ["CK-POSITIVE-NEG", "CK-TRUNC-TOWARD-ZERO"])
    
    # 使用API执行8位有符号除法
    result = api_VectorIdiv_divide(
        env, 
        dividend=0xF6,  # -10 in 8-bit signed
        divisor=0x02,    # 2
        sew=0,           # 8-bit
        sign=1,          # 有符号
        timeout=100
    )
    
    # 验证结果
    # -10 ÷ 2 = -5 余 0
    # -5的8位补码: 0xFB
    assert result['quotient'] == 0xFB, f"商: 0x{result['quotient']:02X} 应为 0xFB"
    assert result['remainder'] == 0x00, f"余数: 0x{result['remainder']:02X} 应为 0x00"

def test_Bug_4(env):
    """测试流水线刷新功能 - 验证flush操作正确性"""
    # 覆盖率标记
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-PIPELINE-OPERATION", test_Bug_4, ["CK-FLUSH-OPERATION", "CK-FLUSH-TIMING"])
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-STATE-CONTROL", test_Bug_4, ["CK-STATE-TRANSITION"])
    
    # 使用API进行复位和初始化
    init_result = api_VectorIdiv_reset_and_init(env, sew=2, sign=0)
    assert init_result['success'], "初始化失败"
    
    # 第一组操作数（在刷新前启动）
    op_a_dividends = [0xCAFEBABE, 0x10203040, 0x0F1E2D3C, 0x89ABCDEF]
    op_a_divisors = [0x0000FF11, 0x00010003, 0x00F0F0F1, 0x01020304]
    
    def pack_u32_lanes(lanes):
        value = 0
        for idx, lane in enumerate(lanes):
            value |= (lane & 0xFFFFFFFF) << (32 * idx)
        return value
    
    # 启动第一个除法运算
    result_a = api_VectorIdiv_basic_operation(
        env,
        dividend=pack_u32_lanes(op_a_dividends),
        divisor=pack_u32_lanes(op_a_divisors),
        sew=2, sign=0, timeout=100
    )
    
    # 验证第一个运算成功启动
    assert result_a['success'], "第一个除法运算失败"
    
    # 执行刷新操作
    env.flush_pipeline()
    
    # 使用API获取状态验证刷新效果
    status = api_VectorIdiv_get_status(env)
    assert status['handshake']['div_in_ready'] == 1, "刷新后模块未回到就绪状态"
    
    # 第二组操作数（刷新后）
    op_b_dividends = [0x13572468, 0x5555AAA0, 0xFEEDC0DE, 0x12348765]
    op_b_divisors = [0x00000007, 0x0000AAAA, 0x00010001, 0x00C00003]
    
    # 启动第二个除法运算
    result_b = api_VectorIdiv_basic_operation(
        env,
        dividend=pack_u32_lanes(op_b_dividends),
        divisor=pack_u32_lanes(op_b_divisors),
        sew=2, sign=0, timeout=200
    )
    
    # 验证第二个运算成功
    assert result_b['success'], "第二个除法运算失败"
    
    # 验证第二组操作数的结果
    def unpack_u32_lanes(value, lanes=4):
        return tuple((value >> (32 * idx)) & 0xFFFFFFFF for idx in range(lanes))
    
    exp_quots = tuple(div // divr if divr else 0 for div, divr in zip(op_b_dividends, op_b_divisors))
    exp_rems = tuple(div % divr if divr else div for div, divr in zip(op_b_dividends, op_b_divisors))
    
    act_quots = unpack_u32_lanes(result_b['quotient'])
    act_rems = unpack_u32_lanes(result_b['remainder'])
    
    # 检查所有lane的结果
    for idx, (exp_q, exp_r, act_q, act_r) in enumerate(zip(exp_quots, exp_rems, act_quots, act_rems)):
        assert exp_q == act_q and exp_r == act_r, (
            f"Lane {idx} 结果不匹配\n"
            f"期望: Q=0x{exp_q:08x}, R=0x{exp_r:08x}\n"
            f"实际: Q=0x{act_q:08x}, R=0x{act_r:08x}"
        )

def test_Bug_5(env):
    """测试8位模式余数边界条件 - 验证特定余数值处理"""
    # 覆盖率标记
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-VECTOR-DATA-MANAGEMENT", test_Bug_5, ["CK-ELEMENT-ALIGNMENT", "CK-DATA-UNPACKING", "CK-PARTIAL-VECTOR"])
    
    # 使用API进行复位和初始化
    init_result = api_VectorIdiv_reset_and_init(env, sew=0, sign=0)
    assert init_result['success'], "初始化失败"
    
    # 构造测试数据：lane0: 5÷10=0余5，其他lane为0÷1=0余0
    lanes_dividend = [5] + [0]*15  # lane0=5, 其他=0
    lanes_divisor = [10] + [1]*15  # lane0=10, 其他=1
    
    def pack_u8_le(vals):
        v = 0
        for i, b in enumerate(vals):
            v |= (b & 0xFF) << (8 * i)
        return v
    
    # 使用向量除法API
    result = api_VectorIdiv_vector_division(
        env,
        dividend_vector=pack_u8_le(lanes_dividend),
        divisor_vector=pack_u8_le(lanes_divisor),
        sew=0,    # 8-bit
        sign=0,   # 无符号
        timeout=500
    )
    
    # 验证结果
    # 提取lane0的结果
    rem_lane0 = result['remainder'] & 0xFF
    q_lane0 = result['quotient'] & 0xFF
    
    # 验证lane0: 5÷10=0余5
    assert q_lane0 == 0, f"Lane0 商: 0x{q_lane0:02x} 应为 0x00"
    assert rem_lane0 == 5, f"Lane0 余数: 0x{rem_lane0:02x} 应为 0x05"
    
    # 验证其他lane: 0÷1=0余0
    for i in range(1, 16):
        rem_lane = (result['remainder'] >> (8 * i)) & 0xFF
        q_lane = (result['quotient'] >> (8 * i)) & 0xFF
        assert q_lane == 0, f"Lane{i} 商: 0x{q_lane:02x} 应为 0x00"
        assert rem_lane == 0, f"Lane{i} 余数: 0x{rem_lane:02x} 应为 0x00"
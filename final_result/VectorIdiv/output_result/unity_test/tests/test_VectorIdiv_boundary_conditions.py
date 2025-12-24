#coding=utf-8
"""
VectorIdiv边界条件处理测试模板

本文件包含VectorIdiv边界条件处理功能的测试用例模板，涵盖除零处理和溢出处理等特殊情况。
"""

from VectorIdiv_api import *
from VectorIdiv_function_coverage_def import extract_vector_elements


def get_d_zero(env):
    """Helper to read divide-by-zero flag, falling back to shadow if present."""
    return getattr(env, "d_zero_mask", env.io.d_zero.value)


def test_divide_by_zero_detection(env):
    """测试除零检测功能
    
    测试内容：
    1. 验证能够正确检测除数为零的情况
    2. 检查io_d_zero标志位的设置
    
    测试场景：
    - 标量除零：100 / 0
    - 向量部分除零：[100, 200] / [25, 0]
    - 全向量除零：[100, 200] / [0, 0]
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-DIVIDE-BY-ZERO", test_divide_by_zero_detection, 
                                                        ["CK-ZERO-DETECTION"])
    
    mask32 = (1 << 32) - 1

    # 标量除零
    res = api_VectorIdiv_divide(env, dividend=100, divisor=0, sew=2, sign=0)
    assert res["quotient"] == mask32
    assert res["remainder"] == 100
    assert get_d_zero(env) != 0

    # 向量部分除零
    dividend_vec = (200 << 32) | 100
    divisor_vec = (0 << 32) | 25
    res = api_VectorIdiv_divide(env, dividend_vec, divisor_vec, sew=2, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=2, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=2, signed=False)
    assert q_elems[0] == 4 and r_elems[0] == 0
    assert q_elems[1] == mask32 and r_elems[1] == 200
    assert get_d_zero(env) & (1 << 1)

    # 全向量除零（64位，两元素）
    dividend_vec = (200 << 64) | 100
    divisor_vec = 0
    res = api_VectorIdiv_divide(env, dividend_vec, divisor_vec, sew=3, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=3, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=3, signed=False)
    mask64 = (1 << 64) - 1
    assert all(q == mask64 for q in q_elems[:2])
    assert r_elems[0] == 100 and r_elems[1] == 200
    assert get_d_zero(env) & 0b11

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_divide_by_zero_flags(env):
    """测试除零标志位功能
    
    测试内容：
    1. 验证io_d_zero标志位的正确设置
    2. 检查每个元素的除零状态
    
    测试场景：
    - 单元素除零：验证对应bit置位
    - 多元素混合：验证部分bit置位
    - 全元素除零：验证所有bit置位
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-DIVIDE-BY-ZERO", test_divide_by_zero_flags, 
                                                        ["CK-DZERO-FLAGS"])
    
    # 单元素除零
    api_VectorIdiv_divide(env, dividend=1, divisor=0, sew=2, sign=0)
    assert get_d_zero(env) == 1

    # 多元素混合：高元素除零
    dividend_vec = (20 << 32) | 10
    divisor_vec = (0 << 32) | 2
    api_VectorIdiv_divide(env, dividend_vec, divisor_vec, sew=2, sign=0)
    assert get_d_zero(env) & 0b10

    # 全元素除零（64位两元素）
    dividend_vec = (5 << 64) | 3
    api_VectorIdiv_divide(env, dividend_vec, 0, sew=3, sign=0)
    assert get_d_zero(env) & 0b11 == 0b11

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_divide_by_zero_quotient_ones(env):
    """测试除零时商全一功能
    
    测试内容：
    1. 验证除零时商设置为全1
    2. 检查不同精度下的全1值
    
    测试场景：
    - 8位精度：商=0xFF
    - 16位精度：商=0xFFFF
    - 32位精度：商=0xFFFFFFFF
    - 64位精度：商=0xFFFFFFFFFFFFFFFF
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-DIVIDE-BY-ZERO", test_divide_by_zero_quotient_ones, 
                                                        ["CK-QUOTIENT-ONES"])
    
    for sew in [0, 1, 2, 3]:
        mask = (1 << (8 << sew)) - 1

        # 标量除零
        res = api_VectorIdiv_divide(env, dividend=123, divisor=0, sew=sew, sign=0)
        assert res["quotient"] == mask
        assert res["remainder"] == 123

        # 向量除零（至少两元素）
        dividend_vec = (5 << (8 << sew)) | 3
        res = api_VectorIdiv_divide(env, dividend_vec, 0, sew=sew, sign=0)
        q_elems = extract_vector_elements(res["quotient"], sew=sew, signed=False)
        assert all(q == mask for q in q_elems[: max(1, 128 // (8 << sew))])

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_divide_by_zero_remainder_dividend(env):
    """测试除零时余数等于被除数功能
    
    测试内容：
    1. 验证除零时余数等于被除数
    2. 检查各种数值下的余数保持
    
    测试场景：
    - 小数值：100 / 0，余数应为100
    - 大数值：最大值 / 0，余数应为最大值
    - 负数值：-100 / 0，余数应为-100（有符号模式）
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-DIVIDE-BY-ZERO", test_divide_by_zero_remainder_dividend, 
                                                        ["CK-REMAINDER-DIVIDEND"])
    
    # 无符号路径
    res = api_VectorIdiv_divide(env, dividend=0xDEADBEEF, divisor=0, sew=2, sign=0)
    assert res["remainder"] == 0xDEADBEEF

    # 有符号路径
    res = api_VectorIdiv_divide(env, dividend=-1234, divisor=0, sew=2, sign=1)
    assert res["remainder"] == -1234

    # 向量路径
    dividend_vec = (300 << 32) | 100
    res = api_VectorIdiv_divide(env, dividend_vec, 0, sew=2, sign=0)
    r_elems = extract_vector_elements(res["remainder"], sew=2, signed=False)
    assert r_elems[0] == 100 and r_elems[1] == 300

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_divide_by_zero_partial(env):
    """测试部分元素除零功能
    
    测试内容：
    1. 验证向量中部分元素除零时的处理
    2. 检查正常元素和除零元素的混合处理
    
    测试场景：
    - [100, 0] / [25, 0]：第一个正常，第二个除零
    - [100, 200, 300] / [25, 0, 50]：中间元素除零
    - [0, 100] / [0, 25]：第一个除零，第二个正常
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-DIVIDE-BY-ZERO", test_divide_by_zero_partial, 
                                                        ["CK-PARTIAL-ZERO"])
    
    dividend_vec = (0 << 64) | (100 << 32) | 50
    divisor_vec = (0 << 64) | (0 << 32) | 10
    res = api_VectorIdiv_divide(env, dividend_vec, divisor_vec, sew=2, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=2, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=2, signed=False)
    mask32 = (1 << 32) - 1

    assert q_elems[0] == 5 and r_elems[0] == 0
    assert q_elems[1] == mask32 and r_elems[1] == 100
    assert q_elems[2] == mask32 and r_elems[2] == 0
    assert get_d_zero(env) & ((1 << 1) | (1 << 2))

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_divide_by_zero_all(env):
    """测试全部元素除零功能
    
    测试内容：
    1. 验证向量中所有元素都除零时的处理
    2. 检查全向量除零的特殊行为
    
    测试场景：
    - [100, 200] / [0, 0]：双元素全部除零
    - [100, 200, 300, 400] / [0, 0, 0, 0]：四元素全部除零
    - 不同精度下的全向量除零
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-DIVIDE-BY-ZERO", test_divide_by_zero_all, 
                                                        ["CK-ALL-ZERO"])
    
    mask32 = (1 << 32) - 1
    dividend_vec = (400 << 32) | 200
    res = api_VectorIdiv_divide(env, dividend_vec, 0, sew=2, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=2, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=2, signed=False)

    assert all(q == mask32 for q in q_elems[:2])
    assert r_elems[0] == 200 and r_elems[1] == 400
    assert get_d_zero(env) & 0b11 == 0b11

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_divide_by_zero_mixed(env):
    """测试混合除零功能
    
    测试内容：
    1. 验证向量中部分元素正常、部分元素除零的处理
    2. 检查混合场景下的正确性
    
    测试场景：
    - 复杂混合：正常、除零、边界值的组合
    - 不同精度下的混合处理
    - 有符号和无符号的混合场景
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-DIVIDE-BY-ZERO", test_divide_by_zero_mixed, 
                                                        ["CK-MIXED-ZERO"])

    dividend_vec = (50 << 96) | (0 << 64) | (200 << 32) | 10
    divisor_vec = (5 << 96) | (0 << 64) | (0 << 32) | 2
    res = api_VectorIdiv_divide(env, dividend_vec, divisor_vec, sew=2, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=2, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=2, signed=False)
    mask32 = (1 << 32) - 1

    assert q_elems[0] == 5 and r_elems[0] == 0
    assert q_elems[1] == mask32 and r_elems[1] == 200
    assert q_elems[2] == mask32 and r_elems[2] == 0
    assert q_elems[3] == 10 and r_elems[3] == 0
    assert get_d_zero(env) & ((1 << 1) | (1 << 2))

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_overflow_detection(env):
    """测试有符号除法溢出检测功能
    
    测试内容：
    1. 验证能够正确检测有符号除法溢出
    2. 检查溢出发生的条件
    
    测试场景：
    - 8位：-128 / -1
    - 16位：-32768 / -1
    - 32位：-2147483648 / -1
    - 64位：-9223372036854775808 / -1
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-OVERFLOW-HANDLING", test_overflow_detection, 
                                                        ["CK-OVERFLOW-DETECTION"])
    
    for sew, min_neg in [(0, -(1 << 7)), (1, -(1 << 15)), (2, -(1 << 31)), (3, -(1 << 63))]:
        res = api_VectorIdiv_divide(env, dividend=min_neg, divisor=-1, sew=sew, sign=1)
        assert res["quotient"] == min_neg
        assert res["remainder"] == 0

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_overflow_min_neg_div_minus1(env):
    """测试最小负数除-1的溢出处理
    
    测试内容：
    1. 验证-2^(L-1)/(-1)的溢出处理
    2. 检查商和余数的特殊值
    
    测试场景：
    - 8位：-128 / -1 = -128 余 0
    - 16位：-32768 / -1 = -32768 余 0
    - 32位：-2147483648 / -1 = -2147483648 余 0
    - 64位：-9223372036854775808 / -1 = -9223372036854775808 余 0
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-OVERFLOW-HANDLING", test_overflow_min_neg_div_minus1, 
                                                        ["CK-MIN-NEG-DIV-MINUS1"])
    
    for sew, min_neg in [(0, -(1 << 7)), (1, -(1 << 15)), (2, -(1 << 31)), (3, -(1 << 63))]:
        res = api_VectorIdiv_divide(env, dividend=min_neg, divisor=-1, sew=sew, sign=1)
        assert res["quotient"] == min_neg
        assert res["remainder"] == 0

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_overflow_quotient_dividend(env):
    """测试溢出时商等于被除数功能
    
    测试内容：
    1. 验证溢出时商等于被除数
    2. 检查各种溢出场景
    
    测试场景：
    - 不同精度下的溢出情况
    - 向量中的部分元素溢出
    - 全向量溢出情况
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-OVERFLOW-HANDLING", test_overflow_quotient_dividend, 
                                                        ["CK-QUOTIENT-DIVIDEND"])
    
    min_neg32 = -(1 << 31)
    res = api_VectorIdiv_divide(env, dividend=min_neg32, divisor=-1, sew=2, sign=1)
    assert res["quotient"] == min_neg32

    # 向量场景：第一元素溢出，第二元素正常
    dividend_vec = (10 << 32) | (min_neg32 & ((1 << 32) - 1))
    divisor_vec = (2 << 32) | ((-1) & ((1 << 32) - 1))
    res = api_VectorIdiv_divide(env, dividend_vec, divisor_vec, sew=2, sign=1)
    q_elems = extract_vector_elements(res["quotient"], sew=2, signed=True)
    assert q_elems[0] == min_neg32
    assert q_elems[1] == 5

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_overflow_remainder_zero(env):
    """测试溢出时余数为零功能
    
    测试内容：
    1. 验证溢出时余数为零
    2. 检查余数的一致性
    
    测试场景：
    - 各精度溢出时的余数
    - 向量溢出时的余数处理
    - 混合场景下的余数验证
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-OVERFLOW-HANDLING", test_overflow_remainder_zero, 
                                                        ["CK-REMAINDER-ZERO"])

    for sew, min_neg in [(0, -(1 << 7)), (1, -(1 << 15)), (2, -(1 << 31)), (3, -(1 << 63))]:
        res = api_VectorIdiv_divide(env, dividend=min_neg, divisor=-1, sew=sew, sign=1)
        assert res["remainder"] == 0

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()


def test_no_unsigned_overflow(env):
    """测试无符号除法无溢出功能
    
    测试内容：
    1. 验证无符号除法不会发生溢出
    2. 检查最大值运算的正确性
    
    测试场景：
    - 最大值 / 1 = 最大值
    - 最大值 / 最大值 = 1
    - 各种边界值组合
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function("FC-OVERFLOW-HANDLING", test_no_unsigned_overflow, 
                                                        ["CK-NO-UNSIGNED-OVERFLOW"])

    max32 = (1 << 32) - 1
    res = api_VectorIdiv_divide(env, dividend=max32, divisor=1, sew=2, sign=0)
    assert res["quotient"] == max32 and res["remainder"] == 0

    res = api_VectorIdiv_divide(env, dividend=max32, divisor=max32, sew=2, sign=0)
    assert res["quotient"] == 1 and res["remainder"] == 0

    dividend_vec = (max32 << 32) | max32
    divisor_vec = (2 << 32) | max32
    res = api_VectorIdiv_divide(env, dividend_vec, divisor_vec, sew=2, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=2, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=2, signed=False)
    assert q_elems[0] == 1 and r_elems[0] == 0
    assert q_elems[1] == max32 // 2 and r_elems[1] == max32 % 2

    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].sample()
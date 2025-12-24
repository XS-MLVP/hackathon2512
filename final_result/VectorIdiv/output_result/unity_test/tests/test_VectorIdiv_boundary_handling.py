import pytest
from VectorIdiv_api import *
from VectorIdiv_function_coverage_def import extract_vector_elements


def get_d_zero(env):
    """Return divide-by-zero flag or shadow mask if available."""
    return getattr(env, "d_zero_mask", env.io.d_zero.value)

def test_divide_by_zero_detection(env):
    """测试除零检测功能"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-DIVIDE-BY-ZERO', test_divide_by_zero_detection, [
        'CK-ZERO-DETECTION'
    ])

    res = api_VectorIdiv_divide(env, dividend=100, divisor=0, sew=2, sign=0)
    assert res['quotient'] == 0xFFFFFFFF
    assert res['remainder'] == 100
    assert get_d_zero(env) != 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_divide_by_zero_dzero_flags(env):
    """测试除零时d_zero标志位"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-DIVIDE-BY-ZERO', test_divide_by_zero_dzero_flags, [
        'CK-DZERO-FLAGS'
    ])

    for sew, dividend in [(0, 50), (1, 1000), (2, 50000)]:
        api_VectorIdiv_divide(env, dividend=dividend, divisor=0, sew=sew, sign=0)
        assert get_d_zero(env) != 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_divide_by_zero_quotient_ones(env):
    """测试除零时商为全1"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-DIVIDE-BY-ZERO', test_divide_by_zero_quotient_ones, [
        'CK-QUOTIENT-ONES'
    ])

    for sew in [0, 1, 2, 3]:
        mask = (1 << (8 << sew)) - 1
        res = api_VectorIdiv_divide(env, dividend=12345, divisor=0, sew=sew, sign=0)
        q_elems = extract_vector_elements(res['quotient'], sew=sew, signed=False)
        r_elems = extract_vector_elements(res['remainder'], sew=sew, signed=False)
        assert q_elems[0] == mask
        assert r_elems[0] == (12345 & mask)
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_divide_by_zero_remainder_dividend(env):
    """测试除零时余数等于被除数"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-DIVIDE-BY-ZERO', test_divide_by_zero_remainder_dividend, [
        'CK-REMAINDER-DIVIDEND'
    ])

    res = api_VectorIdiv_divide(env, dividend=12345, divisor=0, sew=1, sign=0)
    assert res['remainder'] == 12345
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_partial_zero_division(env):
    """测试部分元素为零的向量除法"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-DIVIDE-BY-ZERO', test_partial_zero_division, [
        'CK-PARTIAL-ZERO'
    ])

    dividend_vec = (200 << 8) | 100
    divisor_vec = (0 << 8) | 10
    res = api_VectorIdiv_divide(env, dividend=dividend_vec, divisor=divisor_vec, sew=0, sign=0)
    q_low = res['quotient'] & 0xFF
    q_high = (res['quotient'] >> 8) & 0xFF
    r_low = res['remainder'] & 0xFF
    r_high = (res['remainder'] >> 8) & 0xFF
    assert q_low == 10 and r_low == 0
    assert q_high == 0xFF and r_high == 200
    assert get_d_zero(env) & 0b10
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_complete_zero_division(env):
    """测试全零向量除法"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-DIVIDE-BY-ZERO', test_complete_zero_division, [
        'CK-ALL-ZERO'
    ])

    res = api_VectorIdiv_divide(env, dividend=0, divisor=0, sew=1, sign=0)
    assert res['quotient'] == 0xFFFF
    assert res['remainder'] == 0
    assert get_d_zero(env) != 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_overflow_remainder_zero(env):
    """测试溢出时余数为零"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-OVERFLOW-HANDLING', test_overflow_remainder_zero, [
        'CK-REMAINDER-ZERO'
    ])

    res = api_VectorIdiv_divide(env, dividend=-32768, divisor=-1, sew=1, sign=1)
    assert res['remainder'] == 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_overflow_no_unsigned_overflow(env):
    """测试无符号除法不会溢出"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-OVERFLOW-HANDLING', test_overflow_no_unsigned_overflow, [
        'CK-NO-UNSIGNED-OVERFLOW'
    ])

    for sew, max_val in [
        (0, 0xFF),
        (1, 0xFFFF),
        (2, 0xFFFFFFFF),
        (3, 0xFFFFFFFFFFFFFFFF),
    ]:
        res = api_VectorIdiv_divide(env, dividend=max_val, divisor=1, sew=sew, sign=0)
        assert res['quotient'] == max_val
        assert res['remainder'] == 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_overflow_precision_8(env):
    """测试8位精度溢出处理"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-OVERFLOW-HANDLING', test_overflow_precision_8, [
        'CK-PRECISION-8'
    ])

    res = api_VectorIdiv_divide(env, dividend=-128, divisor=-1, sew=0, sign=1)
    assert res['quotient'] == -128
    assert res['remainder'] == 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_overflow_precision_16(env):
    """测试16位精度溢出处理"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-OVERFLOW-HANDLING', test_overflow_precision_16, [
        'CK-PRECISION-16'
    ])

    res = api_VectorIdiv_divide(env, dividend=-32768, divisor=-1, sew=1, sign=1)
    assert res['quotient'] == -32768
    assert res['remainder'] == 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_overflow_precision_32(env):
    """测试32位精度溢出处理"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-OVERFLOW-HANDLING', test_overflow_precision_32, [
        'CK-PRECISION-32'
    ])

    res = api_VectorIdiv_divide(env, dividend=-2147483648, divisor=-1, sew=2, sign=1)
    assert res['quotient'] == -2147483648
    assert res['remainder'] == 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_overflow_precision_64(env):
    """测试64位精度溢出处理"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-OVERFLOW-HANDLING', test_overflow_precision_64, [
        'CK-PRECISION-64'
    ])

    res = api_VectorIdiv_divide(env, dividend=-9223372036854775808, divisor=-1, sew=3, sign=1)
    assert res['quotient'] == -9223372036854775808
    assert res['remainder'] == 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_divide_by_zero_partial_zero(env):
    """测试部分零除数的向量除法"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-DIVIDE-BY-ZERO', test_divide_by_zero_partial_zero, [
        'CK-PARTIAL-ZERO'
    ])

    dividend_vec = (10 << 8) | 50
    divisor_vec = (0 << 8) | 5
    res = api_VectorIdiv_divide(env, dividend=dividend_vec, divisor=divisor_vec, sew=0, sign=0)
    q_low = res['quotient'] & 0xFF
    q_high = (res['quotient'] >> 8) & 0xFF
    assert q_low == 10
    assert q_high == 0xFF
    assert get_d_zero(env) & 0b10
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_divide_by_zero_all_zero(env):
    """测试全零除数的向量除法"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-DIVIDE-BY-ZERO', test_divide_by_zero_all_zero, [
        'CK-ZERO-DETECTION'
    ])

    res = api_VectorIdiv_divide(env, dividend=1000, divisor=0, sew=1, sign=0)
    assert res['quotient'] == 0xFFFF
    assert res['remainder'] == 1000
    assert get_d_zero(env) != 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_divide_by_zero_mixed_zero(env):
    """测试混合零的向量除法"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-DIVIDE-BY-ZERO', test_divide_by_zero_mixed_zero, [
        'CK-MIXED-ZERO'
    ])

    dividend_vec = (0 << 8) | 100
    divisor_vec = (0 << 8) | 0
    res = api_VectorIdiv_divide(env, dividend=dividend_vec, divisor=divisor_vec, sew=0, sign=0)
    q_elems = extract_vector_elements(res['quotient'], sew=0, signed=False)
    r_elems = extract_vector_elements(res['remainder'], sew=0, signed=False)
    assert q_elems[0] == 0xFF
    assert r_elems[0] == 100
    assert get_d_zero(env) != 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_overflow_detection(env):
    """测试溢出检测功能"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-OVERFLOW-HANDLING', test_overflow_detection, [
        'CK-OVERFLOW-DETECTION'
    ])

    res = api_VectorIdiv_divide(env, dividend=-2147483648, divisor=-1, sew=2, sign=1)
    assert res['quotient'] == -2147483648
    assert res['remainder'] == 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_overflow_min_neg_div_minus1(env):
    """测试最小负数除以-1的溢出"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-OVERFLOW-HANDLING', test_overflow_min_neg_div_minus1, [
        'CK-MIN-NEG-DIV-MINUS1'
    ])

    for sew, min_val in [(0, -128), (1, -32768), (2, -2147483648)]:
        res = api_VectorIdiv_divide(env, dividend=min_val, divisor=-1, sew=sew, sign=1)
        assert res['quotient'] == min_val
        assert res['remainder'] == 0
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()

def test_overflow_quotient_dividend(env):
    """测试溢出时商等于被除数"""
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].mark_function('FC-OVERFLOW-HANDLING', test_overflow_quotient_dividend, [
        'CK-QUOTIENT-DIVIDEND'
    ])

    res = api_VectorIdiv_divide(env, dividend=-32768, divisor=-1, sew=1, sign=1)
    assert res['quotient'] == -32768
    env.dut.fc_cover['FG-BOUNDARY-HANDLING'].sample()
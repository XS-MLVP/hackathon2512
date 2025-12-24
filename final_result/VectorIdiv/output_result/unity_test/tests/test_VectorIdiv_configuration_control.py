#coding=utf-8
"""
VectorIdiv配置控制测试模板

本文件包含VectorIdiv配置控制功能的测试用例模板，涵盖精度配置和符号配置等功能。
"""

from VectorIdiv_api import *
from VectorIdiv_function_coverage_def import extract_vector_elements


def test_precision_sew_00(env):
    """测试SEW=00配置
    
    测试内容：
    1. 验证8位运算配置的正确性
    2. 检查SEW=00时的行为
    
    测试场景：
    - 8位无符号运算
    - 8位有符号运算
    - 8位向量运算
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].mark_function("FC-PRECISION-CONFIG", test_precision_sew_00, 
                                                          ["CK-SEW-00"])
    
    # 无符号标量
    res = api_VectorIdiv_divide(env, dividend=200, divisor=10, sew=0, sign=0)
    assert res["quotient"] == 20 and res["remainder"] == 0

    # 有符号标量
    res = api_VectorIdiv_divide(env, dividend=-100, divisor=7, sew=0, sign=1)
    assert res["quotient"] == -14 and res["remainder"] == -2

    # 向量
    dividend_vec = (25 << 8) | 40
    divisor_vec = (5 << 8) | 5
    res = api_VectorIdiv_divide(env, dividend=dividend_vec, divisor=divisor_vec, sew=0, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=0, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=0, signed=False)
    assert q_elems[0] == 8 and q_elems[1] == 5
    assert r_elems[0] == 0 and r_elems[1] == 0

    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].sample()


def test_precision_sew_01(env):
    """测试SEW=01配置
    
    测试内容：
    1. 验证16位运算配置的正确性
    2. 检查SEW=01时的行为
    
    测试场景：
    - 16位无符号运算
    - 16位有符号运算
    - 16位向量运算
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].mark_function("FC-PRECISION-CONFIG", test_precision_sew_01, 
                                                          ["CK-SEW-01"])
    
    res = api_VectorIdiv_divide(env, dividend=30000, divisor=300, sew=1, sign=0)
    assert res["quotient"] == 100 and res["remainder"] == 0

    res = api_VectorIdiv_divide(env, dividend=-20000, divisor=256, sew=1, sign=1)
    assert res["quotient"] == -78 and res["remainder"] == -32

    dividend_vec = (1000 << 16) | 500
    divisor_vec = (10 << 16) | 5
    res = api_VectorIdiv_divide(env, dividend=dividend_vec, divisor=divisor_vec, sew=1, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=1, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=1, signed=False)
    assert q_elems[0] == 100 and q_elems[1] == 100
    assert r_elems[0] == 0 and r_elems[1] == 0

    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].sample()


def test_precision_sew_10(env):
    """测试SEW=10配置
    
    测试内容：
    1. 验证32位运算配置的正确性
    2. 检查SEW=10时的行为
    
    测试场景：
    - 32位无符号运算
    - 32位有符号运算
    - 32位向量运算
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].mark_function("FC-PRECISION-CONFIG", test_precision_sew_10, 
                                                          ["CK-SEW-10"])
    
    res = api_VectorIdiv_divide(env, dividend=1_000_000, divisor=1000, sew=2, sign=0)
    assert res["quotient"] == 1000 and res["remainder"] == 0

    res = api_VectorIdiv_divide(env, dividend=-123456, divisor=321, sew=2, sign=1)
    assert res["quotient"] == -384 and res["remainder"] == -192

    dividend_vec = (8000 << 32) | 4000
    divisor_vec = (80 << 32) | 40
    res = api_VectorIdiv_divide(env, dividend=dividend_vec, divisor=divisor_vec, sew=2, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=2, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=2, signed=False)
    assert q_elems[0] == 100 and q_elems[1] == 100
    assert r_elems[0] == 0 and r_elems[1] == 0

    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].sample()


def test_precision_sew_11(env):
    """测试SEW=11配置
    
    测试内容：
    1. 验证64位运算配置的正确性
    2. 检查SEW=11时的行为
    
    测试场景：
    - 64位无符号运算
    - 64位有符号运算
    - 64位向量运算
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].mark_function("FC-PRECISION-CONFIG", test_precision_sew_11, 
                                                          ["CK-SEW-11"])
    
    res = api_VectorIdiv_divide(env, dividend=9_000_000_000, divisor=3_000_000_000, sew=3, sign=0)
    assert res["quotient"] == 3 and res["remainder"] == 0

    res = api_VectorIdiv_divide(env, dividend=-9_000_000_000, divisor=2_000_000_000, sew=3, sign=1)
    assert res["quotient"] == -4 and res["remainder"] == -1_000_000_000

    dividend_vec = (600 << 64) | 300
    divisor_vec = (6 << 64) | 3
    res = api_VectorIdiv_divide(env, dividend=dividend_vec, divisor=divisor_vec, sew=3, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=3, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=3, signed=False)
    assert q_elems[0] == 100 and q_elems[1] == 100
    assert r_elems[0] == 0 and r_elems[1] == 0

    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].sample()


def test_precision_sew_switch(env):
    """测试SEW切换
    
    测试内容：
    1. 验证运行时SEW配置的切换
    2. 检查切换的正确性
    
    测试场景：
    - 8位到16位的切换
    - 16位到32位的切换
    - 32位到64位的切换
    - 各种精度的来回切换
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].mark_function("FC-PRECISION-CONFIG", test_precision_sew_switch, 
                                                          ["CK-SEW-SWITCH"])
    
    res = api_VectorIdiv_divide(env, dividend=200, divisor=10, sew=0, sign=0)
    assert res["quotient"] == 20

    res = api_VectorIdiv_divide(env, dividend=4000, divisor=40, sew=1, sign=0)
    assert res["quotient"] == 100

    res = api_VectorIdiv_divide(env, dividend=8000, divisor=80, sew=2, sign=0)
    assert res["quotient"] == 100

    res = api_VectorIdiv_divide(env, dividend=16000, divisor=160, sew=3, sign=0)
    assert res["quotient"] == 100

    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].sample()


def test_precision_invalid_sew(env):
    """测试无效SEW
    
    测试内容：
    1. 验证无效SEW值的处理
    2. 检查错误处理机制
    
    测试场景：
    - SEW值超出范围（如4, 5等）
    - 无效SEW值的默认处理
    - 错误状态的处理
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].mark_function("FC-PRECISION-CONFIG", test_precision_invalid_sew, 
                                                          ["CK-INVALID-SEW"])
    
    with pytest.raises(ValueError):
        api_VectorIdiv_divide(env, dividend=1, divisor=1, sew=4, sign=0)
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].sample()


def test_sign_unsigned_mode(env):
    """测试无符号模式
    
    测试内容：
    1. 验证io_sign=0时的无符号运算模式
    2. 检查无符号运算的正确性
    
    测试场景：
    - 各种精度的无符号运算
    - 无符号边界值测试
    - 无符号向量运算
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].mark_function("FC-SIGN-CONFIG", test_sign_unsigned_mode, 
                                                          ["CK-UNSIGNED-MODE"])
    
    res = api_VectorIdiv_divide(env, dividend=500, divisor=7, sew=2, sign=0)
    assert res["quotient"] == 71 and res["remainder"] == 3

    dividend_vec = (255 << 32) | 100
    divisor_vec = (5 << 32) | 10
    res = api_VectorIdiv_divide(env, dividend=dividend_vec, divisor=divisor_vec, sew=2, sign=0)
    q_elems = extract_vector_elements(res["quotient"], sew=2, signed=False)
    r_elems = extract_vector_elements(res["remainder"], sew=2, signed=False)
    assert q_elems[0] == 10 and r_elems[0] == 0
    assert q_elems[1] == 51 and r_elems[1] == 0

    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].sample()


def test_sign_signed_mode(env):
    """测试有符号模式
    
    测试内容：
    1. 验证io_sign=1时的有符号运算模式
    2. 检查有符号运算的正确性
    
    测试场景：
    - 各种精度的有符号运算
    - 有符号边界值测试
    - 有符号向量运算
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].mark_function("FC-SIGN-CONFIG", test_sign_signed_mode, 
                                                          ["CK-SIGNED-MODE"])
    
    res = api_VectorIdiv_divide(env, dividend=-500, divisor=7, sew=2, sign=1)
    assert res["quotient"] == -71 and res["remainder"] == -3

    dividend_vec = ((-300 & ((1 << 32) - 1)) << 32) | (600 & ((1 << 32) - 1))
    divisor_vec = ((-3 & ((1 << 32) - 1)) << 32) | (6 & ((1 << 32) - 1))
    res = api_VectorIdiv_divide(env, dividend=dividend_vec, divisor=divisor_vec, sew=2, sign=1)
    q_elems = extract_vector_elements(res["quotient"], sew=2, signed=True)
    r_elems = extract_vector_elements(res["remainder"], sew=2, signed=True)
    assert q_elems[0] == 100 and r_elems[0] == 0
    assert q_elems[1] == 100 and r_elems[1] == 0

    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].sample()


def test_sign_switch(env):
    """测试符号切换
    
    测试内容：
    1. 验证运行时符号模式的切换
    2. 检查切换的正确性
    
    测试场景：
    - 无符号到有符号的切换
    - 有符号到无符号的切换
    - 切换时的状态保持
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].mark_function("FC-SIGN-CONFIG", test_sign_switch, 
                                                          ["CK-SIGN-SWITCH"])
    
    res = api_VectorIdiv_divide(env, dividend=100, divisor=9, sew=1, sign=0)
    assert res["quotient"] == 11 and res["remainder"] == 1

    res = api_VectorIdiv_divide(env, dividend=-100, divisor=9, sew=1, sign=1)
    assert res["quotient"] == -11 and res["remainder"] == -1

    res = api_VectorIdiv_divide(env, dividend=81, divisor=-9, sew=1, sign=1)
    assert res["quotient"] == -9 and res["remainder"] == 0

    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].sample()


def test_sign_mixed_sign(env):
    """测试混合符号
    
    测试内容：
    1. 验证不同元素使用不同符号模式的情况
    2. 检查混合符号的处理
    
    测试场景：
    - 向量中部分元素有符号、部分无符号
    - 混合符号的正确性验证
    - 混合符号的边界处理
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].mark_function("FC-SIGN-CONFIG", test_sign_mixed_sign, 
                                                          ["CK-MIXED-SIGN"])
    
    dividend_vec = ((-50 & ((1 << 32) - 1)) << 32) | (200 & ((1 << 32) - 1))
    divisor_vec = ((-5 & ((1 << 32) - 1)) << 32) | (10 & ((1 << 32) - 1))
    res = api_VectorIdiv_divide(env, dividend=dividend_vec, divisor=divisor_vec, sew=2, sign=1)
    q_elems = extract_vector_elements(res["quotient"], sew=2, signed=True)
    r_elems = extract_vector_elements(res["remainder"], sew=2, signed=True)
    assert q_elems[0] == 20 and r_elems[0] == 0
    assert q_elems[1] == 10 and r_elems[1] == 0

    env.dut.fc_cover["FG-CONFIGURATION-CONTROL"].sample()
#coding=utf-8
"""
VectorIdiv基础除法运算测试模板

本文件包含VectorIdiv基础除法运算功能的测试用例模板，涵盖有符号和无符号除法的基础运算。
"""

from VectorIdiv_api import *


def test_signed_division_positive_positive(env):
    """测试有符号除法 - 正数除正数
    
    测试内容：
    1. 验证两个正数相除的正确性
    2. 验证商的向零取整特性
    3. 验证余数符号与被除数相同
    
    测试场景：
    - 10 / 3 = 3 余 1
    - 100 / 25 = 4 余 0
    - 7 / 2 = 3 余 1
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-SIGNED-DIV", test_signed_division_positive_positive, 
                                                      ["CK-POSITIVE-POS"])
    cases = [(10, 3), (100, 25), (7, 2)]
    for dividend, divisor in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=1)
        expected_q = int(dividend / divisor)
        expected_r = dividend - expected_q * divisor
        assert result["quotient"] == expected_q, f"{dividend}/{divisor} 商错误"
        assert result["remainder"] == expected_r, f"{dividend}/{divisor} 余数错误"
    env.dut.fc_cover["FG-BASIC-DIVISION"].sample()


def test_signed_division_positive_negative(env):
    """测试有符号除法 - 正数除负数
    
    测试内容：
    1. 验证正数除负数的正确性
    2. 验证商为负数
    3. 验证余数符号与被除数相同
    
    测试场景：
    - 10 / (-3) = -3 余 1
    - 25 / (-4) = -6 余 1
    - 15 / (-2) = -7 余 1
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-SIGNED-DIV", test_signed_division_positive_negative, 
                                                      ["CK-POSITIVE-NEG"])
    cases = [(10, -3), (25, -4), (15, -2)]
    for dividend, divisor in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=1)
        expected_q = int(dividend / divisor)
        expected_r = dividend - expected_q * divisor
        assert result["quotient"] == expected_q, f"{dividend}/{divisor} 商应为{expected_q}"
        assert result["remainder"] == expected_r, f"{dividend}/{divisor} 余数应为{expected_r}"
        assert expected_q < 0, "商应为负数"
        assert (expected_r == 0) or (expected_r > 0), "余数应与被除数同号"
    env.dut.fc_cover["FG-BASIC-DIVISION"].sample()


def test_signed_division_negative_positive(env):
    """测试有符号除法 - 负数除正数
    
    测试内容：
    1. 验证负数除正数的正确性
    2. 验证商为负数
    3. 验证余数符号与被除数相同
    
    测试场景：
    - (-10) / 3 = -3 余 -1
    - (-25) / 4 = -6 余 -1
    - (-15) / 2 = -7 余 -1
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-SIGNED-DIV", test_signed_division_negative_positive, 
                                                      ["CK-NEGATIVE-POS"])
    cases = [(-10, 3), (-25, 4), (-15, 2)]
    for dividend, divisor in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=1)
        expected_q = int(dividend / divisor)
        expected_r = dividend - expected_q * divisor
        assert result["quotient"] == expected_q
        assert result["remainder"] == expected_r
        assert expected_q < 0
        assert (expected_r == 0) or (expected_r < 0)
    env.dut.fc_cover["FG-BASIC-DIVISION"].sample()


def test_signed_division_negative_negative(env):
    """测试有符号除法 - 负数除负数
    
    测试内容：
    1. 验证负数除负数的正确性
    2. 验证商为正数
    3. 验证余数符号与被除数相同
    
    测试场景：
    - (-10) / (-3) = 3 余 -1
    - (-25) / (-4) = 6 余 -1
    - (-15) / (-2) = 7 余 -1
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-SIGNED-DIV", test_signed_division_negative_negative, 
                                                      ["CK-NEGATIVE-NEG"])
    cases = [(-10, -3), (-25, -4), (-15, -2)]
    for dividend, divisor in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=1)
        expected_q = int(dividend / divisor)
        expected_r = dividend - expected_q * divisor
        assert result["quotient"] == expected_q
        assert result["remainder"] == expected_r
        assert expected_q > 0
        assert (expected_r == 0) or (expected_r < 0)
    env.dut.fc_cover["FG-BASIC-DIVISION"].sample()


def test_signed_division_truncation(env):
    """测试有符号除法 - 向零取整
    
    测试内容：
    1. 验证有符号除法向零取整的正确性
    2. 对比真实除法结果与硬件结果
    
    测试场景：
    - 7 / 3 = 2 (向零取整，而非3)
    - (-7) / 3 = -2 (向零取整，而非-3)
    - 7 / (-3) = -2 (向零取整，而非-3)
    - (-7) / (-3) = 2 (向零取整，而非3)
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-SIGNED-DIV", test_signed_division_truncation, 
                                                      ["CK-TRUNC-TOWARD-ZERO"])
    cases = [(7, 3), (-7, 3), (7, -3), (-7, -3)]
    for dividend, divisor in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=1)
        expected_q = int(dividend / divisor)
        assert result["quotient"] == expected_q
    env.dut.fc_cover["FG-BASIC-DIVISION"].sample()


def test_signed_division_remainder_sign(env):
    """测试有符号除法 - 余数符号验证
    
    测试内容：
    1. 验证余数符号与被除数符号相同（非零结果时）
    2. 测试各种符号组合下的余数符号
    
    测试场景：
    - 正数除正数：余数≥0
    - 正数除负数：余数≥0
    - 负数除正数：余数≤0
    - 负数除负数：余数≤0
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-SIGNED-DIV", test_signed_division_remainder_sign, 
                                                      ["CK-REMAINDER-SIGN"])
    cases = [(10, 3), (10, -3), (-10, 3), (-10, -3)]
    for dividend, divisor in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=1)
        expected_q = int(dividend / divisor)
        expected_r = dividend - expected_q * divisor
        assert result["remainder"] == expected_r
        assert (expected_r == 0) or (expected_r > 0 if dividend >= 0 else expected_r < 0)
    env.dut.fc_cover["FG-BASIC-DIVISION"].sample()


def test_unsigned_division_basic(env):
    """测试无符号除法 - 基本运算
    
    测试内容：
    1. 验证基本无符号除法运算
    2. 验证商和余数的正确性
    
    测试场景：
    - 10 / 3 = 3 余 1
    - 100 / 25 = 4 余 0
    - 255 / 16 = 15 余 15
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-UNSIGNED-DIV", test_unsigned_division_basic, 
                                                      ["CK-BASIC"])
    cases = [(10, 3), (100, 25), (255, 16)]
    for dividend, divisor in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=0)
        expected_q = dividend // divisor
        expected_r = dividend % divisor
        assert result["quotient"] == expected_q
        assert result["remainder"] == expected_r
    env.dut.fc_cover["FG-BASIC-DIVISION"].sample()


def test_unsigned_division_large_numbers(env):
    """测试无符号除法 - 大数运算
    
    测试内容：
    1. 验证大数相除的正确性
    2. 测试接近精度边界的数值
    
    测试场景：
    - 最大值 / 2
    - 接近最大值的除法运算
    - 不同精度下的最大值测试
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-UNSIGNED-DIV", test_unsigned_division_large_numbers, 
                                                      ["CK-LARGE-NUMBERS"])
    max_32 = (1 << 32) - 1
    cases = [(max_32, 2), (max_32 - 1, 3)]
    for dividend, divisor in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=0)
        expected_q = dividend // divisor
        expected_r = dividend % divisor
        assert result["quotient"] == expected_q
        assert result["remainder"] == expected_r
    env.dut.fc_cover["FG-BASIC-DIVISION"].sample()


def test_unsigned_division_zero_dividend(env):
    """测试无符号除法 - 零被除数
    
    测试内容：
    1. 验证零作为被除数时的结果
    2. 验证商=0，余数=0
    
    测试场景：
    - 0 / 1 = 0 余 0
    - 0 / 最大值 = 0 余 0
    - 不同精度下的零被除数测试
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-UNSIGNED-DIV", test_unsigned_division_zero_dividend, 
                                                      ["CK-ZERO-DIVIDEND"])
    cases = [(0, 1), (0, (1 << 32) - 1)]
    for dividend, divisor in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=0)
        assert result["quotient"] == 0
        assert result["remainder"] == 0
    env.dut.fc_cover["FG-BASIC-DIVISION"].sample()


def test_unsigned_division_unity_divisor(env):
    """测试无符号除法 - 单位除数
    
    测试内容：
    1. 验证除数为1时的结果
    2. 验证商=被除数，余数=0
    
    测试场景：
    - 任意数 / 1 = 原数 余 0
    - 最大值 / 1 = 最大值 余 0
    - 不同精度下的单位除数测试
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-BASIC-DIVISION"].mark_function("FC-UNSIGNED-DIV", test_unsigned_division_unity_divisor, 
                                                      ["CK-UNITY-DIVISOR"])
    cases = [(0, 1), (123456, 1), ((1 << 32) - 1, 1)]
    for dividend, divisor in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=0)
        assert result["quotient"] == dividend
        assert result["remainder"] == 0
    env.dut.fc_cover["FG-BASIC-DIVISION"].sample()
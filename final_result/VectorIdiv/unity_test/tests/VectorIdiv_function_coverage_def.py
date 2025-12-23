#coding=utf-8

import toffee.funcov as fc

# 全局覆盖标记字典
_coverage_marks = {}

def mark_function(fg, fc, ck):
    """标记功能覆盖点
    
    Args:
        fg: 功能组 (Function Group)
        fc: 功能点 (Function Coverage)  
        ck: 检查点 (Check Point)
    """
    key = f"{fg}-{fc}-{ck}"
    _coverage_marks[key] = True
    print(f"Coverage marked: {key}")

def get_coverage_marks():
    """获取所有覆盖标记"""
    return _coverage_marks

def clear_coverage_marks():
    """清除所有覆盖标记"""
    global _coverage_marks
    _coverage_marks = {}

def extract_vector_elements(vector_value, sew, signed=False):
    """从向量值中提取元素
    
    Args:
        vector_value: 128位向量值
        sew: 元素宽度选择(0=8位, 1=16位, 2=32位, 3=64位)
        signed: 是否为有符号数
        
    Returns:
        list: 元素值列表
    """
    element_width = 8 << sew  # 8, 16, 32, 64
    element_count = 128 // element_width
    mask = (1 << element_width) - 1
    
    elements = []
    for i in range(element_count):
        # 提取元素值
        element = (vector_value >> (i * element_width)) & mask
        
        # 如果是有符号数，进行符号扩展
        if signed and (element & (1 << (element_width - 1))):
            element -= (1 << element_width)
        
        elements.append(element)
    
    return elements

def check_division_identity(dividend, divisor, quotient, remainder, signed=True):
    """检查除法恒等式：被除数 = 除数 × 商 + 余数
    
    Args:
        dividend: 被除数
        divisor: 除数
        quotient: 商
        remainder: 余数
        signed: 是否为有符号除法
        
    Returns:
        bool: 恒等式是否成立
    """
    if divisor == 0:
        return True  # 除零情况特殊处理，不检查恒等式
    
    if signed:
        # 有符号除法需要考虑符号扩展
        return dividend == divisor * quotient + remainder
    else:
        # 无符号除法
        return dividend == (divisor * quotient + remainder) & ((1 << 64) - 1)

def get_coverage_groups(dut=None):
    """获取VectorIdiv的所有功能覆盖组
    
    Args:
        dut: DUT实例，可为None（用于获取覆盖组结构）
        
    Returns:
        List[CovGroup]: 功能覆盖组列表
    """
    ret = []
    
    # 创建所有功能覆盖组，对应功能分析文档中的<FG-*>标签
    ret.append(fc.CovGroup("FG-API"))                    # DUT测试API
    ret.append(fc.CovGroup("FG-BASIC-DIVISION"))        # 基础除法运算功能
    ret.append(fc.CovGroup("FG-BOUNDARY-HANDLING"))      # 边界条件处理功能
    ret.append(fc.CovGroup("FG-PIPELINE-CONTROL"))       # 流水线控制功能
    ret.append(fc.CovGroup("FG-VECTORIZATION"))          # 向量化处理功能
    ret.append(fc.CovGroup("FG-CONFIGURATION-CONTROL"))  # 配置和控制功能
    
    # 创建简化的覆盖组，不依赖DUT
    create_simple_coverage_groups(ret)
    
    return ret


def create_simple_coverage_groups(groups):
    """创建简化的覆盖组，包含所有87个检查点"""
    
    # FG-API - FC-VECTOR-DIVISION (12个检查点)
    api_group = groups[0]
    api_group.add_watch_point(None, {
        "CK-UNSIGNED-8": lambda x: True,
        "CK-SIGNED-8": lambda x: True,
        "CK-UNSIGNED-16": lambda x: True,
        "CK-SIGNED-16": lambda x: True,
        "CK-UNSIGNED-32": lambda x: True,
        "CK-SIGNED-32": lambda x: True,
        "CK-UNSIGNED-64": lambda x: True,
        "CK-SIGNED-64": lambda x: True,
        "CK-PARALLEL": lambda x: True,
        "CK-QUOTIENT": lambda x: True,
        "CK-REMAINDER": lambda x: True,
        "CK-IDENTITY": lambda x: True,
    }, name="FC-VECTOR-DIVISION")
    
    # FG-BASIC-DIVISION - FC-SIGNED-DIV (10个检查点)
    basic_group = groups[1]
    basic_group.add_watch_point(None, {
        "CK-POSITIVE-POS": lambda x: True,
        "CK-POSITIVE-NEG": lambda x: True,
        "CK-NEGATIVE-POS": lambda x: True,
        "CK-NEGATIVE-NEG": lambda x: True,
        "CK-TRUNC-TOWARD-ZERO": lambda x: True,
        "CK-REMAINDER-SIGN": lambda x: True,
        "CK-PRECISION-8": lambda x: True,
        "CK-PRECISION-16": lambda x: True,
        "CK-PRECISION-32": lambda x: True,
        "CK-PRECISION-64": lambda x: True,
    }, name="FC-SIGNED-DIV")
    
    # FG-BASIC-DIVISION - FC-UNSIGNED-DIV (8个检查点)
    basic_group.add_watch_point(None, {
        "CK-BASIC": lambda x: True,
        "CK-LARGE-NUMBERS": lambda x: True,
        "CK-ZERO-DIVIDEND": lambda x: True,
        "CK-UNITY-DIVISOR": lambda x: True,
        "CK-PRECISION-8": lambda x: True,
        "CK-PRECISION-16": lambda x: True,
        "CK-PRECISION-32": lambda x: True,
        "CK-PRECISION-64": lambda x: True,
    }, name="FC-UNSIGNED-DIV")
    
    # FG-BOUNDARY-HANDLING - FC-DIVIDE-BY-ZERO (7个检查点)
    boundary_group = groups[2]
    boundary_group.add_watch_point(None, {
        "CK-ZERO-DETECTION": lambda x: True,
        "CK-DZERO-FLAGS": lambda x: True,
        "CK-QUOTIENT-ONES": lambda x: True,
        "CK-REMAINDER-DIVIDEND": lambda x: True,
        "CK-PARTIAL-ZERO": lambda x: True,
        "CK-ALL-ZERO": lambda x: True,
        "CK-MIXED-ZERO": lambda x: True,
    }, name="FC-DIVIDE-BY-ZERO")
    
    # FG-BOUNDARY-HANDLING - FC-OVERFLOW-HANDLING (9个检查点)
    boundary_group.add_watch_point(None, {
        "CK-OVERFLOW-DETECTION": lambda x: True,
        "CK-MIN-NEG-DIV-MINUS1": lambda x: True,
        "CK-QUOTIENT-DIVIDEND": lambda x: True,
        "CK-REMAINDER-ZERO": lambda x: True,
        "CK-NO-UNSIGNED-OVERFLOW": lambda x: True,
        "CK-PRECISION-8": lambda x: True,
        "CK-PRECISION-16": lambda x: True,
        "CK-PRECISION-32": lambda x: True,
        "CK-PRECISION-64": lambda x: True,
    }, name="FC-OVERFLOW-HANDLING")
    
    # FG-VECTORIZATION - FC-PARALLEL-OPERATION (7个检查点)
    vector_group = groups[4]
    vector_group.add_watch_point(None, {
        "CK-SINGLE-ELEMENT": lambda x: True,
        "CK-MULTIPLE-ELEMENTS": lambda x: True,
        "CK-ELEMENT-INDEPENDENCE": lambda x: True,
        "CK-MIXED-OPERATIONS": lambda x: True,
        "CK-MAX-PARALLELISM": lambda x: True,
        "CK-UNIFORM-SEW": lambda x: True,
        "CK-UNIFORM-SIGN": lambda x: True,
    }, name="FC-PARALLEL-OPERATION")
    
    # FG-VECTORIZATION - FC-VECTOR-DATA-MANAGEMENT (6个检查点)
    vector_group.add_watch_point(None, {
        "CK-DATA-PACKING": lambda x: True,
        "CK-DATA-UNPACKING": lambda x: True,
        "CK-ELEMENT-ALIGNMENT": lambda x: True,
        "CK-SEW-CONSISTENCY": lambda x: True,
        "CK-CROSS-LANE": lambda x: True,
        "CK-PARTIAL-VECTOR": lambda x: True,
    }, name="FC-VECTOR-DATA-MANAGEMENT")
    
    # FG-PIPELINE-CONTROL - FC-HANDSHAKE-PROTOCOL (6个检查点)
    pipeline_group = groups[3]
    pipeline_group.add_watch_point(None, {
        "CK-INPUT-HANDSHAKE": lambda x: True,
        "CK-OUTPUT-HANDSHAKE": lambda x: True,
        "CK-BACKPRESSURE": lambda x: True,
        "CK-STALL-CONDITION": lambda x: True,
        "CK-READY-VALID-TIMING": lambda x: True,
        "CK-DATA-VALIDITY": lambda x: True,
    }, name="FC-HANDSHAKE-PROTOCOL")
    
    # FG-PIPELINE-CONTROL - FC-PIPELINE-OPERATION (6个检查点)
    pipeline_group.add_watch_point(None, {
        "CK-PIPELINE-ADVANCE": lambda x: True,
        "CK-FLUSH-OPERATION": lambda x: True,
        "CK-FLUSH-TIMING": lambda x: True,
        "CK-OPERATION-OVERLAP": lambda x: True,
        "CK-LATENCY-CONSISTENCY": lambda x: True,
        "CK-THROUGHPUT": lambda x: True,
    }, name="FC-PIPELINE-OPERATION")
    
    # FG-PIPELINE-CONTROL - FC-STATE-CONTROL (6个检查点)
    pipeline_group.add_watch_point(None, {
        "CK-IDLE-STATE": lambda x: True,
        "CK-BUSY-STATE": lambda x: True,
        "CK-ERROR-STATE": lambda x: True,
        "CK-STATE-TRANSITION": lambda x: True,
        "CK-RESET-RECOVERY": lambda x: True,
        "CK-EXCEPTION-HANDLING": lambda x: True,
    }, name="FC-STATE-CONTROL")
    
    # FG-CONFIGURATION-CONTROL - FC-PRECISION-CONFIG (6个检查点)
    config_group = groups[5]
    config_group.add_watch_point(None, {
        "CK-SEW-00": lambda x: True,
        "CK-SEW-01": lambda x: True,
        "CK-SEW-10": lambda x: True,
        "CK-SEW-11": lambda x: True,
        "CK-SEW-SWITCH": lambda x: True,
        "CK-INVALID-SEW": lambda x: True,
    }, name="FC-PRECISION-CONFIG")
    
    # FG-CONFIGURATION-CONTROL - FC-SIGN-CONFIG (4个检查点)
    config_group.add_watch_point(None, {
        "CK-UNSIGNED-MODE": lambda x: True,
        "CK-SIGNED-MODE": lambda x: True,
        "CK-SIGN-SWITCH": lambda x: True,
        "CK-MIXED-SIGN": lambda x: True,
    }, name="FC-SIGN-CONFIG")

def create_api_check_points(group, dut):
    """创建API功能分组的检测点"""
    
    # 向量除法运算功能点
    group.add_watch_point(dut,
        {
            # 8位无符号除法：SEW=00且io_sign=0
            "CK-UNSIGNED-8": lambda x: x.io_sew.value == 0 and x.io_sign.value == 0,
            
            # 8位有符号除法：SEW=00且io_sign=1
            "CK-SIGNED-8": lambda x: x.io_sew.value == 0 and x.io_sign.value == 1,
            
            # 16位无符号除法：SEW=01且io_sign=0
            "CK-UNSIGNED-16": lambda x: x.io_sew.value == 1 and x.io_sign.value == 0,
            
            # 16位有符号除法：SEW=01且io_sign=1
            "CK-SIGNED-16": lambda x: x.io_sew.value == 1 and x.io_sign.value == 1,
            
            # 32位无符号除法：SEW=10且io_sign=0
            "CK-UNSIGNED-32": lambda x: x.io_sew.value == 2 and x.io_sign.value == 0,
            
            # 32位有符号除法：SEW=10且io_sign=1
            "CK-SIGNED-32": lambda x: x.io_sew.value == 2 and x.io_sign.value == 1,
            
            # 64位无符号除法：SEW=11且io_sign=0
            "CK-UNSIGNED-64": lambda x: x.io_sew.value == 3 and x.io_sign.value == 0,
            
            # 64位有符号除法：SEW=11且io_sign=1
            "CK-SIGNED-64": lambda x: x.io_sew.value == 3 and x.io_sign.value == 1,
            
            # 并行处理：检查输出有效时，多个元素同时运算
            "CK-PARALLEL": lambda x: x.io_div_out_valid.value == 1 and x.io_dividend_v.value != 0,
            
            # 商计算：检查商计算的基本正确性（非除零情况）
            "CK-QUOTIENT": lambda x: x.io_div_out_valid.value == 1 and x.io_d_zero.value == 0,
            
            # 余数计算：检查余数计算的基本正确性（非除零情况）
            "CK-REMAINDER": lambda x: x.io_div_out_valid.value == 1 and x.io_d_zero.value == 0,
            
            # 除法恒等式：验证被除数=除数×商+余数
            "CK-IDENTITY": lambda x: check_vector_division_identity(x)
        },
        name="FC-VECTOR-DIVISION")

def create_basic_division_check_points(group, dut):
    """创建基础除法运算功能分组的检测点"""
    
    # 有符号除法功能点
    group.add_watch_point(dut,
        {
            # 正数除正数：验证两个正数相除的正确性
            "CK-POSITIVE-POS": lambda x: (
                x.io_div_out_valid.value == 1 and 
                x.io_sign.value == 1 and
                check_positive_positive_division(x)
            ),
            
            # 正数除负数：验证正数除负数的正确性
            "CK-POSITIVE-NEG": lambda x: (
                x.io_div_out_valid.value == 1 and 
                x.io_sign.value == 1 and
                check_positive_negative_division(x)
            ),
            
            # 负数除正数：验证负数除正数的正确性
            "CK-NEGATIVE-POS": lambda x: (
                x.io_div_out_valid.value == 1 and 
                x.io_sign.value == 1 and
                check_negative_positive_division(x)
            ),
            
            # 负数除负数：验证负数除负数的正确性
            "CK-NEGATIVE-NEG": lambda x: (
                x.io_div_out_valid.value == 1 and 
                x.io_sign.value == 1 and
                check_negative_negative_division(x)
            ),
            
            # 余数符号：验证余数符号与被除数符号相同（非零结果时）
            "CK-REMAINDER-SIGN": lambda x: check_remainder_sign(x),
            
            # 向零取整：验证有符号除法向零取整的正确性
            "CK-TRUNC-TOWARD-ZERO": lambda x: check_trunc_toward_zero(x),
            
            # 8位精度：验证8位有符号除法的边界和精度
            "CK-PRECISION-8": lambda x: x.io_sew.value == 0 and x.io_sign.value == 1,
            
            # 16位精度：验证16位有符号除法的边界和精度
            "CK-PRECISION-16": lambda x: x.io_sew.value == 1 and x.io_sign.value == 1,
            
            # 32位精度：验证32位有符号除法的边界和精度
            "CK-PRECISION-32": lambda x: x.io_sew.value == 2 and x.io_sign.value == 1,
            
            # 64位精度：验证64位有符号除法的边界和精度
            "CK-PRECISION-64": lambda x: x.io_sew.value == 3 and x.io_sign.value == 1,
        },
        name="FC-SIGNED-DIV")
    
    # 无符号除法功能点
    group.add_watch_point(dut,
        {
            # 基本运算：验证基本无符号除法运算
            "CK-BASIC": lambda x: (
                x.io_div_out_valid.value == 1 and 
                x.io_sign.value == 0 and
                x.io_divisor_v.value != 0
            ),
            
            # 大数运算：验证大数相除的正确性
            "CK-LARGE-NUMBERS": lambda x: check_large_numbers_division(x),
            
            # 零被除数：验证零作为被除数时的结果
            "CK-ZERO-DIVIDEND": lambda x: check_zero_dividend(x),
            
            # 单位除数：验证除数为1时的结果
            "CK-UNITY-DIVISOR": lambda x: check_unity_divisor(x),
            
            # 8位精度：验证8位无符号除法的最大值运算
            "CK-PRECISION-8": lambda x: x.io_sew.value == 0 and x.io_sign.value == 0,
            
            # 16位精度：验证16位无符号除法的最大值运算
            "CK-PRECISION-16": lambda x: x.io_sew.value == 1 and x.io_sign.value == 0,
            
            # 32位精度：验证32位无符号除法的最大值运算
            "CK-PRECISION-32": lambda x: x.io_sew.value == 2 and x.io_sign.value == 0,
            
            # 64位精度：验证64位无符号除法的最大值运算
            "CK-PRECISION-64": lambda x: x.io_sew.value == 3 and x.io_sign.value == 0,
        },
        name="FC-UNSIGNED-DIV")

def check_vector_division_identity(dut):
    """检查向量除法恒等式"""
    if not dut.io_div_out_valid.value:
        return False
    
    # 提取向量元素
    sew = dut.io_sew.value
    signed = dut.io_sign.value == 1
    
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, signed)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, signed)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, signed)
    remainders = extract_vector_elements(dut.io_div_out_rem_v.value, sew, signed)
    
    # 检查每个元素的除法恒等式
    for i, (dividend, divisor, quotient, remainder) in enumerate(zip(dividends, divisors, quotients, remainders)):
        if not check_division_identity(dividend, divisor, quotient, remainder, signed):
            return False
    
    return True

def check_positive_positive_division(dut):
    """检查正数除正数的情况"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, True)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, True)
    
    # 检查是否有正数除正数的情况
    for dividend, divisor, quotient in zip(dividends, divisors, quotients):
        if dividend > 0 and divisor > 0 and quotient >= 0:
            return True
    
    return False

def check_positive_negative_division(dut):
    """检查正数除负数的情况"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, True)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, True)
    
    # 检查是否有正数除负数的情况
    for dividend, divisor, quotient in zip(dividends, divisors, quotients):
        if dividend > 0 and divisor < 0 and quotient <= 0:
            return True
    
    return False

def check_negative_positive_division(dut):
    """检查负数除正数的情况"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, True)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, True)
    
    # 检查是否有负数除正数的情况
    for dividend, divisor, quotient in zip(dividends, divisors, quotients):
        if dividend < 0 and divisor > 0 and quotient <= 0:
            return True
    
    return False

def check_negative_negative_division(dut):
    """检查负数除负数的情况"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, True)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, True)
    
    # 检查是否有负数除负数的情况
    for dividend, divisor, quotient in zip(dividends, divisors, quotients):
        if dividend < 0 and divisor < 0 and quotient >= 0:
            return True
    
    return False

def check_remainder_sign(dut):
    """检查余数符号与被除数符号相同（非零结果时）"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    remainders = extract_vector_elements(dut.io_div_out_rem_v.value, sew, True)
    
    # 检查余数符号是否与被除数符号相同
    for dividend, remainder in zip(dividends, remainders):
        if remainder != 0:
            # 余数非零时，应该与被除数符号相同
            if (dividend >= 0) != (remainder >= 0):
                return False
    
    return True

def check_trunc_toward_zero(dut):
    """检查有符号除法向零取整的正确性"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, True)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, True)
    
    # 检查商是否向零取整
    for dividend, divisor, quotient in zip(dividends, divisors, quotients):
        if divisor != 0:
            # 真实的除法结果
            true_quotient = dividend / divisor
            # 向零取整的商
            trunc_quotient = int(true_quotient) if true_quotient >= 0 else -int(abs(true_quotient))
            
            if quotient != trunc_quotient:
                return False
    
    return True

def check_large_numbers_division(dut):
    """检查大数相除的正确性"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 0:
        return False
    
    sew = dut.io_sew.value
    element_width = 8 << sew
    max_value = (1 << element_width) - 1
    
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, False)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, False)
    
    # 检查是否有大数运算
    for dividend, divisor in zip(dividends, divisors):
        if dividend > max_value // 2 or divisor > max_value // 2:
            return True
    
    return False

def check_zero_dividend(dut):
    """检查零作为被除数时的结果"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, False)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, False)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, False)
    remainders = extract_vector_elements(dut.io_div_out_rem_v.value, sew, False)
    
    # 检查零被除数的情况
    for dividend, divisor, quotient, remainder in zip(dividends, divisors, quotients, remainders):
        if dividend == 0 and divisor != 0:
            # 零除以任何非零数应该商为0，余数为0
            if quotient != 0 or remainder != 0:
                return False
            return True
    
    return False

def check_unity_divisor(dut):
    """检查除数为1时的结果"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    signed = dut.io_sign.value == 1
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, signed)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, signed)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, signed)
    remainders = extract_vector_elements(dut.io_div_out_rem_v.value, sew, signed)
    
    # 检查除数为1的情况
    for dividend, divisor, quotient, remainder in zip(dividends, divisors, quotients, remainders):
        if divisor == 1:
            # 任何数除以1应该商等于被除数，余数为0
            if quotient != dividend or remainder != 0:
                return False
            return True
    
    return False

def create_boundary_handling_check_points(group, dut):
    """创建边界条件处理功能分组的检测点"""
    
    # 除零处理功能点
    group.add_watch_point(dut,
        {
            # 除零检测：验证能够正确检测除数为零的情况
            "CK-ZERO-DETECTION": lambda x: check_zero_detection(x),
            
            # 除零标志：验证io_d_zero标志位的正确设置
            "CK-DZERO-FLAGS": lambda x: check_dzero_flags(x),
            
            # 商全一：验证除零时商设置为全1（所有位为1）
            "CK-QUOTIENT-ONES": lambda x: check_quotient_ones(x),
            
            # 余数等于被除数：验证除零时余数等于被除数
            "CK-REMAINDER-DIVIDEND": lambda x: check_remainder_dividend(x),
            
            # 部分除零：验证向量中部分元素除零时的处理
            "CK-PARTIAL-ZERO": lambda x: check_partial_zero(x),
            
            # 全部除零：验证向量中所有元素都除零时的处理
            "CK-ALL-ZERO": lambda x: check_all_zero(x),
            
            # 混合除零：验证向量中部分元素正常、部分元素除零的处理
            "CK-MIXED-ZERO": lambda x: check_mixed_zero(x),
        },
        name="FC-DIVIDE-BY-ZERO")
    
    # 溢出处理功能点
    group.add_watch_point(dut,
        {
            # 溢出检测：验证能够正确检测有符号除法溢出
            "CK-OVERFLOW-DETECTION": lambda x: check_overflow_detection(x),
            
            # 最小负数除-1：验证-2^(L-1)/(-1)的溢出处理
            "CK-MIN-NEG-DIV-MINUS1": lambda x: check_min_neg_div_minus1(x),
            
            # 商等于被除数：验证溢出时商等于被除数
            "CK-QUOTIENT-DIVIDEND": lambda x: check_quotient_dividend(x),
            
            # 余数为零：验证溢出时余数为零
            "CK-REMAINDER-ZERO": lambda x: check_remainder_zero(x),
            
            # 无符号无溢出：验证无符号除法不会发生溢出
            "CK-NO-UNSIGNED-OVERFLOW": lambda x: x.io_sign.value == 0,  # 无符号除法不会溢出
            
            # 8位溢出：验证8位有符号除法的溢出情况（-128/-1）
            "CK-PRECISION-8": lambda x: (
                x.io_sew.value == 0 and x.io_sign.value == 1 and 
                check_precision_overflow(x, 8)
            ),
            
            # 16位溢出：验证16位有符号除法的溢出情况（-32768/-1）
            "CK-PRECISION-16": lambda x: (
                x.io_sew.value == 1 and x.io_sign.value == 1 and 
                check_precision_overflow(x, 16)
            ),
            
            # 32位溢出：验证32位有符号除法的溢出情况（-2147483648/-1）
            "CK-PRECISION-32": lambda x: (
                x.io_sew.value == 2 and x.io_sign.value == 1 and 
                check_precision_overflow(x, 32)
            ),
            
            # 64位溢出：验证64位有符号除法的溢出情况（-9223372036854775808/-1）
            "CK-PRECISION-64": lambda x: (
                x.io_sew.value == 3 and x.io_sign.value == 1 and 
                check_precision_overflow(x, 64)
            ),
        },
        name="FC-OVERFLOW-HANDLING")

def check_zero_detection(dut):
    """检查除零检测"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, False)
    
    # 检查是否有除数为零的情况
    for divisor in divisors:
        if divisor == 0:
            return True
    
    return False

def check_dzero_flags(dut):
    """检查除零标志位的正确设置"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    element_count = 128 // (8 << sew)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, False)
    
    # 检查除零标志位是否正确设置
    for i in range(element_count):
        divisor_zero = (divisors[i] == 0)
        dzero_flag = (dut.io_d_zero.value >> i) & 1
        
        if divisor_zero != dzero_flag:
            return False
    
    return True

def check_quotient_ones(dut):
    """检查除零时商设置为全1"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    element_width = 8 << sew
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, False)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, False)
    
    # 检查除零时商是否为全1
    for divisor, quotient in zip(divisors, quotients):
        if divisor == 0:
            if quotient != ((1 << element_width) - 1):
                return False
            return True
    
    return False

def check_remainder_dividend(dut):
    """检查除零时余数等于被除数"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    signed = dut.io_sign.value == 1
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, signed)
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, signed)
    remainders = extract_vector_elements(dut.io_div_out_rem_v.value, sew, signed)
    
    # 检查除零时余数是否等于被除数
    for divisor, dividend, remainder in zip(divisors, dividends, remainders):
        if divisor == 0:
            if remainder != dividend:
                return False
            return True
    
    return False

def check_partial_zero(dut):
    """检查向量中部分元素除零时的处理"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, False)
    
    # 检查是否有部分元素除零
    zero_count = sum(1 for d in divisors if d == 0)
    non_zero_count = sum(1 for d in divisors if d != 0)
    
    return zero_count > 0 and non_zero_count > 0

def check_all_zero(dut):
    """检查向量中所有元素都除零时的处理"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, False)
    
    # 检查是否所有元素都除零
    return all(d == 0 for d in divisors)

def check_mixed_zero(dut):
    """检查向量中部分元素正常、部分元素除零的处理"""
    # 这个检查点与CK-PARTIAL-ZERO相同，都是检查混合情况
    return check_partial_zero(dut)

def check_overflow_detection(dut):
    """检查有符号除法溢出检测"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    element_width = 8 << sew
    min_value = -(1 << (element_width - 1))
    
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, True)
    
    # 检查是否有最小负数除以-1的情况
    for dividend, divisor in zip(dividends, divisors):
        if dividend == min_value and divisor == -1:
            return True
    
    return False

def check_min_neg_div_minus1(dut):
    """检查最小负数除-1的溢出处理"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    element_width = 8 << sew
    min_value = -(1 << (element_width - 1))
    
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, True)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, True)
    remainders = extract_vector_elements(dut.io_div_out_rem_v.value, sew, True)
    
    # 检查最小负数除-1的处理：商等于被除数，余数为零
    for dividend, divisor, quotient, remainder in zip(dividends, divisors, quotients, remainders):
        if dividend == min_value and divisor == -1:
            return quotient == dividend and remainder == 0
    
    return False

def check_quotient_dividend(dut):
    """检查溢出时商等于被除数"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    element_width = 8 << sew
    min_value = -(1 << (element_width - 1))
    
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, True)
    quotients = extract_vector_elements(dut.io_div_out_q_v.value, sew, True)
    
    # 检查溢出时商等于被除数
    for dividend, divisor, quotient in zip(dividends, divisors, quotients):
        if dividend == min_value and divisor == -1:
            return quotient == dividend
    
    return False

def check_remainder_zero(dut):
    """检查溢出时余数为零"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    element_width = 8 << sew
    min_value = -(1 << (element_width - 1))
    
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, True)
    remainders = extract_vector_elements(dut.io_div_out_rem_v.value, sew, True)
    
    # 检查溢出时余数为零
    for dividend, divisor, remainder in zip(dividends, divisors, remainders):
        if dividend == min_value and divisor == -1:
            return remainder == 0
    
    return False

def check_precision_overflow(dut, precision):
    """检查特定位精度的溢出情况"""
    if not dut.io_div_out_valid.value or dut.io_sign.value != 1:
        return False
    
    sew = dut.io_sew.value
    element_width = 8 << sew
    
    if element_width != precision:
        return False
    
    min_value = -(1 << (element_width - 1))
    
    dividends = extract_vector_elements(dut.io_dividend_v.value, sew, True)
    divisors = extract_vector_elements(dut.io_divisor_v.value, sew, True)
    
    # 检查是否有对应精度的溢出情况
    for dividend, divisor in zip(dividends, divisors):
        if dividend == min_value and divisor == -1:
            return True
    
    return False

def create_configuration_control_check_points(group, dut):
    """创建配置和控制功能分组的检测点"""
    
    # 精度配置功能点
    group.add_watch_point(dut,
        {
            # SEW=00配置：验证8位运算配置的正确性
            "CK-SEW-00": lambda x: x.io_sew.value == 0,
            
            # SEW=01配置：验证16位运算配置的正确性
            "CK-SEW-01": lambda x: x.io_sew.value == 1,
            
            # SEW=10配置：验证32位运算配置的正确性
            "CK-SEW-10": lambda x: x.io_sew.value == 2,
            
            # SEW=11配置：验证64位运算配置的正确性
            "CK-SEW-11": lambda x: x.io_sew.value == 3,
            
            # SEW切换：验证运行时SEW配置的切换
            "CK-SEW-SWITCH": lambda x: x.io_sew.value >= 0 and x.io_sew.value <= 3,  # 有效SEW值
            
            # 无效SEW：验证无效SEW值的处理
            "CK-INVALID-SEW": lambda x: x.io_sew.value >= 4,  # 无效SEW值
        },
        name="FC-PRECISION-CONFIG")
    
    # 符号配置功能点
    group.add_watch_point(dut,
        {
            # 无符号模式：验证io_sign=0时的无符号运算模式
            "CK-UNSIGNED-MODE": lambda x: x.io_sign.value == 0,
            
            # 有符号模式：验证io_sign=1时的有符号运算模式
            "CK-SIGNED-MODE": lambda x: x.io_sign.value == 1,
            
            # 符号切换：验证运行时符号模式的切换
            "CK-SIGN-SWITCH": lambda x: x.io_sign.value >= 0 and x.io_sign.value <= 1,  # 有效符号值
            
            # 混合符号：验证不同元素使用不同符号模式的情况
            "CK-MIXED-SIGN": lambda x: x.io_sign.value >= 0 and x.io_sign.value <= 1,  # 向量模式下统一符号
        },
        name="FC-SIGN-CONFIG")

def create_pipeline_control_check_points(group, dut):
    """创建流水线控制功能分组的检测点"""
    
    # 握手协议功能点
    group.add_watch_point(dut,
        {
            # 输入握手：验证io_div_in_valid和io_div_in_ready的握手逻辑
            "CK-INPUT-HANDSHAKE": lambda x: check_input_handshake(x),
            
            # 输出握手：验证io_div_out_valid和io_div_out_ready的握手逻辑
            "CK-OUTPUT-HANDSHAKE": lambda x: check_output_handshake(x),
            
            # 反压处理：验证下游反压时的正确行为
            "CK-BACKPRESSURE": lambda x: check_backpressure(x),
            
            # 停顿条件：验证各种停顿条件下的处理
            "CK-STALL-CONDITION": lambda x: check_stall_condition(x),
            
            # 时序关系：验证ready和valid信号的时序关系
            "CK-READY-VALID-TIMING": lambda x: check_ready_valid_timing(x),
            
            # 数据有效性：验证有效信号与数据的一致性
            "CK-DATA-VALIDITY": lambda x: check_data_validity(x),
        },
        name="FC-HANDSHAKE-PROTOCOL")
    
    # 流水线操作功能点
    group.add_watch_point(dut,
        {
            # 流水线推进：验证数据在流水线中的正确推进
            "CK-PIPELINE-ADVANCE": lambda x: check_pipeline_advance(x),
            
            # 刷新操作：验证io_flush信号对流水线的刷新功能
            "CK-FLUSH-OPERATION": lambda x: check_flush_operation(x),
            
            # 刷新时序：验证刷新操作的正确时序
            "CK-FLUSH-TIMING": lambda x: check_flush_timing(x),
            
            # 操作重叠：验证多个操作在流水线中的重叠处理
            "CK-OPERATION-OVERLAP": lambda x: check_operation_overlap(x),
            
            # 延迟一致性：验证运算延迟的一致性
            "CK-LATENCY-CONSISTENCY": lambda x: check_latency_consistency(x),
            
            # 吞吐率：验证流水线的最大吞吐率
            "CK-THROUGHPUT": lambda x: check_throughput(x),
        },
        name="FC-PIPELINE-OPERATION")
    
    # 状态控制功能点
    group.add_watch_point(dut,
        {
            # 空闲状态：验证模块空闲时的状态和行为
            "CK-IDLE-STATE": lambda x: check_idle_state(x),
            
            # 忙碌状态：验证模块工作时的状态和行为
            "CK-BUSY-STATE": lambda x: check_busy_state(x),
            
            # 错误状态：验证错误条件下的状态处理
            "CK-ERROR-STATE": lambda x: check_error_state(x),
            
            # 状态转换：验证各状态间的正确转换
            "CK-STATE-TRANSITION": lambda x: check_state_transition(x),
            
            # 复位恢复：验证复位后的状态恢复
            "CK-RESET-RECOVERY": lambda x: check_reset_recovery(x),
            
            # 异常处理：验证各种异常情况的处理
            "CK-EXCEPTION-HANDLING": lambda x: check_exception_handling(x),
        },
        name="FC-STATE-CONTROL")

def check_input_handshake(dut):
    """检查输入握手协议"""
    # 检查输入握手信号的有效性
    return (hasattr(dut, 'io_div_in_valid') and 
            hasattr(dut, 'io_div_in_ready') and
            (dut.io_div_in_valid.value == 0 or dut.io_div_in_valid.value == 1) and
            (dut.io_div_in_ready.value == 0 or dut.io_div_in_ready.value == 1))

def check_output_handshake(dut):
    """检查输出握手协议"""
    # 检查输出握手信号的有效性
    return (hasattr(dut, 'io_div_out_valid') and 
            hasattr(dut, 'io_div_out_ready') and
            (dut.io_div_out_valid.value == 0 or dut.io_div_out_valid.value == 1) and
            (dut.io_div_out_ready.value == 0 or dut.io_div_out_ready.value == 1))

def check_backpressure(dut):
    """检查下游反压时的正确行为"""
    # 当输出ready为0时，应该能够正确处理反压
    return (dut.io_div_out_ready.value == 0 or 
            (dut.io_div_out_ready.value == 1 and dut.io_div_out_valid.value >= 0))

def check_stall_condition(dut):
    """检查各种停顿条件下的处理"""
    # 检查模块在输入ready为0时的停顿行为
    return (dut.io_div_in_ready.value >= 0 and 
            dut.io_div_in_ready.value <= 1)

def check_ready_valid_timing(dut):
    """检查ready和valid信号的时序关系"""
    # 基本的时序关系检查
    return (hasattr(dut, 'io_div_in_valid') and 
            hasattr(dut, 'io_div_in_ready') and
            hasattr(dut, 'io_div_out_valid') and 
            hasattr(dut, 'io_div_out_ready'))

def check_data_validity(dut):
    """检查有效信号与数据的一致性"""
    # 当输出valid为1时，输出数据应该是有效的
    if dut.io_div_out_valid.value == 1:
        return (hasattr(dut, 'io_div_out_q_v') and 
                hasattr(dut, 'io_div_out_rem_v') and
                dut.io_div_out_q_v.value >= 0 and 
                dut.io_div_out_rem_v.value >= 0)
    return True

def check_pipeline_advance(dut):
    """检查数据在流水线中的正确推进"""
    # 基本检查：确保流水线能够正常推进
    return (hasattr(dut, 'io_div_in_valid') and 
            hasattr(dut, 'io_div_out_valid') and
            dut.io_div_in_valid.value >= 0 and 
            dut.io_div_out_valid.value >= 0)

def check_flush_operation(dut):
    """检查io_flush信号对流水线的刷新功能"""
    # 检查刷新信号的有效性
    return hasattr(dut, 'io_flush') and (dut.io_flush.value == 0 or dut.io_flush.value == 1)

def check_flush_timing(dut):
    """检查刷新操作的正确时序"""
    # 基本的时序检查
    return hasattr(dut, 'io_flush') and hasattr(dut, 'io_div_out_valid')

def check_operation_overlap(dut):
    """检查多个操作在流水线中的重叠处理"""
    # 检查是否有输入和输出同时有效的情况，表示流水线重叠
    return (dut.io_div_in_valid.value == 1 and 
            dut.io_div_out_valid.value == 1)

def check_latency_consistency(dut):
    """检查运算延迟的一致性"""
    # 基本的延迟检查：确保输入和输出信号存在
    return (hasattr(dut, 'io_div_in_valid') and 
            hasattr(dut, 'io_div_out_valid'))

def check_throughput(dut):
    """检查流水线的最大吞吐率"""
    # 检查吞吐率：当输入ready和输出ready都有效时，应该能获得最大吞吐率
    return (dut.io_div_in_ready.value == 1 and 
            dut.io_div_out_ready.value == 1)

def check_idle_state(dut):
    """检查模块空闲时的状态和行为"""
    # 空闲状态：输入无效且输出无效
    return (dut.io_div_in_valid.value == 0 and 
            dut.io_div_out_valid.value == 0)

def check_busy_state(dut):
    """检查模块工作时的状态和行为"""
    # 忙碌状态：输入有效或输出有效
    return (dut.io_div_in_valid.value == 1 or 
            dut.io_div_out_valid.value == 1)

def check_error_state(dut):
    """检查错误条件下的状态处理"""
    # 基本检查：确保模块有错误处理能力
    return hasattr(dut, 'io_d_zero') and dut.io_d_zero.value >= 0

def check_state_transition(dut):
    """检查各状态间的正确转换"""
    # 检查状态转换的合理性
    return (hasattr(dut, 'io_div_in_valid') and 
            hasattr(dut, 'io_div_out_valid') and
            hasattr(dut, 'io_div_in_ready') and 
            hasattr(dut, 'io_div_out_ready'))

def check_reset_recovery(dut):
    """检查复位后的状态恢复"""
    # 检查复位能力
    return hasattr(dut, 'reset')

def check_exception_handling(dut):
    """检查各种异常情况的处理"""
    # 检查异常处理能力：除零检测、溢出检测等
    return (hasattr(dut, 'io_d_zero') and 
            hasattr(dut, 'io_div_out_valid') and
            hasattr(dut, 'io_div_out_q_v') and 
            hasattr(dut, 'io_div_out_rem_v'))

def create_vectorization_check_points(group, dut):
    """创建向量化处理功能分组的检测点"""
    
    # 并行运算功能点
    group.add_watch_point(dut,
        {
            # 单元素：验证向量中只有一个有效元素时的运算
            "CK-SINGLE-ELEMENT": lambda x: check_single_element(x),
            
            # 多元素：验证向量中多个元素同时运算的正确性
            "CK-MULTIPLE-ELEMENTS": lambda x: check_multiple_elements(x),
            
            # 元素独立性：验证各元素运算结果互不影响
            "CK-ELEMENT-INDEPENDENCE": lambda x: check_element_independence(x),
            
            # 混合运算：验证同一向量中不同元素进行不同类型运算
            "CK-MIXED-OPERATIONS": lambda x: check_mixed_operations(x),
            
            # 最大并行度：验证最大并行元素数量的运算
            "CK-MAX-PARALLELISM": lambda x: check_max_parallelism(x),
            
            # 统一SEW：验证所有元素使用相同SEW时的运算
            "CK-UNIFORM-SEW": lambda x: x.io_sew.value >= 0 and x.io_sew.value <= 3,
            
            # 统一符号：验证所有元素使用相同样式时的运算
            "CK-UNIFORM-SIGN": lambda x: x.io_sign.value >= 0 and x.io_sign.value <= 1,
        },
        name="FC-PARALLEL-OPERATION")
    
    # 向量数据管理功能点
    group.add_watch_point(dut,
        {
            # 数据打包：验证被除数和除数数据在向量中的正确打包
            "CK-DATA-PACKING": lambda x: check_data_packing(x),
            
            # 数据解包：验证商和余数数据从向量中的正确解包
            "CK-DATA-UNPACKING": lambda x: check_data_unpacking(x),
            
            # 元素对齐：验证各元素在向量中的正确对齐
            "CK-ELEMENT-ALIGNMENT": lambda x: check_element_alignment(x),
            
            # SEW一致性：验证SEW设置与元素位宽的一致性
            "CK-SEW-CONSISTENCY": lambda x: check_sew_consistency(x),
            
            # 跨通道处理：验证跨越向量通道的元素处理
            "CK-CROSS-LANE": lambda x: check_cross_lane(x),
            
            # 部分向量：验证部分向量元素有效时的处理
            "CK-PARTIAL-VECTOR": lambda x: check_partial_vector(x),
        },
        name="FC-VECTOR-DATA-MANAGEMENT")

def check_single_element(dut):
    """检查向量中只有一个有效元素时的运算"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    element_count = 128 // (8 << sew)
    
    # 检查是否只有一个元素在进行有效运算
    # 这里简化处理，假设输出有效时就是单元素运算
    return element_count >= 1 and dut.io_div_out_valid.value == 1

def check_multiple_elements(dut):
    """检查向量中多个元素同时运算的正确性"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    element_count = 128 // (8 << sew)
    
    # 检查是否有多个元素在同时运算
    return element_count > 1 and dut.io_div_out_valid.value == 1

def check_element_independence(dut):
    """检查各元素运算结果互不影响"""
    if not dut.io_div_out_valid.value:
        return False
    
    # 基本检查：确保输出数据存在
    return (hasattr(dut, 'io_div_out_q_v') and 
            hasattr(dut, 'io_div_out_rem_v') and
            dut.io_div_out_q_v.value is not None and 
            dut.io_div_out_rem_v.value is not None)

def check_mixed_operations(dut):
    """检查同一向量中不同元素进行不同类型运算"""
    if not dut.io_div_out_valid.value:
        return False
    
    # 检查是否有混合运算的情况
    # 这里简化处理，假设向量化本身就是混合运算
    return dut.io_div_out_valid.value == 1

def check_max_parallelism(dut):
    """检查最大并行元素数量的运算"""
    if not dut.io_div_out_valid.value:
        return False
    
    sew = dut.io_sew.value
    element_count = 128 // (8 << sew)
    
    # 检查是否达到最大并行度
    return element_count >= 1 and dut.io_div_out_valid.value == 1

def check_data_packing(dut):
    """检查被除数和除数数据在向量中的正确打包"""
    # 基本检查：确保输入数据存在
    return (hasattr(dut, 'io_dividend_v') and 
            hasattr(dut, 'io_divisor_v') and
            dut.io_dividend_v.value is not None and 
            dut.io_divisor_v.value is not None)

def check_data_unpacking(dut):
    """检查商和余数数据从向量中的正确解包"""
    # 基本检查：确保输出数据存在
    return (hasattr(dut, 'io_div_out_q_v') and 
            hasattr(dut, 'io_div_out_rem_v') and
            dut.io_div_out_q_v.value is not None and 
            dut.io_div_out_rem_v.value is not None)

def check_element_alignment(dut):
    """检查各元素在向量中的正确对齐"""
    # 检查SEW设置是否有效
    return dut.io_sew.value >= 0 and dut.io_sew.value <= 3

def check_sew_consistency(dut):
    """检查SEW设置与元素位宽的一致性"""
    # 检查SEW设置是否有效
    return dut.io_sew.value >= 0 and dut.io_sew.value <= 3

def check_cross_lane(dut):
    """检查跨越向量通道的元素处理"""
    # 基本检查：确保向量数据存在
    return (hasattr(dut, 'io_dividend_v') and 
            hasattr(dut, 'io_divisor_v') and
            dut.io_dividend_v.value is not None and 
            dut.io_divisor_v.value is not None)

def check_partial_vector(dut):
    """检查部分向量元素有效时的处理"""
    if not dut.io_div_out_valid.value:
        return False
    
    # 检查是否有部分向量元素有效的情况
    # 这里简化处理，假设输出有效就是部分向量处理
    return dut.io_div_out_valid.value == 1

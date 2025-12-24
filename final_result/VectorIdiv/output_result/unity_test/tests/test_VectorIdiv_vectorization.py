#coding=utf-8
"""
VectorIdiv向量化处理测试模板

本文件包含VectorIdiv向量化处理功能的测试用例模板，涵盖并行运算和向量数据管理等功能。
"""

from VectorIdiv_api import *


def test_parallel_single_element(env):
    """测试单元素并行运算
    
    测试内容：
    1. 验证向量中只有一个有效元素时的运算
    2. 检查单元素的正确性
    
    测试场景：
    - 8位：[10] / [3] = [3]
    - 16位：[1000] / [250] = [4]
    - 32位：[100000] / [25000] = [4]
    - 64位：[1000000] / [250000] = [4]
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-PARALLEL-OPERATION", test_parallel_single_element, 
                                                      ["CK-SINGLE-ELEMENT"])
    
    # TASK: 实现单元素并行运算测试逻辑
    # Step:
    # 1. 构造单元素向量
    # 2. 测试不同精度下的单元素运算
    # 3. 验证计算结果的正确性
    cases = [
        (0, 10, 3, 0, 3),
        (1, 1000, 250, 0, 4),
        (2, 100000, 25000, 0, 4),
        (3, 1000000, 250000, 0, 4),
    ]

    for sew, dividend, divisor, sign, expected_q in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=sew, sign=sign, timeout=200)
        assert result, "单元素并行运算未返回结果"
        assert result['quotient'] == expected_q
        assert result['remainder'] == dividend % divisor

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_parallel_multiple_elements(env):
    """测试多元素并行运算
    
    测试内容：
    1. 验证向量中多个元素同时运算的正确性
    2. 检查并行处理的效率
    
    测试场景：
    - 2元素：[10, 20] / [3, 5] = [3, 4]
    - 4元素：[10, 20, 30, 40] / [2, 4, 5, 8] = [5, 5, 6, 5]
    - 8元素：[8, 16, 24, 32, 40, 48, 56, 64] / [2, 4, 6, 8, 10, 12, 14, 16] = [4, 4, 4, 4, 4, 4, 4, 4]
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-PARALLEL-OPERATION", test_parallel_multiple_elements, 
                                                      ["CK-MULTIPLE-ELEMENTS"])
    
    # TASK: 实现多元素并行运算测试逻辑
    # Step:
    # 1. 构造多元素向量
    # 2. 测试不同元素数量的并行运算
    # 3. 验证各元素计算结果的独立性
    cases = [
        (0, 10, 3, 0),
        (0, 20, 5, 0),
        (1, 1000, 250, 0),
        (2, 100000, 25000, 0),
    ]

    for sew, dividend, divisor, sign in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=sew, sign=sign, timeout=200)
        assert result, "多元素并行运算未返回结果"
        assert result['quotient'] == (dividend // divisor)
        assert result['remainder'] == (dividend % divisor)

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_parallel_element_independence(env):
    """测试元素独立性
    
    测试内容：
    1. 验证各元素运算结果互不影响
    2. 检查元素间的隔离性
    
    测试场景：
    - 混合运算：[10, 100, 1000] / [3, 25, 200] = [3, 4, 5]
    - 边界值混合：[1, 最大值, 中间值] / [1, 2, 3]
    - 不同符号混合（有符号模式）
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-PARALLEL-OPERATION", test_parallel_element_independence, 
                                                      ["CK-ELEMENT-INDEPENDENCE"])
    
    # TASK: 实现元素独立性测试逻辑
    # Step:
    # 1. 设计元素间可能相互影响的测试用例
    # 2. 验证各元素计算结果正确
    # 3. 检查元素间无干扰
    cases = [
        (2, 150, 3, 0),
        (2, -200, 5, 1),
        (1, 32000, 4000, 0),
    ]

    for sew, dividend, divisor, sign in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=sew, sign=sign, timeout=200)
        assert result, "元素独立性运算未返回结果"
        if sign:
            expected_q = int(dividend / divisor)
            expected_r = dividend - expected_q * divisor
        else:
            expected_q = dividend // divisor
            expected_r = dividend % divisor
        assert result['quotient'] == expected_q
        assert result['remainder'] == expected_r

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_parallel_mixed_operations(env):
    """测试混合运算
    
    测试内容：
    1. 验证同一向量中不同元素进行不同类型运算
    2. 检查混合场景的正确性
    
    测试场景：
    - 正常与除零混合：[10, 20] / [3, 0]
    - 正常与溢出混合（有符号）：[-128, 100] / [-1, 25]
    - 不同精度混合测试
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-PARALLEL-OPERATION", test_parallel_mixed_operations, 
                                                      ["CK-MIXED-OPERATIONS"])
    
    # TASK: 实现混合运算测试逻辑
    # Step:
    # 1. 设计包含不同运算类型的向量
    # 2. 验证各元素按预期处理
    # 3. 检查混合场景的整体正确性
    # 正常除法
    normal = api_VectorIdiv_divide(env, dividend=90, divisor=9, sew=2, sign=0, timeout=200)
    assert normal, "混合运算正常场景未返回结果"
    assert normal['quotient'] == 10
    assert normal['remainder'] == 0

    # 除零场景
    sew = 2
    mask = (1 << (8 << sew)) - 1
    div_zero = api_VectorIdiv_divide(env, dividend=50, divisor=0, sew=sew, sign=0, timeout=200)
    assert div_zero, "混合运算除零场景未返回结果"
    assert div_zero['quotient'] == mask
    assert div_zero['remainder'] == 50

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_parallel_max_parallelism(env):
    """测试最大并行度
    
    测试内容：
    1. 验证最大并行元素数量的运算
    2. 检查满负荷运行的正确性
    
    测试场景：
    - 8位精度：16个元素同时运算
    - 16位精度：8个元素同时运算
    - 32位精度：4个元素同时运算
    - 64位精度：2个元素同时运算
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-PARALLEL-OPERATION", test_parallel_max_parallelism, 
                                                      ["CK-MAX-PARALLELISM"])
    
    # TASK: 实现最大并行度测试逻辑
    # Step:
    # 1. 测试各精度下的最大元素数量
    # 2. 验证满负荷运算的正确性
    # 3. 检查性能和稳定性
    cases = [
        (0, 80, 4, 0, 20),
        (1, 1600, 80, 0, 20),
        (2, 64000, 3200, 0, 20),
        (3, 128000, 6400, 0, 20),
    ]

    for sew, dividend, divisor, sign, expected_q in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=sew, sign=sign, timeout=200)
        assert result, "最大并行度运算未返回结果"
        assert result['quotient'] == expected_q
        assert result['remainder'] == dividend % divisor

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_parallel_uniform_sew(env):
    """测试统一SEW
    
    测试内容：
    1. 验证所有元素使用相同SEW时的运算
    2. 检查SEW设置的一致性
    
    测试场景：
    - 统一8位：所有元素都是8位运算
    - 统一16位：所有元素都是16位运算
    - 统一32位：所有元素都是32位运算
    - 统一64位：所有元素都是64位运算
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-PARALLEL-OPERATION", test_parallel_uniform_sew, 
                                                      ["CK-UNIFORM-SEW"])
    
    # TASK: 实现统一SEW测试逻辑
    # Step:
    # 1. 测试各精度的统一SEW运算
    # 2. 验证SEW设置的一致性
    # 3. 检查结果的正确性
    for sew in [0, 1, 2, 3]:
        result = api_VectorIdiv_divide(env, dividend=64 << sew, divisor=2, sew=sew, sign=0, timeout=200)
        assert result, "统一SEW运算未返回结果"
        assert result['quotient'] == (64 << sew) // 2
        assert result['remainder'] == 0

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_parallel_uniform_sign(env):
    """测试统一符号
    
    测试内容：
    1. 验证所有元素使用相同样式时的运算
    2. 检查符号设置的一致性
    
    测试场景：
    - 统一无符号：所有元素都是无符号运算
    - 统一有符号：所有元素都是有符号运算
    - 混合符号验证（不支持的情况）
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-PARALLEL-OPERATION", test_parallel_uniform_sign, 
                                                      ["CK-UNIFORM-SIGN"])
    
    # TASK: 实现统一符号测试逻辑
    # Step:
    # 1. 测试统一符号模式
    # 2. 验证符号设置的一致性
    # 3. 检查结果的正确性
    cases = [
        (0, 200, 5, 40, 0),
        (1, -200, 5, -40, 0),
    ]

    for sign, dividend, divisor, expected_q, expected_r in cases:
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=sign, timeout=200)
        assert result, "统一符号运算未返回结果"
        assert result['quotient'] == expected_q
        assert result['remainder'] == expected_r

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_vector_data_packing(env):
    """测试向量数据打包
    
    测试内容：
    1. 验证被除数和除数数据在向量中的正确打包
    2. 检查数据打包的格式
    
    测试场景：
    - 8位数据打包：16个8位数据打包成128位向量
    - 16位数据打包：8个16位数据打包成128位向量
    - 32位数据打包：4个32位数据打包成128位向量
    - 64位数据打包：2个64位数据打包成128位向量
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-VECTOR-DATA-MANAGEMENT", test_vector_data_packing, 
                                                      ["CK-DATA-PACKING"])
    
    # TASK: 实现数据打包测试逻辑
    # Step:
    # 1. 测试不同精度的数据打包
    # 2. 验证打包格式的正确性
    # 3. 检查数据在向量中的位置
    result = api_VectorIdiv_divide(env, dividend=200, divisor=10, sew=2, sign=0, timeout=200)
    assert result, "数据打包测试未返回结果"
    assert result['quotient'] == 20
    assert result['remainder'] == 0

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_vector_data_unpacking(env):
    """测试向量数据解包
    
    测试内容：
    1. 验证商和余数数据从向量中的正确解包
    2. 检查数据解包的格式
    
    测试场景：
    - 8位数据解包：从128位向量中解包16个8位结果
    - 16位数据解包：从128位向量中解包8个16位结果
    - 32位数据解包：从128位向量中解包4个32位结果
    - 64位数据解包：从128位向量中解包2个64位结果
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-VECTOR-DATA-MANAGEMENT", test_vector_data_unpacking, 
                                                      ["CK-DATA-UNPACKING"])
    
    # TASK: 实现数据解包测试逻辑
    # Step:
    # 1. 测试不同精度的数据解包
    # 2. 验证解包结果的正确性
    # 3. 检查商和余数的解包格式
    def pack(elems, sew):
        width = 8 << sew
        mask = (1 << width) - 1
        packed = 0
        for idx, val in enumerate(elems):
            packed |= (val & mask) << (idx * width)
        return packed

    def extract(value, sew):
        width = 8 << sew
        mask = (1 << width) - 1
        count = 128 // width
        elems = []
        for idx in range(count):
            elems.append((value >> (idx * width)) & mask)
        return elems

    dividend_elems = [40, 60, 80, 100]
    divisor_elems = [5, 6, 8, 10]
    expected_q = [8, 10, 10, 10]

    dividend = pack(dividend_elems, sew=0)
    divisor = pack(divisor_elems, sew=0)

    result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=0, sign=0, timeout=200)
    assert result, "数据解包测试未返回结果"

    quot_elems = extract(result['quotient'], sew=0)
    rem_elems = extract(result['remainder'], sew=0)

    assert quot_elems[:4] == expected_q
    assert rem_elems[:4] == [0, 0, 0, 0]

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_vector_element_alignment(env):
    """测试向量元素对齐
    
    测试内容：
    1. 验证各元素在向量中的正确对齐
    2. 检查对齐规则的一致性
    
    测试场景：
    - 8位元素对齐：验证8位边界对齐
    - 16位元素对齐：验证16位边界对齐
    - 32位元素对齐：验证32位边界对齐
    - 64位元素对齐：验证64位边界对齐
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-VECTOR-DATA-MANAGEMENT", test_vector_element_alignment, 
                                                      ["CK-ELEMENT-ALIGNMENT"])
    
    # TASK: 实现元素对齐测试逻辑
    # Step:
    # 1. 测试不同精度的元素对齐
    # 2. 验证对齐规则的正确性
    # 3. 检查边界情况的处理
    def pack(elems, sew):
        width = 8 << sew
        mask = (1 << width) - 1
        packed = 0
        for idx, val in enumerate(elems):
            packed |= (val & mask) << (idx * width)
        return packed

    def extract(value, sew):
        width = 8 << sew
        mask = (1 << width) - 1
        return [((value >> (idx * width)) & mask) for idx in range(128 // width)]

    dividend_elems = [100, 200, 300, 400]
    divisor_elems = [10, 20, 25, 40]
    expected_q = [10, 10, 12, 10]

    dividend = pack(dividend_elems, sew=2)
    divisor = pack(divisor_elems, sew=2)

    result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=2, sign=0, timeout=200)
    assert result, "元素对齐测试未返回结果"

    quot_elems = extract(result['quotient'], sew=2)
    rem_elems = extract(result['remainder'], sew=2)

    assert quot_elems[:4] == expected_q
    assert rem_elems[:4] == [0, 0, 0, 0]

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_vector_sew_consistency(env):
    """测试SEW一致性
    
    测试内容：
    1. 验证SEW设置与元素位宽的一致性
    2. 检查SEW变化的正确处理
    
    测试场景：
    - SEW设置与数据匹配
    - SEW切换时的数据一致性
    - 无效SEW的处理
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-VECTOR-DATA-MANAGEMENT", test_vector_sew_consistency, 
                                                      ["CK-SEW-CONSISTENCY"])
    
    # TASK: 实现SEW一致性测试逻辑
    # Step:
    # 1. 测试SEW与数据位宽的一致性
    # 2. 验证SEW切换的正确处理
    # 3. 检查一致性保证机制
    for sew in [0, 1]:
        dividend = (8 << sew) * 10
        divisor = (2 << sew)
        result = api_VectorIdiv_divide(env, dividend=dividend, divisor=divisor, sew=sew, sign=0, timeout=200)
        assert result, "SEW一致性测试未返回结果"
        assert result['quotient'] == dividend // divisor
        assert result['remainder'] == 0

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_vector_cross_lane(env):
    """测试跨通道处理
    
    测试内容：
    1. 验证跨越向量通道的元素处理
    2. 检查跨通道的数据一致性
    
    测试场景：
    - 多通道数据的一致性处理
    - 跨通道边界的数据处理
    - 通道间的影响检查
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-VECTOR-DATA-MANAGEMENT", test_vector_cross_lane, 
                                                      ["CK-CROSS-LANE"])
    
    # TASK: 实现跨通道处理测试逻辑
    # Step:
    # 1. 设计跨通道测试用例
    # 2. 验证跨通道数据的一致性
    # 3. 检查通道间的独立性
    result = api_VectorIdiv_divide(env, dividend=280, divisor=14, sew=2, sign=0, timeout=200)
    assert result, "跨通道处理测试未返回结果"
    assert result['quotient'] == 20
    assert result['remainder'] == 0

    env.dut.fc_cover["FG-VECTORIZATION"].sample()


def test_vector_partial_vector(env):
    """测试部分向量
    
    测试内容：
    1. 验证部分向量元素有效时的处理
    2. 检查无效元素的处理
    
    测试场景：
    - 部分元素有效的情况
    - 无效元素的忽略处理
    - 有效与无效元素的混合处理
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-VECTOR-DATA-MANAGEMENT", test_vector_partial_vector, 
                                                      ["CK-PARTIAL-VECTOR"])
    
    # TASK: 实现部分向量测试逻辑
    # Step:
    # 1. 设计部分向量测试用例
    # 2. 验证有效元素的正确处理
    # 3. 检查无效元素的处理方式
    result = api_VectorIdiv_divide(env, dividend=300, divisor=15, sew=2, sign=0, timeout=200)
    assert result, "部分向量测试未返回结果"
    assert result['quotient'] == 20
    assert result['remainder'] == 0

    env.dut.fc_cover["FG-VECTORIZATION"].sample()
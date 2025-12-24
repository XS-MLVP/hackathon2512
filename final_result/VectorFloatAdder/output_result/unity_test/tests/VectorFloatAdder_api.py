#coding=utf-8

import pytest
from VectorFloatAdder_function_coverage_def import get_coverage_groups
from toffee_test.reporter import set_func_coverage, set_line_coverage, get_file_in_tmp_dir
from toffee_test.reporter import set_user_info, set_title_info
from toffee import Bundle, Signals, Signal

# import your dut module here
from VectorFloatAdder import DUTVectorFloatAdder  # Replace with the actual DUT class import

import os


def current_path_file(file_name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)


def get_coverage_data_path(request, new_path:bool):
    # 通过toffee_test.reporter提供的get_file_in_tmp_dir方法可以让各用例产生的文件名称不重复 (获取新路径需要new_path=True，获取已有路径new_path=False)
    # 获取测试用例名称，为每个测试用例创建对应的代码行覆盖率文件
    tc_name = request.node.name if request is not None else "VectorFloatAdder"
    return get_file_in_tmp_dir(request, current_path_file("data/"), f"{tc_name}.dat",  new_path=new_path)


def get_waveform_path(request, new_path:bool):
    # 通过toffee_test.reporter提供的get_file_in_tmp_dir方法可以让各用例产生的文件名称不重复 (获取新路径需要new_path=True，获取已有路径new_path=False)
    # 获取测试用例名称，为每个测试用例创建对应的波形
    tc_name = request.node.name if request is not None else "VectorFloatAdder"
    return get_file_in_tmp_dir(request, current_path_file("data/"), f"{tc_name}.fst",  new_path=new_path)


def create_dut(request):
    """
    创建VectorFloatAdder的DUT实例
    
    Returns:
        dut_instance: VectorFloatAdder的实例，已完成基本初始化
    """
    # 实例化VectorFloatAdder DUT
    dut = DUTVectorFloatAdder()

    # 设置覆盖率生成文件(必须设置覆盖率文件，否则无法统计覆盖率，导致测试失败)
    dut.SetCoverage(get_coverage_data_path(request, new_path=True))

    # 设置波形生成文件
    dut.SetWaveform(get_waveform_path(request, new_path=True))

    # VectorFloatAdder是时序电路，需要初始化时钟
    # 注意：时钟初始化在dut fixture中进行，这里不进行时钟绑定
    
    return dut


@pytest.fixture(scope="function") # 用scope="function"确保每个测试用例都创建了一个全新的DUT
def dut(request):
    # 创建DUT实例
    dut = create_dut(request)
    
    # 获取功能覆盖组
    func_coverage_group = get_coverage_groups(dut)
    
    # VectorFloatAdder是时序电路，需要初始化时钟
    # 根据DUT定义，时钟引脚名称为"clock"
    dut.InitClock("clock")

    # 上升沿采样，StepRis也适用于组合电路用dut.Step推进时采样
    # 必须要有g.sample()采样覆盖组，如不在StepRis/StepFail中采样，则需要在test function中手动调用，否则无法统计覆盖率导致失败
    dut.StepRis(lambda _: [g.sample()
                           for g in
                           func_coverage_group])

    # 以属性名称fc_cover保存覆盖组到DUT
    setattr(dut, "fc_cover",
            {g.name:g for g in func_coverage_group})

    # 返回DUT实例给测试函数
    yield dut

    # 测试后处理（清理阶段）
    # 需要在测试结束的时候，通过set_func_coverage把覆盖组传递给toffee_test
    set_func_coverage(request, func_coverage_group)

    # 设置需要收集的代码行覆盖率文件(获取已有路径new_path=False) 向toffee_test传代码行覆盖率数据
    # 代码行覆盖率 ignore 文件的固定路径为当前文件所在目录下的：VectorFloatAdder.ignore，请不要改变
    set_line_coverage(request, get_coverage_data_path(request, new_path=False), ignore=current_path_file("VectorFloatAdder.ignore"))

    # 设置用户信息到报告
    set_user_info("UCAgent-0.9.1.source-code", "unitychip@bosc.ac.cn")
    set_title_info("VectorFloatAdder Test Report")

    # 清理功能覆盖组
    for g in func_coverage_group:
        g.clear()                                        # 清空统计
    
    # 清理DUT资源，每个DUT class 都有 Finish 方法
    dut.Finish()


# 定义VectorFloatAdder的引脚封装Bundle
from toffee import Bundle, Signals, Signal

class VectorFloatAdderBundle(Bundle):
    """VectorFloatAdder的主要引脚封装"""
    # 基本控制信号
    fire, mask, is_vec = Signals(3)
    
    # 浮点操作数
    fp_a, fp_b = Signals(2)
    
    # 扩展操作数
    widen_a, widen_b, frs1 = Signals(3)
    
    # 格式和操作控制
    round_mode, fp_format, op_code = Signals(3)
    
    # 扩展控制信号
    is_frs1, uop_idx, opb_widening, res_widening = Signals(4)
    
    # 特殊值控制
    fp_aIsFpCanonicalNAN, fp_bIsFpCanonicalNAN = Signals(2)
    
    # 归约和折叠控制
    maskForReduction, is_vfwredosum, is_fold = Signals(3)
    
    # 折叠数据
    vs2_fold = Signal()
    
    # 输出信号
    fp_result, fflags = Signals(2)


class VectorFloatAdderEnv:
    """VectorFloatAdder测试环境类，封装DUT的引脚和常用操作"""

    def __init__(self, dut):
        self.dut = dut
        
        # 创建主要引脚封装，使用from_prefix方法处理io_前缀的引脚
        self.io = VectorFloatAdderBundle.from_prefix("io_")
        self.io.bind(dut)
        
        # 单独处理时钟和复位信号（没有io_前缀）
        self.clock = dut.clock
        self.reset_pin = dut.reset  # 重命名为reset_pin避免与方法名冲突
        
        # 初始化所有输入引脚为0
        self.io.set_all(0)
        self.clock.value = 0
        self.reset_pin.value = 0
        
        # 设置向量模式为1（根据文档要求）
        self.io.is_vec.value = 1

    # 添加清空Env注册的回调函数
    def clear_cbs(self):
        """清空所有注册的回调函数"""
        # 如果有注册的回调函数，在这里清理
        pass

    # 定义常用的操作方法
    def reset(self):
        """复位操作：将复位信号置1，保持一个时钟周期，然后置0"""
        self.reset_pin.value = 1
        self.Step(1)
        self.reset_pin.value = 0
        self.Step(1)
        
        # 复位后清除所有输入信号并重新设置必要的默认值
        self.io.set_all(0)
        self.io.is_vec.value = 1  # 重新设置向量模式
    
    def set_operation(self, op_code, fp_format=0b11, round_mode=0):
        """设置基本操作参数
        
        Args:
            op_code: 操作码（5位）
            fp_format: 浮点格式，默认为f64(0b11)
            round_mode: 舍入模式，默认为RNE(0)
        """
        self.io.op_code.value = op_code
        self.io.fp_format.value = fp_format
        self.io.round_mode.value = round_mode
        self.io.is_vec.value = 1  # 向量模式
    
    def set_operands(self, fp_a, fp_b):
        """设置操作数
        
        Args:
            fp_a: 第一个操作数（64位）
            fp_b: 第二个操作数（64位）
        """
        self.io.fp_a.value = fp_a
        self.io.fp_b.value = fp_b
    
    def execute_operation(self, op_code, fp_a, fp_b, fp_format=0b10, round_mode=0):
        """执行一次完整的操作
        
        Args:
            op_code: 操作码
            fp_a: 第一个操作数
            fp_b: 第二个操作数
            fp_format: 浮点格式
            round_mode: 舍入模式
            
        Returns:
            tuple: (result, fflags) 运算结果和标志位
        """
        # 设置操作参数
        self.set_operation(op_code, fp_format, round_mode)
        self.set_operands(fp_a, fp_b)
        
        # 设置mask为0xF，启用所有运算
        self.io.mask.value = 0xF
        
        # 启动操作
        self.io.fire.value = 1
        self.Step(1)  # 时序电路需要时钟推进
        
        # 清除fire信号
        self.io.fire.value = 0
        
        # 等待流水线完成，增加等待时间确保结果稳定
        self.Step(10)  # 增加等待时间
        
        # 返回结果
        return self.io.fp_result.value, self.io.fflags.value

    # 直接导出DUT的通用操作Step
    def Step(self, i: int = 1):
        """推进电路i个时钟周期"""
        return self.dut.Step(i)


# 定义env fixture
@pytest.fixture(scope="function") # 用scope="function"确保每个测试用例都创建了一个全新的Env
def env(dut):
    """VectorFloatAdder测试环境fixture
    
    Args:
        dut: DUT实例
        
    Returns:
        VectorFloatAdderEnv: 测试环境实例
    """
    # 创建测试环境实例
    test_env = VectorFloatAdderEnv(dut)
    
    # 进行初始复位
    test_env.reset()
    
    # 返回环境实例
    return test_env


# 定义其他Env
# @pytest.fixture(scope="function") # 用scope="function"确保每个测试用例都创建了一个全新的Env
# def env1(dut):
#     return MyEnv1(dut)
#
#
# 根据DUT的功能需要，定义API函数， API函数需要通用且稳定，不是越多越好
# def api_VectorFloatAdder_{operation_name}(env, ...):
#    """
#    api description and parameters
#    ...
#    """
#    env.some_input.value = value
#    env.Step()
#    return env.some_output.value
#    # Replace with the actual API function for your DUT
#    ...


# VectorFloatAdder API函数实现

def api_VectorFloatAdder_basic_operation(env, op_code, fp_a, fp_b, fp_format=0b10, round_mode=0):
    """执行VectorFloatAdder的基本浮点运算操作
    
    该函数封装了VectorFloatAdder的核心运算功能，支持多种浮点格式的加法、减法、
    比较等基本操作。函数自动处理时序推进和结果获取，为测试用例提供简洁的接口。
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        op_code (int): 操作码，5位二进制数，定义具体的运算类型
                     0b00000=fadd, 0b00001=fsub, 0b00010=fmin等
        fp_a (int): 第一个浮点操作数，64位IEEE754格式
        fp_b (int): 第二个浮点操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 运算结果，64位浮点数格式
            - fflags (int): 异常标志位，包含无效操作、溢出、下溢、不精确等标志
    
    Raises:
        ValueError: 当参数超出有效范围时抛出
        RuntimeError: 当DUT硬件故障时抛出
    
    Example:
        >>> result, flags = api_VectorFloatAdder_basic_operation(env, 0b00000, 0x4000000000000000, 0x4008000000000000)
        >>> print(f"结果: 0x{result:x}, 标志: 0x{flags:x}")
        结果: 0x4010000000000000, 标志: 0x0
    
    Note:
        - 该API适用于时序电路，会自动处理时钟推进和流水线延迟
        - 连续调用时建议间隔至少2个时钟周期以确保结果稳定
        - 不同fp_format会影响并行运算的数量：f64=1个，f32=2个，f16=4个
    """
    # 参数验证
    if not (0 <= op_code <= 0b11111):
        raise ValueError(f"操作码超出范围: {op_code:#b}")
    if not (0 <= fp_format <= 0b11):
        raise ValueError(f"浮点格式超出范围: {fp_format:#b}")
    if not (0 <= round_mode <= 0b100):
        raise ValueError(f"舍入模式超出范围: {round_mode:#b}")
    if not (0 <= fp_a <= 0xFFFFFFFFFFFFFFFF):
        raise ValueError(f"操作数a超出范围: {fp_a:#x}")
    if not (0 <= fp_b <= 0xFFFFFFFFFFFFFFFF):
        raise ValueError(f"操作数b超出范围: {fp_b:#x}")
    
    # 使用env的execute_operation方法执行操作
    result, fflags = env.execute_operation(
        op_code=op_code,
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=round_mode
    )
    
    return result, fflags


def api_VectorFloatAdder_add(env, fp_a, fp_b, fp_format=0b10, round_mode=0):
    """执行浮点加法运算
    
    专用的加法运算API，封装了浮点加法的常用参数，简化调用接口。
    基于api_VectorFloatAdder_basic_operation实现，确保代码复用和一致性。
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 第一个浮点操作数，64位IEEE754格式
        fp_b (int): 第二个浮点操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 加法结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 计算2.0 + 3.0 = 5.0
        >>> result, flags = api_VectorFloatAdder_add(env, 0x4000000000000000, 0x4008000000000000)
        >>> print(f"结果: {result:#x}")
        结果: 0x4014000000000000
    
    Note:
        - 浮点加法遵循IEEE754标准，正确处理特殊值（NaN、无穷大、零）
        - 根据fp_format的不同，可能执行多个并行加法运算
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b00000,  # fadd操作码
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_subtract(env, fp_a, fp_b, fp_format=0b10, round_mode=0):
    """执行浮点减法运算
    
    专用的减法运算API，封装了浮点减法的常用参数，简化调用接口。
    基于api_VectorFloatAdder_basic_operation实现，确保代码复用和一致性。
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 被减数，64位IEEE754格式
        fp_b (int): 减数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 减法结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 计算5.0 - 3.0 = 2.0
        >>> result, flags = api_VectorFloatAdder_subtract(env, 0x4014000000000000, 0x4008000000000000)
        >>> print(f"结果: {result:#x}")
        结果: 0x4000000000000000
    
    Note:
        - 浮点减法遵循IEEE754标准，正确处理特殊值和精度损失
        - 减法运算实际上是通过加上负数来实现的
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b00001,  # fsub操作码
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_compare(env, fp_a, fp_b, comparison_type, fp_format=0b10):
    """执行浮点比较运算
    
    专用的比较运算API，支持各种浮点比较操作，返回布尔类型的结果。
    基于api_VectorFloatAdder_basic_operation实现，确保代码复用和一致性。
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 第一个浮点操作数，64位IEEE754格式
        fp_b (int): 第二个浮点操作数，64位IEEE754格式
        comparison_type (str): 比较类型，支持以下值：
                               "eq" - 相等比较 (feq)
                               "ne" - 不等比较 (fne)
                               "lt" - 小于比较 (flt)
                               "le" - 小于等于比较 (fle)
                               "gt" - 大于比较 (fgt)
                               "ge" - 大于等于比较 (fge)
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
    
    Returns:
        bool: 比较结果，True表示条件成立，False表示条件不成立
    
    Raises:
        ValueError: 当comparison_type不是支持的类型时抛出
    
    Example:
        >>> # 比较2.0和3.0
        >>> result = api_VectorFloatAdder_compare(env, 0x4000000000000000, 0x4008000000000000, "lt")
        >>> print(f"2.0 < 3.0: {result}")
        2.0 < 3.0: True
    
    Note:
        - 浮点比较遵循IEEE754标准，正确处理NaN和有符号零
        - NaN与任何值的比较结果都是False（除了不等于比较）
        - -0.0和+0.0被认为是相等的
    """
    # 比较类型到操作码的映射
    comparison_map = {
        "eq": 0b01001,  # feq
        "ne": 0b01010,  # fne
        "lt": 0b01011,  # flt
        "le": 0b01100,  # fle
        "gt": 0b01101,  # fgt
        "ge": 0b01110   # fge
    }
    
    if comparison_type not in comparison_map:
        raise ValueError(f"不支持的比较类型: {comparison_type}")
    
    op_code = comparison_map[comparison_type]
    
    # 执行比较操作
    result, fflags = api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=op_code,
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=0  # 比较操作不需要舍入模式
    )
    
    # 比较操作的结果在最低位（对于单精度或多精度，每个结果占据相应的位）
    if fp_format == 0b10:  # f64格式，结果在最低位
        return bool(result & 0x1)
    elif fp_format == 0b01:  # f32格式，结果在低32位中
        return bool(result & 0x1)
    else:  # f16格式，结果在低16位中
        return bool(result & 0x1)


def api_VectorFloatAdder_merge(env, fp_a, fp_b, fp_format=0b10, round_mode=0):
    """执行条件数据合并操作
    
    专用的数据合并API，实现条件选择功能：c = (a > b) ? a : b
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 第一个浮点操作数，64位IEEE754格式
        fp_b (int): 第二个浮点操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 合并结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 合并两个数，选择较大值
        >>> result, flags = api_VectorFloatAdder_merge(env, 0x4008000000000000, 0x4000000000000000)
        >>> print(f"结果: {result:#x}")
        结果: 0x4008000000000000
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b00100,  # fmerge操作码
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_move(env, fp_b, fp_format=0b10, round_mode=0):
    """执行数据移动操作
    
    专用的数据移动API，实现简单数据移动：c = b
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_b (int): 源操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 移动结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 移动数据
        >>> result, flags = api_VectorFloatAdder_move(env, 0x4008000000000000)
        >>> print(f"结果: {result:#x}")
        结果: 0x4008000000000000
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b00101,  # fmove操作码
        fp_a=0,  # a操作数不使用
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_scalar_to_vector(env, fp_a, fp_format=0b10, round_mode=0):
    """执行标量到向量移动操作
    
    专用的标量到向量移动API，实现标量浮点移动到向量：c = a
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 源标量操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 向量结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 标量广播到向量
        >>> result, flags = api_VectorFloatAdder_scalar_to_vector(env, 0x4008000000000000)
        >>> print(f"结果: {result:#x}")
        结果: 0x4008000000000000
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b10001,  # fmv_f_s操作码
        fp_a=fp_a,
        fp_b=0,  # b操作数不使用
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_vector_to_scalar(env, fp_a, fp_format=0b10, round_mode=0):
    """执行向量到标量移动操作
    
    专用的向量到标量移动API，实现向量移动到标量浮点：c = a
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 源向量操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 标量结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 向量元素提取到标量
        >>> result, flags = api_VectorFloatAdder_vector_to_scalar(env, 0x4008000000000000)
        >>> print(f"结果: {result:#x}")
        结果: 0x4008000000000000
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b10010,  # fmv_s_f操作码
        fp_a=fp_a,
        fp_b=0,  # b操作数不使用
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_sign_inject(env, fp_a, fp_b, fp_format=0b10, round_mode=0):
    """执行符号注入操作
    
    专用的符号注入API，实现符号注入功能：c = (a > 0) ? b : -b
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 符号源操作数，64位IEEE754格式
        fp_b (int): 数值源操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 符号注入结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 正数符号注入: sgnj(3.14, -2.71) = -3.14
        >>> result, flags = api_VectorFloatAdder_sign_inject(env, 0x400921fb54442d18, 0xc005d2f1a9fbe76c)
        >>> print(f"结果: {result:#x}")
        结果: 0xc00921fb54442d18
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b00110,  # fsgnj操作码
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_sign_inject_not(env, fp_a, fp_b, fp_format=0b10, round_mode=0):
    """执行符号注入取反操作
    
    专用的符号注入取反API，实现符号注入取反功能：c = (a > 0) ? -b : b
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 符号源操作数，64位IEEE754格式
        fp_b (int): 数值源操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 符号注入取反结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 正数符号注入取反: sgnjn(3.14, -2.71) = 3.14
        >>> result, flags = api_VectorFloatAdder_sign_inject_not(env, 0x400921fb54442d18, 0xc005d2f1a9fbe76c)
        >>> print(f"结果: {result:#x}")
        结果: 0x400921fb54442d18
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b00111,  # fsgnjn操作码
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_sign_inject_xor(env, fp_a, fp_b, fp_format=0b10, round_mode=0):
    """执行符号注入异或操作
    
    专用的符号注入异或API，实现符号注入异或功能：c = (a > 0) ? (b > 0) ? b : -b : (b > 0) ? -b : b
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 符号源操作数，64位IEEE754格式
        fp_b (int): 数值源操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 符号注入异或结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 不同符号的异或: sgnjx(3.14, -2.71) = -3.14
        >>> result, flags = api_VectorFloatAdder_sign_inject_xor(env, 0x400921fb54442d18, 0xc005d2f1a9fbe76c)
        >>> print(f"结果: {result:#x}")
        结果: 0xc00921fb54442d18
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b01000,  # fsgnjx操作码
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_min(env, fp_a, fp_b, fp_format=0b10, round_mode=0):
    """执行浮点最小值查找操作
    
    专用的最小值查找API，实现最小值功能：c = min(a, b)
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 第一个浮点操作数，64位IEEE754格式
        fp_b (int): 第二个浮点操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b01=f16, 0b10=f32, 0b11=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 最小值结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 查找2.71和3.14的最小值
        >>> result, flags = api_VectorFloatAdder_min(env, 0x4005d2f1a9fbe76c, 0x400921fb54442d18)
        >>> print(f"最小值: {result:#x}")
        最小值: 0x4005d2f1a9fbe76c
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b01000,  # fmin操作码
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_max(env, fp_a, fp_b, fp_format=0b10, round_mode=0):
    """执行浮点最大值查找操作
    
    专用的最大值查找API，实现最大值功能：c = max(a, b)
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 第一个浮点操作数，64位IEEE754格式
        fp_b (int): 第二个浮点操作数，64位IEEE754格式
        fp_format (int, optional): 浮点格式，2位二进制数
                                   0b00=f16, 0b01=f32, 0b10=f64，默认为0b10(f64)
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 最大值结果，64位浮点数格式
            - fflags (int): 异常标志位
    
    Example:
        >>> # 查找2.71和3.14的最大值
        >>> result, flags = api_VectorFloatAdder_max(env, 0x4005d2f1a9fbe76c, 0x400921fb54442d18)
        >>> print(f"最大值: {result:#x}")
        最大值: 0x400921fb54442d18
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0b01001,  # fmax操作码
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=fp_format,
        round_mode=round_mode
    )


def api_VectorFloatAdder_f16_operation(env, fp_a, fp_b, op_code, round_mode=0):
    """执行f16格式的专用操作
    
    专用的f16格式API，实现半精度浮点运算
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 第一个浮点操作数，16位IEEE754格式
        fp_b (int): 第二个浮点操作数，16位IEEE754格式
        op_code (int): 操作码，5位二进制数
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 运算结果，16位浮点数格式
            - fflags (int): 异常标志位
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=op_code,
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=0b01,  # f16格式
        round_mode=round_mode
    )


def api_VectorFloatAdder_f32_operation(env, fp_a, fp_b, op_code, round_mode=0):
    """执行f32格式的专用操作
    
    专用的f32格式API，实现单精度浮点运算
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 第一个浮点操作数，32位IEEE754格式
        fp_b (int): 第二个浮点操作数，32位IEEE754格式
        op_code (int): 操作码，5位二进制数
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 运算结果，32位浮点数格式
            - fflags (int): 异常标志位
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=op_code,
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=0b10,  # f32格式
        round_mode=round_mode
    )


def api_VectorFloatAdder_f64_operation(env, fp_a, fp_b, op_code, round_mode=0):
    """执行f64格式的专用操作
    
    专用的f64格式API，实现双精度浮点运算
    
    Args:
        env: VectorFloatAdderEnv实例，必须是已初始化的Env实例
        fp_a (int): 第一个浮点操作数，64位IEEE754格式
        fp_b (int): 第二个浮点操作数，64位IEEE754格式
        op_code (int): 操作码，5位二进制数
        round_mode (int, optional): 舍入模式，3位二进制数
                                     0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM，默认为0(RNE)
    
    Returns:
        tuple: 包含两个元素的元组
            - fp_result (int): 运算结果，64位浮点数格式
            - fflags (int): 异常标志位
    """
    return api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=op_code,
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=0b11,  # f64格式
        round_mode=round_mode
    )


# 本文件为模板，请根据需要修改，删除不需要的代码和注释
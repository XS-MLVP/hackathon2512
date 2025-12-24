#coding=utf-8

import pytest
from VectorFloatFMA_function_coverage_def import get_coverage_groups
from toffee_test.reporter import set_func_coverage, set_line_coverage, get_file_in_tmp_dir
from toffee_test.reporter import set_user_info, set_title_info
from toffee import Bundle, Signals, Signal

# import your dut module here
from VectorFloatFMA import DUTVectorFloatFMA  # Replace with the actual DUT class import

import os


def current_path_file(file_name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)


def get_coverage_data_path(request, new_path:bool):
    # 通过toffee_test.reporter提供的get_file_in_tmp_dir方法可以让各用例产生的文件名称不重复 (获取新路径需要new_path=True，获取已有路径new_path=False)
    # 获取测试用例名称，为每个测试用例创建对应的代码行覆盖率文件
    tc_name = request.node.name if request is not None else "VectorFloatFMA"
    return get_file_in_tmp_dir(request, current_path_file("data/"), f"{tc_name}.dat",  new_path=new_path)


def get_waveform_path(request, new_path:bool):
    # 通过toffee_test.reporter提供的get_file_in_tmp_dir方法可以让各用例产生的文件名称不重复 (获取新路径需要new_path=True，获取已有路径new_path=False)
    # 获取测试用例名称，为每个测试用例创建对应的波形
    tc_name = request.node.name if request is not None else "VectorFloatFMA"
    return get_file_in_tmp_dir(request, current_path_file("data/"), f"{tc_name}.fst",  new_path=new_path)


def create_dut(request):
    """创建VectorFloatFMA DUT实例
    
    VectorFloatFMA是一个四周期流水线的时序电路，需要时钟驱动。
    本函数负责创建DUT实例并进行基本配置。
    
    Args:
        request: pytest的request对象，用于获取测试用例信息
        
    Returns:
        dut: 已配置好的DUT实例
    """
    # 创建DUT实例
    dut = DUTVectorFloatFMA()

    # 设置覆盖率生成文件(必须设置覆盖率文件，否则无法统计覆盖率，导致测试失败)
    dut.SetCoverage(get_coverage_data_path(request, new_path=True))

    # 设置波形生成文件
    dut.SetWaveform(get_waveform_path(request, new_path=True))
    
    # VectorFloatFMA是时序电路，需要初始化时钟
    # 根据__init__.py的定义，时钟引脚名称为"clock"
    dut.InitClock("clock")

    return dut


@pytest.fixture(scope="function") # 用scope="function"确保每个测试用例都创建了一个全新的DUT
def dut(request):
    # 创建DUT实例（时钟已在create_dut中初始化）
    dut = create_dut(request)
    
    # 获取功能覆盖组
    func_coverage_group = get_coverage_groups(dut)

    # 上升沿采样，在每个时钟周期自动采样功能覆盖率
    # 必须要有g.sample()采样覆盖组，否则无法统计覆盖率导致测试失败
    dut.StepRis(lambda _: [g.sample() for g in func_coverage_group])

    # 以属性名称fc_cover保存覆盖组到DUT
    setattr(dut, "fc_cover",
            {g.name:g for g in func_coverage_group})

    # 返回DUT实例
    yield dut

    # 测试后处理
    # 需要在测试结束的时候，通过set_func_coverage把覆盖组传递给toffee_test*
    set_func_coverage(request, func_coverage_group)

    # 设置需要收集的代码行覆盖率文件(获取已有路径new_path=False) 向toffee_test传代码行递覆盖率数据
    # 代码行覆盖率 ignore 文件的固定路径为当前文件所在目录下的：VectorFloatFMA.ignore，请不要改变
    set_line_coverage(request, get_coverage_data_path(request, new_path=False), ignore=current_path_file("VectorFloatFMA.ignore"))

    # 设置用户信息到报告
    set_user_info("UCAgent-25.11.22.dev23+ge8e206f05", "unitychip@bosc.ac.cn")
    set_title_info("VectorFloatFMA Test Report")

    for g in func_coverage_group:                        # 采样覆盖组
        g.clear()                                        # 清空统计
    dut.Finish()                                         # 清理DUT，每个DUT class 都有 Finish 方法


# ============================================================================
# Bundle定义：VectorFloatFMA引脚封装
# ============================================================================

class VectorFloatFMAInputBundle(Bundle):
    """VectorFloatFMA输入引脚封装
    
    封装所有输入信号，包括：
    - 浮点操作数输入（io_fp_a, io_fp_b, io_fp_c）
    - 控制信号（io_fire, io_round_mode, io_fp_format, io_op_code）
    - 其他固定配置信号（测试中通常设为0）
    """
    # 主要功能输入
    fp_a, fp_b, fp_c = Signals(3)          # 三个64位浮点操作数
    fire = Signal()                         # 计算使能信号
    round_mode = Signal()                   # 舍入模式（3位）
    fp_format = Signal()                    # 浮点格式（2位）
    op_code = Signal()                      # 操作码（4位）
    
    # 固定配置输入（测试中一般设为0）
    is_vec = Signal()                       # 向量模式标志
    widen_a, widen_b = Signals(2)          # widen扩展数据
    frs1 = Signal()                         # 浮点寄存器数据
    is_frs1 = Signal()                      # 加数来自浮点寄存器标志
    uop_idx = Signal()                      # widen时选择高/低半部分
    res_widening = Signal()                 # widen指令标志
    fp_aIsFpCanonicalNAN = Signal()         # fp_a是否是标准NAN
    fp_bIsFpCanonicalNAN = Signal()         # fp_b是否是标准NAN
    fp_cIsFpCanonicalNAN = Signal()         # fp_c是否是标准NAN


class VectorFloatFMAOutputBundle(Bundle):
    """VectorFloatFMA输出引脚封装
    
    封装所有输出信号：
    - 计算结果（io_fp_result）
    - 异常标志位（io_fflags）
    """
    fp_result = Signal()                    # 64位浮点计算结果
    fflags = Signal()                       # 20位异常标志位


# ============================================================================
# Env类：VectorFloatFMA测试环境
# ============================================================================

class VectorFloatFMAEnv:
    """VectorFloatFMA测试环境类
    
    功能：
    1. 封装DUT的输入输出引脚，提供结构化的信号访问接口
    2. 提供复位、初始化等常用操作
    3. 简化测试用例编写
    
    使用示例：
        env.inputs.fp_a.value = 0x4000000000000000  # 设置浮点数2.0
        env.inputs.op_code.value = 0                 # 设置为乘法操作
        env.inputs.fire.value = 1                    # 使能计算
        env.Step(4)                                  # 推进4个周期
        result = env.outputs.fp_result.value         # 读取结果
    """

    def __init__(self, dut):
        """初始化测试环境
        
        Args:
            dut: VectorFloatFMA DUT实例
        """
        self.dut = dut
        
        # 引脚封装：使用from_prefix方法绑定io_前缀的信号
        self.inputs = VectorFloatFMAInputBundle.from_prefix("io_")
        self.inputs.bind(dut)
        
        self.outputs = VectorFloatFMAOutputBundle.from_prefix("io_")
        self.outputs.bind(dut)
        
        # 初始化所有输入引脚为0
        self._initialize_inputs()
    
    def _initialize_inputs(self):
        """初始化所有输入信号为默认值
        
        - 主要功能输入设为0
        - 固定配置输入根据测试要求设置
        """
        # 将所有输入初始化为0
        self.inputs.set_all(0)
        
        # 固定配置：根据README.md的要求
        self.inputs.is_vec.value = 1  # 向量模式固定为1
        
        # 其他固定为0的信号已在set_all(0)中设置
        # io_widen_a = 0
        # io_widen_b = 0
        # io_frs1 = 0
        # io_is_frs1 = 0
        # io_uop_idx = 0
        # io_res_widening = 0
        # io_fp_aIsFpCanonicalNAN = 0
        # io_fp_bIsFpCanonicalNAN = 0
        # io_fp_cIsFpCanonicalNAN = 0

    def reset(self, cycles=2):
        """执行DUT复位操作
        
        Args:
            cycles: 复位周期数，默认2个周期
        """
        # 拉高复位信号
        self.dut.reset.value = 1
        self.inputs.fire.value = 0  # 复位期间禁止计算
        self.Step(cycles)
        
        # 释放复位
        self.dut.reset.value = 0
        self.Step(1)
    
    def configure_operation(self, op_code, fp_format=1, round_mode=0):
        """配置FMA操作参数
        
        Args:
            op_code: 操作码（0-8）
                0: vfmul, 1: vfmacc, 2: vfnmacc, 3: vfmsac, 4: vfnmsac
                5: vfmadd, 6: vfnmadd, 7: vfmsub, 8: vfnmsub
            fp_format: 浮点格式（0=FP16, 1=FP32, 2=FP64），默认FP32
            round_mode: 舍入模式（0=RNE, 1=RTZ, 2=RDN, 3=RUP, 4=RMM），默认RNE
        """
        self.inputs.op_code.value = op_code
        self.inputs.fp_format.value = fp_format
        self.inputs.round_mode.value = round_mode
    
    def set_operands(self, fp_a, fp_b, fp_c):
        """设置浮点操作数
        
        Args:
            fp_a: 源操作数vs2（64位整数表示的浮点数）
            fp_b: 源操作数vs1（64位整数表示的浮点数）
            fp_c: 源操作数vd（64位整数表示的浮点数）
        """
        self.inputs.fp_a.value = fp_a
        self.inputs.fp_b.value = fp_b
        self.inputs.fp_c.value = fp_c
    
    def fire_operation(self):
        """触发FMA计算
        
        设置io_fire=1，启动流水线计算
        """
        self.inputs.fire.value = 1
    
    def clear_fire(self):
        """清除fire信号
        
        设置io_fire=0，停止新输入进入流水线
        """
        self.inputs.fire.value = 0
    
    def get_result(self):
        """获取计算结果
        
        Returns:
            tuple: (result, fflags) 计算结果和异常标志位
        """
        return self.outputs.fp_result.value, self.outputs.fflags.value
    
    # 直接导出DUT的Step操作
    def Step(self, i: int = 1):
        """推进时钟周期
        
        Args:
            i: 推进的周期数，默认1
            
        Returns:
            DUT的Step返回值
        """
        return self.dut.Step(i)


# 定义env fixture, 请取消下面的注释，并根据需要修改名称
@pytest.fixture(scope="function") # 用scope="function"确保每个测试用例都创建了一个全新的Env
def env(dut):
     # 一般情况下为每个test都创建全新的 env 不需要 yield
     return VectorFloatFMAEnv(dut)


# 定义其他Env
# @pytest.fixture(scope="function") # 用scope="function"确保每个测试用例都创建了一个全新的Env
# def env1(dut):
#     return MyEnv1(dut)
#
#
# ============================================================================
# VectorFloatFMA API函数
# ============================================================================

def api_VectorFloatFMA_fma_operation(env, fp_a, fp_b, fp_c, op_code, 
                                     fp_format=1, round_mode=0, timeout_cycles=10):
    """执行VectorFloatFMA的融合乘加运算
    
    这是最底层的API函数，直接封装DUT的基本操作。支持所有9种操作码和3种浮点格式。
    该函数会自动处理流水线延迟（4周期），并等待结果输出。
    
    Args:
        env: VectorFloatFMAEnv实例，已初始化的测试环境
        fp_a (int): 源操作数vs2，64位整数表示的浮点数
        fp_b (int): 源操作数vs1，64位整数表示的浮点数
        fp_c (int): 源操作数vd，64位整数表示的浮点数
        op_code (int): 操作码，范围[0-8]
            0: vfmul (乘法)
            1: vfmacc (正乘加)
            2: vfnmacc (负乘负加)
            3: vfmsac (正乘减)
            4: vfnmsac (负乘正加)
            5: vfmadd (变体正乘加)
            6: vfnmadd (变体负乘负加)
            7: vfmsub (变体正乘减)
            8: vfnmsub (变体负乘正加)
        fp_format (int, optional): 浮点格式，默认FP32
            0: FP16 (半精度)
            1: FP32 (单精度)
            2: FP64 (双精度)
        round_mode (int, optional): 舍入模式，默认RNE
            0: RNE (最近偶数舍入)
            1: RTZ (向零舍入)
            2: RDN (向下舍入)
            3: RUP (向上舍入)
            4: RMM (最近最大值舍入)
        timeout_cycles (int, optional): 最大等待周期数，默认10
    
    Returns:
        tuple: (result, fflags) 包含两个元素的元组
            - result (int): 计算结果，64位整数表示的浮点数
            - fflags (int): 异常标志位，20位
    
    Raises:
        ValueError: 当操作码、格式或舍入模式超出有效范围时抛出
        TimeoutError: 当等待超时时抛出（实际上此处不会超时，因为流水线固定延迟）
    
    Example:
        >>> # 计算 2.0 × 3.0 = 6.0 (FP64格式)
        >>> fp_a = 0x4000000000000000  # 2.0
        >>> fp_b = 0x4008000000000000  # 3.0
        >>> result, fflags = api_VectorFloatFMA_fma_operation(
        ...     env, fp_a, fp_b, 0, op_code=0, fp_format=2)
        >>> # result应为0x4018000000000000 (6.0)
    
    Note:
        - VectorFloatFMA是4周期流水线，该API会自动推进4个周期
        - 操作数虽然都是64位，但会根据fp_format解释有效位
        - 连续调用时会自动处理流水线，无需手动控制间隔
    """
    # 参数验证
    if not (0 <= op_code <= 8):
        raise ValueError(f"无效的操作码: {op_code}, 有效范围[0-8]")
    if fp_format not in [1, 2, 3]:
        raise ValueError(f"无效的浮点格式: {fp_format}, 有效值为1(FP16), 2(FP32), 3(FP64)")
    if not (0 <= round_mode <= 4):
        raise ValueError(f"无效的舍入模式: {round_mode}, 有效范围[0-4]")
    
    # 设置操作数
    env.set_operands(fp_a, fp_b, fp_c)
    
    # 配置操作参数
    env.configure_operation(op_code, fp_format, round_mode)
    
    # 触发计算
    env.fire_operation()
    
    # 推进流水线4个周期（固定延迟）
    env.Step(4)
    
    # 清除fire信号
    env.clear_fire()
    
    # 读取结果
    result, fflags = env.get_result()
    
    return result, fflags


def api_VectorFloatFMA_multiply(env, fp_a, fp_b, fp_format=1, round_mode=0):
    """执行浮点乘法运算（vfmul）
    
    封装op_code=0的乘法操作，简化测试用例编写。
    计算公式：result = fp_a × fp_b
    
    Args:
        env: VectorFloatFMAEnv实例
        fp_a (int): 第一个浮点数（乘数）
        fp_b (int): 第二个浮点数（被乘数）
        fp_format (int, optional): 浮点格式，默认FP32
        round_mode (int, optional): 舍入模式，默认RNE
    
    Returns:
        tuple: (result, fflags) 乘法结果和异常标志
    
    Example:
        >>> # 计算 2.5 × 4.0 = 10.0 (FP32)
        >>> fp_a = 0x40200000  # 2.5 in FP32
        >>> fp_b = 0x40800000  # 4.0 in FP32
        >>> result, fflags = api_VectorFloatFMA_multiply(env, fp_a, fp_b)
    """
    return api_VectorFloatFMA_fma_operation(env, fp_a, fp_b, 0, 
                                            op_code=0, 
                                            fp_format=fp_format, 
                                            round_mode=round_mode)


def api_VectorFloatFMA_fmacc(env, fp_a, fp_b, fp_c, fp_format=1, round_mode=0):
    """执行正乘加运算（vfmacc）
    
    封装op_code=1的正乘加操作。
    计算公式：result = (fp_a × fp_b) + fp_c
    
    Args:
        env: VectorFloatFMAEnv实例
        fp_a (int): 第一个浮点数
        fp_b (int): 第二个浮点数
        fp_c (int): 加数
        fp_format (int, optional): 浮点格式，默认FP32
        round_mode (int, optional): 舍入模式，默认RNE
    
    Returns:
        tuple: (result, fflags) 乘加结果和异常标志
    
    Example:
        >>> # 计算 2.0 × 3.0 + 4.0 = 10.0
        >>> result, fflags = api_VectorFloatFMA_fmacc(
        ...     env, 0x40000000, 0x40400000, 0x40800000)
    """
    return api_VectorFloatFMA_fma_operation(env, fp_a, fp_b, fp_c, 
                                            op_code=1, 
                                            fp_format=fp_format, 
                                            round_mode=round_mode)


def api_VectorFloatFMA_fmsac(env, fp_a, fp_b, fp_c, fp_format=1, round_mode=0):
    """执行正乘减运算（vfmsac）
    
    封装op_code=3的正乘减操作。
    计算公式：result = (fp_a × fp_b) - fp_c
    
    Args:
        env: VectorFloatFMAEnv实例
        fp_a (int): 第一个浮点数
        fp_b (int): 第二个浮点数
        fp_c (int): 被减数
        fp_format (int, optional): 浮点格式，默认FP32
        round_mode (int, optional): 舍入模式，默认RNE
    
    Returns:
        tuple: (result, fflags) 乘减结果和异常标志
    
    Example:
        >>> # 计算 5.0 × 2.0 - 3.0 = 7.0
        >>> result, fflags = api_VectorFloatFMA_fmsac(
        ...     env, 0x40A00000, 0x40000000, 0x40400000)
    """
    return api_VectorFloatFMA_fma_operation(env, fp_a, fp_b, fp_c, 
                                            op_code=3, 
                                            fp_format=fp_format, 
                                            round_mode=round_mode)


def api_VectorFloatFMA_batch_operations(env, operations, fp_format=1, round_mode=0):
    """批量执行多个FMA操作
    
    支持流水线化的批量操作，连续输入多个操作并收集所有结果。
    适用于性能测试和覆盖率提升。
    
    Args:
        env: VectorFloatFMAEnv实例
        operations (list): 操作列表，每个元素为(fp_a, fp_b, fp_c, op_code)的元组
        fp_format (int, optional): 浮点格式，默认FP32
        round_mode (int, optional): 舍入模式，默认RNE
    
    Returns:
        list: 结果列表，每个元素为(result, fflags)的元组
    
    Example:
        >>> operations = [
        ...     (0x40000000, 0x40400000, 0, 0),  # 2.0 × 3.0
        ...     (0x40800000, 0x40A00000, 0, 0),  # 4.0 × 5.0
        ... ]
        >>> results = api_VectorFloatFMA_batch_operations(env, operations)
    
    Note:
        - 该API会连续输入所有操作，然后等待流水线排空
        - 适合测试流水线的连续操作能力
    """
    results = []
    
    # 连续输入所有操作
    for fp_a, fp_b, fp_c, op_code in operations:
        env.set_operands(fp_a, fp_b, fp_c)
        env.configure_operation(op_code, fp_format, round_mode)
        env.fire_operation()
        env.Step(1)
        
        # 在第4个操作开始后，第1个结果就会输出
        if len(results) < len(operations):
            if len(results) >= 4:  # 流水线延迟4周期
                result, fflags = env.get_result()
                results.append((result, fflags))
    
    # 停止输入
    env.clear_fire()
    
    # 收集剩余结果
    remaining = len(operations) - len(results)
    for _ in range(remaining):
        env.Step(1)
        result, fflags = env.get_result()
        results.append((result, fflags))
    
    return results
#coding=utf-8

import pytest
from VectorIdiv_function_coverage_def import get_coverage_groups
from toffee_test.reporter import set_func_coverage, set_line_coverage, get_file_in_tmp_dir
from toffee_test.reporter import set_user_info, set_title_info
from toffee import Bundle, Signals, Signal

# import your dut module here
from VectorIdiv import DUTVectorIdiv  # Replace with the actual DUT class import

import os


def current_path_file(file_name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)


def get_coverage_data_path(request, new_path:bool):
    # 通过toffee_test.reporter提供的get_file_in_tmp_dir方法可以让各用例产生的文件名称不重复 (获取新路径需要new_path=True，获取已有路径new_path=False)
    # 获取测试用例名称，为每个测试用例创建对应的代码行覆盖率文件
    tc_name = request.node.name if request is not None else "VectorIdiv"
    return get_file_in_tmp_dir(request, current_path_file("data/"), f"{tc_name}.dat",  new_path=new_path)


def get_waveform_path(request, new_path:bool):
    # 通过toffee_test.reporter提供的get_file_in_tmp_dir方法可以让各用例产生的文件名称不重复 (获取新路径需要new_path=True，获取已有路径new_path=False)
    # 获取测试用例名称，为每个测试用例创建对应的波形
    tc_name = request.node.name if request is not None else "VectorIdiv"
    return get_file_in_tmp_dir(request, current_path_file("data/"), f"{tc_name}.fst",  new_path=new_path)


def create_dut(request):
    """
    创建VectorIdiv DUT实例的工厂函数
    
    Returns:
        dut_instance: VectorIdiv的DUT实例，已完成基本初始化
    """
    # 导入并实例化VectorIdiv DUT类
    dut = DUTVectorIdiv()

    # 设置覆盖率生成文件(必须设置覆盖率文件，否则无法统计覆盖率，导致测试失败)
    dut.SetCoverage(get_coverage_data_path(request, new_path=True))

    # 设置波形生成文件
    dut.SetWaveform(get_waveform_path(request, new_path=True))

    # VectorIdiv是时序电路，需要配置时钟
    # 注意：这里不进行时钟绑定，时钟绑定在dut fixture中进行
    # 不对DUT的任何引脚/接口进行赋值操作
    
    return dut


@pytest.fixture(scope="function") # 用scope="function"确保每个测试用例都创建了一个全新的DUT
def dut(request):
    """VectorIdiv DUT fixture，管理测试的完整生命周期"""
    # 第1步：创建DUT实例
    dut = create_dut(request)                         # 创建DUT
    func_coverage_group = get_coverage_groups(dut)
    
    # 第2步：配置时钟（VectorIdiv是时序电路）
    # 根据VectorIdiv_top.sv和__init__.py，时钟信号名为"clock"
    dut.InitClock("clock")

    # 第3步：设置覆盖率采样回调
    # 上升沿采样，StepRis也适用于组合电路用dut.Step推进时采样
    # 必须要有g.sample()采样覆盖组，如何不在StepRis/StepFail中采样，则需要在test function中手动调用，否则无法统计覆盖率导致失败
    dut.StepRis(lambda _: [g.sample()
                           for g in
                           func_coverage_group])

    # 第4步：绑定覆盖率组到DUT实例
    # 以属性名称fc_cover保存覆盖组到DUT
    setattr(dut, "fc_cover",
            {g.name:g for g in func_coverage_group})

    # 第5步：返回DUT实例给测试函数
    yield dut

    # 第6步：测试后处理（清理阶段）
    # 通过set_func_coverage把覆盖组传递给toffee_test
    set_func_coverage(request, func_coverage_group)

    # 设置需要收集的代码行覆盖率文件(获取已有路径new_path=False) 向toffee_test传代码行递覆盖率数据
    # 代码行覆盖率 ignore 文件的固定路径为当前文件所在目录下的：VectorIdiv.ignore，请不要改变
    set_line_coverage(request, get_coverage_data_path(request, new_path=False), ignore=current_path_file("VectorIdiv.ignore"))

    # 设置用户信息到报告
    set_user_info("UCAgent-25.11.22.dev2+gc92ac64e0", "unitychip@bosc.ac.cn")
    set_title_info("VectorIdiv Test Report")

    # 第7步：清理资源
    for g in func_coverage_group:                        # 清空覆盖组统计
        g.clear()                                        
    dut.Finish()                                         # 清理DUT，每个DUT class 都有 Finish 方法


# 定义VectorIdiv的基础引脚Bundle类
class VectorIdivBasicBundle(Bundle):
    """VectorIdiv基础控制引脚封装"""
    clock, reset = Signals(2)
    sew, sign = Signals(2)  # io_sew, io_sign
    flush, d_zero = Signals(2)  # io_flush, io_d_zero


# 定义VectorIdiv的数据输入Bundle类  
class VectorIdivInputBundle(Bundle):
    """VectorIdiv数据输入引脚封装"""
    dividend_v, divisor_v = Signals(2)  # io_dividend_v, io_divisor_v


# 定义VectorIdiv的除法控制Bundle类
class VectorIdivDivControlBundle(Bundle):
    """VectorIdiv除法控制引脚封装"""
    div_in_valid, div_in_ready = Signals(2)  # io_div_in_valid, io_div_in_ready
    div_out_ready, div_out_valid = Signals(2)  # io_div_out_ready, io_div_out_valid


# 定义VectorIdiv的输出Bundle类
class VectorIdivOutputBundle(Bundle):
    """VectorIdiv输出引脚封装"""
    div_out_q_v, div_out_rem_v = Signals(2)  # io_div_out_q_v, io_div_out_rem_v


# 定义Mock组件类，模拟上下游依赖
class VectorIdivMock:
    """VectorIdiv的Mock组件，模拟上下游依赖"""
    
    def __init__(self, env):
        self.env = env
        self.input_queue = []
        self.output_queue = []
        self.pipeline_stalls = 0
        
    def push_input(self, dividend, divisor, sew=2, sign=0):
        """推送输入数据到队列"""
        self.input_queue.append({
            'dividend': dividend,
            'divisor': divisor, 
            'sew': sew,
            'sign': sign
        })
    
    def pop_output(self):
        """从输出队列获取结果"""
        if self.output_queue:
            return self.output_queue.pop(0)
        return None
    
    def handle_pipeline(self):
        """处理流水线事件"""
        # 模拟输入握手
        if self.env.io.div_in_valid.value == 1 and self.env.io.div_in_ready.value == 1:
            if self.input_queue:
                input_data = self.input_queue.pop(0)
                # 模拟处理延迟
                self.pipeline_stalls += 1
                
        # 模拟输出握手  
        if self.env.io.div_out_valid.value == 1 and self.env.io.div_out_ready.value == 1:
            # 收集输出结果
            quotient = self.env.io.div_out_q_v.value
            remainder = self.env.io.div_out_rem_v.value
            self.output_queue.append({
                'quotient': quotient,
                'remainder': remainder,
                'cycle': self.pipeline_stalls
            })


# 定义VectorIdivEnv类，封装DUT的引脚和常用操作
class VectorIdivEnv:
    """VectorIdiv测试环境，提供引脚封装和基本操作"""

    def __init__(self, dut):
        self.dut = dut
        
        # 使用from_dict方法进行分组引脚映射
        self.basic = VectorIdivBasicBundle.from_dict({
            'clock': 'clock',
            'reset': 'reset',
            'sew': 'io_sew',
            'sign': 'io_sign',
            'flush': 'io_flush',
            'd_zero': 'io_d_zero'
        })
        
        self.input = VectorIdivInputBundle.from_dict({
            'dividend_v': 'io_dividend_v',
            'divisor_v': 'io_divisor_v'
        })
        
        self.div_control = VectorIdivDivControlBundle.from_dict({
            'div_in_valid': 'io_div_in_valid',
            'div_in_ready': 'io_div_in_ready',
            'div_out_ready': 'io_div_out_ready',
            'div_out_valid': 'io_div_out_valid'
        })
        
        self.output = VectorIdivOutputBundle.from_dict({
            'div_out_q_v': 'io_div_out_q_v',
            'div_out_rem_v': 'io_div_out_rem_v'
        })
        
        # 绑定到DUT
        self.basic.bind(dut)
        self.input.bind(dut)
        self.div_control.bind(dut)
        self.output.bind(dut)
        
        # 为了兼容性，提供统一的io接口
        self.io = type('IoBundle', (), {})()
        self.io.basic = self.basic
        self.io.input = self.input  
        self.io.div_control = self.div_control
        self.io.output = self.output
        # 导出关键信号到io顶层
        self.io.sew = self.basic.sew
        self.io.sign = self.basic.sign
        self.io.flush = self.basic.flush
        self.io.d_zero = self.basic.d_zero
        self.io.dividend_v = self.input.dividend_v
        self.io.divisor_v = self.input.divisor_v
        self.io.div_in_valid = self.div_control.div_in_valid
        self.io.div_in_ready = self.div_control.div_in_ready
        self.io.div_out_ready = self.div_control.div_out_ready
        self.io.div_out_valid = self.div_control.div_out_valid
        self.io.div_out_q_v = self.output.div_out_q_v
        self.io.div_out_rem_v = self.output.div_out_rem_v
        
        # 初始化所有输入引脚为0
        self.basic.set_all(0)
        self.input.set_all(0)
        self.div_control.set_all(0)
        
        # 实例化Mock组件
        self.mock = VectorIdivMock(self)
        
        # 添加StepRis回调用于Mock组件驱动
        self.dut.StepRis(self._handle_mock_events)

    def _handle_mock_events(self, cycle):
        """处理Mock组件事件的内部回调"""
        self.mock.handle_pipeline()

    # 根据需要添加清空Env注册的回调函数
    def clear_cbs(self):
        """清空所有注册的回调函数"""
        # 如果有注册的回调函数，在这里清除
        pass

    def reset(self):
        """执行VectorIdiv的复位操作"""
        self.basic.reset.value = 1
        self.dut.Step(5)  # 保持复位5个时钟周期
        self.basic.reset.value = 0
        self.dut.Step(5)  # 等待电路稳定
        
        # 手动清零输入信号（因为reset可能不会自动清零所有输入）
        self.basic.set_all(0)
        self.input.set_all(0) 
        self.div_control.set_all(0)
        
        # 清空Mock组件状态
        self.mock.input_queue.clear()
        self.mock.output_queue.clear()
        self.mock.pipeline_stalls = 0

    # 直接导出DUT的通用操作Step
    def Step(self, i:int = 1):
        return self.dut.Step(i)
    
    def start_division(self, dividend, divisor, sew=2, sign=0):
        """启动除法运算
        
        Args:
            dividend: 被除数
            divisor: 除数  
            sew: 元素宽度(0=8bit, 1=16bit, 2=32bit, 3=64bit)
            sign: 是否有符号(0=无符号, 1=有符号)
        """
        # 设置参数
        self.basic.sew.value = sew
        self.basic.sign.value = sign
        self.input.dividend_v.value = dividend
        self.input.divisor_v.value = divisor
        
        # 启动运算
        self.div_control.div_in_valid.value = 1
        self.Step()
        self.div_control.div_in_valid.value = 0
    
    def wait_for_result(self, timeout=100):
        """等待除法运算完成
        
        Args:
            timeout: 最大等待周期数
            
        Returns:
            dict: 包含商和余数的字典，超时返回None
        """
        # 设置输出准备信号
        self.div_control.div_out_ready.value = 1
        
        for _ in range(timeout):
            if self.div_control.div_out_valid.value == 1:
                result = {
                    'quotient': self.output.div_out_q_v.value,
                    'remainder': self.output.div_out_rem_v.value
                }
                self.div_control.div_out_ready.value = 0
                return result
            self.Step()
        
        # 超时
        self.div_control.div_out_ready.value = 0
        return None
    
    def perform_division(self, dividend, divisor, sew=2, sign=0, timeout=100):
        """执行完整的除法运算
        
        Args:
            dividend: 被除数
            divisor: 除数
            sew: 元素宽度
            sign: 是否有符号
            timeout: 最大等待周期
            
        Returns:
            dict: 运算结果，失败返回None
        """
        self.start_division(dividend, divisor, sew, sign)
        return self.wait_for_result(timeout)
    
    def flush_pipeline(self):
        """清空流水线"""
        self.basic.flush.value = 1
        self.Step(2)
        self.basic.flush.value = 0
    
    def get_status(self):
        """获取VectorIdiv当前状态
        
        Returns:
            dict: 包含各种状态信号的字典
        """
        return {
            'div_in_ready': self.io.div_in_ready.value,
            'div_out_valid': self.io.div_out_valid.value, 
            'd_zero': self.io.d_zero.value,
            'current_sew': self.io.sew.value,
            'current_sign': self.io.sign.value
        }


# 定义env fixture, 请取消下面的注释，并根据需要修改名称
@pytest.fixture(scope="function") # 用scope="function"确保每个测试用例都创建了一个全新的Env
def env(dut):
     # 一般情况下为每个test都创建全新的 env 不需要 yield
     return VectorIdivEnv(dut)


# 定义其他Env
# @pytest.fixture(scope="function") # 用scope="function"确保每个测试用例都创建了一个全新的Env
# def env1(dut):
#     return MyEnv1(dut)
#
#
# 根据DUT的功能需要，定义API函数， API函数需要通用且稳定，不是越多越好

def api_VectorIdiv_divide(env, dividend: int, divisor: int, sew: int = 2, sign: int = 0, timeout: int = 100):
    """VectorIdiv除法运算API，执行标量或向量除法运算

    该API提供VectorIdiv的核心除法功能，支持8/16/32/64位精度和有符号/无符号运算模式。
    自动处理握手协议和时序控制，为测试用例提供简洁的除法运算接口。

    Args:
        env: VectorIdivEnv实例，必须是已初始化的Env实例
        dividend (int): 被除数，支持标量或向量格式（128位），取值范围取决于SEW设置
        divisor (int): 除数，支持标量或向量格式（128位），取值范围取决于SEW设置
        sew (int, optional): 元素宽度选择，0=8位, 1=16位, 2=32位, 3=64位，默认为2（32位）
        sign (int, optional): 运算模式，0=无符号运算, 1=有符号运算，默认为0（无符号）
        timeout (int, optional): 最大等待周期数，防止死循环，默认为100

    Returns:
        dict: 运算结果字典，包含以下键值：
            - quotient (int): 商，向量格式（128位）
            - remainder (int): 余数，向量格式（128位）
            失败时返回None

    Raises:
        ValueError: 当参数超出有效范围时抛出
        TimeoutError: 当运算超时时抛出
        RuntimeError: 当DUT硬件故障时抛出

    Example:
        >>> # 32位无符号除法：100 ÷ 25 = 4 余 0
        >>> result = api_VectorIdiv_divide(env, 100, 25, sew=2, sign=0)
        >>> print(f"商: {result['quotient']}, 余数: {result['remainder']}")
        商: 4, 余数: 0

        >>> # 8位有符号向量除法
        >>> dividend = 0x05040302  # [2, 3, 4, 5]
        >>> divisor = 0x02020202    # [2, 2, 2, 2]  
        >>> result = api_VectorIdiv_divide(env, dividend, divisor, sew=0, sign=1)

    Note:
        - 该API适用于时序电路，会自动处理握手协议和时钟推进
        - 向量模式下，所有元素使用相同的SEW和SIGN设置
        - 除零情况下，商设置为全1，余数等于被除数，d_zero标志位置位
        - 连续调用时建议间隔至少1个时钟周期
    """
    # 参数验证
    if not isinstance(dividend, int) or not isinstance(divisor, int):
        raise TypeError("dividend和divisor必须是整数类型")
    
    if sew not in [0, 1, 2, 3]:
        raise ValueError(f"无效的SEW值: {sew}，必须是0(8位)、1(16位)、2(32位)或3(64位)")
    
    if sign not in [0, 1]:
        raise ValueError(f"无效的SIGN值: {sign}，必须是0(无符号)或1(有符号)")
    
    if timeout <= 0:
        raise ValueError(f"超时时间必须为正数: {timeout}")
    
    # 检查数值范围（基于SEW）
    element_width = 8 << sew  # 8, 16, 32, 64
    max_value = (1 << element_width) - 1
    
    if sign == 1:  # 有符号数范围检查
        min_value = -(1 << (element_width - 1))
        if dividend < min_value or dividend > max_value:
            raise ValueError(f"有符号被除数超出{element_width}位范围: [{min_value}, {max_value}]")
        if divisor < min_value or divisor > max_value:
            raise ValueError(f"有符号除数超出{element_width}位范围: [{min_value}, {max_value}]")
    else:  # 无符号数范围检查
        if dividend < 0 or dividend > max_value:
            raise ValueError(f"无符号被除数超出{element_width}位范围: [0, {max_value}]")
        if divisor < 0 or divisor > max_value:
            raise ValueError(f"无符号除数超出{element_width}位范围: [0, {max_value}]")
    
    # 执行除法运算
    result = env.perform_division(dividend, divisor, sew, sign, timeout)
    
    if result is None:
        raise TimeoutError(f"除法运算超时，被除数: {dividend}, 除数: {divisor}, 超时周期: {timeout}")
    
    return result


def api_VectorIdiv_basic_operation(env, dividend: int, divisor: int, sew: int, sign: int, 
                                 start_cycle: int = 0, timeout: int = 100):
    """VectorIdiv底层操作API，提供最基础的除法运算控制

    该API提供对VectorIdiv硬件的直接控制，包括精确的时序控制和状态监控。
    适用于需要细粒度控制或特殊测试场景的高级用户。

    Args:
        env: VectorIdivEnv实例，必须是已初始化的Env实例
        dividend (int): 被除数，128位向量格式
        divisor (int): 除数，128位向量格式
        sew (int): 元素宽度，0=8位, 1=16位, 2=32位, 3=64位
        sign (int): 运算模式，0=无符号, 1=有符号
        start_cycle (int, optional): 开始执行的时钟周期，默认为0（立即执行）
        timeout (int, optional): 最大等待周期数，默认为100

    Returns:
        dict: 详细的运算结果字典，包含以下键值：
            - success (bool): 运算是否成功
            - quotient (int): 商，128位向量格式
            - remainder (int): 余数，128位向量格式  
            - cycles_used (int): 使用的时钟周期数
            - div_by_zero (bool): 是否发生除零
            - overflow (bool): 是否发生溢出（仅适用于有符号运算）
            - start_cycle (int): 运算开始的实际时钟周期
            - end_cycle (int): 运算结束的时钟周期

    Raises:
        ValueError: 当参数无效时抛出
        RuntimeError: 当硬件状态异常时抛出
        TimeoutError: 当运算超时时抛出

    Example:
        >>> # 精确控制除法运算时序
        >>> result = api_VectorIdiv_basic_operation(
        ...     env, dividend=100, divisor=25, sew=2, sign=0, 
        ...     start_cycle=10, timeout=50
        ... )
        >>> if result['success']:
        ...     print(f"运算成功，耗时{result['cycles_used']}个周期")

    Note:
        - 该API提供最底层的硬件控制，需要用户自行处理握手协议
        - 适用于性能测试、时序分析等高级应用场景
        - 返回更详细的诊断信息，便于问题定位和分析
    """
    # 参数验证
    if not all(isinstance(x, int) for x in [dividend, divisor, sew, sign, start_cycle, timeout]):
        raise TypeError("所有参数必须是整数类型")
    
    if sew not in [0, 1, 2, 3]:
        raise ValueError(f"无效的SEW值: {sew}")
    
    if sign not in [0, 1]:
        raise ValueError(f"无效的SIGN值: {sign}")
    
    if start_cycle < 0:
        raise ValueError(f"开始周期不能为负数: {start_cycle}")
    
    if timeout <= 0:
        raise ValueError(f"超时时间必须为正数: {timeout}")
    
    # 等待到指定的开始周期
    current_cycle = 0
    while current_cycle < start_cycle:
        env.Step(1)
        current_cycle += 1
    
    # 记录开始状态
    start_status = env.get_status()
    actual_start_cycle = current_cycle
    
    # 设置运算参数
    env.io.sew.value = sew
    env.io.sign.value = sign
    env.io.dividend_v.value = dividend
    env.io.divisor_v.value = divisor
    
    # 等待输入准备就绪
    wait_cycles = 0
    while env.io.div_in_ready.value == 0 and wait_cycles < 10:
        env.Step(1)
        wait_cycles += 1
        current_cycle += 1
    
    if wait_cycles >= 10:
        raise RuntimeError("输入准备信号超时，硬件可能处于异常状态")
    
    # 启动运算
    env.io.div_in_valid.value = 1
    env.Step(1)
    env.io.div_in_valid.value = 0
    current_cycle += 1
    
    # 等待运算完成
    env.io.div_out_ready.value = 1
    operation_cycles = 0
    div_by_zero_detected = False
    
    while env.io.div_out_valid.value == 0 and operation_cycles < timeout:
        env.Step(1)
        operation_cycles += 1
        current_cycle += 1
        
        # 检查除零标志
        if env.io.d_zero.value != 0:
            div_by_zero_detected = True
    
    if operation_cycles >= timeout:
        env.io.div_out_ready.value = 0
        raise TimeoutError(f"除法运算超时，已等待{timeout}个周期")
    
    # 读取结果
    quotient = env.io.div_out_q_v.value
    remainder = env.io.div_out_rem_v.value
    env.io.div_out_ready.value = 0
    env.Step(1)  # 完成握手
    current_cycle += 1
    
    # 检查溢出（仅适用于有符号运算）
    overflow_detected = False
    if sign == 1:
        element_width = 8 << sew
        min_value = -(1 << (element_width - 1))
        
        # 提取向量元素检查是否有最小负数除-1的溢出情况
        from VectorIdiv_function_coverage_def import extract_vector_elements
        dividends = extract_vector_elements(dividend, sew, True)
        divisors = extract_vector_elements(divisor, sew, True)
        
        for d, r in zip(dividends, divisors):
            if d == min_value and r == -1:
                overflow_detected = True
                break
    
    return {
        'success': True,
        'quotient': quotient,
        'remainder': remainder,
        'cycles_used': operation_cycles + wait_cycles + 2,  # 总周期数
        'div_by_zero': div_by_zero_detected,
        'overflow': overflow_detected,
        'start_cycle': actual_start_cycle,
        'end_cycle': current_cycle
    }


def api_VectorIdiv_check_div_by_zero(env, divisor: int, sew: int = 2, timeout: int = 50):
    """VectorIdiv除零检测API，专门用于测试除零检测功能

    该API专门用于验证VectorIdiv的除零检测机制，包括d_zero标志位的正确设置
    和除零情况下的特殊处理行为。

    Args:
        env: VectorIdivEnv实例，必须是已初始化的Env实例
        divisor (int): 测试除数，预期会触发除零检测
        sew (int, optional): 元素宽度，默认为2（32位）
        timeout (int, optional): 最大等待周期数，默认为50

    Returns:
        bool: True表示正确检测到除零，False表示未检测到或检测异常

    Raises:
        ValueError: 当参数无效时抛出
        TimeoutError: 当检测超时时抛出

    Example:
        >>> # 测试除零检测
        >>> detected = api_VectorIdiv_check_div_by_zero(env, divisor=0, sew=2)
        >>> if detected:
        ...     print("除零检测功能正常")

    Note:
        - 该API专门用于除零检测功能验证
        - 使用固定的被除数0x12345678进行测试
        - 检查d_zero标志位是否正确置位
    """
    # 参数验证
    if not isinstance(divisor, int):
        raise TypeError("除数必须是整数类型")
    
    if sew not in [0, 1, 2, 3]:
        raise ValueError(f"无效的SEW值: {sew}")
    
    if timeout <= 0:
        raise ValueError(f"超时时间必须为正数: {timeout}")
    
    try:
        # 执行除零测试
        result = api_VectorIdiv_divide(env, 0x12345678, divisor, sew, 0, timeout)
        
        # 检查d_zero信号是否被置位
        return env.io.d_zero.value == 1
        
    except (TimeoutError, RuntimeError):
        # 如果发生异常，认为除零检测失败
        return False


def api_VectorIdiv_vector_division(env, dividend_vector: int, divisor_vector: int, 
                                  sew: int = 2, sign: int = 0, timeout: int = 100):
    """VectorIdiv向量除法运算API，专门用于向量并行除法运算

    该API专门针对VectorIdiv的向量化处理能力，支持多个元素同时进行除法运算。
    自动处理向量数据打包和解包，提供直观的向量运算接口。

    Args:
        env: VectorIdivEnv实例，必须是已初始化的Env实例
        dividend_vector (int): 被除数向量，128位向量格式
        divisor_vector (int): 除数向量，128位向量格式
        sew (int, optional): 元素宽度，0=8位, 1=16位, 2=32位, 3=64位，默认为2（32位）
        sign (int, optional): 运算模式，0=无符号, 1=有符号，默认为0（无符号）
        timeout (int, optional): 最大等待周期数，默认为100

    Returns:
        dict: 向量运算结果字典，包含以下键值：
            - quotient (int): 商向量，128位向量格式
            - remainder (int): 余数向量，128位向量格式
            - element_count (int): 运算的元素数量
            - element_width (int): 元素宽度（位）
            失败时返回None

    Raises:
        ValueError: 当参数无效或向量格式错误时抛出
        TimeoutError: 当运算超时时抛出

    Example:
        >>> # 32位向量除法：[100, 200] ÷ [25, 50] = [4, 4]
        >>> dividend = (200 << 32) | 100  # 向量[100, 200]
        >>> divisor = (50 << 32) | 25    # 向量[25, 50]
        >>> result = api_VectorIdiv_vector_division(env, dividend, divisor, sew=2)
        >>> print(f"商向量: 0x{result['quotient']:016x}")

        >>> # 8位向量除法：[10, 20, 30, 40] ÷ [2, 4, 6, 8] = [5, 5, 5, 5]
        >>> dividend = 0x281C1410  # [16, 20, 28, 40] 小端序
        >>> divisor = 0x08060402   # [2, 4, 6, 8] 小端序
        >>> result = api_VectorIdiv_vector_division(env, dividend, divisor, sew=0)

    Note:
        - 向量元素按小端序排列在128位向量中
        - 所有元素使用相同的SEW和SIGN设置
        - 元素数量 = 128 ÷ (8 << sew)
        - 适用于测试VectorIdiv的并行处理能力
    """
    # 参数验证
    if not all(isinstance(x, int) for x in [dividend_vector, divisor_vector, sew, sign, timeout]):
        raise TypeError("所有参数必须是整数类型")
    
    if sew not in [0, 1, 2, 3]:
        raise ValueError(f"无效的SEW值: {sew}")
    
    if sign not in [0, 1]:
        raise ValueError(f"无效的SIGN值: {sign}")
    
    if timeout <= 0:
        raise ValueError(f"超时时间必须为正数: {timeout}")
    
    # 检查向量范围
    if dividend_vector < 0 or dividend_vector > 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
        raise ValueError("被除数向量超出128位范围")
    
    if divisor_vector < 0 or divisor_vector > 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
        raise ValueError("除数向量超出128位范围")
    
    # 执行向量除法运算
    result = api_VectorIdiv_divide(env, dividend_vector, divisor_vector, sew, sign, timeout)
    
    if result is None:
        return None
    
    # 添加向量特定信息
    element_width = 8 << sew
    element_count = 128 // element_width
    
    result['element_count'] = element_count
    result['element_width'] = element_width
    
    return result


def api_VectorIdiv_get_status(env):
    """获取VectorIdiv当前状态，提供详细的硬件状态信息

    该API用于监控VectorIdiv的实时状态，包括握手信号、配置参数和错误标志。
    适用于调试、状态监控和测试验证场景。

    Args:
        env: VectorIdivEnv实例，必须是已初始化的Env实例

    Returns:
        dict: 详细的状态信息字典，包含以下键值：
            - handshake (dict): 握手协议状态
                - div_in_ready (int): 输入准备信号，1表示准备就绪
                - div_out_valid (int): 输出有效信号，1表示输出有效
            - configuration (dict): 配置参数状态
                - current_sew (int): 当前元素宽度设置
                - current_sign (int): 当前符号模式设置
            - flags (dict): 状态标志
                - d_zero (int): 除零标志，非零表示检测到除零
                - flush_active (int): 流水线清空标志
            - pipeline (dict): 流水线状态
                - input_queue_size (int): Mock组件输入队列大小
                - output_queue_size (int): Mock组件输出队列大小
                - pipeline_stalls (int): 流水线停顿计数

    Example:
        >>> # 监控VectorIdiv状态
        >>> status = api_VectorIdiv_get_status(env)
        >>> print(f"输入准备: {status['handshake']['div_in_ready']}")
        >>> print(f"当前SEW: {status['configuration']['current_sew']}")
        >>> if status['flags']['d_zero'] != 0:
        ...     print("检测到除零情况")

    Note:
        - 该API提供只读状态信息，不会修改硬件状态
        - 状态信息实时反映硬件当前状态
        - 包含Mock组件的内部状态，便于调试和验证
    """
    # 基本硬件状态
    basic_status = {
        'handshake': {
            'div_in_ready': env.io.div_in_ready.value,
            'div_out_valid': env.io.div_out_valid.value,
        },
        'configuration': {
            'current_sew': env.io.sew.value,
            'current_sign': env.io.sign.value,
        },
        'flags': {
            'd_zero': env.io.d_zero.value,
            'flush_active': env.io.flush.value,
        }
    }
    
    # Mock组件状态（如果存在）
    if hasattr(env, 'mock') and env.mock is not None:
        basic_status['pipeline'] = {
            'input_queue_size': len(env.mock.input_queue),
            'output_queue_size': len(env.mock.output_queue),
            'pipeline_stalls': env.mock.pipeline_stalls,
        }
    else:
        basic_status['pipeline'] = {
            'input_queue_size': 0,
            'output_queue_size': 0,
            'pipeline_stalls': 0,
        }
    
    return basic_status


def api_VectorIdiv_reset_and_init(env, sew: int = 2, sign: int = 0):
    """VectorIdiv复位和初始化API，提供完整的硬件初始化流程

    该API执行VectorIdiv的完整复位和初始化序列，包括硬件复位、参数配置
    和状态验证，确保硬件处于已知的初始状态。

    Args:
        env: VectorIdivEnv实例，必须是已初始化的Env实例
        sew (int, optional): 初始化元素宽度设置，默认为2（32位）
        sign (int, optional): 初始化符号模式设置，默认为0（无符号）

    Returns:
        dict: 初始化结果字典，包含以下键值：
            - success (bool): 初始化是否成功
            - reset_cycles (int): 复位使用的时钟周期数
            - final_config (dict): 最终配置状态
            - status_check (bool): 状态验证是否通过

    Raises:
        ValueError: 当参数无效时抛出
        RuntimeError: 当初始化失败时抛出

    Example:
        >>> # 复位并初始化为32位有符号模式
        >>> result = api_VectorIdiv_reset_and_init(env, sew=2, sign=1)
        >>> if result['success']:
        ...     print("初始化成功")
        ...     print(f"复位耗时: {result['reset_cycles']}个周期")

    Note:
        - 该API会清空所有输入信号和内部状态
        - 自动验证初始化后的配置状态
        - 适用于测试用例开始前的环境准备
    """
    # 参数验证
    if not isinstance(sew, int) or not isinstance(sign, int):
        raise TypeError("SEW和SIGN必须是整数类型")
    
    if sew not in [0, 1, 2, 3]:
        raise ValueError(f"无效的SEW值: {sew}")
    
    if sign not in [0, 1]:
        raise ValueError(f"无效的SIGN值: {sign}")
    
    try:
        # 执行复位
        env.reset()
        reset_cycles = 10  # 复位固定使用10个周期（5个复位+5个稳定）
        
        # 配置初始参数
        env.io.sew.value = sew
        env.io.sign.value = sign
        env.Step(2)  # 等待配置生效
        
        # 验证配置状态
        final_config = {
            'sew': env.io.sew.value,
            'sign': env.io.sign.value,
        }
        
        status_check = (final_config['sew'] == sew and final_config['sign'] == sign)
        
        if not status_check:
            raise RuntimeError("配置验证失败，硬件可能存在异常")
        
        return {
            'success': True,
            'reset_cycles': reset_cycles + 2,
            'final_config': final_config,
            'status_check': status_check,
        }
        
    except Exception as e:
        raise RuntimeError(f"初始化失败: {e}")


# 本文件为模板，请根据需要修改，删除不需要的代码和注释
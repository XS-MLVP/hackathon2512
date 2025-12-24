#coding=utf-8

from VectorIdiv_api import *  # 重要，必须用 import *， 而不是 import env，不然会出现 dut 没定义错误
import pytest


def test_api_VectorIdiv_env_basic_functionality(env):
    """测试env fixture的基本功能
    
    验证env fixture是否正确初始化，包括：
    - 引脚封装是否正确
    - Mock组件是否正常工作
    - 基本操作方法是否可用
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-VECTOR-DIVISION", test_api_VectorIdiv_env_basic_functionality, 
                                              ["CK-UNSIGNED-32", "CK-QUOTIENT", "CK-REMAINDER"])
    
    # 验证env的基本属性
    assert hasattr(env, 'dut'), "env应该有dut属性"
    assert hasattr(env, 'basic'), "env应该有basic引脚封装"
    assert hasattr(env, 'input'), "env应该有input引脚封装"
    assert hasattr(env, 'div_control'), "env应该有div_control引脚封装"
    assert hasattr(env, 'output'), "env应该有output引脚封装"
    assert hasattr(env, 'io'), "env应该有统一的io接口"
    
    # 验证io接口的关键信号
    assert hasattr(env.io, 'sew'), "io接口应该有sew信号"
    assert hasattr(env.io, 'sign'), "io接口应该有sign信号"
    assert hasattr(env.io, 'dividend_v'), "io接口应该有dividend_v信号"
    assert hasattr(env.io, 'divisor_v'), "io接口应该有divisor_v信号"
    assert hasattr(env.io, 'div_in_valid'), "io接口应该有div_in_valid信号"
    assert hasattr(env.io, 'div_in_ready'), "io接口应该有div_in_ready信号"
    assert hasattr(env.io, 'div_out_ready'), "io接口应该有div_out_ready信号"
    assert hasattr(env.io, 'div_out_valid'), "io接口应该有div_out_valid信号"
    assert hasattr(env.io, 'div_out_q_v'), "io接口应该有div_out_q_v信号"
    assert hasattr(env.io, 'div_out_rem_v'), "io接口应该有div_out_rem_v信号"
    assert hasattr(env.io, 'd_zero'), "io接口应该有d_zero信号"
    assert hasattr(env.io, 'flush'), "io接口应该有flush信号"
    
    # 验证Mock组件
    assert hasattr(env, 'mock'), "env应该有mock组件"
    assert hasattr(env.mock, 'input_queue'), "mock组件应该有input_queue"
    assert hasattr(env.mock, 'output_queue'), "mock组件应该有output_queue"
    assert hasattr(env.mock, 'pipeline_stalls'), "mock组件应该有pipeline_stalls"
    
    # 验证基本操作方法
    assert hasattr(env, 'Step'), "env应该有Step方法"
    assert hasattr(env, 'reset'), "env应该有reset方法"
    assert hasattr(env, 'start_division'), "env应该有start_division方法"
    assert hasattr(env, 'wait_for_result'), "env应该有wait_for_result方法"
    assert hasattr(env, 'perform_division'), "env应该有perform_division方法"
    assert hasattr(env, 'get_status'), "env应该有get_status方法"
    
    # 测试基本信号操作
    env.io.sew.value = 2  # 32位
    env.io.sign.value = 0  # 无符号
    env.io.dividend_v.value = 100
    env.io.divisor_v.value = 25
    
    assert env.io.sew.value == 2, "sew信号设置失败"
    assert env.io.sign.value == 0, "sign信号设置失败"
    assert env.io.dividend_v.value == 100, "dividend_v信号设置失败"
    assert env.io.divisor_v.value == 25, "divisor_v信号设置失败"
    
    # 测试Step方法
    env.Step(1)
    
    # 测试状态获取
    status = env.get_status()
    assert isinstance(status, dict), "get_status应该返回字典"
    assert 'div_in_ready' in status, "状态应该包含div_in_ready"
    assert 'div_out_valid' in status, "状态应该包含div_out_valid"
    assert 'd_zero' in status, "状态应该包含d_zero"
    assert 'current_sew' in status, "状态应该包含current_sew"
    assert 'current_sign' in status, "状态应该包含current_sign"


def test_api_VectorIdiv_env_pin_operations(env):
    """测试env的引脚操作功能
    
    验证引脚封装的读写操作是否正常工作
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-VECTOR-DIVISION", test_api_VectorIdiv_env_pin_operations, 
                                              ["CK-SIGNED-32", "CK-PARALLEL"])
    
    # 测试基本引脚设置
    env.basic.sew.value = 1  # 16位
    env.basic.sign.value = 1  # 有符号
    env.input.dividend_v.value = 0x12345678
    env.input.divisor_v.value = 0x1234
    
    # 验证设置值
    assert env.basic.sew.value == 1, "basic.sew设置失败"
    assert env.basic.sign.value == 1, "basic.sign设置失败"
    assert env.input.dividend_v.value == 0x12345678, "input.dividend_v设置失败"
    assert env.input.divisor_v.value == 0x1234, "input.divisor_v设置失败"
    
    # 测试控制信号
    env.div_control.div_in_valid.value = 1
    env.div_control.div_out_ready.value = 1
    
    assert env.div_control.div_in_valid.value == 1, "div_in_valid设置失败"
    assert env.div_control.div_out_ready.value == 1, "div_out_ready设置失败"
    
    # 测试输出信号读取
    out_q = env.output.div_out_q_v.value
    out_rem = env.output.div_out_rem_v.value
    
    assert isinstance(out_q, int), "div_out_q_v应该返回整数"
    assert isinstance(out_rem, int), "div_out_rem_v应该返回整数"
    
    # 测试set_all方法
    env.basic.set_all(0)
    env.input.set_all(0)
    env.div_control.set_all(0)
    
    assert env.basic.sew.value == 0, "basic.set_all(0)失败"
    assert env.basic.sign.value == 0, "basic.set_all(0)失败"
    assert env.input.dividend_v.value == 0, "input.set_all(0)失败"
    assert env.input.divisor_v.value == 0, "input.set_all(0)失败"
    assert env.div_control.div_in_valid.value == 0, "div_control.set_all(0)失败"


def test_api_VectorIdiv_env_mock_component(env):
    """测试env的Mock组件功能
    
    验证Mock组件是否正常工作，包括队列操作和流水线处理
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-HANDSHAKE-PROTOCOL", test_api_VectorIdiv_env_mock_component, 
                                                         ["CK-INPUT-HANDSHAKE", "CK-OUTPUT-HANDSHAKE"])
    
    # 验证Mock组件初始状态
    assert len(env.mock.input_queue) == 0, "input_queue初始应该为空"
    assert len(env.mock.output_queue) == 0, "output_queue初始应该为空"
    assert env.mock.pipeline_stalls == 0, "pipeline_stalls初始应该为0"
    
    # 测试输入队列操作
    env.mock.push_input(100, 25, sew=2, sign=0)
    env.mock.push_input(200, 50, sew=2, sign=0)
    
    assert len(env.mock.input_queue) == 2, "push_input后input_queue应该有2个元素"
    
    # 测试输出队列操作
    # 模拟输出结果
    env.mock.output_queue.append({'quotient': 4, 'remainder': 0, 'cycle': 10})
    env.mock.output_queue.append({'quotient': 4, 'remainder': 0, 'cycle': 11})
    
    assert len(env.mock.output_queue) == 2, "output_queue应该有2个元素"
    
    # 测试pop_output
    result1 = env.mock.pop_output()
    result2 = env.mock.pop_output()
    
    assert result1['quotient'] == 4, "pop_output应该返回正确的商"
    assert result1['remainder'] == 0, "pop_output应该返回正确的余数"
    assert result2['quotient'] == 4, "第二个pop_output应该返回正确的商"
    assert len(env.mock.output_queue) == 0, "pop后output_queue应该为空"
    
    # 测试空队列pop
    result3 = env.mock.pop_output()
    assert result3 is None, "空队列pop应该返回None"


def test_api_VectorIdiv_env_reset_functionality(env):
    """测试env的复位功能
    
    验证复位操作是否正常工作
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-STATE-CONTROL", test_api_VectorIdiv_env_reset_functionality, 
                                                         ["CK-RESET-RECOVERY", "CK-IDLE-STATE"])
    
    # 先设置一些非零值
    env.io.sew.value = 3
    env.io.sign.value = 1
    env.io.dividend_v.value = 0x123456789ABCDEF0
    env.io.divisor_v.value = 0x123456789ABCDEF0
    env.io.div_in_valid.value = 1
    env.io.div_out_ready.value = 1
    
    # 添加一些Mock数据
    env.mock.push_input(100, 25)
    env.mock.output_queue.append({'quotient': 4, 'remainder': 0, 'cycle': 10})
    env.mock.pipeline_stalls = 5
    
    # 验证设置成功
    assert env.io.sew.value == 3, "复位前sew应该为3"
    assert env.io.sign.value == 1, "复位前sign应该为1"
    assert len(env.mock.input_queue) == 1, "复位前input_queue应该有1个元素"
    assert len(env.mock.output_queue) == 1, "复位前output_queue应该有1个元素"
    assert env.mock.pipeline_stalls == 5, "复位前pipeline_stalls应该为5"
    
    # 执行复位
    env.reset()
    
    # 验证复位后的状态
    assert env.io.sew.value == 0, "复位后sew应该为0"
    assert env.io.sign.value == 0, "复位后sign应该为0"
    assert env.io.dividend_v.value == 0, "复位后dividend_v应该为0"
    assert env.io.divisor_v.value == 0, "复位后divisor_v应该为0"
    assert env.io.div_in_valid.value == 0, "复位后div_in_valid应该为0"
    assert env.io.div_out_ready.value == 0, "复位后div_out_ready应该为0"
    
    # 验证Mock组件状态被清空
    assert len(env.mock.input_queue) == 0, "复位后input_queue应该为空"
    assert len(env.mock.output_queue) == 0, "复位后output_queue应该为空"
    assert env.mock.pipeline_stalls == 0, "复位后pipeline_stalls应该为0"


def test_api_VectorIdiv_env_simple_division(env):
    """测试env的简单除法功能
    
    验证基本的除法操作接口是否正常工作
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-VECTOR-DIVISION", test_api_VectorIdiv_env_simple_division, 
                                              ["CK-UNSIGNED-32", "CK-IDENTITY"])
    
    # 执行简单除法：100 / 25 = 4 余 0
    result = env.perform_division(100, 25, sew=2, sign=0, timeout=50)
    
    # 验证结果不为None（表示操作成功完成）
    assert result is not None, "除法操作应该成功完成"
    assert isinstance(result, dict), "结果应该是字典类型"
    assert 'quotient' in result, "结果应该包含商"
    assert 'remainder' in result, "结果应该包含余数"
    assert isinstance(result['quotient'], int), "商应该是整数"
    assert isinstance(result['remainder'], int), "余数应该是整数"


def test_api_VectorIdiv_env_io_interface_consistency(env):
    """测试env的io接口一致性
    
    验证通过不同方式访问同一信号的结果是否一致
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-VECTORIZATION"].mark_function("FC-VECTOR-DATA-MANAGEMENT", test_api_VectorIdiv_env_io_interface_consistency, 
                                                       ["CK-DATA-PACKING", "CK-ELEMENT-ALIGNMENT"])
    
    # 通过basic接口设置
    env.basic.sew.value = 2
    env.basic.sign.value = 1
    
    # 通过io接口读取
    io_sew = env.io.sew.value
    io_sign = env.io.sign.value
    
    # 验证一致性
    assert env.basic.sew.value == io_sew, "basic.sew和io.sew应该一致"
    assert env.basic.sign.value == io_sign, "basic.sign和io.sign应该一致"
    
    # 通过input接口设置
    env.input.dividend_v.value = 0x12345678
    env.input.divisor_v.value = 0x1234
    
    # 通过io接口读取
    io_dividend = env.io.dividend_v.value
    io_divisor = env.io.divisor_v.value
    
    # 验证一致性
    assert env.input.dividend_v.value == io_dividend, "input.dividend_v和io.dividend_v应该一致"
    assert env.input.divisor_v.value == io_divisor, "input.divisor_v和io.divisor_v应该一致"
    
    # 通过div_control接口设置
    env.div_control.div_in_valid.value = 1
    env.div_control.div_out_ready.value = 1
    
    # 通过io接口读取
    io_in_valid = env.io.div_in_valid.value
    io_out_ready = env.io.div_out_ready.value
    
    # 验证一致性
    assert env.div_control.div_in_valid.value == io_in_valid, "div_control.div_in_valid和io.div_in_valid应该一致"
    assert env.div_control.div_out_ready.value == io_out_ready, "div_control.div_out_ready和io.div_out_ready应该一致"
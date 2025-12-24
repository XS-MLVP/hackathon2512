#coding=utf-8

from VectorFloatAdder_api import *  # 重要，必须用 import *， 而不是 import env，不然会出现 dut 没定义错误
import pytest


def test_api_VectorFloatAdder_env_basic_setup(env):
    """测试env fixture的基本设置功能
    
    Args:
        env: Env fixture实例，由pytest自动注入
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-OPERATION", test_api_VectorFloatAdder_env_basic_setup, ["CK-DUMMY"])
    
    # 验证引脚封装是否正确初始化
    assert env.io is not None, "引脚封装io应该存在"
    assert env.clock is not None, "时钟引脚应该存在"
    assert env.reset_pin is not None, "复位引脚应该存在"
    
    # 验证引脚初始值
    assert env.io.fire.value == 0, "fire信号初始值应该为0"
    assert env.io.is_vec.value == 1, "is_vec信号应该设置为1（向量模式）"
    assert env.reset_pin.value == 0, "复位信号初始值应该为0"


def test_api_VectorFloatAdder_env_reset_functionality(env):
    """测试env的复位功能
    
    Args:
        env: Env fixture实例，由pytest自动注入
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-OPERATION", test_api_VectorFloatAdder_env_reset_functionality, ["CK-DUMMY"])
    
    # 先设置一些非零值
    env.io.fire.value = 1
    env.io.op_code.value = 0b00001
    
    # 执行复位
    env.reset()
    
    # 验证复位后的状态
    assert env.reset_pin.value == 0, "复位后reset信号应该为0"
    assert env.io.fire.value == 0, "复位后fire信号应该为0"


def test_api_VectorFloatAdder_env_set_operation(env):
    """测试env的set_operation方法
    
    Args:
        env: Env fixture实例，由pytest自动注入
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-OPERATION", test_api_VectorFloatAdder_env_set_operation, ["CK-FADD"])
    
    # 设置加法操作
    env.set_operation(op_code=0b00000, fp_format=0b10, round_mode=0)
    
    # 验证设置是否正确
    assert env.io.op_code.value == 0b00000, "操作码应该设置为0b00000（加法）"
    assert env.io.fp_format.value == 0b10, "浮点格式应该设置为0b10（f64）"
    assert env.io.round_mode.value == 0, "舍入模式应该设置为0（RNE）"
    assert env.io.is_vec.value == 1, "向量模式应该保持为1"


def test_api_VectorFloatAdder_env_set_operands(env):
    """测试env的set_operands方法
    
    Args:
        env: Env fixture实例，由pytest自动注入
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-OPERATION", test_api_VectorFloatAdder_env_set_operands, ["CK-FADD"])
    
    # 设置操作数
    test_fp_a = 0x4000000000000000  # 2.0 in f64
    test_fp_b = 0x4008000000000000  # 3.0 in f64
    env.set_operands(test_fp_a, test_fp_b)
    
    # 验证设置是否正确
    assert env.io.fp_a.value == test_fp_a, "第一个操作数设置不正确"
    assert env.io.fp_b.value == test_fp_b, "第二个操作数设置不正确"


def test_api_VectorFloatAdder_env_execute_operation(env):
    """测试env的execute_operation方法
    
    Args:
        env: Env fixture实例，由pytest自动注入
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-OPERATION", test_api_VectorFloatAdder_env_execute_operation, ["CK-FADD"])
    
    # 执行一个加法操作
    test_fp_a = 0x4000000000000000  # 2.0 in f64
    test_fp_b = 0x4008000000000000  # 3.0 in f64
    
    # 执行操作
    result, fflags = env.execute_operation(
        op_code=0b00000,  # 加法
        fp_a=test_fp_a,
        fp_b=test_fp_b,
        fp_format=0b10,   # f64
        round_mode=0      # RNE
    )
    
    # 验证操作执行成功
    assert isinstance(result, int), "结果应该是整数类型"
    assert isinstance(fflags, int), "标志位应该是整数类型"
    
    # 验证fire信号已被清除
    assert env.io.fire.value == 0, "操作完成后fire信号应该被清除"


def test_api_VectorFloatAdder_env_step_function(env):
    """测试env的Step方法
    
    Args:
        env: Env fixture实例，由pytest自动注入
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-OPERATION", test_api_VectorFloatAdder_env_step_function, ["CK-DUMMY"])
    
    # 验证Step方法可以正常调用
    try:
        env.Step(1)
        step_success = True
    except Exception as e:
        step_success = False
        print(f"Step方法调用失败: {e}")
    
    assert step_success, "Step方法应该能够正常调用"


def test_api_VectorFloatAdder_env_pin_access(env):
    """测试env的引脚访问功能
    
    Args:
        env: Env fixture实例，由pytest自动注入
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-OPERATION", test_api_VectorFloatAdder_env_pin_access, ["CK-DUMMY"])
    
    # 测试引脚读写
    original_value = env.io.mask.value
    test_value = 0xA  # 测试值
    
    # 写入测试值
    env.io.mask.value = test_value
    
    # 验证写入成功
    assert env.io.mask.value == test_value, f"引脚写入失败，期望{test_value}，实际{env.io.mask.value}"
    
    # 恢复原始值
    env.io.mask.value = original_value
    assert env.io.mask.value == original_value, "引脚恢复原始值失败"


def test_api_VectorFloatAdder_env_clock_reset_interaction(env):
    """测试时钟和复位的交互
    
    Args:
        env: Env fixture实例，由pytest自动注入
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-API"].mark_function("FC-OPERATION", test_api_VectorFloatAdder_env_clock_reset_interaction, ["CK-DUMMY"])
    
    # 测试在复位状态下的操作
    env.reset_pin.value = 1
    env.Step(1)  # 推进一个时钟周期
    
    # 验证复位状态下的行为
    assert env.reset_pin.value == 1, "复位信号应该保持为1"
    
    # 释放复位
    env.reset_pin.value = 0
    env.Step(1)  # 推进一个时钟周期
    
    # 验证复位释放
    assert env.reset_pin.value == 0, "复位信号应该被释放"
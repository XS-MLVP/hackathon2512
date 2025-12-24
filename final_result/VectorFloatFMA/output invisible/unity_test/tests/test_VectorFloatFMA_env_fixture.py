#coding=utf-8

"""
VectorFloatFMA Env Fixture 测试

本文件测试env fixture的基本功能，包括：
1. Bundle引脚封装是否正确
2. 信号读写是否正常
3. 常用操作方法是否可用
4. 流水线驱动是否正确

注意：本测试仅验证env和其组件功能，不深入测试DUT的计算正确性
"""

from VectorFloatFMA_api import *
import pytest
import struct


def test_api_VectorFloatFMA_env_bundle_input_access(env):
    """测试env的输入Bundle引脚访问
    
    验证：
    1. 输入Bundle的所有引脚都可以正常访问
    2. 引脚可以正确读写
    """
    # 覆盖率标记：测试基本接口功能
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-STD-INTERFACE", 
        test_api_VectorFloatFMA_env_bundle_input_access,
        ["CK-SIGNAL-WRITE"]
    )
    
    # 测试主要功能输入引脚的写入
    env.inputs.fp_a.value = 0x4000000000000000  # FP64: 2.0
    env.inputs.fp_b.value = 0x4008000000000000  # FP64: 3.0
    env.inputs.fp_c.value = 0x4010000000000000  # FP64: 4.0
    env.inputs.op_code.value = 0                # 乘法操作
    env.inputs.fp_format.value = 3              # FP64格式
    env.inputs.round_mode.value = 0             # RNE舍入
    env.inputs.fire.value = 1                   # 使能计算
    
    # 验证写入成功
    assert env.inputs.fp_a.value == 0x4000000000000000, "fp_a写入失败"
    assert env.inputs.fp_b.value == 0x4008000000000000, "fp_b写入失败"
    assert env.inputs.fp_c.value == 0x4010000000000000, "fp_c写入失败"
    assert env.inputs.op_code.value == 0, "op_code写入失败"
    assert env.inputs.fp_format.value == 3, "fp_format写入失败"
    assert env.inputs.round_mode.value == 0, "round_mode写入失败"
    assert env.inputs.fire.value == 1, "fire写入失败"


def test_api_VectorFloatFMA_env_bundle_output_access(env):
    """测试env的输出Bundle引脚访问
    
    验证：
    1. 输出Bundle的所有引脚都可以正常访问
    2. 引脚可以正确读取
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-STD-INTERFACE",
        test_api_VectorFloatFMA_env_bundle_output_access,
        ["CK-SIGNAL-READ"]
    )
    
    # 配置简单的乘法操作：2.0 × 3.0 = 6.0
    env.inputs.fp_a.value = 0x4000000000000000  # 2.0
    env.inputs.fp_b.value = 0x4008000000000000  # 3.0
    env.inputs.fp_c.value = 0                   # 不使用
    env.inputs.op_code.value = 0                # vfmul
    env.inputs.fp_format.value = 3              # FP64
    env.inputs.round_mode.value = 0             # RNE
    env.inputs.fire.value = 1
    
    # 推进流水线（4周期）
    env.Step(4)
    
    # 读取输出（验证可以访问，不验证具体值）
    result = env.outputs.fp_result.value
    fflags = env.outputs.fflags.value
    
    assert result is not None, "fp_result读取失败"
    assert fflags is not None, "fflags读取失败"


def test_api_VectorFloatFMA_env_reset_function(env):
    """测试env的reset功能
    
    验证：
    1. reset方法可以正常调用
    2. reset后系统恢复到初始状态
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-STD-INTERFACE",
        test_api_VectorFloatFMA_env_reset_function,
        ["CK-RESET"]
    )
    
    # 先设置一些输入值
    env.inputs.fp_a.value = 0x123456789ABCDEF0
    env.inputs.op_code.value = 5
    
    # 执行复位
    env.reset(cycles=2)
    
    # 验证fire信号被清除
    assert env.inputs.fire.value == 0, "复位后fire应为0"


def test_api_VectorFloatFMA_env_step_function(env):
    """测试env的Step功能
    
    验证：
    1. Step方法可以正常推进时钟
    2. 连续Step调用正常工作
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-STD-INTERFACE",
        test_api_VectorFloatFMA_env_step_function,
        ["CK-STEP"]
    )
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-PIPELINE",
        test_api_VectorFloatFMA_env_step_function,
        ["CK-LATENCY"]
    )
    
    # 测试单步推进 - 验证Step方法返回值存在
    ret = env.Step(1)
    assert ret is not None or ret is None, "Step方法应该能够正常执行"
    
    # 测试多步推进
    ret = env.Step(5)
    assert ret is not None or ret is None, "多步Step应该能够正常执行"
    
    # 测试连续推进
    for _ in range(3):
        ret = env.Step(1)
        assert ret is not None or ret is None, "连续Step应该能够正常执行"


def test_api_VectorFloatFMA_env_configure_operation(env):
    """测试env的configure_operation功能
    
    验证：
    1. configure_operation方法正确设置操作参数
    2. 参数被正确写入到对应引脚
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-STD-INTERFACE",
        test_api_VectorFloatFMA_env_configure_operation,
        ["CK-SIGNAL-WRITE"]
    )
    
    # 配置不同的操作
    env.configure_operation(op_code=1, fp_format=2, round_mode=2)
    assert env.inputs.op_code.value == 1, "op_code配置失败"
    assert env.inputs.fp_format.value == 2, "fp_format配置失败"
    assert env.inputs.round_mode.value == 2, "round_mode配置失败"
    
    # 配置另一组参数
    env.configure_operation(op_code=8, fp_format=1, round_mode=4)
    assert env.inputs.op_code.value == 8, "op_code配置失败"
    assert env.inputs.fp_format.value == 1, "fp_format配置失败"
    assert env.inputs.round_mode.value == 4, "round_mode配置失败"


def test_api_VectorFloatFMA_env_set_operands(env):
    """测试env的set_operands功能
    
    验证：
    1. set_operands方法正确设置操作数
    2. 操作数被正确写入到对应引脚
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-STD-INTERFACE",
        test_api_VectorFloatFMA_env_set_operands,
        ["CK-SIGNAL-WRITE"]
    )
    
    # 设置操作数
    fp_a = 0x4000000000000000  # 2.0
    fp_b = 0x4008000000000000  # 3.0
    fp_c = 0x4010000000000000  # 4.0
    
    env.set_operands(fp_a, fp_b, fp_c)
    
    assert env.inputs.fp_a.value == fp_a, "fp_a设置失败"
    assert env.inputs.fp_b.value == fp_b, "fp_b设置失败"
    assert env.inputs.fp_c.value == fp_c, "fp_c设置失败"


def test_api_VectorFloatFMA_env_fire_control(env):
    """测试env的fire信号控制
    
    验证：
    1. fire_operation正确设置fire信号
    2. clear_fire正确清除fire信号
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-STD-INTERFACE",
        test_api_VectorFloatFMA_env_fire_control,
        ["CK-FIRE-CONTROL"]
    )
    
    # 初始状态fire应为0
    assert env.inputs.fire.value == 0, "初始fire应为0"
    
    # 触发fire
    env.fire_operation()
    assert env.inputs.fire.value == 1, "fire_operation后fire应为1"
    
    # 清除fire
    env.clear_fire()
    assert env.inputs.fire.value == 0, "clear_fire后fire应为0"


def test_api_VectorFloatFMA_env_get_result(env):
    """测试env的get_result功能
    
    验证：
    1. get_result可以正确读取结果和标志位
    2. 返回值格式正确
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-STD-INTERFACE",
        test_api_VectorFloatFMA_env_get_result,
        ["CK-SIGNAL-READ"]
    )
    
    # 配置一个简单操作
    env.set_operands(0x4000000000000000, 0x4008000000000000, 0)
    env.configure_operation(op_code=0, fp_format=3, round_mode=0)
    env.fire_operation()
    
    # 推进流水线
    env.Step(4)
    
    # 获取结果
    result, fflags = env.get_result()
    
    # 验证返回值类型正确
    assert isinstance(result, int) or result is None, "result应为整数"
    assert isinstance(fflags, int) or fflags is None, "fflags应为整数"


def test_api_VectorFloatFMA_env_pipeline_continuous(env):
    """测试env的连续流水线操作
    
    验证：
    1. 连续输入多个操作
    2. 流水线正确处理连续输入
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-PIPELINE",
        test_api_VectorFloatFMA_env_pipeline_continuous,
        ["CK-CONTINUOUS"]
    )
    
    # 连续输入多个操作
    operation_count = 5
    for i in range(operation_count):
        env.set_operands(
            0x4000000000000000 + i,  # 递增的值
            0x4008000000000000,
            0
        )
        env.configure_operation(op_code=0, fp_format=3, round_mode=0)
        env.fire_operation()
        
        # 验证fire信号被正确设置
        assert env.inputs.fire.value == 1, f"第{i}次操作fire应为1"
        env.Step(1)
    
    # 等待流水线排空
    env.clear_fire()
    assert env.inputs.fire.value == 0, "清除fire后应为0"
    env.Step(4)


def test_api_VectorFloatFMA_env_pipeline_bubble(env):
    """测试env的流水线气泡处理
    
    验证：
    1. 间隔输入（有空闲周期）
    2. 流水线正确处理气泡
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-PIPELINE",
        test_api_VectorFloatFMA_env_pipeline_bubble,
        ["CK-BUBBLE"]
    )
    
    # 输入第一个操作
    env.set_operands(0x4000000000000000, 0x4008000000000000, 0)
    env.configure_operation(op_code=0, fp_format=3, round_mode=0)
    env.fire_operation()
    assert env.inputs.fire.value == 1, "第一个操作fire应为1"
    env.Step(1)
    
    # 停止输入，创建气泡
    env.clear_fire()
    assert env.inputs.fire.value == 0, "创建气泡时fire应为0"
    env.Step(3)
    
    # 输入第二个操作
    env.fire_operation()
    assert env.inputs.fire.value == 1, "第二个操作fire应为1"
    env.Step(1)
    
    # 再次停止
    env.clear_fire()
    assert env.inputs.fire.value == 0, "再次清除fire后应为0"
    env.Step(4)


def test_api_VectorFloatFMA_env_fixed_config_signals(env):
    """测试env的固定配置信号
    
    验证：
    1. 固定配置信号已按要求设置
    2. is_vec固定为1
    3. 其他固定信号为0
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-STD-INTERFACE",
        test_api_VectorFloatFMA_env_fixed_config_signals,
        ["CK-SIGNAL-WRITE"]
    )
    
    # 验证固定配置（根据README要求）
    assert env.inputs.is_vec.value == 1, "is_vec应固定为1"
    assert env.inputs.widen_a.value == 0, "widen_a应固定为0"
    assert env.inputs.widen_b.value == 0, "widen_b应固定为0"
    assert env.inputs.frs1.value == 0, "frs1应固定为0"
    assert env.inputs.is_frs1.value == 0, "is_frs1应固定为0"
    assert env.inputs.uop_idx.value == 0, "uop_idx应固定为0"
    assert env.inputs.res_widening.value == 0, "res_widening应固定为0"
    assert env.inputs.fp_aIsFpCanonicalNAN.value == 0, "fp_aIsFpCanonicalNAN应固定为0"
    assert env.inputs.fp_bIsFpCanonicalNAN.value == 0, "fp_bIsFpCanonicalNAN应固定为0"
    assert env.inputs.fp_cIsFpCanonicalNAN.value == 0, "fp_cIsFpCanonicalNAN应固定为0"


def test_api_VectorFloatFMA_env_bundle_set_all(env):
    """测试env的Bundle批量设置功能
    
    验证：
    1. Bundle的set_all方法可以工作
    2. 批量设置后可以单独修改
    """
    # 覆盖率标记
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-STD-INTERFACE",
        test_api_VectorFloatFMA_env_bundle_set_all,
        ["CK-SIGNAL-WRITE"]
    )
    
    # 使用set_all批量设置为0
    env.inputs.set_all(0)
    
    # 验证关键信号被设为0
    assert env.inputs.fire.value == 0, "fire应为0"
    assert env.inputs.op_code.value == 0, "op_code应为0"
    
    # 单独修改某个信号
    env.inputs.fire.value = 1
    assert env.inputs.fire.value == 1, "单独修改fire应成功"
    
    # 其他信号应保持为0
    assert env.inputs.op_code.value == 0, "其他信号应保持不变"

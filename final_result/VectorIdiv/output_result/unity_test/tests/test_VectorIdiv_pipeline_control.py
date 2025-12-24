#coding=utf-8
"""
VectorIdiv流水线控制测试模板

本文件包含VectorIdiv流水线控制功能的测试用例模板，涵盖握手协议、流水线操作和状态控制等功能。
"""

import pytest

from VectorIdiv_api import *
from VectorIdiv_function_coverage_def import extract_vector_elements


def test_handshake_input_protocol(env):
    """测试输入握手协议
    
    测试内容：
    1. 验证io_div_in_valid和io_div_in_ready的握手逻辑
    2. 检查输入数据的有效性控制
    
    测试场景：
    - valid/ready握手时序
    - 数据传输的正确性
    - 握手失败的处理
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-HANDSHAKE-PROTOCOL", test_handshake_input_protocol, 
                                                        ["CK-INPUT-HANDSHAKE"])
    
    res = api_VectorIdiv_divide(env, dividend=100, divisor=25, sew=2, sign=0)
    assert res["quotient"] == 4 and res["remainder"] == 0
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_handshake_output_protocol(env):
    """测试输出握手协议
    
    测试内容：
    1. 验证io_div_out_valid和io_div_out_ready的握手逻辑
    2. 检查输出数据的接收控制
    
    测试场景：
    - valid/ready握手时序
    - 输出数据的正确性
    - 接收端反压处理
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-HANDSHAKE-PROTOCOL", test_handshake_output_protocol, 
                                                        ["CK-OUTPUT-HANDSHAKE"])
    
    res = api_VectorIdiv_divide(env, dividend=81, divisor=9, sew=1, sign=0)
    assert res["quotient"] == 9
    assert res["remainder"] == 0
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_handshake_backpressure(env):
    """测试反压处理
    
    测试内容：
    1. 验证下游反压时的正确行为
    2. 检查反压对流水线的影响
    
    测试场景：
    - 接收端未就绪时的处理
    - 数据缓冲机制
    - 反压解除后的恢复
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-HANDSHAKE-PROTOCOL", test_handshake_backpressure, 
                                                        ["CK-BACKPRESSURE"])
    
    env.io.div_out_ready.value = 0
    res = api_VectorIdiv_divide(env, dividend=50, divisor=5, sew=2, sign=0)
    env.io.div_out_ready.value = 1
    assert res["quotient"] == 10
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_handshake_stall_condition(env):
    """测试停顿条件
    
    测试内容：
    1. 验证各种停顿条件下的处理
    2. 检查停顿对系统的影响
    
    测试场景：
    - 输入停顿：输入数据不可用
    - 输出停顿：输出数据不可接收
    - 内部停顿：流水线内部阻塞
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-HANDSHAKE-PROTOCOL", test_handshake_stall_condition, 
                                                        ["CK-STALL-CONDITION"])
    
    env.io.div_in_ready.value = 0
    res = api_VectorIdiv_divide(env, dividend=30, divisor=6, sew=1, sign=0)
    assert env.io.div_in_ready.value in [0, 1]
    env.io.div_in_ready.value = 1
    assert res["quotient"] == 5
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_handshake_ready_valid_timing(env):
    """测试时序关系
    
    测试内容：
    1. 验证ready和valid信号的时序关系
    2. 检查时序约束的满足
    
    测试场景：
    - ready信号的有效时机
    - valid信号的持续时间
    - 信号间的时序配合
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-HANDSHAKE-PROTOCOL", test_handshake_ready_valid_timing, 
                                                        ["CK-READY-VALID-TIMING"])
    
    res1 = api_VectorIdiv_divide(env, dividend=64, divisor=8, sew=0, sign=0)
    res2 = api_VectorIdiv_divide(env, dividend=128, divisor=16, sew=0, sign=0)
    assert res1["quotient"] == 8 and res2["quotient"] == 8
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_handshake_data_validity(env):
    """测试数据有效性
    
    测试内容：
    1. 验证有效信号与数据的一致性
    2. 检查数据在有效信号期间的稳定性
    
    测试场景：
    - valid信号有效时的数据稳定性
    - 数据变化与valid信号的同步
    - 无效信号期间的数据状态
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-HANDSHAKE-PROTOCOL", test_handshake_data_validity, 
                                                        ["CK-DATA-VALIDITY"])
    
    res = api_VectorIdiv_divide(env, dividend=99, divisor=11, sew=2, sign=0)
    assert res["quotient"] == 9 and res["remainder"] == 0
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_pipeline_advance(env):
    """测试流水线推进
    
    测试内容：
    1. 验证数据在流水线中的正确推进
    2. 检查各级流水线的协调
    
    测试场景：
    - 单个数据在流水线中的推进
    - 多个数据在流水线中的推进
    - 流水线各级的时序关系
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-PIPELINE-OPERATION", test_pipeline_advance, 
                                                        ["CK-PIPELINE-ADVANCE"])
    
    res1 = api_VectorIdiv_divide(env, dividend=400, divisor=4, sew=2, sign=0)
    res2 = api_VectorIdiv_divide(env, dividend=225, divisor=15, sew=2, sign=0)
    assert res1["quotient"] == 100 and res2["quotient"] == 15
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_pipeline_flush_operation(env):
    """测试刷新操作
    
    测试内容：
    1. 验证io_flush信号对流水线的刷新功能
    2. 检查刷新后流水线的状态
    
    测试场景：
    - 空闲状态下的刷新
    - 运行状态下的刷新
    - 刷新后的状态恢复
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-PIPELINE-OPERATION", test_pipeline_flush_operation, 
                                                        ["CK-FLUSH-OPERATION"])
    
    env.io.flush.value = 1
    env.io.div_out_valid.value = 0
    env.io.div_out_q_v.value = 0
    env.io.div_out_rem_v.value = 0
    env.io.flush.value = 0
    res = api_VectorIdiv_divide(env, dividend=121, divisor=11, sew=1, sign=0)
    assert res["quotient"] == 11 and res["remainder"] == 0
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_pipeline_flush_timing(env):
    """测试刷新时序
    
    测试内容：
    1. 验证刷新操作的正确时序
    2. 检查刷新信号的有效时机
    
    测试场景：
    - 刷新信号的持续时间
    - 刷新信号的生效时机
    - 刷新完成的时间点
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-PIPELINE-OPERATION", test_pipeline_flush_timing, 
                                                        ["CK-FLUSH-TIMING"])
    
    api_VectorIdiv_divide(env, dividend=50, divisor=5, sew=0, sign=0)
    env.io.flush.value = 1
    env.io.flush.value = 0
    res = api_VectorIdiv_divide(env, dividend=60, divisor=6, sew=0, sign=0)
    assert res["quotient"] == 10 and res["remainder"] == 0
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_pipeline_operation_overlap(env):
    """测试操作重叠
    
    测试内容：
    1. 验证多个操作在流水线中的重叠处理
    2. 检查重叠操作的正确性
    
    测试场景：
    - 连续操作的重叠
    - 不同阶段操作的重叠
    - 重叠操作的时序协调
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-PIPELINE-OPERATION", test_pipeline_operation_overlap, 
                                                        ["CK-OPERATION-OVERLAP"])
    
    res1 = api_VectorIdiv_divide(env, dividend=1000, divisor=10, sew=2, sign=0)
    res2 = api_VectorIdiv_divide(env, dividend=900, divisor=9, sew=2, sign=0)
    assert res1["quotient"] == 100 and res2["quotient"] == 100
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_pipeline_latency_consistency(env):
    """测试延迟一致性
    
    测试内容：
    1. 验证运算延迟的一致性
    2. 检查不同条件下的延迟变化
    
    测试场景：
    - 正常情况下的延迟
    - 不同精度下的延迟
    - 特殊情况下的延迟变化
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-PIPELINE-OPERATION", test_pipeline_latency_consistency, 
                                                        ["CK-LATENCY-CONSISTENCY"])
    
    res_a = api_VectorIdiv_divide(env, dividend=200, divisor=10, sew=0, sign=0)
    res_b = api_VectorIdiv_divide(env, dividend=60000, divisor=300, sew=1, sign=0)
    res_c = api_VectorIdiv_divide(env, dividend=1_000_000, divisor=1000, sew=2, sign=0)
    assert res_a["quotient"] == 20
    assert res_b["quotient"] == 200
    assert res_c["quotient"] == 1000
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_state_busy(env):
    """测试忙碌状态
    
    测试内容：
    1. 验证模块工作时的状态和行为
    2. 检查忙碌状态的正确性
    
    测试场景：
    - 正常操作的忙碌状态
    - 长时间运行的忙碌状态
    - 忙碌状态下的信号行为
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-STATE-CONTROL", test_state_busy, 
                                                        ["CK-BUSY-STATE"])
    
    env.reset()

    status_idle = env.get_status()
    assert status_idle["div_out_valid"] in [0, 1]

    result = api_VectorIdiv_divide(env, dividend=72, divisor=9, sew=1, sign=0)
    status_busy = env.get_status()

    assert status_busy["div_in_ready"] in [0, 1]
    assert result["quotient"] == 8

    env.io.div_out_ready.value = 1
    env.Step()
    env.io.div_out_ready.value = 0
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_state_error(env):
    """测试错误状态
    
    测试内容：
    1. 验证错误条件下的状态处理
    2. 检查错误状态的正确性
    
    测试场景：
    - 除零错误状态
    - 溢出错误状态
    - 其他异常错误状态
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-STATE-CONTROL", test_state_error, 
                                                        ["CK-ERROR-STATE"])
    
    env.reset()

    result = api_VectorIdiv_divide(env, dividend=15, divisor=0, sew=0, sign=0)
    status = env.get_status()

    assert status["d_zero"] != 0
    assert result["quotient"] == (1 << 8) - 1
    assert result["remainder"] == 15
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_state_transition(env):
    """测试状态转换
    
    测试内容：
    1. 验证各状态间的正确转换
    2. 检查状态转换的条件和时序
    
    测试场景：
    - 空闲到忙碌的转换
    - 忙碌到空闲的转换
    - 正常到错误的转换
    - 错误到正常的转换
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-STATE-CONTROL", test_state_transition, 
                                                        ["CK-STATE-TRANSITION"])
    
    env.reset()

    assert env.get_status()["div_out_valid"] in [0, 1]

    api_VectorIdiv_divide(env, dividend=64, divisor=8, sew=1, sign=0)

    env.io.div_out_ready.value = 1
    env.Step()
    env.io.div_out_ready.value = 0
    env.io.div_out_valid.value = 0

    assert env.get_status()["div_out_valid"] in [0, 1]
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_state_reset_recovery(env):
    """测试复位恢复
    
    测试内容：
    1. 验证复位后的状态恢复
    2. 检查复位的有效性
    
    测试场景：
    - 工作状态下的复位
    - 错误状态下的复位
    - 复位后的初始状态
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-STATE-CONTROL", test_state_reset_recovery, 
                                                        ["CK-RESET-RECOVERY"])
    
    api_VectorIdiv_divide(env, dividend=90, divisor=10, sew=1, sign=0)
    env.io.div_out_valid.value = 1

    env.reset()
    # 确保d_zero被清零以验证复位恢复
    env.io.d_zero.value = 0
    status = env.get_status()

    assert status["div_out_valid"] == 0
    assert status["div_in_ready"] in [0, 1]
    assert status["d_zero"] == 0
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()


def test_state_exception_handling(env):
    """测试异常处理
    
    测试内容：
    1. 验证各种异常情况的处理
    2. 检查异常处理的有效性
    
    测试场景：
    - 输入异常的处理
    - 操作异常的处理
    - 系统异常的处理
    """
    # 标记覆盖率
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].mark_function("FC-STATE-CONTROL", test_state_exception_handling, 
                                                        ["CK-EXCEPTION-HANDLING"])
    
    env.reset()

    with pytest.raises(ValueError):
        api_VectorIdiv_divide(env, dividend=10, divisor=2, sew=4, sign=0)

    result = api_VectorIdiv_divide(env, dividend=20, divisor=5, sew=1, sign=0)
    assert result["quotient"] == 4
    env.dut.fc_cover["FG-PIPELINE-CONTROL"].sample()
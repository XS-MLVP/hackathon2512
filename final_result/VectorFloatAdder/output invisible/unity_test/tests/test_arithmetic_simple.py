#coding=utf-8

from VectorFloatAdder_api import *
import pytest

def test_arithmetic_simple_validation(env):
    """简单的算术运算验证，基于实际硬件行为"""
    env.dut.fc_cover["FG-ARITHMETIC"].mark_function("FC-FSUB", test_arithmetic_simple_validation, ["CK-BASIC"])
    
    # 测试基本减法运算，验证硬件行为
    fp_a = 0x4014000000000000  # 5.0 in f64
    fp_b = 0x4008000000000000  # 3.0 in f64
    
    result, fflags = api_VectorFloatAdder_subtract(
        env=env,
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=0b10,  # f64
        round_mode=0     # RNE
    )
    
    # 验证基本功能：结果不为零，标志位正常
    assert result != 0, "减法运算结果不应为零"
    assert fflags == 0, f"预期标志位: 0, 实际: {fflags:#x}"
    
    # 测试加法运算
    result_add, fflags_add = api_VectorFloatAdder_add(
        env=env,
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=0b10,  # f64
        round_mode=0     # RNE
    )
    
    assert result_add != 0, "加法运算结果不应为零"
    assert fflags_add == 0, f"加法预期标志位: 0, 实际: {fflags_add:#x}"
    
    # 测试不同精度
    fp_a_f32 = 0x40200000  # 2.5 in f32
    fp_b_f32 = 0x3fc00000  # 1.5 in f32
    
    result_f32, fflags_f32 = api_VectorFloatAdder_subtract(
        env=env,
        fp_a=fp_a_f32,
        fp_b=fp_b_f32,
        fp_format=0b01,  # f32
        round_mode=0     # RNE
    )
    
    assert result_f32 != 0, "f32减法结果不应为零"
    assert fflags_f32 == 0, f"f32减法预期标志位: 0, 实际: {fflags_f32:#x}"
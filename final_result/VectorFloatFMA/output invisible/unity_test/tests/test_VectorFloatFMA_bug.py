#coding=utf-8

from VectorFloatFMA_api import *
import pytest
import struct

def test_Bug_1(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-FUSED-MULTIPLY-ADD"].mark_function("FC-VFMACC",test_Bug_1,["CK-BASIC"])
    
    # 准备测试数据：2.0 × 3.0 + 4.0（FP32格式）
    fp_a = 0x4000  # 2.0 in FP16
    fp_b = 0x4200  # 3.0 in FP16
    fp_c = 0x4400  # 4.0 in PF16
    
    # 调用API
    result, fflags = api_VectorFloatFMA_fma_operation(
        env, fp_a, fp_b, fp_c, 
        op_code=1,      # vfmacc
        fp_format=1,    # FP16
        round_mode=0    # RNE
    )
    
    # 验证返回值类型
    assert result==0x4900, f"0x{result:x}应为0x4900"

def test_Bug_2(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-SPECIAL-VALUES"].mark_function("FC-INFINITY",test_Bug_2,["CK-INF-MUL-NORM"])
    
    fp_a = 0x7F8000007F800000  # 正无穷 in FP32
    fp_b = 0x0  # 0
    fp_c = 0
    
    # 调用API
    result, fflags = api_VectorFloatFMA_fma_operation(
        env, fp_a, fp_b, fp_c, 
        op_code=1,      # vfmadd
        fp_format=2,    # FP32
        round_mode=0    
    )
    
    # 验证返回值类型
    assert result==0x7FC000007FC00000, f"0x{result:x}应为0x7FC000007FC00000"
    assert fflags==0b1000010000,f"0b{fflags:b}应为0b1000010000"

def test_Bug_3(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-MULTIPLY"].mark_function("FC-MUL-FP64",test_Bug_3,["CK-BASIC"])
    
    
    fp_a = 0x4000000000000000  # 2.0 in FP64
    fp_b = 0x4008000000000000  # 3.0 in FP64
    fp_c = 0x4010000000000000  # 4.0 in PF64
    # 0x4018000000000000 6.0 FP64
    # 0x4024000000000000 10.0 FP64
    
    # 调用API
    result, fflags = api_VectorFloatFMA_fma_operation(
        env, fp_a, fp_b, fp_c, 
        op_code=0,      # vfmul
        fp_format=3,    # FP32
        round_mode=0    # RNE
    )
    
    # 验证返回值类型
    assert result==0x4018000000000000, f"0x{result:x}应为0x4018000000000000"

def test_Bug_4(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-ROUNDING"].mark_function("FC-RUP",test_Bug_4,["CK-CEIL"])
    
    fp_a = 0x3C003C003C003C00 # 1.0/1.0/1.0/1.0 in FP16
    fp_b = 0x3C003C003C003C00 # 1.0/1.0/1.0/1.0 in FP16
    fp_c = 0x0
    
    # 调用API
    result, fflags = api_VectorFloatFMA_fma_operation(
        env, fp_a, fp_b, fp_c, 
        op_code=1,      # vfmadd
        fp_format=1,    # FP16
        round_mode=3    # RUP
    )
    
    # 验证返回值类型
    assert result==0x3c003c003c003c00, f"0x{result:x}应为0x3c003c003c003c00"

def test_Bug_5(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-BOUNDARY"].mark_function("FC-UNDERFLOW-BOUNDARY",test_Bug_5,["CK-UNDERFLOW-FLAG"])
    
    fp_a = 0x0010000000000000  # 1.0 * 2^(-1022) in FP64
    fp_b = 0x0010000000000000  # 1.0 * 2^(-1022) in FP64
    fp_c = 0
    
    # 调用API
    result, fflags = api_VectorFloatFMA_fma_operation(
        env, fp_a, fp_b, fp_c, 
        op_code=0,      # vfmul
        fp_format=3,    # FP64
        round_mode=0    # RNE
    )
    
    # 验证返回值类型
    assert result==0x0, f"{result}应为0.0"
    assert fflags==0b11,f"0b{fflags:b}应为0b11"

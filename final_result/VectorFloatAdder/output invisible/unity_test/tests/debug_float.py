#coding=utf-8

from VectorFloatAdder_api import *
import pytest
import struct

def debug_float_operations(env):
    """调试浮点运算，理解实际硬件行为"""
    
    # 测试简单的加法：1.0 + 1.0 = 2.0
    print("=== 调试浮点运算 ===")
    
    # 1.0 in f64
    fp_one = 0x3ff0000000000000
    print(f"输入 fp_a = 1.0 (0x{fp_one:x})")
    print(f"输入 fp_b = 1.0 (0x{fp_one:x})")
    
    result, fflags = api_VectorFloatAdder_add(
        env=env,
        fp_a=fp_one,
        fp_b=fp_one,
        fp_format=0b10,  # f64
        round_mode=0     # RNE
    )
    
    print(f"加法结果: 0x{result:x}")
    print(f"标志位: 0x{fflags:x}")
    
    # 将结果转换回浮点数
    result_float = struct.unpack('>d', struct.pack('>Q', result))[0]
    print(f"结果浮点数值: {result_float}")
    
    # 测试减法：2.0 - 1.0 = 1.0
    fp_two = 0x4000000000000000  # 2.0 in f64
    print(f"\n输入 fp_a = 2.0 (0x{fp_two:x})")
    print(f"输入 fp_b = 1.0 (0x{fp_one:x})")
    
    result_sub, fflags_sub = api_VectorFloatAdder_subtract(
        env=env,
        fp_a=fp_two,
        fp_b=fp_one,
        fp_format=0b10,  # f64
        round_mode=0     # RNE
    )
    
    print(f"减法结果: 0x{result_sub:x}")
    print(f"标志位: 0x{fflags_sub:x}")
    
    # 将结果转换回浮点数
    result_sub_float = struct.unpack('>d', struct.pack('>Q', result_sub))[0]
    print(f"结果浮点数值: {result_sub_float}")
    
    # 测试不同的浮点格式
    print(f"\n=== 测试f32格式 ===")
    fp_one_f32 = 0x3f800000  # 1.0 in f32
    result_f32, fflags_f32 = api_VectorFloatAdder_add(
        env=env,
        fp_a=fp_one_f32,
        fp_b=fp_one_f32,
        fp_format=0b01,  # f32
        round_mode=0     # RNE
    )
    
    print(f"f32加法结果: 0x{result_f32:x}")
    print(f"f32标志位: 0x{fflags_f32:x}")
    
    # f32结果在低32位
    result_f32_low = result_f32 & 0xFFFFFFFF
    result_f32_float = struct.unpack('>f', struct.pack('>I', result_f32_low))[0]
    print(f"f32结果浮点数值: {result_f32_float}")
    
    print(f"\n=== 测试f16格式 ===")
    fp_one_f16 = 0x3c00  # 1.0 in f16
    result_f16, fflags_f16 = api_VectorFloatAdder_add(
        env=env,
        fp_a=fp_one_f16,
        fp_b=fp_one_f16,
        fp_format=0b00,  # f16
        round_mode=0     # RNE
    )
    
    print(f"f16加法结果: 0x{result_f16:x}")
    print(f"f16标志位: 0x{fflags_f16:x}")
    
    # f16结果在低16位
    result_f16_low = result_f16 & 0xFFFF
    # 简单的f16到f32转换用于显示
    result_f16_as_f32 = float.fromhex(struct.pack('>H', result_f16_low).hex())
    print(f"f16结果浮点数值(近似): {result_f16_as_f32}")
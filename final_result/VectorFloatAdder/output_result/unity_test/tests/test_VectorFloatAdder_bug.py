#coding=utf-8

from VectorFloatAdder_api import *
import pytest
import struct

def test_Bug_1(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-EXTREME"].mark_function("FC-EXTREME-FIND", test_Bug_1, ["CK-MAX"])
    
    # 准备测试数据：FMAX(1.0, 2.0)应该返回2.0
    # FP16: 1.0 = 0x3C00, 2.0 = 0x4000
    fp_a = 0x3C003C00  # 1.0/1.0 in FP16 (32位，2个lane)
    fp_b = 0x40004000  # 2.0/2.0 in FP16 (32位，2个lane)
    
    # 使用API调用
    result, fflags = api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=3,      # FMAX
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=1,    # FP16
        round_mode=0    # RNE
    )
    
    # 验证结果：应该返回最大值2.0 (0x4000)
    expected_result = 0x40004000
    assert result == expected_result, f"FMAX(1.0, 2.0) = 0x{result:x}, 应为0x{expected_result:x}"

def test_Bug_2(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-SPECIAL-VALUES"].mark_function("FC-INF-HANDLE", test_Bug_2, ["CK-INF-ARITHMETIC"])
    
    # 准备测试数据：1.0 + 无穷大
    fp_a = 0x3F800000  # 1.0 in FP32
    fp_b = 0x7F800000  # +无穷大 in FP32
    
    # 使用API调用
    result, fflags = api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=0,      # FADD
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=2,    # FP32
        round_mode=0    # RNE
    )
    
    # 验证结果：应该返回无穷大，而不是sNaN
    expected_result = 0x7F800000
    assert result == expected_result, f"1.0 + Inf = 0x{result:x}, 应为0x{expected_result:x}"

def test_Bug_3(env):
    # 覆盖率标记
    env.dut.fc_cover["FG-SPECIAL"].mark_function("FC-FLOAT-CLASS", test_Bug_3, ["CK-CLASSIFY"])
    
    # 准备测试数据：sNaN
    snan_val = 0x7FF0000000000001  # sNaN in FP64
    
    # 使用API调用
    result, fflags = api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=15,     # FCLASS
        fp_a=snan_val,
        fp_b=0,
        fp_format=3,    # FP64
        round_mode=0
    )
    
    # 验证结果：sNaN应该设置bit 8
    snan_bit = (result >> 8) & 1
    assert snan_bit == 1, f"FCLASS(sNaN)结果0x{result:x}中bit 8应为1"

def test_Bug_4(env):
    env.dut.fc_cover["FG-ROUNDING-EXCEPTION"].mark_function("FC-EXCEPTION-HANDLE", test_Bug_4, ["CK-INVALID-OP"])

    # 使用正确的sNaN编码
    fp_a = 0x7C01  # 正确的FP16 sNaN: 指数=0x1F, 尾数=0x01 (非零)
    fp_b = 0x3C00  # 1.0 in FP16

    # 使用API调用
    result, fflags = api_VectorFloatAdder_f16_operation(
        env=env,
        fp_a=fp_a,
        fp_b=fp_b,
        op_code=0,     # FADD
        round_mode=0
    )
    
    # 验证标志位：应该设置无效操作标志(NV)
    expected_nv_flag = 0x10
    assert (fflags & expected_nv_flag) == expected_nv_flag, f"fflags=0x{fflags:x} 应设置NV标志(0x10)"

def test_Bug_5(env):
    env.dut.fc_cover["FG-VECTOR-MASK"].mark_function("FC-REDUCTION", test_Bug_5, ["CK-REDUCTION-MASK"])

    # 准备测试数据
    val_b = -1.5
    fp_b = struct.unpack('<Q', struct.pack('<d', val_b))[0]
    fp_a = struct.unpack('<Q', struct.pack('<d', 2.5))[0]

    # 使用API调用
    result, fflags = api_VectorFloatAdder_basic_operation(
        env=env,
        op_code=26,     # FSUM_URE
        fp_a=fp_a,
        fp_b=fp_b,
        fp_format=3,    # FP64
        round_mode=0    # RNE
    )
    
    # 验证结果：掩码为0时应返回-0.0
    expected_result = 0x8000000000000000  # -0.0 in FP64
    assert result == expected_result, f"归约求和(掩码=0) = 0x{result:x}, 应为-0.0(0x{expected_result:x})"
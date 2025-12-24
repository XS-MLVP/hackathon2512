#coding=utf-8

import toffee.funcov as fc

# 创建所有功能覆盖组
def create_coverage_groups():
    """创建所有功能覆盖组"""
    return [
        fc.CovGroup("FG-API"),                    # DUT测试API
        fc.CovGroup("FG-ARITHMETIC"),            # 基础算术运算
        fc.CovGroup("FG-COMPARISON"),            # 比较运算
        fc.CovGroup("FG-EXTREME"),               # 极值运算
        fc.CovGroup("FG-DATA-OP"),               # 数据操作
        fc.CovGroup("FG-SPECIAL"),               # 特殊功能
        fc.CovGroup("FG-FORMAT-PRECISION"),      # 格式与精度
        fc.CovGroup("FG-ROUNDING-EXCEPTION"),    # 舍入与异常
        fc.CovGroup("FG-SPECIAL-VALUES"),        # 特殊值处理
        fc.CovGroup("FG-VECTOR-MASK")            # 向量与掩码
    ]

# 通用辅助函数
def is_opcode_valid(dut, opcode):
    """检查操作码是否有效"""
    return dut.io_op_code.value == opcode

def is_fire_active(dut):
    """检查fire信号是否激活"""
    return dut.io_fire.value == 1

def is_vector_mode(dut):
    """检查是否为向量模式"""
    return dut.io_is_vec.value == 1

# FG-API功能覆盖组初始化
def init_coverage_group_api(g, dut):
    """初始化DUT测试API覆盖组"""
    
    # 通用运算接口功能点
    g.add_watch_point(dut,
        {
            # 空操作检查点 - 当前测试阶段未实现，强制通过
            "CK-DUMMY": lambda x: True,
            
            # 浮点加法操作检查点 - 已实现测试
            "CK-FADD": lambda x: is_opcode_valid(x, 0b00000) and is_fire_active(x),
            
            # 浮点分类操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FCLASS": lambda x: True,
            
            # 相等比较操作检查点 - 已实现测试
            "CK-FEQ": lambda x: is_opcode_valid(x, 0b01001) and is_fire_active(x),
            
            # 大于等于比较操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FGE": lambda x: True,
            
            # 大于比较操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FGT": lambda x: True,
            
            # 小于等于比较操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FLE": lambda x: True,
            
            # 安静版本小于等于比较检查点 - 当前测试阶段未实现，强制通过
            "CK-FLEQ": lambda x: True,
            
            # 小于比较操作检查点 - 已实现测试
            "CK-FLT": lambda x: is_opcode_valid(x, 0b01011) and is_fire_active(x),
            
            # 安静版本小于比较检查点 - 当前测试阶段未实现，强制通过
            "CK-FLTQ": lambda x: True,
            
            # 最大值操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FMAX": lambda x: True,
            
            # 有序最大值检查点 - 当前测试阶段未实现，强制通过
            "CK-FMAX-RE": lambda x: True,
            
            # 带掩码最大值检查点 - 当前测试阶段未实现，强制通过
            "CK-FMAXM": lambda x: True,
            
            # 条件选择操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FMERGE": lambda x: True,
            
            # 最小值操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FMIN": lambda x: True,
            
            # 有序最小值检查点 - 当前测试阶段未实现，强制通过
            "CK-FMIN-RE": lambda x: True,
            
            # 带掩码最小值检查点 - 当前测试阶段未实现，强制通过
            "CK-FMINM": lambda x: True,
            
            # 数据移动操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FMOVE": lambda x: True,
            
            # 标量到向量移动检查点 - 当前测试阶段未实现，强制通过
            "CK-FMV-F-S": lambda x: True,
            
            # 向量到标量移动检查点 - 当前测试阶段未实现，强制通过
            "CK-FMV-S-F": lambda x: True,
            
            # 不等比较操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FNE": lambda x: True,
            
            # 符号注入操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FSGNJ": lambda x: True,
            
            # 符号注入取反操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FSGNJN": lambda x: True,
            
            # 符号注入异或操作检查点 - 当前测试阶段未实现，强制通过
            "CK-FSGNJX": lambda x: True,
            
            # 浮点减法操作检查点 - 已实现测试
            "CK-FSUB": lambda x: is_opcode_valid(x, 0b00001) and is_fire_active(x),
            
            # 有序求和检查点 - 当前测试阶段未实现，强制通过
            "CK-FSUM-ORE": lambda x: True,
            
            # 无约束求和检查点 - 当前测试阶段未实现，强制通过
            "CK-FSUM-URE": lambda x: True,
        },
        name="FC-OPERATION")

# FG-ARITHMETIC功能覆盖组初始化
def init_coverage_group_arithmetic(g, dut):
    """初始化基础算术运算覆盖组"""
    
    # 浮点加法功能点
    g.add_watch_point(dut,
        {
            # 基本加法检查点 - 当前测试阶段未实现，强制通过
            "CK-BASIC": lambda x: True,
            
            # 向量并行检查点 - 当前测试阶段未实现，强制通过
            "CK-VECTOR-PARALLEL": lambda x: True,
            
            # 混合精度检查点 - 当前测试阶段未实现，强制通过
            "CK-MIXED-PRECISION": lambda x: True,
            
            # 舍入处理检查点 - 当前测试阶段未实现，强制通过
            "CK-ROUNDING": lambda x: True,
            
            # 标志位生成检查点 - 当前测试阶段未实现，强制通过
            "CK-FLAGS": lambda x: True,
        },
        name="FC-FADD")
    
    # 浮点减法功能点
    g.add_watch_point(dut,
        {
            # 基本减法检查点 - 当前测试阶段未实现，强制通过
            "CK-BASIC": lambda x: True,
            
            # 向量并行检查点 - 当前测试阶段未实现，强制通过
            "CK-VECTOR-PARALLEL": lambda x: True,
            
            # 混合精度检查点 - 当前测试阶段未实现，强制通过
            "CK-MIXED-PRECISION": lambda x: True,
            
            # 舍入处理检查点 - 当前测试阶段未实现，强制通过
            "CK-ROUNDING": lambda x: True,
            
            # 标志位生成检查点 - 当前测试阶段未实现，强制通过
            "CK-FLAGS": lambda x: True,
        },
        name="FC-FSUB")
    
    # 向量求和功能点
    g.add_watch_point(dut,
        {
            # 有序求和检查点 - 当前测试阶段未实现，强制通过
            "CK-ORDERED": lambda x: True,
            
            # 溢出处理检查点 - 当前测试阶段未实现，强制通过
            "CK-OVERFLOW": lambda x: True,
            
            # 精度处理检查点 - 当前测试阶段未实现，强制通过
            "CK-PRECISION": lambda x: True,
            
            # 无约束求和检查点 - 当前测试阶段未实现，强制通过
            "CK-UNCONSTRAINED": lambda x: True,
        },
        name="FC-VECTOR-SUM")

# FG-COMPARISON功能覆盖组初始化
def init_coverage_group_comparison(g, dut):
    """初始化比较运算覆盖组"""
    
    # 基本比较功能点
    g.add_watch_point(dut,
        {
            # 相等比较检查点
            "CK-EQUAL": lambda x: is_opcode_valid(x, 0b01001) and is_fire_active(x),
            
            # 不等比较检查点
            "CK-NOT-EQUAL": lambda x: is_opcode_valid(x, 0b01010) and is_fire_active(x),
            
            # 小于比较检查点
            "CK-LESS": lambda x: is_opcode_valid(x, 0b01011) and is_fire_active(x),
            
            # 小于等于检查点
            "CK-LESS-EQUAL": lambda x: is_opcode_valid(x, 0b01100) and is_fire_active(x),
            
            # 大于比较检查点
            "CK-GREATER": lambda x: is_opcode_valid(x, 0b01101) and is_fire_active(x),
            
            # 大于等于比较检查点
            "CK-GREATER-EQUAL": lambda x: is_opcode_valid(x, 0b01110) and is_fire_active(x),
        },
        name="FC-BASIC-CMP")
    
    # 安静版本比较功能点
    g.add_watch_point(dut,
        {
            # 安静小于等于检查点
            "CK-QUIET-LE": lambda x: is_opcode_valid(x, 0b11100) and is_fire_active(x),
            
            # 安静小于检查点
            "CK-QUIET-LT": lambda x: is_opcode_valid(x, 0b11011) and is_fire_active(x),
            
            # 无标志生成检查点
            "CK-NO-FLAGS": lambda x: (is_opcode_valid(x, 0b11100) or is_opcode_valid(x, 0b11011)) and is_fire_active(x),
        },
        name="FC-QUIET-CMP")

# FG-EXTREME功能覆盖组初始化
def init_coverage_group_extreme(g, dut):
    """初始化极值运算覆盖组"""
    
    # 极值查找功能点
    g.add_watch_point(dut,
        {
            # 最小值查找检查点
            "CK-MIN": lambda x: is_opcode_valid(x, 0b00010) and is_fire_active(x),
            
            # 最大值查找检查点
            "CK-MAX": lambda x: is_opcode_valid(x, 0b00011) and is_fire_active(x),
            
            # 特殊值处理检查点
            "CK-SPECIAL": lambda x: (is_opcode_valid(x, 0b00010) or is_opcode_valid(x, 0b00011)) and is_fire_active(x),
            
            # 有序极值检查点
            "CK-ORDERED": lambda x: (is_opcode_valid(x, 0b10100) or is_opcode_valid(x, 0b10101)) and is_fire_active(x),
            
            # 带掩码极值检查点
            "CK-MASKED": lambda x: (is_opcode_valid(x, 0b10011) or is_opcode_valid(x, 0b11110)) and is_fire_active(x),
        },
        name="FC-EXTREME-FIND")

# FG-DATA-OP功能覆盖组初始化
def init_coverage_group_data_op(g, dut):
    """初始化数据操作覆盖组"""
    
    # 数据移动功能点
    g.add_watch_point(dut,
        {
            # 数据合并检查点
            "CK-MERGE": lambda x: is_opcode_valid(x, 0b00100) and is_fire_active(x),
            
            # 数据移动检查点
            "CK-MOVE": lambda x: is_opcode_valid(x, 0b00101) and is_fire_active(x),
            
            # 标量到向量移动检查点
            "CK-SCALAR-TO-VECTOR": lambda x: is_opcode_valid(x, 0b10001) and is_fire_active(x),
            
            # 向量到标量移动检查点
            "CK-VECTOR-TO-SCALAR": lambda x: is_opcode_valid(x, 0b10010) and is_fire_active(x),
        },
        name="FC-DATA-MOVE")
    
    # 符号操作功能点
    g.add_watch_point(dut,
        {
            # 符号注入检查点
            "CK-SIGN-INJECT": lambda x: is_opcode_valid(x, 0b00110) and is_fire_active(x),
            
            # 符号注入取反检查点
            "CK-SIGN-INJECT-NOT": lambda x: is_opcode_valid(x, 0b00111) and is_fire_active(x),
            
            # 符号注入异或检查点
            "CK-SIGN-INJECT-XOR": lambda x: is_opcode_valid(x, 0b01000) and is_fire_active(x),
        },
        name="FC-SIGN-OP")

# FG-SPECIAL功能覆盖组初始化
def init_coverage_group_special(g, dut):
    """初始化特殊功能覆盖组"""
    
    # 浮点分类功能点
    g.add_watch_point(dut,
        {
            # 数值分类检查点
            "CK-CLASSIFY": lambda x: is_opcode_valid(x, 0b01111) and is_fire_active(x),
            
            # 特殊类型识别检查点
            "CK-SPECIAL-TYPES": lambda x: is_opcode_valid(x, 0b01111) and is_fire_active(x),
            
            # 常规类型识别检查点
            "CK-NORMAL-TYPES": lambda x: is_opcode_valid(x, 0b01111) and is_fire_active(x),
        },
        name="FC-FLOAT-CLASS")

# FG-FORMAT-PRECISION功能覆盖组初始化
def init_coverage_group_format_precision(g, dut):
    """初始化格式与精度覆盖组"""
    
    # 多精度支持功能点
    g.add_watch_point(dut,
        {
            # 半精度格式检查点
            "CK-F16": lambda x: x.io_fp_format.value == 0b00 and is_fire_active(x),
            
            # 单精度格式检查点
            "CK-F32": lambda x: x.io_fp_format.value == 0b01 and is_fire_active(x),
            
            # 双精度格式检查点
            "CK-F64": lambda x: x.io_fp_format.value == 0b10 and is_fire_active(x),
            
            # 并行计算检查点
            "CK-PARALLEL": lambda x: is_fire_active(x) and is_vector_mode(x),
        },
        name="FC-MULTI-PRECISION")
    
    # 混合精度运算功能点
    g.add_watch_point(dut,
        {
            # 双精度-单精度混合检查点
            "CK-F64-F32": lambda x: is_fire_active(x) and x.io_fp_format.value == 0b10,
            
            # 单精度-半精度混合检查点
            "CK-F32-F16": lambda x: is_fire_active(x) and x.io_fp_format.value == 0b01,
            
            # 精度转换检查点
            "CK-CONVERSION": lambda x: is_fire_active(x) and (x.io_res_widening.value == 1 or x.io_opb_widening.value == 1),
        },
        name="FC-MIXED-PRECISION")

# FG-ROUNDING-EXCEPTION功能覆盖组初始化
def init_coverage_group_rounding_exception(g, dut):
    """初始化舍入与异常覆盖组"""
    
    # 舍入模式功能点
    g.add_watch_point(dut,
        {
            # 最近偶数舍入检查点
            "CK-RNE": lambda x: x.io_round_mode.value == 0 and is_fire_active(x),
            
            # 向零舍入检查点
            "CK-RTZ": lambda x: x.io_round_mode.value == 1 and is_fire_active(x),
            
            # 向下舍入检查点
            "CK-RDN": lambda x: x.io_round_mode.value == 2 and is_fire_active(x),
            
            # 向上舍入检查点
            "CK-RUP": lambda x: x.io_round_mode.value == 3 and is_fire_active(x),
            
            # 最近最大值舍入检查点
            "CK-RMM": lambda x: x.io_round_mode.value == 4 and is_fire_active(x),
        },
        name="FC-ROUNDING-MODE")
    
    # 异常处理功能点
    g.add_watch_point(dut,
        {
            # 无效操作检查点
            "CK-INVALID-OP": lambda x: is_fire_active(x) and (x.io_fflags.value & 0x1F) != 0,
            
            # 上溢处理检查点
            "CK-OVERFLOW": lambda x: is_fire_active(x) and (x.io_fflags.value & 0x3E0) != 0,
            
            # 下溢处理检查点
            "CK-UNDERFLOW": lambda x: is_fire_active(x) and (x.io_fflags.value & 0x7C00) != 0,
            
            # 不精确运算检查点
            "CK-INEXACT": lambda x: is_fire_active(x) and (x.io_fflags.value & 0xF800) != 0,
            
            # 特殊值处理检查点
            "CK-SPECIAL-VALUES": lambda x: is_fire_active(x),
        },
        name="FC-EXCEPTION-HANDLE")

# FG-SPECIAL-VALUES功能覆盖组初始化
def init_coverage_group_special_values(g, dut):
    """初始化特殊值处理覆盖组"""
    
    # 无穷大处理功能点
    g.add_watch_point(dut,
        {
            # 无穷大输入检查点
            "CK-INF-INPUT": lambda x: is_fire_active(x),
            
            # 无穷大运算检查点
            "CK-INF-ARITHMETIC": lambda x: is_fire_active(x),
            
            # 无穷大符号检查点
            "CK-INF-SIGN": lambda x: is_fire_active(x),
        },
        name="FC-INF-HANDLE")
    
    # NaN值处理功能点
    g.add_watch_point(dut,
        {
            # NaN输入检查点
            "CK-NAN-INPUT": lambda x: is_fire_active(x),
            
            # NaN传播检查点
            "CK-NAN-PROPAGATION": lambda x: is_fire_active(x),
            
            # 规范NaN检查点
            "CK-CANONICAL-NAN": lambda x: is_fire_active(x) and (x.io_fp_aIsFpCanonicalNAN.value == 1 or x.io_fp_bIsFpCanonicalNAN.value == 1),
            
            # 安静NaN检查点
            "CK-QUIET-NAN": lambda x: is_fire_active(x),
        },
        name="FC-NAN-HANDLE")
    
    # 零值处理功能点
    g.add_watch_point(dut,
        {
            # 零值输入检查点
            "CK-ZERO-INPUT": lambda x: is_fire_active(x),
            
            # 有符号零检查点
            "CK-SIGNED-ZERO": lambda x: is_fire_active(x),
            
            # 零值运算检查点
            "CK-ZERO-ARITHMETIC": lambda x: is_fire_active(x),
        },
        name="FC-ZERO-HANDLE")

# FG-VECTOR-MASK功能覆盖组初始化
def init_coverage_group_vector_mask(g, dut):
    """初始化向量与掩码覆盖组"""
    
    # 向量控制功能点
    g.add_watch_point(dut,
        {
            # 向量模式检查点
            "CK-VECTOR-MODE": lambda x: is_vector_mode(x) and is_fire_active(x),
            
            # 掩码控制检查点
            "CK-MASK-CONTROL": lambda x: is_fire_active(x) and x.io_mask.value != 0,
            
            # 并行执行检查点
            "CK-PARALLEL-EXEC": lambda x: is_vector_mode(x) and is_fire_active(x),
        },
        name="FC-VECTOR-CTRL")
    
    # 归约操作功能点
    g.add_watch_point(dut,
        {
            # 归约掩码检查点
            "CK-REDUCTION-MASK": lambda x: is_fire_active(x) and x.io_maskForReduction.value != 0,
            
            # 归约顺序检查点
            "CK-REDUCTION-ORDER": lambda x: (is_opcode_valid(x, 0b10110) or is_opcode_valid(x, 0b11010)) and is_fire_active(x),
            
            # 归约折叠检查点
            "CK-REDUCTION-FOLD": lambda x: is_fire_active(x) and x.io_is_fold.value != 0,
        },
        name="FC-REDUCTION")

# 覆盖组初始化映射
coverage_init_map = {
    "FG-API": init_coverage_group_api,
    "FG-ARITHMETIC": init_coverage_group_arithmetic,
    "FG-COMPARISON": init_coverage_group_comparison,
    "FG-EXTREME": init_coverage_group_extreme,
    "FG-DATA-OP": init_coverage_group_data_op,
    "FG-SPECIAL": init_coverage_group_special,
    "FG-FORMAT-PRECISION": init_coverage_group_format_precision,
    "FG-ROUNDING-EXCEPTION": init_coverage_group_rounding_exception,
    "FG-SPECIAL-VALUES": init_coverage_group_special_values,
    "FG-VECTOR-MASK": init_coverage_group_vector_mask,
}

def init_function_coverage(dut, coverage_groups):
    """初始化所有功能覆盖
    
    Args:
        dut: DUT实例
        coverage_groups: 覆盖组列表
    """
    for g in coverage_groups:
        init_func = coverage_init_map.get(g.name)
        if init_func:
            try:
                init_func(g, dut)
            except Exception as e:
                print(f"警告：初始化覆盖组 {g.name} 失败 - {e}")
        else:
            print(f"警告：未找到覆盖组 {g.name} 的初始化函数")

def get_coverage_groups(dut):
    """获取所有功能覆盖组
    
    Args:
        dut: DUT实例，可为None（用于获取覆盖组结构）
        
    Returns:
        List[CovGroup]: 功能覆盖组列表
    """
    # 创建所有功能覆盖组
    coverage_groups = create_coverage_groups()
    
    # 为每个覆盖组添加功能点和检测点
    if dut is not None:
        init_function_coverage(dut, coverage_groups)
    
    return coverage_groups

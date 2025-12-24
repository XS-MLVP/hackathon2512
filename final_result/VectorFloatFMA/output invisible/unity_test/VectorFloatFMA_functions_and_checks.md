# VectorFloatFMA 功能点与检测点描述

## DUT 整体功能描述

VectorFloatFMA（向量浮点乘加融合单元）是实现RISC-V V扩展的向量浮点乘加指令的专用硬件单元。它执行融合乘加运算（FMA: a×b+c），采用四周期流水线架构，支持FP16、FP32、FP64三种IEEE 754浮点格式，提供9种操作码变体和5种舍入模式，能够处理NaN、无穷大等特殊值，并生成符合标准的异常标志。

### 端口接口说明

**通用控制端口：**
- `clock`：时钟信号，1位，驱动流水线
- `reset`：复位信号，1位，初始化电路状态

**主要功能输入端口：**
- `io_fp_a`：源操作数vs2，64位，第一个浮点数输入
- `io_fp_b`：源操作数vs1，64位，第二个浮点数输入
- `io_fp_c`：源操作数vd，64位，第三个浮点数输入
- `io_fire`：计算使能信号，1位，为1时输入有效并开始计算
- `io_round_mode`：舍入模式选择，3位，有效值0-4对应IEEE 754五种舍入模式
- `io_fp_format`：浮点格式选择，2位，00=FP16, 01=FP32, 10=FP64, 11=无效
- `io_op_code`：操作码，4位，有效值0-8对应9种乘加变体操作

**输出端口：**
- `io_fp_result`：计算结果，64位，根据io_fp_format解释为对应精度的浮点数
- `io_fflags`：异常标志位，20位，包含IEEE 754定义的五类异常标志

### 操作码定义

| opcode | 指令名 | 计算公式 | 说明 |
|--------|--------|----------|------|
| 0000 | vfmul | vd = vs2 × vs1 | 简单浮点乘法 |
| 0001 | vfmacc | vd = +(vs2 × vs1) + vd | 正乘加 |
| 0010 | vfnmacc | vd = -(vs2 × vs1) - vd | 负乘负加 |
| 0011 | vfmsac | vd = +(vs2 × vs1) - vd | 正乘减 |
| 0100 | vfnmsac | vd = -(vs2 × vs1) + vd | 负乘正加 |
| 0101 | vfmadd | vd = +(vs2 × vd) + vs1 | 操作数顺序不同的正乘加 |
| 0110 | vfnmadd | vd = -(vs2 × vd) - vs1 | 操作数顺序不同的负乘负加 |
| 0111 | vfmsub | vd = +(vs2 × vd) - vs1 | 操作数顺序不同的正乘减 |
| 1000 | vfnmsub | vd = -(vs2 × vd) + vs1 | 操作数顺序不同的负乘正加 |

### 关键特性

- **流水线深度**：4周期，输入后第4个周期输出结果
- **多精度支持**：FP16（半精度）、FP32（单精度）、FP64（双精度）
- **舍入模式**：RNE(0), RTZ(1), RDN(2), RUP(3), RMM(4)
- **特殊值处理**：符合IEEE 754标准的NaN、Inf、零、非规格化数处理
- **异常标志**：无效操作、除零、溢出、下溢、不精确

## 功能分组与检测点

### DUT测试API

<FG-API>

本分组定义VectorFloatFMA测试所需的标准API接口和基本操作方法。

#### 标准测试接口

<FC-STD-INTERFACE>

提供与DUT交互的标准接口，包括信号设置、时钟驱动、结果读取等基本操作。

**检测点：**
- <CK-STEP> Step接口驱动：验证Step()方法能够正确驱动流水线推进
- <CK-SIGNAL-WRITE> 信号写入：验证能够正确设置输入信号值（io_fp_a/b/c等）
- <CK-SIGNAL-READ> 信号读取：验证能够正确读取输出信号值（io_fp_result, io_fflags）
- <CK-RESET> 复位功能：验证reset信号能够正确初始化DUT状态
- <CK-FIRE-CONTROL> Fire信号控制：验证io_fire信号能够正确控制计算使能

#### 流水线操作

<FC-PIPELINE>

验证四周期流水线的基本操作和数据流转。

**检测点：**
- <CK-LATENCY> 流水线延迟：验证输入后恰好4个周期产生输出
- <CK-CONTINUOUS> 连续输入：验证连续多个周期输入数据的流水线处理能力
- <CK-BUBBLE> 流水线气泡：验证间隔输入（有空闲周期）时的正确性

### 基础乘法运算

<FG-MULTIPLY>

验证基础的浮点乘法运算功能（opcode=0），这是所有乘加操作的基础。

#### FP32基础乘法

<FC-MUL-FP32>

验证单精度（FP32）浮点乘法的基本正确性。

**检测点：**
- <CK-BASIC> 基本乘法：验证简单正数乘法，如2.0 × 3.0 = 6.0
- <CK-POSITIVE> 正数相乘：验证两个正数相乘结果正确
- <CK-NEGATIVE> 负数相乘：验证包含负数的乘法及符号处理
- <CK-FRACTION> 小数乘法：验证小数相乘的精度
- <CK-ONE> 乘以1：验证 a × 1.0 = a
- <CK-ZERO> 乘以0：验证 a × 0 = 0（零的符号需符合标准）

#### FP16基础乘法

<FC-MUL-FP16>

验证半精度（FP16）浮点乘法，范围和精度受限。

**检测点：**
- <CK-BASIC> 基本乘法：验证FP16格式的基本乘法运算
- <CK-RANGE> 范围测试：验证FP16有效范围[-65504, 65504]内的运算
- <CK-PRECISION> 精度测试：验证FP16的10位尾数精度

#### FP64基础乘法

<FC-MUL-FP64>

验证双精度（FP64）浮点乘法，最高精度和最大范围。

**检测点：**
- <CK-BASIC> 基本乘法：验证FP64格式的基本乘法运算
- <CK-LARGE> 大数乘法：验证接近FP64上限的大数运算
- <CK-PRECISION> 精度测试：验证FP64的52位尾数精度

### 乘加融合运算

<FG-FUSED-MULTIPLY-ADD>

验证融合乘加（FMA）操作，这是VectorFloatFMA的核心功能，包含各种操作码变体。

#### 正乘加运算（vfmacc）

<FC-VFMACC>

验证opcode=1的正乘加运算：vd = +(vs2 × vs1) + vd

**检测点：**
- <CK-BASIC> 基本正乘加：验证简单的a×b+c运算
- <CK-POSITIVE-ALL> 全正数：验证三个正数的乘加运算
- <CK-MIXED-SIGN> 混合符号：验证包含正负数的乘加运算
- <CK-ROUNDING> 舍入效应：验证乘加中间结果舍入的正确性

#### 负乘负加运算（vfnmacc）

<FC-VFNMACC>

验证opcode=2的负乘负加运算：vd = -(vs2 × vs1) - vd

**检测点：**
- <CK-BASIC> 基本负乘负加：验证 -(a×b) - c 的计算
- <CK-SIGN> 符号处理：验证两次取负的符号正确性
- <CK-CANCEL> 相消效应：验证 -(a×b) - c 当两项接近时的精度

#### 正乘减运算（vfmsac）

<FC-VFMSAC>

验证opcode=3的正乘减运算：vd = +(vs2 × vs1) - vd

**检测点：**
- <CK-BASIC> 基本正乘减：验证 (a×b) - c 的计算
- <CK-SUBTRACTION> 减法精度：验证减法操作的精度保持
- <CK-NEGATIVE-RESULT> 负结果：验证当c > a×b时结果为负

#### 负乘正加运算（vfnmsac）

<FC-VFNMSAC>

验证opcode=4的负乘正加运算：vd = -(vs2 × vs1) + vd

**检测点：**
- <CK-BASIC> 基本负乘正加：验证 -(a×b) + c 的计算
- <CK-SIGN-MIX> 符号混合：验证负乘结果与正加数的组合
- <CK-COMPENSATION> 补偿效应：验证 c 可以部分或完全抵消 -(a×b)

#### 变体乘加运算（vfmadd）

<FC-VFMADD>

验证opcode=5的变体乘加运算：vd = +(vs2 × vd) + vs1，操作数顺序与vfmacc不同

**检测点：**
- <CK-BASIC> 基本变体乘加：验证操作数顺序调换后的正确性
- <CK-OPERAND-ORDER> 操作数顺序：对比验证与vfmacc在操作数映射上的差异

#### 变体负乘负加（vfnmadd）

<FC-VFNMADD>

验证opcode=6的变体负乘负加：vd = -(vs2 × vd) - vs1

**检测点：**
- <CK-BASIC> 基本变体负乘负加：验证操作数顺序调换的负乘负加
- <CK-OPERAND-ORDER> 操作数顺序：验证正确的操作数映射

#### 变体正乘减（vfmsub）

<FC-VFMSUB>

验证opcode=7的变体正乘减：vd = +(vs2 × vd) - vs1

**检测点：**
- <CK-BASIC> 基本变体正乘减：验证操作数顺序调换的正乘减
- <CK-OPERAND-ORDER> 操作数顺序：验证正确的操作数映射

#### 变体负乘正加（vfnmsub）

<FC-VFNMSUB>

验证opcode=8的变体负乘正加：vd = -(vs2 × vd) + vs1

**检测点：**
- <CK-BASIC> 基本变体负乘正加：验证操作数顺序调换的负乘正加
- <CK-OPERAND-ORDER> 操作数顺序：验证正确的操作数映射

### 舍入模式

<FG-ROUNDING>

验证IEEE 754标准定义的五种舍入模式在不同运算中的正确性。

#### 最近偶数舍入（RNE）

<FC-RNE>

验证舍入模式0：Round to Nearest, ties to Even（最近舍入，平局取偶数）

**检测点：**
- <CK-ROUND-DOWN> 向下舍入：验证结果更接近下界时向下舍
- <CK-ROUND-UP> 向上舍入：验证结果更接近上界时向上舍
- <CK-TIE-EVEN> 平局取偶：验证正好在中间时选择偶数位的尾数
- <CK-NO-ROUND> 精确结果：验证无需舍入时结果不变

#### 向零舍入（RTZ）

<FC-RTZ>

验证舍入模式1：Round Towards Zero（向零舍入，截断）

**检测点：**
- <CK-TRUNCATE-POS> 正数截断：验证正数向下舍入（朝零方向）
- <CK-TRUNCATE-NEG> 负数截断：验证负数向上舍入（朝零方向）
- <CK-NO-ROUND> 精确结果：验证无需舍入时结果不变

#### 向下舍入（RDN）

<FC-RDN>

验证舍入模式2：Round Down（向负无穷舍入）

**检测点：**
- <CK-FLOOR> 向下取整：验证总是向更小的值舍入
- <CK-POSITIVE> 正数舍入：验证正数向下舍入效果
- <CK-NEGATIVE> 负数舍入：验证负数向下舍入（绝对值更大）

#### 向上舍入（RUP）

<FC-RUP>

验证舍入模式3：Round Up（向正无穷舍入）

**检测点：**
- <CK-CEIL> 向上取整：验证总是向更大的值舍入
- <CK-POSITIVE> 正数舍入：验证正数向上舍入（绝对值更大）
- <CK-NEGATIVE> 负数舍入：验证负数向上舍入效果

#### 最近最大值舍入（RMM）

<FC-RMM>

验证舍入模式4：Round to Nearest, ties to Max Magnitude（最近舍入，平局取绝对值更大）

**检测点：**
- <CK-ROUND-NEAREST> 最近舍入：验证非平局情况下的最近舍入
- <CK-TIE-AWAY> 平局远离零：验证平局时选择绝对值更大的值

### 特殊值处理

<FG-SPECIAL-VALUES>

验证IEEE 754定义的特殊浮点值（NaN、Inf、零、非规格化数）的处理。

#### NaN处理

<FC-NAN>

验证NaN（Not a Number）的传播和生成规则。

**检测点：**
- <CK-NAN-PROP-A> NaN传播-操作数A：验证io_fp_a为NaN时结果为NaN
- <CK-NAN-PROP-B> NaN传播-操作数B：验证io_fp_b为NaN时结果为NaN
- <CK-NAN-PROP-C> NaN传播-操作数C：验证io_fp_c为NaN时结果为NaN
- <CK-NAN-GEN-0INF> NaN生成-0×Inf：验证0乘以无穷大生成NaN
- <CK-NAN-GEN-INFSUB> NaN生成-Inf-Inf：验证无穷大减无穷大生成NaN
- <CK-QNAN> 安静NaN：验证qNaN的正确处理
- <CK-SNAN> 信号NaN：验证sNaN的正确处理（如果支持）

#### 无穷大处理

<FC-INFINITY>

验证无穷大（Infinity）的运算规则。

**检测点：**
- <CK-INF-MUL-NORM> Inf×正常数：验证无穷大乘以非零正常数为无穷大
- <CK-INF-MUL-INF> Inf×Inf：验证无穷大相乘为无穷大
- <CK-INF-ADD-NORM> Inf+正常数：验证无穷大加正常数为无穷大
- <CK-INF-ADD-INF-SAME> Inf+Inf（同号）：验证同号无穷大相加为无穷大
- <CK-INF-ADD-INF-DIFF> Inf-Inf（异号）：验证异号无穷大相加为NaN
- <CK-INF-SIGN> 无穷大符号：验证正负无穷大的符号处理

#### 零值处理

<FC-ZERO>

验证零（包括+0和-0）的运算规则和符号处理。

**检测点：**
- <CK-ZERO-MUL> 零乘法：验证任何数乘以零为零
- <CK-ZERO-ADD> 零加法：验证数加零为其自身
- <CK-ZERO-SIGN-POS> 正零：验证+0的正确生成和传播
- <CK-ZERO-SIGN-NEG> 负零：验证-0的正确生成和传播
- <CK-ZERO-SIGN-RULE> 零符号规则：验证0×0, (+0)+(-0)等的符号规则

#### 非规格化数

<FC-SUBNORMAL>

验证非规格化数（Denormal/Subnormal）的处理。

**检测点：**
- <CK-SUBN-INPUT> 非规格化输入：验证输入为非规格化数时的正确处理
- <CK-SUBN-OUTPUT> 非规格化输出：验证结果下溢到非规格化数时的正确性
- <CK-SUBN-MUL> 非规格化乘法：验证非规格化数的乘法运算
- <CK-SUBN-ADD> 非规格化加法：验证非规格化数的加法运算

### 边界值与极限情况

<FG-BOUNDARY>

验证各种边界条件和极限情况的鲁棒性。

#### 数值边界

<FC-VALUE-BOUNDARY>

验证各浮点格式的最大最小值边界。

**检测点：**
- <CK-MAX-FP16> FP16最大值：验证FP16最大值65504附近的运算
- <CK-MIN-FP16> FP16最小值：验证FP16最小正规格化数附近的运算
- <CK-MAX-FP32> FP32最大值：验证FP32最大值（约3.4e38）附近的运算
- <CK-MIN-FP32> FP32最小值：验证FP32最小正规格化数附近的运算
- <CK-MAX-FP64> FP64最大值：验证FP64最大值（约1.8e308）附近的运算
- <CK-MIN-FP64> FP64最小值：验证FP64最小正规格化数附近的运算

#### 溢出边界

<FC-OVERFLOW-BOUNDARY>

验证结果溢出的边界情况。

**检测点：**
- <CK-OVERFLOW-MUL> 乘法溢出：验证大数相乘导致溢出
- <CK-OVERFLOW-ADD> 加法溢出：验证大数相加导致溢出
- <CK-OVERFLOW-TO-INF> 溢出至无穷：验证溢出时结果为无穷大
- <CK-OVERFLOW-FLAG> 溢出标志：验证溢出时fflags的溢出位正确设置

#### 下溢边界

<FC-UNDERFLOW-BOUNDARY>

验证结果下溢的边界情况。

**检测点：**
- <CK-UNDERFLOW-MUL> 乘法下溢：验证小数相乘导致下溢
- <CK-UNDERFLOW-SUB> 减法下溢：验证接近值相减导致下溢
- <CK-UNDERFLOW-TO-ZERO> 下溢至零：验证下溢时结果为零（或非规格化数）
- <CK-UNDERFLOW-FLAG> 下溢标志：验证下溢时fflags的下溢位正确设置

### 异常标志

<FG-EXCEPTION-FLAGS>

验证io_fflags输出的各种异常标志位的正确性。

#### 无效操作标志

<FC-FLAG-INVALID>

验证无效操作（Invalid Operation）异常标志。

**检测点：**
- <CK-INV-0INF> 0×Inf：验证0乘以无穷大时设置无效操作标志
- <CK-INV-INFSUB> Inf-Inf：验证无穷大减无穷大时设置无效操作标志
- <CK-INV-NAN-OP> NaN操作：验证涉及NaN的运算设置无效操作标志
- <CK-INV-SNAN> 信号NaN：验证sNaN触发无效操作标志

#### 除零标志

<FC-FLAG-DIVZERO>

验证除零（Division by Zero）异常标志（在FMA中可能不常见）。

**检测点：**
- <CK-DZ-CHECK> 除零检查：验证是否有除零情况（FMA可能不适用）

#### 溢出标志

<FC-FLAG-OVERFLOW>

验证溢出（Overflow）异常标志。

**检测点：**
- <CK-OF-MUL> 乘法溢出：验证大数相乘时设置溢出标志
- <CK-OF-ADD> 加法溢出：验证大数相加时设置溢出标志
- <CK-OF-ROUND> 舍入溢出：验证舍入导致溢出时设置标志

#### 下溢标志

<FC-FLAG-UNDERFLOW>

验证下溢（Underflow）异常标志。

**检测点：**
- <CK-UF-MUL> 乘法下溢：验证小数相乘时设置下溢标志
- <CK-UF-SUB> 减法下溢：验证接近值相减时设置下溢标志
- <CK-UF-DENORM> 非规格化：验证结果为非规格化数时的下溢标志

#### 不精确标志

<FC-FLAG-INEXACT>

验证不精确（Inexact）异常标志。

**检测点：**
- <CK-NX-ROUND> 舍入不精确：验证舍入导致精度损失时设置不精确标志
- <CK-NX-OVERFLOW> 溢出不精确：验证溢出时同时设置不精确标志
- <CK-NX-UNDERFLOW> 下溢不精确：验证下溢时同时设置不精确标志

### 输入有效性

<FG-INPUT-VALIDITY>

验证对无效输入的处理和鲁棒性。

#### 无效操作码

<FC-INVALID-OPCODE>

验证超出有效范围的操作码（9-15）的处理。

**检测点：**
- <CK-OP-9> 操作码9：验证opcode=9时的行为（应为无效）
- <CK-OP-15> 操作码15：验证opcode=15时的行为
- <CK-OP-INVALID-RESULT> 无效操作码结果：验证无效操作码时的输出可预测性

#### 无效舍入模式

<FC-INVALID-ROUNDING>

验证超出有效范围的舍入模式（5-7）的处理。

**检测点：**
- <CK-RM-5> 舍入模式5：验证round_mode=5时的行为
- <CK-RM-7> 舍入模式7：验证round_mode=7时的行为
- <CK-RM-INVALID-RESULT> 无效舍入模式结果：验证无效舍入模式时的处理

#### 无效浮点格式

<FC-INVALID-FORMAT>

验证无效的浮点格式选择（fp_format=3）的处理。

**检测点：**
- <CK-FMT-3> 格式11：验证fp_format=3时的行为
- <CK-FMT-INVALID-RESULT> 无效格式结果：验证无效格式时的输出可预测性

### 多格式综合验证

<FG-MULTI-PRECISION>

验证不同浮点格式下的全面功能正确性。

#### FP16完整验证

<FC-FP16-FULL>

验证FP16格式下的各种操作和特殊情况。

**检测点：**
- <CK-FP16-ALL-OPS> 所有操作码：验证FP16下9种操作码的正确性
- <CK-FP16-ROUNDING> 舍入模式：验证FP16下5种舍入模式
- <CK-FP16-SPECIAL> 特殊值：验证FP16的NaN、Inf、零处理
- <CK-FP16-OVERFLOW> 溢出处理：验证FP16易溢出的特性

#### FP32完整验证

<FC-FP32-FULL>

验证FP32格式下的各种操作和特殊情况。

**检测点：**
- <CK-FP32-ALL-OPS> 所有操作码：验证FP32下9种操作码的正确性
- <CK-FP32-ROUNDING> 舍入模式：验证FP32下5种舍入模式
- <CK-FP32-SPECIAL> 特殊值：验证FP32的NaN、Inf、零处理
- <CK-FP32-PRECISION> 精度验证：验证FP32的23位尾数精度

#### FP64完整验证

<FC-FP64-FULL>

验证FP64格式下的各种操作和特殊情况。

**检测点：**
- <CK-FP64-ALL-OPS> 所有操作码：验证FP64下9种操作码的正确性
- <CK-FP64-ROUNDING> 舍入模式：验证FP64下5种舍入模式
- <CK-FP64-SPECIAL> 特殊值：验证FP64的NaN、Inf、零处理
- <CK-FP64-PRECISION> 精度验证：验证FP64的52位尾数精度

---

**文档版本**：v1.0  
**创建日期**：2025-12-03  
**作者**：AI验证工程师  
**说明**：本文档定义了VectorFloatFMA的功能分组、功能点和检测点，为后续测试用例开发和覆盖率分析提供基础框架。

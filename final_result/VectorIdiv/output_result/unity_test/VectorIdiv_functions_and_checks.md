# VectorIdiv 功能点与检测点描述

## DUT 整体功能描述

VectorIdiv是一个向量整数除法器，支持多种位宽的整数除法运算，采用SRT-4算法实现。该模块能够并行处理多个除法运算，支持有符号和无符号除法操作，遵循RISC-V标准标量整数乘除法规范。

### 端口接口说明

**输入端口：**
- `clock`：时钟信号，1位，驱动时序电路
- `reset`：复位信号，1位，用于初始化电路状态
- `io_sew`：元素宽度选择，2位，控制操作数位宽（00=8位，01=16位，10=32位，11=64位）
- `io_sign`：符号位选择，1位，0=无符号除法，1=有符号除法
- `io_dividend_v`：被除数向量，128位，包含多个待除元素
- `io_divisor_v`：除数向量，128位，包含多个除数元素
- `io_flush`：刷新操作信号，1位，用于清除流水线中的操作
- `io_div_in_valid`：输入数据有效信号，1位，表示输入数据准备就绪
- `io_div_out_ready`：输出数据准备好接收信号，1位，表示下游准备好接收结果

**输出端口：**
- `io_d_zero`：除零标志向量，16位，每个bit对应一个元素的除零状态
- `io_div_in_ready`：输入数据准备好接收信号，1位，表示模块准备好接收新数据
- `io_div_out_valid`：输出数据有效信号，1位，表示输出结果有效
- `io_div_out_q_v`：商向量，128位，包含各元素的除法商结果
- `io_div_out_rem_v`：余数向量，128位，包含各元素的除法余数结果

**控制接口：**
- 握手协议：采用valid/ready握手协议进行数据流控制
- 流水线控制：支持多级流水线操作和刷新机制

## 功能分组与检测点

### DUT测试API

<FG-API>

#### 向量除法运算功能

<FC-VECTOR-DIVISION>

提供VectorIdiv的核心向量除法运算接口，支持多种精度和符号模式的并行除法运算。这是DUT的主要功能实现，涵盖了所有配置下的除法操作。

**检测点：**
- <CK-UNSIGNED-8> 8位无符号除法：验证SEW=00且io_sign=0时的8位无符号整数除法运算
- <CK-SIGNED-8> 8位有符号除法：验证SEW=00且io_sign=1时的8位有符号整数除法运算
- <CK-UNSIGNED-16> 16位无符号除法：验证SEW=01且io_sign=0时的16位无符号整数除法运算
- <CK-SIGNED-16> 16位有符号除法：验证SEW=01且io_sign=1时的16位有符号整数除法运算
- <CK-UNSIGNED-32> 32位无符号除法：验证SEW=10且io_sign=0时的32位无符号整数除法运算
- <CK-SIGNED-32> 32位有符号除法：验证SEW=10且io_sign=1时的32位有符号整数除法运算
- <CK-UNSIGNED-64> 64位无符号除法：验证SEW=11且io_sign=0时的64位无符号整数除法运算
- <CK-SIGNED-64> 64位有符号除法：验证SEW=11且io_sign=1时的64位有符号整数除法运算
- <CK-PARALLEL> 并行处理：验证同一向量中多个元素同时进行除法运算的正确性
- <CK-QUOTIENT> 商计算：验证除法运算的商计算正确性，遵循向零取整规则
- <CK-REMAINDER> 余数计算：验证除法运算的余数计算正确性，满足被除数=除数×商+余数
- <CK-IDENTITY> 除法恒等式：验证所有正常情况下的除法恒等式成立

### 基础除法运算功能

<FG-BASIC-DIVISION>

包含VectorIdiv的基本除法运算功能，涵盖不同精度和符号模式的基础运算。

#### 有符号除法功能

<FC-SIGNED-DIV>

实现有符号整数除法运算，支持8位、16位、32位、64位精度，遵循RISC-V有符号除法规范。

**检测点：**
- <CK-POSITIVE-POS> 正数除正数：验证两个正数相除的正确性，如10/3=3余1
- <CK-POSITIVE-NEG> 正数除负数：验证正数除负数的正确性，如10/(-3)=-3余1
- <CK-NEGATIVE-POS> 负数除正数：验证负数除正数的正确性，如(-10)/3=-3余-1
- <CK-NEGATIVE-NEG> 负数除负数：验证负数除负数的正确性，如(-10)/(-3)=3余-1
- <CK-TRUNC-TOWARD-ZERO> 向零取整：验证有符号除法向零取整的正确性
- <CK-REMAINDER-SIGN> 余数符号：验证余数符号与被除数符号相同（非零结果时）
- <CK-PRECISION-8> 8位精度：验证8位有符号除法的边界和精度
- <CK-PRECISION-16> 16位精度：验证16位有符号除法的边界和精度
- <CK-PRECISION-32> 32位精度：验证32位有符号除法的边界和精度
- <CK-PRECISION-64> 64位精度：验证64位有符号除法的边界和精度

#### 无符号除法功能

<FC-UNSIGNED-DIV>

实现无符号整数除法运算，支持8位、16位、32位、64位精度，遵循RISC-V无符号除法规范。

**检测点：**
- <CK-BASIC> 基本运算：验证基本无符号除法运算，如10/3=3余1
- <CK-LARGE-NUMBERS> 大数运算：验证大数相除的正确性
- <CK-ZERO-DIVIDEND> 零被除数：验证零作为被除数时的结果（商=0，余数=0）
- <CK-UNITY-DIVISOR> 单位除数：验证除数为1时的结果（商=被除数，余数=0）
- <CK-PRECISION-8> 8位精度：验证8位无符号除法的最大值运算
- <CK-PRECISION-16> 16位精度：验证16位无符号除法的最大值运算
- <CK-PRECISION-32> 32位精度：验证32位无符号除法的最大值运算
- <CK-PRECISION-64> 64位精度：验证64位无符号除法的最大值运算

### 边界条件处理功能

<FG-BOUNDARY-HANDLING>

包含各种边界条件和特殊情况的处理功能，确保除法器在极端情况下的正确行为。

#### 除零处理功能

<FC-DIVIDE-BY-ZERO>

处理除数为零的特殊情况，按照RISC-V规范设置商和余数的特殊值。

**检测点：**
- <CK-ZERO-DETECTION> 除零检测：验证能够正确检测除数为零的情况
- <CK-DZERO-FLAGS> 除零标志：验证io_d_zero标志位的正确设置
- <CK-QUOTIENT-ONES> 商全一：验证除零时商设置为全1（所有位为1）
- <CK-REMAINDER-DIVIDEND> 余数等于被除数：验证除零时余数等于被除数
- <CK-PARTIAL-ZERO> 部分除零：验证向量中部分元素除零时的处理
- <CK-ALL-ZERO> 全部除零：验证向量中所有元素都除零时的处理
- <CK-MIXED-ZERO> 混合除零：验证向量中部分元素正常、部分元素除零的处理

#### 溢出处理功能

<FC-OVERFLOW-HANDLING>

处理有符号除法的溢出情况，主要发生在最小负数除以-1时。

**检测点：**
- <CK-OVERFLOW-DETECTION> 溢出检测：验证能够正确检测有符号除法溢出
- <CK-MIN-NEG-DIV-MINUS1> 最小负数除-1：验证-2^(L-1)/(-1)的溢出处理
- <CK-QUOTIENT-DIVIDEND> 商等于被除数：验证溢出时商等于被除数
- <CK-REMAINDER-ZERO> 余数为零：验证溢出时余数为零
- <CK-NO-UNSIGNED-OVERFLOW> 无符号无溢出：验证无符号除法不会发生溢出
- <CK-PRECISION-8> 8位溢出：验证8位有符号除法的溢出情况（-128/-1）
- <CK-PRECISION-16> 16位溢出：验证16位有符号除法的溢出情况（-32768/-1）
- <CK-PRECISION-32> 32位溢出：验证32位有符号除法的溢出情况（-2147483648/-1）
- <CK-PRECISION-64> 64位溢出：验证64位有符号除法的溢出情况（-9223372036854775808/-1）

### 向量化处理功能

<FG-VECTORIZATION>

包含向量化并行处理的相关功能，确保多个元素能够正确、独立地进行除法运算。

#### 并行运算功能

<FC-PARALLEL-OPERATION>

实现向量中多个元素的并行除法运算，确保元素间的独立性和正确性。

**检测点：**
- <CK-SINGLE-ELEMENT> 单元素：验证向量中只有一个有效元素时的运算
- <CK-MULTIPLE-ELEMENTS> 多元素：验证向量中多个元素同时运算的正确性
- <CK-ELEMENT-INDEPENDENCE> 元素独立性：验证各元素运算结果互不影响
- <CK-MIXED-OPERATIONS> 混合运算：验证同一向量中不同元素进行不同类型运算
- <CK-MAX-PARALLELISM> 最大并行度：验证最大并行元素数量的运算
- <CK-UNIFORM-SEW> 统一SEW：验证所有元素使用相同SEW时的运算
- <CK-UNIFORM-SIGN> 统一符号：验证所有元素使用相同样式时的运算

#### 向量数据管理功能

<FC-VECTOR-DATA-MANAGEMENT>

处理向量数据的打包、解包和元素访问，确保数据在向量中的正确组织。

**检测点：**
- <CK-DATA-PACKING> 数据打包：验证被除数和除数数据在向量中的正确打包
- <CK-DATA-UNPACKING> 数据解包：验证商和余数数据从向量中的正确解包
- <CK-ELEMENT-ALIGNMENT> 元素对齐：验证各元素在向量中的正确对齐
- <CK-SEW-CONSISTENCY> SEW一致性：验证SEW设置与元素位宽的一致性
- <CK-CROSS-LANE> 跨通道处理：验证跨越向量通道的元素处理
- <CK-PARTIAL-VECTOR> 部分向量：验证部分向量元素有效时的处理

### 流水线控制功能

<FG-PIPELINE-CONTROL>

包含流水线操作和控制的相关功能，确保数据流的正确性和时序的准确性。

#### 握手协议功能

<FC-HANDSHAKE-PROTOCOL>

实现输入和输出的握手协议，控制数据在流水线中的流动。

**检测点：**
- <CK-INPUT-HANDSHAKE> 输入握手：验证io_div_in_valid和io_div_in_ready的握手逻辑
- <CK-OUTPUT-HANDSHAKE> 输出握手：验证io_div_out_valid和io_div_out_ready的握手逻辑
- <CK-BACKPRESSURE> 反压处理：验证下游反压时的正确行为
- <CK-STALL-CONDITION> 停顿条件：验证各种停顿条件下的处理
- <CK-READY-VALID-TIMING> 时序关系：验证ready和valid信号的时序关系
- <CK-DATA-VALIDITY> 数据有效性：验证有效信号与数据的一致性

#### 流水线操作功能

<FC-PIPELINE-OPERATION>

管理流水线的各级操作，包括数据推进、刷新和状态维护。

**检测点：**
- <CK-PIPELINE-ADVANCE> 流水线推进：验证数据在流水线中的正确推进
- <CK-FLUSH-OPERATION> 刷新操作：验证io_flush信号对流水线的刷新功能
- <CK-FLUSH-TIMING> 刷新时序：验证刷新操作的正确时序
- <CK-OPERATION-OVERLAP> 操作重叠：验证多个操作在流水线中的重叠处理
- <CK-LATENCY-CONSISTENCY> 延迟一致性：验证运算延迟的一致性
- <CK-THROUGHPUT> 吞吐率：验证流水线的最大吞吐率

#### 状态控制功能

<FC-STATE-CONTROL>

控制模块的各种工作状态，包括空闲、工作、错误等状态的管理。

**检测点：**
- <CK-IDLE-STATE> 空闲状态：验证模块空闲时的状态和行为
- <CK-BUSY-STATE> 忙碌状态：验证模块工作时的状态和行为
- <CK-ERROR-STATE> 错误状态：验证错误条件下的状态处理
- <CK-STATE-TRANSITION> 状态转换：验证各状态间的正确转换
- <CK-RESET-RECOVERY> 复位恢复：验证复位后的状态恢复
- <CK-EXCEPTION-HANDLING> 异常处理：验证各种异常情况的处理

### 配置和控制功能

<FG-CONFIGURATION-CONTROL>

包含模块配置和控制的相关功能，确保各种配置下的正确工作。

#### 精度配置功能

<FC-PRECISION-CONFIG>

配置和控制运算精度，通过SEW信号选择8位、16位、32位或64位运算。

**检测点：**
- <CK-SEW-00> SEW=00配置：验证8位运算配置的正确性
- <CK-SEW-01> SEW=01配置：验证16位运算配置的正确性
- <CK-SEW-10> SEW=10配置：验证32位运算配置的正确性
- <CK-SEW-11> SEW=11配置：验证64位运算配置的正确性
- <CK-SEW-SWITCH> SEW切换：验证运行时SEW配置的切换
- <CK-INVALID-SEW> 无效SEW：验证无效SEW值的处理

#### 符号配置功能

<FC-SIGN-CONFIG>

配置和控制运算符号模式，通过io_sign信号选择有符号或无符号运算。

**检测点：**
- <CK-UNSIGNED-MODE> 无符号模式：验证io_sign=0时的无符号运算模式
- <CK-SIGNED-MODE> 有符号模式：验证io_sign=1时的有符号运算模式
- <CK-SIGN-SWITCH> 符号切换：验证运行时符号模式的切换
- <CK-MIXED-SIGN> 混合符号：验证不同元素使用不同符号模式的情况
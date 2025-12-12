# BUG3 分析报告：FP32 NaN 值处理错误

## 1. 问题概述
**BUG描述**：针对 FP32 格式高 32 位结果的 NaN 处理分支中，错误地使用了 `32'h7FC00001` 作为 NaN 的值。
**相关规范**：RISC-V Instruction Set Manual Volume I: Unprivileged Architecture

## 2. 规范原文引用与位置

根据 `riscv-unprivileged.pdf` 文档，RISC-V 架构明确定义了浮点单元生成的标准 NaN（Canonical NaN）的位模式。

### Canonical NaN 定义
在 **Chapter 20 "F" Extension for Single-Precision Floating-Point, Version 2.2** 的 **20.3. NaN Generation and Propagation** 章节中：

> "Except when otherwise stated, if the result of a floating-point operation is NaN, it is the canonical NaN. The canonical NaN has a positive sign and all significand bits clear except the MSB, a.k.a. the quiet bit. For single-precision floating-point, this corresponds to the pattern **0x7fc00000**."
>
> *()*

### 向量扩展中的 NaN 处理
如果该 FP32 位于向量操作中（由“高 32 位”推测可能涉及 SIMD 或向量寄存器），根据 `riscv-v-spec-1.0.pdf` 的 **13. Vector Floating-Point Instructions** 章节：

> "The vector floating-point instructions have the same behavior as the scalar floating-point instructions with regard to NaNs."
>
> *()*

这意味着向量扩展同样遵循非特权级规范中关于 Canonical NaN 的定义。

## 3. 修正建议
实现中使用的 `32'h7FC00001` 是一个非规范的 NaN 值（尾数部分最低位为1）。根据规范，生成的 NaN 应修正为 **`32'h7FC00000`**。
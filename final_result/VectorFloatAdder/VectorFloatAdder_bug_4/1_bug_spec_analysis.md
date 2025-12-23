
---

## 1. IEEE 754-2008 标准分析 (IEEE Standard for Floating-Point Arithmetic)

该标准是浮点运算的核心依据。此缺陷违反了标准中关于“必须提供状态标志”以及“无效操作触发条件”的规定。

### 1.1 违规条款：异常标志的设置 (Status Flags)
* **章节**: **Clause 7. Default Exception Handling**
* **子章节**: **7.1 Overview**
* **相关原文**:
    > "A floating-point system shall provide a status flag for each type of exception... The default action for an exception is to flag the occurrence of the exception..."
    > "For each exception... the corresponding status flag shall be set to 1."
* **分析**: 标准强制要求当异常发生时，对应的标志位必须置 1。Bug 代码在应触发 NV 异常时返回 `5'h0`（全 0），直接违反了此“Set to 1”的强制性要求。

### 1.2 违规条款：无效操作的定义 (Invalid Operation)
* **章节**: **Clause 7. Default Exception Handling**
* **子章节**: **7.2 Invalid Operation**
* **相关原文**:
    > "The invalid operation exception is signaled if an operand is invalid for the operation to be performed."
    > "The default result of an operation that signals the invalid operation exception shall be a quiet NaN..."
    > "Conditions that arise... include: a) Any operation on a signaling NaN..."
    > "c) Addition or subtraction: magnitude subtraction of infinities, such as (+Infinity) + (-Infinity)."
* **分析**: 缺陷描述中提到“涉及信号 NaN（sNaN）输入、无效的无穷大运算”。IEEE 754 明确规定这些场景必须 Signal（触发）Invalid Operation 异常。逻辑错误导致该信号未被传出，导致硬件行为与标准定义不符。

---

## 2. RISC-V 非特权级架构规范分析 (RISC-V Unprivileged ISA)

RISC-V 架构手册定义了硬件如何将 IEEE 754 异常映射到具体的寄存器（`fcsr` / `fflags`）。

### 2.1 违规条款：浮点状态寄存器定义 (Floating-Point Control and Status Register)
* **文档**: `riscv-unprivileged.pdf`
* **章节**: **Chapter 8. "F" Standard Extension for Single-Precision Floating-Point** (注：FP16/Half-precision 遵循相同的 CSR 状态位布局)
* **子章节**: **8.2 Floating-Point Control and Status Register**
* **相关内容**:
    * **fflags 寄存器布局**:
        * Bit 4: **NV** (Invalid Operation)
        * Bit 3: **DZ** (Divide by Zero)
        * Bit 2: **OF** (Overflow)
        * Bit 1: **UF** (Underflow)
        * Bit 0: **NX** (Inexact)
* **违规分析**: RISC-V 规范要求硬件维护 `fflags` 寄存器。如果加法器模块输出了错误的 `5'h0`，导致流水线写回阶段未能将 Bit 4 (NV) 置位，上层软件（如操作系统或数学库）读取 `fcsr` 时将获得错误的状态信息。

### 2.2 违规条款：异常标志的积累 (Accrued Exceptions)
* **相关原文**:
    > "Floating-point exceptions are accrued in the exception flags... The exception flags are sticky: once set, they remain set until explicitly cleared by software."
* **分析**: 虽然 Bug 是“覆盖”当前操作的标志，但由于它返回了 `0`，如果软件依赖单次指令的异常反馈，或者这是一个全新计算序列的开始，`NV` 位将错误地保持为 0。

---

## 3. RISC-V 向量扩展规范分析 (RISC-V Vector Extension)

如果该 FP16 加法器被用于向量单元（V-Extension），则还涉及向量特定的错误处理。

### 3.1 向量异常处理
* **文档**: `riscv-v-spec-1.0.pdf`
* **章节**: **Section 13. Vector Floating-Point Instructions**
* **子章节**: **13.1. Vector Floating-Point Exception Handling**
* **相关原文**:
    > "Vector floating-point exceptions are always accrued into the standard scalar fflags register."
* **分析**: 即使在向量运算中，底层加法器产生的异常也必须汇总到全局 `fflags` 中。如果底层 FP16 单元逻辑有误（屏蔽了 NV），向量指令执行后，全局状态寄存器同样会缺失该异常标志，影响 `vadd.vv` 等指令的正确性。

---
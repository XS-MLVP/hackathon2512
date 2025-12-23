# FMIN/FMAX 逻辑反转 Bug 规范分析报告

**Bug 描述**: 
在硬件描述语言生成的逻辑中，多路复用器（Mux）的选择信号与数据路径交叉连接。
- **错误逻辑**: `(is_max ? _result_min_T_19 : 16'h0) | (is_min ? _result_max_T_21 : 16'h0)`
- **表现**: 指令 `FMAX` 输出更小的值，指令 `FMIN` 输出更大的值（语义完全反转）。

该行为严重违反了以下三个上传文档中的核心规范。

---

## 1. IEEE 754-2008 (Floating-Point Arithmetic)
**文档**: `IEEE754-2008.pdf`
**关键定义**: `minNum` 和 `maxNum` 操作

### 相关章节与内容
- **Section 5.3.1 General operations** (Page 19)
    - 规范定义了 `minNum(x, y)` 和 `maxNum(x, y)` 为通用操作。
    - **原文引用**: 
      > "minNum(x, y) is the canonicalized number x if x < y, x if y is NaN, y if x is NaN..."
      > "maxNum(x, y) is the canonicalized number y if x < y, y if x is NaN, x if y is NaN..."
    
- **符号零的处理 (Signed Zero)**
    - IEEE 754 规定 `-0.0` 也就是 `x` 小于 `+0.0` 也就是 `y`。
    - **Bug 影响**: 如果逻辑反转，`FMAX(-0.0, +0.0)` 本应返回 `+0.0`，现在的 Bug 会导致其返回 `-0.0`，破坏了数值比较的符号正确性。

### 违规分析
Bug 导致硬件实现的算术行为与 IEEE 754-2008 第 5.3.1 节定义的数学属性完全对立。

---

## 2. RISC-V Unprivileged Spec (Scalar ISA)
**文档**: `riscv-unprivileged.pdf`
**关键指令**: `FMIN.S`, `FMAX.S`, `FMIN.D`, `FMAX.D`

### 相关章节与内容
- **Chapter 11: "F" Standard Extension for Single-Precision Floating-Point**
- **Section 11.6: Single-Precision Floating-Point Computational Instructions** (Page 66-67 in standard versions)
    - **原文引用**:
      > "FMIN.S and FMAX.S perform the single-precision IEEE 754-2008 minNum and maxNum operations, respectively."
      > "If both inputs are NaNs, the result is the canonical NaN. If only one operand is a NaN, the result is the numerical operand."

- **Chapter 12: "D" Standard Extension (Double-Precision)**
    - 同样适用于 `FMIN.D` 和 `FMAX.D`。

### 违规分析
RISC-V 标量指令集直接映射到 IEEE 754 操作。
- **正确行为**: `is_max` 信号有效时，应执行 `maxNum` (选择较大值/非NaN)。
- **Bug 行为**: `is_max` 信号有效时，选择了 `_result_min` (即 `minNum` 的结果)。
这导致处理器在执行标准汇编指令 `fmax.s` 时，实际上在执行 `fmin.s` 的功能，破坏了软件的控制流假设。

---

## 3. RISC-V Vector Spec (Vector ISA)
**文档**: `riscv-v-spec-1.0.pdf`
**关键指令**: `vfmin.vv`, `vfmax.vv` (及其标量变体 `vfmin.vf` 等)

### 相关章节与内容
- **Section 13.13: Vector Floating-Point Min/Max Instructions** (Page 78)
    - **指令列表**: `vfmin.vv`, `vfmin.vf`, `vfmax.vv`, `vfmax.vf`
    - **原文引用**:
      > "vfmin and vfmax perform the IEEE 754-2008 minNum and maxNum operations respectively."

- **Section 14.4: Vector Floating-Point Reduction Instructions**
    - **指令**: `vfredmin.vs`, `vfredmax.vs` (有序规约)
    - **原文引用**:
      > "The vfredmax.vs instruction ... produces the maximum of the vector elements..."

### 违规分析
如果上述 Bug 位于共享的浮点执行单元（FPU）后端：
1. **并行错误**: 向量指令 `vfmax.vv` 会导致整个向量寄存器组中的每个元素都错误地计算为最小值。
2. **规约错误**: 在执行 `vfredmax`（寻找最大值）算法时，由于硬件实际上在取最小值，最终规约结果将是整个向量中的最小值，而非最大值。
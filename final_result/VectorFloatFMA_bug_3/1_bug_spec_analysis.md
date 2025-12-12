# BUG 3 分析报告：FMA 运算中 fp_c 符号位反转失效

## BUG 描述分析
**描述**：FMA 浮点运算指令实现过程中，在需要符号反转的 FMA 操作时，`fp_c` 的符号位没有正确反转。

**分析**：
FMA（Fused Multiply-Add）指令通常包含四种变体：`FMADD`, `FMSUB`, `FNMSUB`, `FNMADD`。标准的基础 FMA 操作定义为 $(a \times b) + c$。
当执行减法类操作（如 `FMSUB`）时，数学上等同于 $(a \times b) + (-c)$。此时，作为加数/减数的操作数 `fp_c`（即 RISC-V 中的 `rs3`）需要进行符号反转。如果该功能失效，`FMSUB` 将错误地变为 `FMADD`，或者 `FNMADD` 将错误地变为 `FNMSUB`。

## 原始 Spec 依据

### 1. RISC-V Instruction Set Manual (Unprivileged)
RISC-V 手册明确定义了 FMA 指令族中四个指令的具体数学行为，明确指出了哪些指令需要对 `rs3`（即 `fp_c`）进行减法（即符号反转）操作。

**相关文档**: `riscv-unprivileged.pdf`
**位置**: Chapter 20 "F" Extension for Single-Precision Floating-Point, Section 20.6, **Page 124**

> **原文引用**:
> * **FMADD.S**: "FMADD.S computes $(rs1 \times rs2) + rs3$."
> * **FMSUB.S**: "FMSUB.S computes $(rs1 \times rs2) - rs3$."
> * **FNMSUB.S**: "FNMSUB.S computes $-(rs1 \times rs2) + rs3$."
> * **FNMADD.S**: "FNMADD.S computes $-(rs1 \times rs2) - rs3$."

**分析**:
根据上述定义：
* 对于 `FMSUB.S`，操作数 `rs3` (`fp_c`) 前是减号，意味着硬件实现时必须反转 `fp_c` 的符号位。
* 对于 `FNMADD.S`，操作数 `rs3` (`fp_c`) 前也是减号，同样需要反转符号位。
BUG 描述中的“需要符号反转”即对应上述两种情况。

### 2. IEEE Standard 754-2008
IEEE 754 标准定义了融合乘加（fusedMultiplyAdd）的数学基础，并规定了该操作应视为无限精度计算后只进行一次舍入。

**相关文档**: `IEEE754_2008.pdf`
**位置**: Clause 2 Definitions, **Page 4**; Clause 5 Operations, **Page 21**

> **原文引用 (Page 4)**:
> "2.1.28 fusedMultiplyAdd: The operation fusedMultiplyAdd(x, y, z) computes $(x \times y) + z$ as if with unbounded range and precision, rounding only once to the destination format."

> **原文引用 (Page 21)**:
> "formatOf-fusedMultiplyAdd(source1, source2, source3): The operation fusedMultiplyAdd(x, y, z) computes $(x \times y) + z$..."

**分析**:
IEEE 标准定义的基础操作是“加法” ($+z$)。因此，为了实现 RISC-V 规定的 `FMSUB` ($(a \times b) - c$)，实现者必须在调用基础 FMA 单元之前，在逻辑上将 $c$ 的符号取反，从而利用标准加法器实现减法逻辑。

### 3. 符号位处理与零结果 (Sign Bit Handling)
如果符号位没有正确反转，不仅数值结果错误，还会导致零结果的符号错误（例如 $(+x) + (-x)$ 应该得到 $+0$ 或 $-0$，具体取决于舍入模式，但如果符号未反转变为 $(+x) + (+x)$，结果将完全不同）。

**相关文档**: `IEEE754_2008.pdf`
**位置**: Clause 6.3 The sign bit, **Page 35**

> **原文引用**:
> "When $(a \times b) + c$ is exactly zero, the sign of fusedMultiplyAdd(a, b, c) shall be determined by the rules above for a sum of operands."

**分析**:
若 `fp_c` 符号反转失败，本应产生零结果的操作（如 $5 \times 2 - 10$）将变为 $5 \times 2 + 10 = 20$，导致严重的功能错误。

## 总结
该 BUG 违反了 `riscv-unprivileged.pdf` 第 124 页关于 `FMSUB` 和 `FNMADD` 指令的数学定义。硬件在处理这两种指令时，未能依据 Spec 要求执行 `- rs3` 操作（即未能正确反转 `fp_c` 的符号位），导致实际执行的运算变成了 `FMADD` 或 `FNMSUB` 的逻辑。
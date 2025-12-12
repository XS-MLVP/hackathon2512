# Bug Spec Analysis FMA

## BUG 分析
**BUG 描述：** FMA 指令在特定零值条件下返回错误的异常标志，原本应返回正确的 UF (Underflow, 下溢) 和 NX (Inexact, 不精确) 标志，实际返回的标志位组合错误。

**相关架构规则分析：**
该 BUG 涉及浮点运算中的**融合乘加 (FMA)** 操作、**下溢 (Underflow)** 的判定条件以及**微小值 (Tininess)** 的检测时机。
1.  **FMA 定义：** 必须先以无限精度计算乘法和加法，最后只进行一次舍入。
2.  **Tininess 检测时机：** RISC-V 架构强制规定 Tininess 的检测必须在**舍入后 (after rounding)** 进行。如果硬件在舍入前检测（即根据无限精度的中间结果判定），会导致在结果舍入为 0 或最小规格化数时产生错误的 UF 标志。
3.  **异常逻辑：**
    * **UF (Underflow):** 当结果微小 (tiny, 非零且绝对值小于最小规格化数) 且不精确 (inexact) 时触发。
    * **NX (Inexact):** 当舍入后的结果与无限精度结果不一致时触发。
    * **精确零值：** 如果结果恰好为 0，既不是 Tiny 也不是 Inexact，因此不应设置 UF 或 NX。

---

## RISC-V Instruction Set Manual, Volume I: Unprivileged Architecture

### 1. 单精度浮点 FMA 指令定义
该部分定义了单精度 FMA 指令，强调了融合操作的必要性（中间不做舍入）。

* [cite_start]**内容：** "Floating-point fused multiply-add instructions require a new standard instruction format... FMADD.S computes $(rs1 \times rs2) + rs3$." [cite: 3218]
* **关联性：** 确立了 FMA 的数学定义，是验证运算结果的基础。
* **来源文件：** `riscv-unprivileged.pdf`
* **位置：** Page 124 (Section 20.6)

### 2. Tininess 检测时机 (Underflow 的关键判定)
这是 RISC-V 规范中关于下溢判定的核心强制要求。如果硬件实现为了兼容其他架构而在“舍入前”检测 Tininess，就会导致此 BUG。

* [cite_start]**内容：** "Operations on subnormal numbers are handled in accordance with the IEEE 754-2008 standard. In the parlance of the IEEE standard, **tininess is detected after rounding**." [cite: 3217]
* **关联性：** BUG 描述提到在“特定零值”条件下出错。如果中间结果微小（Tiny）但舍入后变为 0，若按“舍入后”检测，则 0 不是 Tiny，不应报 UF；若按“舍入前”检测，则可能错误地报出 UF。这解释了标志位组合错误的原因。
* **来源文件：** `riscv-unprivileged.pdf`
* **位置：** Page 122 (Section 20.4)

### 3. 累积异常标志 (UF 和 NX)
定义了状态寄存器中 UF 和 NX 的位定义。

* **内容：** Table 26 lists the Accrued exception flags.
    * **UF:** Underflow
    * [cite_start]**NX:** Inexact [cite: 3216]
* **关联性：** 定义了 BUG 描述中提到的具体标志位。
* **来源文件：** `riscv-unprivileged.pdf`
* **位置：** Page 121 (Section 20.2)

---

## IEEE Standard for Floating-Point Arithmetic (IEEE 754-2008)

### 1. FusedMultiplyAdd (FMA) 的数学定义
定义了“单次舍入”的要求，这区别于先乘后加（两次舍入）。

* [cite_start]**内容：** "The operation fusedMultiplyAdd(x, y, z) computes $(x \times y) + z$ as if with unbounded range and precision, rounding only once to the destination format." [cite: 1021]
* **关联性：** 只有严格遵守“无限精度中间结果”并只做一次舍入，才能正确判断结果是否为精确的 0 或微小值。
* **来源文件：** `IEEE754_2008.pdf`
* **位置：** Page 33 / PDF Page 21 (Section 5.4.1)

### 2. 下溢 (Underflow) 定义
定义了触发 UF 标志的充分必要条件：结果微小 (Tiny) 且 不精确 (Inexact)。

* [cite_start]**内容：** "The underflow exception shall be signaled when a tiny non-zero result is detected... In addition, under default exception handling for underflow, **if the rounded result is inexact**... the **underflow flag shall be raised and the inexact... exception shall be signaled**." [cite: 1599, 1606]
* **关联性：** 解释了 UF 和 NX 之间的联动关系。如果结果微小但是精确的（例如精确抵消为极小值），则不应触发 UF。BUG 提到的“错误的标志位组合”可能指出现了 UF 但没出现 NX，或者反之。
* **来源文件：** `IEEE754_2008.pdf`
* **位置：** Page 50 / PDF Page 38 (Section 7.5)

### 3. 不精确 (Inexact) 定义
* [cite_start]**内容：** "Unless stated otherwise, if the rounded result of an operation is inexact—that is, it differs from what would have been computed were both exponent range and precision unbounded—then the inexact exception shall be signaled." [cite: 1611]
* **关联性：** 在零值条件下，如果 FMA 的结果精确抵消为 0（例如 $1.0 \times 1.0 - 1.0$），则结果是精确的，不应设置 NX。
* **来源文件：** `IEEE754_2008.pdf`
* **位置：** Page 50 / PDF Page 38 (Section 7.6)
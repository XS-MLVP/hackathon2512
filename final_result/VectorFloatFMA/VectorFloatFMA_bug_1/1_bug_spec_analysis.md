# Float16 Lane 0 操作数 C 符号反转分析

## 1. BUG 分析 (BUG Analysis)
**Bug 描述：**
在 Float16 Lane 0 的运算控制逻辑中，操作数 C 的符号位被错误地取反了，导致加/减运算被错误地反转。


## 2. 规范参考 (Specification References)

### 2.1. IEEE Std 754-2008 (浮点算术标准)
**相关性：** 定义了融合乘加运算（FusedMultiplyAdd）的基础数学行为。标准要求该运算被计算为 $(x \times y) + z$，且不应对 $z$（操作数 C）进行隐式的符号修改。

* **文件：** `IEEE754_2008.pdf`
* **章节：** 5.4.1 Arithmetic operations
* **页码：** 19 (基于标准页码，参考 5.4.1 节)

> **Quote:**
> "formatOf-fusedMultiplyAdd(x, y, z) computes (x × y) + z as if with unbounded range and precision, rounding only once to the destination format."

**分析：**
标准明确将该运算定义为加上 `z`。对 `z`（操作数 C）取反违反了这一数学定义。


### 2.2. RISC-V Unprivileged Spec (标量基准规范)
**相关性：** 尽管 Bug 出现在 "Lane 0"（向量），但其算术逻辑通常遵循标量 "F"（单精度）或 "Zfh"（半精度）扩展的定义。向量规范在算术核心部分引用了这些行为。

* **文件：** `riscv-unprivileged.pdf`
* **章节：** 11.6 Single-Precision Floating-Point Computational Instructions (以及扩展至 Float16 的 Zfh)
* **页码：** (通常在完整文档的第 11 或 12 章附近)

> **Quote (Definition of Fused Multiply-Add):**
> "FMADD.S computes (rs1 × rs2) + rs3."

> **Quote (Sign Injection Instructions - Context for correct sign handling):**
> "FSGNJ.S rx, ry, ry moves y to x (which is the IEEE copy operation). FSGNJN.S rx, ry, ry moves the negation of y to x (which is the IEEE negate operation)."

**分析：**
规范清晰地区分了保留符号的操作（FMADD 中的 `rs3`）与取反符号的操作（例如 `FNMADD` 或 `FNMSUB`）。
* `FMADD`: $(rs1 \times rs2) + rs3$
* `FMSUB`: $(rs1 \times rs2) - rs3$
* 该 Bug 导致 `FMADD` 的行为类似于 `FMSUB`。


### 2.3. RISC-V Vector Specification (v1.0 向量规范)
**相关性：** 该 Bug 特别提到了 **"Lane 0"** 和 **Float16**，这涉及在 `SEW=16`（16位元素）上运行的向量扩展（`v` 扩展）。该文档定义了向量 FMA 指令如何处理加数。

* **文件：** `riscv-v-spec-1.0.pdf`
* **章节：** 13.6. Vector Single-Width Floating-Point Fused Multiply-Add Instructions
* **页码：** (参考 13.6 节逻辑)

> **Quote (Instruction Encoding & Behavior):**
> "vfmadd.vv vd, vs1, vs2"
> "vfmadd.vf vd, vs1, rs2"
>
> "Operation: vd[i] = (vs1[i] * vs2[i]) + vd[i]" (for .vv variant where vd is the accumulator/Operand C)

**分析：**
在 RISC-V 向量 FMA 指令中，目的寄存器 `vd` 通常充当第三个操作数（操作数 C/加数）。
* 正确行为：`vd[i] + (product)`
* Bug 行为：`-vd[i] + (product)` 或 `(product) - vd[i]`
* 规范要求将累加值（`vd[i]`）相加。反转其符号位是对 `vfmadd` 指令定义的这一功能性违反。

**关于 Float16 (SEW=16) 的具体说明：**
> **Quote (Section 13.2):**
> "Vector floating-point instructions follow the standard scalar floating-point behavior... The floating-point operation is performed according to the standard floating-point rules for the selected SEW."

这证实了 16位向量 FMA 必须遵守第 2.1 节中引用的 IEEE 754 规则。


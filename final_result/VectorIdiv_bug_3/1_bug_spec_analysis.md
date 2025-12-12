# **向量整数除法有符号数处理逻辑原始规格说明**

本文档专门针对 **向量整数除法（Vector Integer Division）** 中有符号数（Signed Integer）的处理逻辑进行规范溯源分析。依据 RISC-V 标准，有符号除法在处理除零和溢出时的行为有特定规定。

## **1\. 向量扩展规范 (Vector Spec)**

向量规范明确声明向量整数除法指令（vdiv.vv, vdiv.vx 等）的行为等同于标量整数除法。

* **来源文档**：riscv-v-spec-1.0.pdf  
* **章节**：11. Vector Integer Arithmetic Instructions  
* **小节**：11.11. Vector Integer Divide Instructions  
* **关键原文**："The divide and remainder instructions are equivalent to the RISC-V standard scalar integer multiply/divides, with the same results for extreme inputs."  
  **译文**：除法和取余指令等同于 RISC-V 标准标量整数乘/除法，对于极端输入（如除零、溢出）具有相同的结果。  
  **分析**：这意味着我们需要参考标量规范来确定有符号除法的具体行为，特别是针对有符号数的溢出情况。

## **2\. 非特权级基础规范 (Unprivileged Spec)**

标量规范详细定义了有符号除法在各种边界条件下的行为。

* **来源文档**：riscv-unprivileged.pdf  
* **章节**：Chapter 12\. "M" Extension for Integer Multiplication and Division  
* **小节**：12.2. Division Operations  
* **关键定义**：  
  规范通过表格定义了有符号除法（DIV）的特殊情况处理：

| 异常条件 (Condition) | 被除数 (Dividend) | 除数 (Divisor) | DIVU/DIVW 结果 | REMU/REMW 结果 | DIV/DIVW 结果 | REM/REM 结果 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Division by zero** | $x$ | $0$ | $2^L \- 1$ | $x$ | $-1$ | $x$ |
| **Overflow (signed only)** | $-2^{L-1}$ | $-1$ | \- | \- | $-2^{L-1}$ | $0$ |

*   
  *注：*$L$ *为数据宽度（XLEN 或 32）。对于向量，即为 SEW (Selected Element Width)。*  
  **关于溢出 (Overflow) 的特别说明**："Signed division overflow occurs only when the most-negative integer is divided by \-1. The quotient of a signed division with overflow is equal to the dividend, and the remainder is zero. Unsigned division overflow cannot occur."  
  **译文**：有符号除法溢出仅发生在最小负整数（most-negative integer, 即 $-2^{L-1}$）除以 \-1 时。有符号除法溢出的商等于被除数（即 $-2^{L-1}$），余数为 0。无符号除法不会发生溢出。  
  **结论**：  
  1. **有符号除零**：结果为 \-1（即全 1 的位模式）。  
  2. **有符号溢出**：当被除数为最小负数（如 8 位下的 \-128，16 位下的 \-32768 等）且除数为 \-1 时，商为该最小负数本身（因为正数范围无法表示该绝对值），余数为 0。

## **3\. 规格总结：向量有符号整数除法行为**

对于指令 vdiv.vv, vdiv.vx (有符号除法) 和 vrem.vv, vrem.vx (有符号取余)，硬件必须满足以下规格：

1. **正常计算**：执行标准的补码除法运算。  
2. **除零处理**：  
   * vdiv (商)：写入全 1 (-1)。  
   * vrem (余)：写入被除数 (x)。  
3. **溢出处理 (Overflow)**：  
   * **条件**：被除数 \= $-2^{SEW-1}$ (最小负数)，除数 \= $-1$。  
   * vdiv (商)：写入 $-2^{SEW-1}$ (即被除数本身)。  
   * vrem (余)：写入 0。

**验证注意**：在 VectorIdiv 模块验证中，除了除零测试外，必须包含针对有符号数溢出的边界测试用例（即最小负数除以 \-1）。如果 DUT 在此情况下产生了错误的结果（例如尝试返回无法表示的正数）或产生了异常，则属于 **Bug**。
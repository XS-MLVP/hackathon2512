# **向量整数除法除零异常检测功能原始规格说明**

本文档专门针对 **向量整数除法（Vector Integer Division）** 在除数为零时的行为进行规范溯源分析。依据 RISC-V 标准，该操作**不应产生异常陷阱（Trap）**。

## **1\. 向量扩展规范 (Vector Spec)**

向量规范未直接定义整数除零的语义，而是明确声明其行为继承自标量架构。

* **来源文档**：riscv-v-spec-1.0.pdf  
* **章节**：11. Vector Integer Arithmetic Instructions  
* **小节**：11.11. Vector Integer Divide Instructions  
* **关键原文**："The divide and remainder instructions are equivalent to the RISC-V standard scalar integer multiply/divides, with the same results for extreme inputs."  
  **译文**：除法和取余指令等同于 RISC-V 标准标量整数乘/除法，对于极端输入（如除零、溢出）具有相同的结果。  
  **分析**：此条款确立了向量整数除法（vdiv.vv, vdiv.vx 等）在遇到除零情况时，必须遵循标量整数除法（div）的处理逻辑。

## **2\. 非特权级基础规范 (Unprivileged Spec)**

由于向量规范引用了标量规范，因此标量规范中关于整数除零的定义即为向量整数除零的权威定义。

* **来源文档**：riscv-unprivileged.pdf  
* **章节**：Chapter 12\. "M" Extension for Integer Multiplication and Division  
* **小节**：12.2. Division Operations  
* 关键定义：  
  规范通过表格严格定义了除零时的返回值，而非异常行为。

| 异常条件 (Condition)     | 被除数 (Dividend) | 除数 (Divisor) | DIVU/DIVW 结果   | REMU/REMW 结果 | DIV/DIVW 结果 | REM/REM 结果 |
|:-------------------- |:-------------- |:------------ |:-------------- |:------------ |:----------- |:---------- |
| **Division by zero** | $x$            | $0$          | 2^L \- 1  (全1) | $x$ (被除数)    | $-1$ (全1)   | $x$ (被除数)  |

* *注：*$L$ *为数据宽度（XLEN 或 32）。对于向量，即为 SEW (Selected Element Width)。*  
* **设计原理 (Rationale)**："We considered raising exceptions on integer divide by zero... However, this would be the only arithmetic trap in the standard ISA... and would require language implementers to interact with the execution environment’s trap handlers for this case."  
  **译文**：我们曾考虑在整数除零时引发异常... 然而，这将是标准 ISA 中唯一的算术陷阱... 并且需要语言实现者在这种情况下与执行环境的陷阱处理程序进行交互（这会增加复杂性）。  
  **结论**：RISC-V 架构设计上有意避免了整数除零产生硬件异常。

## **3\. 规格总结：向量整数除法除零行为**

基于上述文档，对于指令 vdiv.vv, vdiv.vx, vdiv.vi 及其对应的无符号版本和取余版本，当某个元素的除数为 0 时，硬件必须满足以下规格：

1. **不产生 Trap**：流水线不应因除零而停止或跳转至异常处理程序。  
2. **不设置标志位**：整数运算（不同于浮点）不涉及 fcsr 状态寄存器，无“除零”标志位。  
3. **返回特定值**：  
   * **除法 (Quotient)**：目标元素应写入全 1 的位模式（即 \-1）。  
   * **取余 (Remainder)**：目标元素应写入被除数的值（即 x % 0 \= x）。

**验证注意**：在黑客马拉松项目的 VectorIdiv 模块中，如果出现除零导致处理挂起或产生异常信号，则属于 **不符合 Spec 的 Bug**。硬件可能需要内部检测除零（如 PPT 中提到的 io\_d\_zero 信号），但该检测应仅用于生成上述规定的默认结果，而不应触发系统级异常。
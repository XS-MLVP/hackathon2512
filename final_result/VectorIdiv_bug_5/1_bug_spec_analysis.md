# **向量整数除法余数输出逻辑原始规格说明**

本文档专门针对 **向量整数除法（Vector Integer Division）** 中的余数（Remainder）输出逻辑进行规范溯源分析。依据 RISC-V 标准，余数的符号和数值必须满足特定的代数关系。

## **1\. 向量扩展规范 (Vector Spec)**

向量规范明确声明向量整数除法指令（vrem.vv, vrem.vx 等）的行为等同于标量整数除法。

* **来源文档**：riscv-v-spec-1.0.pdf  
* **章节**：11. Vector Integer Arithmetic Instructions  
* **小节**：11.11. Vector Integer Divide Instructions  
* **关键原文**："The divide and remainder instructions are equivalent to the RISC-V standard scalar integer multiply/divides, with the same results for extreme inputs."  
  **译文**：除法和取余指令等同于 RISC-V 标准标量整数乘/除法，对于极端输入具有相同的结果。  
  **分析**：这表明向量取余指令的逻辑与标量指令完全一致，因此需要参考非特权级规范来确定具体的余数定义。

## **2\. 非特权级基础规范 (Unprivileged Spec)**

标量规范详细定义了除法和取余运算满足的数学关系，以及余数的符号规则。

* **来源文档**：riscv-unprivileged.pdf  
* **章节**：Chapter 12\. "M" Extension for Integer Multiplication and Division  
* **小节**：12.2. Division Operations  
* **关键定义**：  
  1. **代数关系 (Algebraic Relationship)**:"For both signed and unsigned division, except in the case of overflow, it holds that $dividend \= divisor \\times quotient \+ remainder$."  
     **译文**：对于有符号和无符号除法，除了溢出情况外，始终满足：被除数 \= 除数 × 商 \+ 余数。  
  2. **符号规则 (Sign of Remainder)**:"For REM, the sign of a nonzero result equals the sign of the dividend."  
     **译文**：对于有符号取余指令 (REM)，非零结果的符号等于被除数（dividend）的符号。  
  3. **零与溢出情况 (Zero and Overflow)**:  
     * **除以零**：余数等于被除数（$x$）。"The remainder of division by zero equals the dividend."  
     * **有符号溢出**（仅限最小负数除以 \-1）：余数为 0。"The quotient of a signed division with overflow is equal to the dividend, and the remainder is zero."

## **3\. 规格总结：向量整数除法余数输出逻辑**

对于向量取余指令 vrem.vv, vrem.vx (有符号) 和 vremu.vv, vremu.vx (无符号)，硬件输出必须满足以下逻辑：

1. 基本余数公式：  
   $$余数 \= 被除数 \- (除数 \\times 商)$$

   其中“商”是向零取整（rounding towards zero）的结果。  
2. 符号一致性 (仅有符号数)：  
   若余数不为 0，其符号位必须与被除数一致。  
   * $(+A) \\% (+B) \\rightarrow \+R$  
   * $(+A) \\% (-B) \\rightarrow \+R$  
   * $(-A) \\% (+B) \\rightarrow \-R$  
   * $(-A) \\% (-B) \\rightarrow \-R$  
3. **特殊情况输出**：  
   * **除数为 0**：余数 \= 被除数。  
   * **溢出 (最小负数 / \-1)**：余数 \= 0。

**验证注意**：在验证 VectorIdiv 的余数输出时，需重点检查被除数为负数的情况，确保余数符号正确（与被除数相同），而非与除数相同或总是为正。此外，需验证除数为 0 时余数是否正确返回了被除数。
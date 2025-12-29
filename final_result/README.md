# 万众一芯黑客马拉松(第一期)赛题解析

## 赛题介绍

万众一芯黑客马拉松(第一期)以“AI驱动开源芯片验证”为主题，聚焦基于大语言模型的硬件验证智能体 UCAgent 在芯片验证领域的实际应用。

**比赛要求参赛队伍在限定时间内，利用 UCAgent 人机协同进行单元测试模块验证，分析 Fail 测试用例，找出赛题中隐藏的 Bug。**

本次比赛提供了“香山”处理器的3个向量运算模块，向每个模块中分别手工注入了5个 Bug，共计15个 Bug 供参赛队伍发现和分析。比赛的更多细节请前往比赛仓库(https://github.com/XS-MLVP/hackathon2512)查看。

本次比赛，来自中国科学院软件研究所的 HASSLab 小队实力强劲，找到了本次比赛的所有 Bug，荣获两个赛道的第一名。该队伍的答案目前已收录在比赛仓库中，供大家参考。

在后续交流中，众多参赛者表示对 UCAgent 有浓厚的兴趣，希望将其应用到实际工程中，以及希望继续参与黑客马拉松的后续比赛。

但不少参赛者表示无法充分发挥 UCAgent 在模块验证中的作用，因此下面将以本次黑客马拉松的赛题为例，向大家介绍如何利用 UCAgent 以及大模型来高效地完成一个模块的验证工作。

希望本教程能帮助大家更加熟悉 UCAgent 的使用，在后续比赛中取得更好的名次，以及将 UCAgent 应用到自己的工程实践中。

UCAgent 手册：https://open-verify.cc/mlvp/docs/ucagent
UCAgent 仓库：https://github.com/XS-MLVP/UCAgent
hackathon2512 仓库：https://github.com/XS-MLVP/hackathon2512

## 赛题解析

### 基于 UCAgent 的芯片验证

UCAgent 可以快速构建待测模块(Design Under Test, DUT)的基础测试环境以及测试用例，从而复现较简单的 Bug。对于复杂情况，通过与大模型的交互，基于已有环境快速地生成指定功能点的测试用例，从而复现潜在的 Bug。甚至通过大模型直接分析模块源代码，分析潜在的缺陷代码并针对性地生成测试用例。

### 大致流程

1. 先使用 UCAgent 为 Origin 版本 DUT 生成基础测试环境和测试用例。
2. 使用 Bug 版本 DUT 替换原 DUT 后，执行 pytest 测试，检查是否出现 Fail。
3. 若出现 Fail，则分析对应测试用例，发现潜在的 Bug。
4. 若未出现 Fail ，说明当前测试用例不足以覆盖 Bug 情况。在 UCAgent 生成的测试用例的基础和模板上，**使用大模型为指定功能点生成测试用例**，尝试触发 Bug。
5. 对于更加复杂的情况，**直接使用大模型分析源代码**，针对可能的缺陷代码以及严苛的触发条件，针对性地生成测试用例，并多轮随机生成测试激励，从而触发 Bug。

下面以 VectorIdiv 模块赛题作为演示，展示 UCAgent 的详细使用步骤以及相关命令。

### 使用步骤

#### (1) 文件准备

在 UCAgent 项目的 example 目录下创建 VectorIdiv 目录，并将 hackathon2512 仓库中提供的 Origin 版本 VectorIdiv.v 文件和 Spec 文件拷贝到该目录下。

#### (2) 构建 DUT

```bash
# 在 UCAgent 目录下执行 make 命令执行 Picker 打包
cd UCAgent
make init_VectorIdiv
```
执行该命令后，将在 UCAgent 项目下创建 output 目录，其中 VectorIdiv 目录存放 Picker 打包后的 python 包，VectorIdiv_RTL 存放源代码副本，后续 UCAgent 生成的所有文件都将保存在 output 目录下。

#### (3) 收集测试用例

以 UCAgent 的 MCP 模式为例，我们选用了 Copilot CLI 的 Claude Sonnet 4.5 模型，其模型能力较强，能取得更好的验证结果。

```bash
# 启动 UCAgent 的 MCP 模式
make mcp_VectorIdiv

# 事先安装与配置好 Copilot 后，另起终端，在 output 目录下启动 CLI
cd UCAgent/output
copilot

# 选择好模型后，在 CLI 中输入提示词后，芯片验证过程开始运行
> /model
> 请通过工具RoleInfo获取你的角色信息和基本指导，然后完成任务。请使务必用工具ReadTextFile读取文件，这样才能让UCAgent知晓你阅读了哪些文件。
```
等待 UCAgent 完成全部芯片验证阶段，全自动验证过程持续约3小时左右。

#### (4) 验证测试用例
```bash
# 进入用例目录，运行测试
cd output/unity_test/tests
pytest

# 得到类似输出
...
collected 41 items                                                             

test_VectorIdiv_api_basic.py ..........                                  [ 24%]
test_VectorIdiv_boundary.py ...                                          [ 31%]
test_VectorIdiv_comprehensive.py .....                                   [ 43%]
test_VectorIdiv_control.py ....                                          [ 53%]
test_VectorIdiv_division.py ............                                 [ 82%]
test_VectorIdiv_env_fixture.py .....                                     [ 95%]
test_VectorIdiv_remainder.py ..                                          [100%]
===== 41 passed, 5 warnings in 10.94s =====
```
上述结果表明 UCAgent 共生成了41个测试用例，且全部通过测试。

#### (5) 替换 DUT，进行回归测试

重命名 output 目录为 origin，替换 example/VectorIdiv 目录下的源代码为 Bug 版本(Bug_1为例)，执行 make 命令重新构建 DUT 后，将 origin 目录下相关文件拷贝到 output 目录下。
```bash
# 文件拷贝
cp origin/unity_test output
cp origin/uc_test_report output

# 运行测试
cd output/unity_test/tests
pytest

# 获得类似以下输出
collected 41 items                                                             

test_VectorIdiv_api_basic.py ......F...                                  [ 24%]
test_VectorIdiv_boundary.py FF.                                          [ 31%]
test_VectorIdiv_comprehensive.py .....                                   [ 43%]
test_VectorIdiv_control.py ....                                          [ 53%]
test_VectorIdiv_division.py ..F..F..F...F                                [ 82%]
test_VectorIdiv_env_fixture.py .....                                     [ 95%]
test_VectorIdiv_remainder.py ..                                          [100%]
===== 7 failed, 34 passed, 5 warnings in 7.89s =====
```
在测试用例足以覆盖 Bug 的情况下，替换 DUT 后执行回归测试将出现 Fail，上述的**F**标志表示测试用例未通过，疑似存在 Bug。

**以 HASSLab 小队的实际体验，UCAgent 生成的测试用例能够复现 VectorIdiv 模块5个 Bug 中的3个。**

#### (6) Bug 分析

分析 Fail 的测试用例细节：
```python
env = <VectorIdiv_api.VectorIdivEnv object at 0x7f10384229c0>

    def test_api_VectorIdiv_check_div_zero_function(env):
        """测试除零检测API
    
        验证api_VectorIdiv_check_div_zero能正确检测除零
        """
        # 覆盖率标记
        env.dut.fc_cover["FG-DIV-I64"].mark_function("FC-DIV-ZERO-I64", test_api_VectorIdiv_check_div_zero_function,
                                                      ["CK-UNSIGNED-ZERO", "CK-ZERO-FLAG-BIT"])
    
        # 检查除数为0时的除零标志
        dzf = api_VectorIdiv_check_div_zero(env, 0, sew=3)
    
        # 对于64位模式，有2个元素，第一个元素除0应该触发标志
>       assert dzf != 0, f"除数为0时应设置除零标志，实际dzf={dzf}"
E       AssertionError: 除数为0时应设置除零标志，实际dzf=0
E       assert 0 != 0

test_VectorIdiv_api_basic.py:127: AssertionError
```
上述 Fail 的测试用例表明 d_zero 信号在除零时未被正确置 1，这与 Spec 描述不符，认定为 Bug。

#### (7) 基于大模型补充测试用例

对于复杂 Bug，UCAgent 最初生成的测试用例可能不足以触发 Bug，执行回归测试不会出现 Fail。但 UCAgent 已经构建了基础的测试环境和大部分测试用例，因此可以通过**大模型交互**，针对特定功能点补充测试用例，以 Bug_5 为例:
```bash
# 以 VSCode 的 Copilot 为例，基于提供的 Bug 提示，直接与大模型进行交互
> 请你以目前已有的测试用例为模板，为余数数值验证相关功能点补充测试用例。

# 测试用例生成完毕后，重复步骤5，替换成 Bug_5 的 DUT，然后对生成的测试文件运行测试，看能否出现 Fail
pytest test_VectorIdiv_remainder.py
```
```python
# Fail 的测试用例
env = <VectorIdiv_api.VectorIdivEnv object at 0x7f7715b23230>

    def test_remainder_value_verification(env):
        """测试余数数值验证"""
        env.dut.fc_cover["FG-REMAINDER"].mark_function("FC-REMAINDER-VALUE", test_remainder_value_verification,
                                                        ["CK-BASIC", "CK-ZERO-REMAINDER", 
                                                        "CK-MAX-REMAINDER", "CK-ALL-WIDTH"])
        
        # 测试余数计算
        q, r, _ = api_VectorIdiv_divide_simple(env, 105, 10, width=64, is_signed=False)
        # 验证：被除数 = 商×除数 + 余数
>       assert 105 == q * 10 + r, f"余数验证失败: 105 ≠ {q}×10 + {r}"
E       AssertionError: 余数验证失败: 105 ≠ 10×10 + 4
E       assert 105 == 104

test_VectorIdiv_remainder.py:30: AssertionError
```
大模型通常可以在10-20分钟内完成相应功能点的批量测试用例生成，从而触发 Bug。

#### (8) 复杂 Bug 复现

VectorIdiv 的 Bug_2 修改了选商表中的某些值，其触发条件较为苛刻。针对这类 Bug，单纯的“黑盒”测试可能无法快速地复现 Bug。因此，切换为“白盒”测试，先利用**大模型分析源代码**，从而发现潜在的缺陷，再针对性地生成测试用例从而触发。
```python
# 大模型分析发现 Bug_2 在特定条件下将被触发。因此尝试在一定输入范围内以遍历的方式，随机测试激励，从而触发 Bug。
iterations = 50000
for i in range(iterations):
    # Generate
    dividend = random.getrandbits(64)
    # Bias for Index 6 (0xE... pattern in MSB)
    r = random.random()
    if r < 0.5:
        base = random.getrandbits(60)
        divisor = (0xE << 60) | base
    elif r < 0.8:
        divisor = random.getrandbits(64)
    else:
        divisor = random.randint(1, 100000)
    if divisor == 0:
        divisor = 1
    
    q, r, _ = api_VectorIdiv_divide_simple(env, dividend, divisor, width=64, is_signed=False)
    
    # Check
    q_act = q & 0xFFFFFFFFFFFFFFFF
    r_act = r & 0xFFFFFFFFFFFFFFFF  
    q_exp = dividend // divisor
    r_exp = dividend % divisor 
    if q_act != q or r_act != r:
        print(f"Mismatch at iteration {i}")
        print(f"Dividend: {dividend} (0x{dividend:x})")
        print(f"Divisor:  {divisor} (0x{divisor:x})")
        print(f"Exp Q:    {q_exp} (0x{q_exp:x})")
        print(f"Act Q:    {q_act} (0x{q_act:x})")
        print(f"Exp R:    {r_exp} (0x{r_exp:x})")
        print(f"Act R:    {r_act} (0x{r_act:x})")
        sys.exit(1)
```
```bash
# 触发 Bug 的测试激励
Mismatch at iteration 308
Dividend: 17360576827843868672 (0xf0ed28a50782f800)
Divisor:  40627 (0x9eb3)
Exp Q:    427316238655176 (0x184a4509c9ec8)
Act Q:    427316401036592 (0x184a45a4a5d30)
Exp R:    33320 (0x8228)
Act R:    12144 (0x2f70)
```

### UCAgent 使用总结

**先使用 UCAgent 生成基础测试环境以及测试用例，复现大部分 Bug，再使用大模型针对性地生成测试用例，复现复杂 Bug。**

目前 UCAgent 仍在积极优化完善功能中，上述功能目前已初步以“随机测试用例生成”和“增量验证”的功能实现，能实现多轮随机测试用例的生成，以及对指定功能的测试用例增量式补充。后续更多的功能补充请关注 UCAgent 仓库。

## 赛题 Bug 复现与分析

比赛的15个赛题答案已经在比赛仓库中更新，大家可以下载比赛仓库后，输入命令行，直接复现 Bug。同时，提供了完善的 UCAgent 结果，供大家参考。

### VectorFloatAdder 模块

查看测试用例：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatFMA/output_result/unity_test/tests/test_VectorFloatFMA_bug.py

**Bug_1 描述：** FP16格式下，指令fmax输出较小的值，而指令fmin输出较大的值，两个操作的opcode颠倒。

查看 Bug 详细分析(由LLM生成)：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatFMA/VectorFloatFMA_bug_1/1_bug_spec_analysis.md

**Bug 复现命令：**
```bash
# 1. hackathon2512仓库下，Picker 打包
cd hackathon2512
make build_one_dut DUT_FILE=bug_file/VectorFloatAdder_bug_1.v

# 2. 将VectorFloatAdder目录下的结果拷贝到目标目录下
cp VectorFloatAdder/output_result/* dutcache/VectorFloatAdder_bug_1

# 3. 进入目录，修改output/unity_test/.pytest.ini中的report-dir为本地路径，然后执行测试
cd dutcache/VectorFloatAdder_bug_1/unity_test/tests
pytest 

# 4. 出现 Fail，分析 Bug
```
后续 Bug 复现的命令行类似，将命令行中的模块名和赛题号更改即可。

output_result 目录下，unity_test 目录下可执行的测试文件以及 UCAgent 生成的阶段验证报告，uc_test_report 目录下为覆盖率报告。

**Bug_2 描述：** FP32格式下，加法溢出到无穷时，应该输出无穷大(0x7F800000)，而不是sNaN(0x7F800001)。根据IEEE 754标准，指数全1且尾数不为0代表sNaN。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatAdder/VectorFloatAdder_bug_2/1_bug_spec_analysis.md

**Bug_3 描述：** fclass指令用于检查浮点寄存器中的值，并将其分类为一个10位的掩码写入整数寄存器。其中第8位专门用于标识sNaN。但Bug导致无法正确识别sNaN类型，对应标志位被硬编码为常量0。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatAdder/VectorFloatAdder_bug_3/1_bug_spec_analysis.md   

**Bug_4 描述：** FP16格式下，fadd操作的输入信号涉及NaN、无穷大时，fflags标志位中的无效操作标志(NV)未被正常触发。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatAdder/VectorFloatAdder_bug_4/1_bug_spec_analysis.md

**Bug_5 描述：** 在RDN舍入模式（rm=2）下，计算结果是精确零的情况下，应该输出-0.0（0x8000000000000000），但是结果是+0.0（0x0）。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatAdder/VectorFloatAdder_bug_5/1_bug_spec_analysis.md

### VectorFloatFMA 模块

查看测试用例：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatFMA/output_result/unity_test/tests/test_VectorFloatFMA_bug.py

**Bug_1 描述：** 执行Float 16 Lane 0的乘加操作时，操作数C的符号位被错误取反，a\*b+c被计算成a\*b-c。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatFMA/VectorFloatFMA_bug_1/1_bug_spec_analysis.md

**Bug_2 描述：** Float 32 Lane 1结果的NaN处理分支，输出结果使用0x7fc00001作为了NaN的值。按RISC-V标准，应该用0x7fc00000表示NaN。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatFMA/VectorFloatFMA_bug_2/1_bug_spec_analysis.md

**Bug_3 描述：** 执行64位乘法操作时，未能正确忽略操作数C，a\*b被计算成a\*b+c。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatFMA/VectorFloatFMA_bug_3/1_bug_spec_analysis.md

**Bug_4 描述：** 在RUP舍入模式（rm=3）下，无需舍入的结果被错误地向上舍入一位，结果始终差1bit。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatFMA/VectorFloatFMA_bug_4/1_bug_spec_analysis.md

**Bug_5 描述：** FP64格式下，2个极小数相乘超出表示范围时，触发下溢，但fflags标志位中下溢UF判断失效，未被置1。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorFloatFMA/VectorFloatFMA_bug_5/1_bug_spec_analysis.md

### VectorIdiv 模块


**Bug_1 描述：** 除数为零时，应触发除零异常，但对应标志信号d_zero未被置1。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorIdiv/VectorIdiv_bug_1/1_bug_spec_analysis.md

**Bug_2 描述：** SRT4算法通过查找表常量与部分余数进行比较，决定下一次迭代的商位选择(-2,-1,0,+1,+2)。但当部分余数落在456到464之间时，原本应选择+2的情况被错误判断为+1。后续迭代基于错误商值计算，导致最终商和余数均错误。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorIdiv/VectorIdiv_bug_2/1_bug_spec_analysis.md

**Bug_3 描述：** int 8格式下，符号位错误传递，int 8有符号数被当成无符号数计算。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorIdiv/VectorIdiv_bug_3/1_bug_spec_analysis.md

**Bug_4 描述：** flush信号有效时，应能够清除当前流水线中正在进行的所有操作，复位内部状态，并准备接收新的指令，或者处于空闲状态，且不应输出任何无效的计算结果。但实际当flush信号置1时，内部状态未被清除，仍在输出。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorIdiv/VectorIdiv_bug_4/1_bug_spec_analysis.md

**Bug_5 描述：** int 8格式下，余数是5的情况下被错误的计算成4。

查看 Bug 详细分析：https://github.com/XS-MLVP/hackathon2512/blob/main/final_result/VectorIdiv/VectorIdiv_bug_5/1_bug_spec_analysis.md

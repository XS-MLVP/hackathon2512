# 万众一芯黑客马拉松（第一期）优秀答案示例

## 示例概述

本仓库的 final_result 文件夹包含了 **HASSLab队**​ 在本期黑客马拉松比赛中完成的全部提交内容。该队伍在比赛规定时间内成功完成了全部 15 道找 Bug 题目，并提交了正确的答案。

## 比赛与完成情况

**参赛队伍：HASSLab 队**

**完成题目数量：15 道**

**提交结果：全部正确**

### 文件夹结构说明

final_result文件夹的组织结构如下：

```plaintext
final_result
├── VectorFloatAdder_bug_1/
│   ├── 0_bug_description.md      # Bug 描述文档
│   ├── 1_bug_spec_analysis.md    # 相关规范（Spec）分析
│   └── 2_testcase.py             # 用于验证 Bug 的 测试用例文件 
│ 
├── VectorFloatAdder_bug_2/
├── ...
└── Vectorldiv_bug_5/

```

每个 Bug 对应的子文件夹中包含三个文件：

**0_bug_description.md：** 对该 Bug 的详细描述。

**1_bug_spec_analysis.md：** 对相关设计规范（Spec）的分析，说明 Bug 与规范的偏差。

**2_testcase.py：** Python 测试用例，通过对比在无 Bug 版本的 DUT 下运行结果来验证 Bug 的存在。

## 使用与验证步骤

要运行测试用例并验证 Bug，请按以下步骤操作：

### 前置要求

1. Python 3.x
2. 题目对应的 DUT 文件夹
    
    在仓库根目录下执行：
    ```bash
    make build_one_dut DUT_FILE=bug_file/xxx_bug_x
    ```
   会在 ```dutcache/xxx_bug_x``` 路径下生成该 ```xxx_bug_x``` 题目对应的 DUT 文件夹

   最后将该 DUT 文件夹复制到对应 ```final_result/xxx_bug_x``` 题目示例文件夹下即可完成配置

### 运行步骤
以 ```VectorFloatAdder_bug_1``` 为例查看验证示例结果：

进入任意一个 Bug 文件夹，例如：
```bash
cd final_result/VectorFloatAdder_bug_1
```
将 ```2_testcase.py``` 放置在所生成的 ```VectorFloatAdder``` DUT 文件夹​下：
```bash
cp 2_testcase.py VectorFloatAdder_bug_1/VectorFloatAdder
```

运行测试用例：

```bash
cd VectorFloatAdder && python 2_testcase.py
```
得出该题目有bug的 test_case 运行结果。

将其与仓库 ```origin_file``` 文件夹中的无bug版本在对比验证，无bug版本的配置运行步骤同上。

### 注意事项

请确保测试用例在每道题目对应的 DUT 文件夹下运行。

不同题目的所对应的 DUT 不同，请使用各题目的verilog文件单独编译出的 DUT 作为对应测试用例的运行环境。

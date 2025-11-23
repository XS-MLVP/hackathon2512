## 2025-12 万众一芯黑客马拉松（第一期）

欢迎参加本次黑客马拉松活动！本次黑客马拉松以“**AI驱动开源芯片验证**”为主题，聚焦基于大语言模型的硬件验证智能体UCAgent的实际应用。各位将在限定时间内，利用UCAgent人机协同进行UT模块验证，分析Fail test cases，找出赛题中隐藏的Bug。通过参与，您不仅能体验UCAgent工具在开源验证中的便利，还能作为开发者参与到开源芯片验证的生态中。

本次活动提供了15个人工注入的Bug供大家进行发现和分析，共有两个赛道：找Bug赛道和Token效率赛道。

- **Bug分级：** 每个模块含有注入5个bug，分别对应5个RTL原文件，简单难度2个、中等难度1个、困难难度2个。
- **Bug积分：** 简单难度 100分/个，中等难度300分/个, 困难500分/个。
- **Token效率：** 效率 `E = Bug个数/消耗总Token`


### 赛道介绍

- **找Bug赛道**： 对参赛队伍按获得的Bug积分进行排名（bug数需要大于5个），前三名将获得`证书 + 现金奖励`，其他名次将获得`证书`。
- **效率赛道**：利用UCAgent API模式分析Bug，按Token效率进行排名(bug数需不少于12个)，前三名将获得`证书 + 现金奖励`，其他名次将获得`证书`。
- **额外奖励**：首位发现Origin版本中的非人工注入Bug，获得现金奖励：`500-1000元/个 + 证书`。具体金额由UT设计者给出的Bug等级来定。

注：除了效率赛道外，其他赛道可用您任何擅长的工具或者方法，不仅限于UCAgent技术路线。

### 本仓库介绍

目标：
- 提供注入Bug的RTL/Scala文件，spec参考地址等资源文件
- 提供UCAgent基本使用示例，快速生成Fail测试用例（数小时内）

目录结构：
```bash
├── Makefile                         # 主执行文件
├── README.md
├── bug_file                         # 注入bug的RTL（有混淆）
│   ├── VectorIdiv_bug_1.v
│   └── ...                          # 活动正式开启后，增加剩余文件
├── origin_file                      # 原始RTL（无混淆），由Scala文件转换而来
│   ├── VectorFloatAdder_origin.v
│   ├── VectorFloatFMA_origin.v
│   └── VectorIdiv_origin.v
├── output                           # UCAgent临时结果存放目录
├── result                           # 最终结果保存目录
├── dutcache                         # DUT-python包缓存目录，防止DUT重复编译，提升效率
└── spec                             # spec文档和验证要求文档
    ├── VectorIdiv.md                # 命名规则 {DUTNAME}.md 和 {DUTNAME}_spec.md
    ├── VectorIdiv_spec.md           # 如果有其他文件，请以 {DUTNAME}_<name>.md 的方法进行命名
    └── ...
```

UT模块Scala文件地址 (源于：https://github.com/OpenXiangShan/YunSuan)：
- VectorFloatAdder：[点击打开](https://github.com/OpenXiangShan/YunSuan/blob/master/src/main/scala/yunsuan/vector/VectorFloatAdder.scala)
- VectorFloatFMA：[点击打开](https://github.com/OpenXiangShan/YunSuan/blob/master/src/main/scala/yunsuan/vector/VectorFloatFMA.scala)
- VectorIdiv：[点击打开](https://github.com/OpenXiangShan/YunSuan/blob/master/src/main/scala/yunsuan/vector/VectorFloatFMA.scala)

其他参考文档(请从官方spec中摘取DUT相关内容作为UCAgent的输入)：

- RISC-V官方V扩展Spec：[点击打开](https://github.com/riscvarchive/riscv-v-spec/blob/master/v-spec.adoc)
- RISC-V官方ISA-Spec：[点击打开]https://docs.riscv.org/reference/isa/

### 安装依赖

OS环境：建议 ubuntu 24.04 LST （window下建议使用WSL2）

本仓库UCAgent的使用模式为： MCP + [iFlow-CLI](https://platform.iflow.cn/cli/quickstart)

请先通过pip安装好[UCAgent](https://github.com/XS-MLVP/UCAgent)及其依赖

其他依赖：
- Nodejs v20+: 建议通过 nvm [https://github.com/nvm-sh/nvm](https://github.com/nvm-sh/nvm)安装Nodejs
- npx: 安装命令`npm install -g npx`， 用于免安装执行最新版本 iFlow
- Tmux: [https://tmuxcheatsheet.com/how-to-install-tmux/](https://tmuxcheatsheet.com/how-to-install-tmux/)

iFlow的MCP和Hooks配置（~/.iflow/settings.json）建议如下：

```json
{
  ...
  "mcpServers": {
    "unitytest": {
      "httpUrl": "http://127.0.0.1:5000/mcp",
      "timeout": 100000     # 调到100s，很多case运行时间比较长，防止超时
    }
  },
  "allowMCPServers": [
    "unitytest"
  ],
  "hooks": {
  "Stop": [{"hooks": [{
"type": "command",
"command": "tmux send-keys `ucagent --hook-message 'continue|quit'`; sleep 1; tmux send-keys Enter",
"timeout": 3
    }]}]
  }
}
```

上述Hooks用于让iFlow在Tmux中可以自动继续执行而不需要人工干预。

### 开始运行


```bash
# 请先完成依赖安装

git clone https://github.com/XS-MLVP/hackathon2512.git

cd hackathon2512

# 编译DUT（可选）
make build_dut_cache

# 自动顺序验证，基于Tmux（需要提前完成iFlow登录认证）
#   VTARGET 参数：用于指定待验证的RTL文件（多文件用`;`隔开，支持通配符）
#   TIMES 参数：用于指定UCAgent的验证次数（重复验证的次数）
#   UCARGS 参数：传递自定义参数到UCAgent
#   如果没有发现DUT，会自动编译
make run # 默认VTARGET为bug_file/*.v;origin_file/*.v
make run VTARGET=bug_file/*.v
make run VTARGET=bug_file/VectorIdiv_bug_1.v TIMES=3

# 修改UCAgent默认参数
TEMPLATE_MUST_FAIL=false make run VTARGET=origin_file/VectorIdiv_origin.v

# 单独启动DUT的MCP服务
make run_seq_mcp VTARGET=bug_file/VectorIdiv_bug_1.v PORT=5000

# 继续上次UCAgent， 不加 CONTINUE=1 会清空工作目录重新运行
make run_seq_mcp VTARGET=bug_file/VectorIdiv_bug_1.v PORT=5000 CONTINUE=1

# 清空临时数据
make clean

# 清空所有
make clean_all
```

结果位于`result/<port>/`目录下, port为每次启动时随机选择的MCP端口。
PORT 可以通过参数指定 eg: `make run PORT=5005`。

请根据您的需要修改`Makefile`，例如支持 Claude Code 等。

### 成果提交

#### 找Bug赛道

- **有提交次数限制，每天不能超过 10 次**
- 提交内容（每个Bug都需要的材料）：
  - Bug分析描述：Bug表现描述+可能的原因分析（需要精简）
  - 测试用例：复现Bug的Fail测试用例（需要能运行，可打包整个UCAgent给出的结果，给出case对应文件和名称）
  - Spec分析：Bug对应Spec的片段分析（与Spec如何不符，需要给出Spec来源连接）
- 多个Bug同时提交时，请按目录进行区分

成果提交内容示例：
```bash
bug25112001.zip/       # 压缩包以： 时间 + 第几次提交命名，例如25年11月20日第01次提交
├── bug1_overflow  # 第一个bug
│   ├── bug_description.md       # bug分析描述
│   ├── bug_spec_analysis.md     # spec分析
│   └── test_cases/              # 可执行的Fail测试用例
└── bug2_carray    # 第二个bug
│   ├── bug_description.md
│   ├── bug_spec_analysis.md
│   └── test_cases/
└── ...

```

#### 效率赛道

提交要求同上 + Langfuse系统中Token消耗截图（需要截出可区分用户的唯一标识）。

#### 额外奖励

提交要求同“找Bug赛道”。

#### 提交地址
- Bug提交地址：http://82.157.193.13:10101 （暂未开通）


**API 模式接入Token监控**

- Langfuse监控地址：http://82.157.193.13:10102（暂未开通，用于效率赛道记录 UCAgent 的 Token 使用情况）
- 在UCAgent的yaml配置中填写(例如：~/.ucagent/setting.yaml)：
```
langfuse:
  enable: $(ENABLE_LANGFUSE, true)
  public_key: $(LANGFUSE_PUBLIC_KEY, <YOUR_LANGFUSE_PUBLIC_KEY>)
  secret_key: $(LANGFUSE_SECRET_KEY, <YOUR_LANGFUSE_SECRET_KEY>)
  base_url: $(LANGFUSE_URL, http://82.157.193.13:10102)
```


Bug提交账号、langfuse的key等，会在活动正式开始时私信发送，如有任何疑问请联系群主。

### 其他

- 可以使用任何 LLM，开源或者商业
- 可以使用任何 Code Agent，例如 Claude Code、Gemimi CLI、TRAE等
- 如果发现Origin中相同的Bug，先提交者获得奖励

~~关于取得更好结果的碎碎念：~~

- 例子中的Spec给的太简单了，我能否给更完整的Spec呢？例如IEEE的标准，NEMU中的C代码实现等。
- UCAgent API模式中，原有的Context管理也简单，简单优化就可能提升个10倍效率。
- 既然都是注入Bug，我是否可以提前用Origin版本生成大量的测试用例，当发布bug的时候直接替换Python包快速跑出Fail用例，先人一步。
- 我可以先通过MCP的方式把Bug都跑出来，然后把Bug描述给LLM去用API模式跑效率赛道，这样时间代价更小。
- 既然例子中提供了Batch执行模式，我可以让LLM晚上连续工作，我白天分析其结果。
- LLM存在随机性，每次跑出的结果都不一样，因此可以多跑，充分发挥“随机性”在验证工作中的作用。
- 为何用iFLow作为例子呢？因为它API免费，国内开源大模型几乎都有：GLM 4.6, Qwen3-coder, MinMax M2，Kimi-k2 thinking 等。
- 使用更强的模型，对于一些商业模型，训练数据中就包含了 RSIC-V 的 Specification，不给完整spec也能发现bug。

# Wolf-Silicon 
# 野狼 Silicon
## 项目简介：大模型多智能体自动数字IC前端流程

### 故事设定

在广袤的大草原上，有一群精通数字IC设计的野狼（多智能体），他们听从明月之神（用户）的旨意开展项目工作。

### 角色介绍

- Project Manager Wolf：项目负责人，理解用户需求、编写设计规格文档；审阅验证报告，决定是否询问用户
- CModel Engineer Wolf ：根据设计文档编写、编译CModel
- Design Engineer Wolf ：根据项目文档、CModel编写RTL代码
- Verification Engineer Wolf：根据项目文档、CModel、RTL代码编写验证代码、编写验证报告

## 注意AI安全，谨防野狼伤人！

本项目涉及AI生成代码及自动运行，为保证安全，务必在安全的容器或者沙箱环境中运行！

本项目涉及AI生成代码及自动运行，为保证安全，务必在安全的容器或者沙箱环境中运行！

本项目涉及AI生成代码及自动运行，为保证安全，务必在安全的容器或者沙箱环境中运行！

## 使用说明（粗糙版）

### 环境准备

- 准备一个安全的容器或者沙箱环境（建议 Ubuntu 22.04）
- 环境内安装好 g++ 和 verilator，python 3.10+
- `pip install openai`

### 准备配置文件

在 `wolf_silicon` 目录下创建 `model_client.py` 文件，填入你的API KEY和服务地址内容如下：

```python
from openai import OpenAI

mc = OpenAI(
    api_key="xx-xxxxxx",
    base_url="xxxxxxxxxx"
)
```

### 确认模型类型

`wolf_silicon/agent.py` 中可指定调用的模型名称，目前主要用 `gpt-4o` 开展了实验。

```python
class WolfSiliconAgent(object):
    def __init__(self,...) -> None:
        # config
        self.MODEL_NAME = "gpt-4o"
        self.TRANSLATION_MODEL_NAME = "gpt-3.5-turbo" # 用于翻译产生中文日志的模型，可以用便宜的模型
        # ...
```

修改模型之后，要注意不同模型的 role 不一样，自己根据报错修改吧！

### 运行

```bash
python3 wolf_silicon/main.py --req xxx.md # 制定一个文本的需求文档
```

例如

```bash
python3 wolf_silicon/main.py --req challenge/lemmings3.md
```


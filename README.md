# Wolf-Silicon

** 施工中 **

## 项目简介：多智能体的自动化RTL生成过程

### 角色介绍

- Project Manager：项目负责人，理解用户需求、编写设计文档（spec.md)
- CModel Engineer：根据设计文档编写、编译CModel
- Design Engineer：根据项目文档、CModel编写RTL代码
- Verification Engineer：根据项目文档、CModel、RTL代码编写验证代码、编写验证报告

### 角色工具技能

- Project Manager：review_user_reqirements, ask_user_questions, write_spec, review_spec, review_verification_report
- CModel Engineer：codebase_tools, review_spec, review_verification_report, compile_cmodel, run_cmodel
- Design Engineer：codebase_tools, review_spec, review_verification_report, run_cmodel, lint_design
- Verification Engineer：codebase_tools, review_spec, run_cmodel, compile_testbench, run_testbench, write_verification_report

### 上下游关系

| 角色 | 输入 | 输出 | 下游角色 |
| --- | --- | --- | --- |
| Project Manager | 用户需求，验证报告 | 设计文档 | CModel Engineer |
| CModel Engineer | 设计文档，验证报告 | CModel | Design Engineer |
| Design Engineer | 设计文档，CModel，验证报告 | RTL代码 | Verification Engineer |
| Verification Engineer | 设计文档，CModel，RTL代码 | 验证代码，验证报告 | Project Manager |

### 角色工作流程

1. Project Manager

| 环境状态 | 工作流 |
| --- | --- |
| 有用户需求，没有设计文档或者设计文档落后 | review_user_reqirements, write_spec |
| 有用户需求，有设计文档，没有验证报告或者验证报告落后 | review_user_reqirements, write_spec |
| 有用户需求，有设计文档，有验证报告 | review_verification_report, 判断任务结束或者更新设计文档继续 |

1. CModel Engineer

| 环境状态 | 工作流 |
| --- | --- |
| 有设计文档，没有CModel或者CModel落后 | review_spec, 设计 cmodel, compile_cmodel, run_cmodel |
| 有设计文档，有CModel，没有验证报告或者验证报告落后 | review_spec, 设计 cmodel, compile_cmodel, run_cmodel |
| 有设计文档，有CModel，有验证报告 | review_spec, 设计 cmodel, compile_cmodel, run_cmodel |
| 缺少设计文档 | 退回项目经理处理 |

3. Design Engineer

| 环境状态 | 工作流 |
| --- | --- |
| 有设计文档，有CModel，没有设计代码或者设计代码落后 | review_spec, run_cmodel, 编写设计代码， lint_design |
| 有设计文档，有CModel，有设计代码，没有验证报告或者验证报告落后 | review_spec, run_cmodel, 编写设计代码， lint_design |
| 有设计文档，有CModel，有设计代码，有验证报告 | review_verification_report, review_spec, run_cmodel, 编写设计代码，lint_design |
| 缺少设计文档或缺少CModel | 退回项目经理处理 |

4. Verification Engineer

| 环境状态 | 工作流 |
| --- | --- |
| 有设计文档，有CModel，有设计代码，没有验证代码或者验证代码落后 | review_spec, run_cmodel, 编写验证代码，compile_testbench, run_testbench, write_verification_report |
| 有设计文档，有CModel，有设计代码，有验证代码，没有验证报告或者验证报告落后 | review_spec, run_cmodel, 编写验证代码，compile_testbench, run_testbench, write_verification_report |
| 有设计文档，有CModel，有设计代码，有验证代码，有验证报告 | review_verification_report, review_spec, run_cmodel, 编写验证代码，compile_testbench, run_testbench, write_verification_report |
| 缺少设计文档或缺少CModel或缺少设计代码 | 退回项目经理处理 |
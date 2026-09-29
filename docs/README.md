# CatCommStudio 文档导航

本目录使用 Markdown 维护产品需求、功能设计、流程和实现记录，图示使用 Mermaid。当前项目处于需求与交互设计阶段；新增模板和占位文件不代表功能已确认、已实现或已验证。

## 1. 从哪里开始

| 内容 | 入口 | 维护内容 |
| --- | --- | --- |
| 产品方向 | [产品定义](product-definition.md) | 目标用户、范围、已确认方向、候选功能与待确认问题 |
| 基础库能力 | [通信能力映射](communication-capabilities.md) | 接口核对依据、能力限制与产品操作的对应关系 |
| 需求明细 | 下方的模块需求表 | 用户目标、功能规则、异常处理与验收条件 |
| 用户与系统流程 | [连接流程](flows/connection.md)、[进程生命周期](flows/process-lifecycle.md) | 操作步骤、状态变化、异常与恢复路径 |
| 技术设计 | [多进程架构](multiprocess-architecture.md)、[功能设计模板](design/_template.md) | 模块职责、接口、数据与资源生命周期 |
| 实现和验证 | [实现状态表](implementation-status.md)、[验证记录模板](verification/_template.md) | 代码依据、实际执行的检查与已知限制 |
| 协作方式 | [提交规范](../CONTRIBUTING.md)、[Git 工作流](git-workflow.md) | 分支、提交、验证与发布约定 |

## 2. 目录结构

```text
docs/
├── README.md
├── product-definition.md
├── communication-capabilities.md
├── multiprocess-architecture.md
├── git-workflow.md
├── requirements/
│   ├── _template.md              # 单条需求模板
│   ├── common.md                 # 通用收发、日志、配置等
│   ├── process.md                # 功能实例和进程管理
│   ├── serial.md
│   ├── network.md
│   ├── ble.md
│   ├── usb.md
│   └── hid.md
├── flows/
│   ├── _template.md              # 流程与状态模板
│   ├── connection.md
│   └── process-lifecycle.md
├── design/
│   └── _template.md              # 功能实现方案模板
├── implementation-status.md
└── verification/
    └── _template.md              # 实际验证记录模板
```

## 3. 模块需求

| 模块 | 文档 | 需求编号中的模块名 |
| --- | --- | --- |
| 通用能力 | [通用需求](requirements/common.md) | `COMMON` |
| 功能实例与进程 | [进程需求](requirements/process.md) | `PROCESS` |
| 串口 | [串口需求](requirements/serial.md) | `SERIAL` |
| 网络 | [网络需求](requirements/network.md) | `NETWORK` |
| 蓝牙 | [BLE 需求](requirements/ble.md) | `BLE` |
| USB | [USB 需求](requirements/usb.md) | `USB` |
| HID | [HID 需求](requirements/hid.md) | `HID` |

以上文件是填写入口，尚未完成已有候选功能的逐条拆分。新增模块时补充此表，不能仅根据基础库接口或品牌图标推定产品范围。

## 4. 编号与状态

需求编号使用 `REQ-{MODULE}-{NNN}`，例如 `REQ-SERIAL-001`；此处只是格式示例，不分配实际需求。每个模块从 `001` 递增，已分配编号保持稳定，废弃后不复用。

流程、设计、验证记录分别使用 `FLOW-{MODULE}-{NNN}`、`DESIGN-{MODULE}-{NNN}`、`VERIFY-{MODULE}-{NNN}`。创建正式条目时替换所有花括号占位符。各文档使用相对链接关联需求，必要时链接到标题锚点；拆分或移动文件时同步更新引用。

| 维度 | 可用值 | 维护位置 |
| --- | --- | --- |
| 需求结论 | 设计建议、待确认、已确认、已否决、已废弃 | 需求条目；确认或否决时记录依据 |
| 实现状态 | 未评估、未开始、进行中、部分实现、已实现 | 实现状态表；已有实现需附代码或提交依据 |
| 验证状态 | 未验证、部分验证、通过、失败、受阻 | 实现状态表；附验证记录和适用范围 |
| 优先级 | 待定、P0、P1、P2 | 需求条目；P0 为目标版本必需，P1 为重要，P2 为可选 |
| 目标版本 | 待定或已确定的版本 | 需求条目；需求已确认不自动代表进入首版 |

同一需求可以同时是“已确认、部分实现、部分验证”。基础库存在接口不等于 CatCommStudio 已集成；单个平台或设备验证通过也不等于全平台通过。各项状态由实际依据更新，不根据文档是否写完推断。

## 5. 填写和维护顺序

1. 阅读产品定义和能力边界，把新需求写入所属模块，复制[单条需求模板](requirements/_template.md)并分配编号。
2. 写清用户目标、规则、异常和可观察的验收条件；未确定的行为保留为问题，记录需求结论及范围依据。
3. 有分支或多种状态时，复制[流程模板](flows/_template.md)，关联需求并补齐正常、失败、取消和恢复路径。
4. 需要独立说明实现方案时，复制[功能设计模板](design/_template.md)，明确职责、接口和数据处理。
5. 在[实现状态表](implementation-status.md)登记需求；完成代码后记录实际实现范围与依据。
6. 按验收条件执行检查，复制[验证记录模板](verification/_template.md)记录环境、版本和结果，再回填验证状态。

需求正文是规则与验收条件的维护位置；流程与设计文档引用它，避免多处重复定义。实现状态表只维护进度和证据。变更规则时检查关联的流程、设计和已有验证记录是否仍适用，并在同一次变更中更新受影响内容。

Mermaid 图需要支持 Mermaid 的预览工具。流程图用于说明操作分支，状态图用于说明状态转换；图中的规则需要能对应到需求条目。模板中的图示仅展示填写方式。

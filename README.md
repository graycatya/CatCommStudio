# CatCommStudio

面向嵌入式开发和设备测试的多通信调试工具，计划支持串口、蓝牙、网络、USB、HID 等通信方式，通信核心复用 [SimpleCommKit](https://github.com/graycatya/SimpleCommKit)。

当前处于需求整理、功能规划和 UI 交互设计阶段。

已确定采用多进程设计：主进程负责创建或打开串口、网络、USB、蓝牙、HID 等通信功能子进程。已有脚本基础为 [SimpleScriptEngine](https://github.com/graycatya/SimpleScriptEngine)，进程信息与监控能力参考 [SimpleProcessInfo](https://github.com/graycatya/SimpleProcessInfo)；具体集成边界见架构说明。

## 项目资料

- [产品定义](docs/product-definition.md)
- [通信能力与产品功能映射](docs/communication-capabilities.md)
- [多进程架构与基础库职责](docs/multiprocess-architecture.md)
- [协作与提交规范](CONTRIBUTING.md)
- [Git 开发与发布流程](docs/git-workflow.md)

## 分支

- `main`：稳定发布分支，当前保存项目初始化资料。
- `develop`：日常开发集成分支。
- `release/<版本号>`：按需创建的发布准备分支。

功能、修复和文档任务从 `develop` 创建对应分支，具体命名及合并方式见开发与发布流程。

## 许可证

本项目使用 [Apache License 2.0](LICENSE)。

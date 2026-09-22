# SimpleCommKit 与 CatCommStudio 功能映射

日期：2026-09-22。状态：需求设计依据，UI 建议尚待确认；本次补充已确认的多进程方向，通信接口核对版本保持不变。

用户已确认通信核心库实现。本文依据 [SimpleCommKit 提交 fc13bff](https://github.com/graycatya/SimpleCommKit/tree/fc13bff9c71c911b18579afe95a8f71a5cbf1c32) 的公开头文件、部分实现和构建配置核对接口范围，未进行编译、设备实测或完整代码审计。

## 1. 能力与交互对应

| 模块 | 已核对的公开接口能力 | 建议的用户操作 |
| --- | --- | --- |
| [串口][serial] | 端口枚举、打开/关闭、参数设置、读写、热插拔回调 | 选择端口、配置串口参数、收发数据、查看设备移除状态 |
| [BLE Central][ble] | 适配器选择、扫描、连接、服务/特征查询、特征与描述符读写、Notify/Indicate 订阅 | 扫描并选择设备、浏览服务/特征树、按特征能力执行读取、写入与订阅 |
| [TCP][tcp] | 客户端连接、服务端监听、按客户端发送、广播；TLS；客户端重连配置 | 选择客户端/服务端模式、管理连接对象、选择发送目标、设置重连与 TLS |
| [UDP][udp] | 绑定本地地址、向指定远端发送、默认目标设置；服务端接收回调包含发送方地址 | 设置本地与目标地址、发送数据报、查看来源并回复；以收发状态呈现 |
| [USB][usb] | 枚举、打开、接口声明/释放、接口/端点查询、四种传输类型、读取轮询、插拔检测 | 选择设备/接口/端点、填写传输参数、执行请求、查看结果；等时传输是否纳入首版待定 |
| [HID][hid] | 按路径打开多设备、按设备写入、发送 Feature Report、读取轮询、插拔检测 | 选择设备、设置读取长度、编辑 Report ID 和数据、普通写入或发送 Feature Report |
| [WebSocket][ws] | 客户端/服务端、文本/二进制发送、按客户端发送/广播、TLS；客户端重连 | 配置 URL 或监听地址、选择消息发送类型和目标、查看消息 |
| [MQTT][mqtt] | 客户端连接、身份认证、遗嘱、发布/订阅、QoS/retain 参数、TLS、重连 | 配置 Broker、管理订阅、编辑主题与消息、设置 QoS/retain |

## 2. 影响需求的边界

- 蓝牙基线为 BLE Central；当前核对范围未发现经典蓝牙 SPP/RFCOMM 或 BLE Peripheral 的公开模块。
- HID 公开头文件提供 `send_Feature_Report`，未见读取 Feature Report 的公开接口。需求表应将其列为可选扩展，避免把“支持 HID”解释为全部报告操作都已开放。
- USB 头文件比 README 协议列表更细，已包含 `isochronous_Transfer`；它仍需要独立的产品范围决定和设备验证。
- 模块的回调名称、连接生命周期和返回值并不完全相同。例如 TCP 使用 `connect`，串口使用 `open`，BLE 使用 `peripheral_Connect`。建议在应用层按会话整理状态与事件，同时保留通信类型特有的操作。
- [构建配置][cmake]将模块作为可选项；其中 iOS 分支关闭串口、HID、USB。核心库的跨平台定位不能直接当作所有模块在每个平台上的交付承诺，CatCommStudio 仍需确定目标平台并验证实际组合。

## 3. CatCommStudio 上层职责建议

已确认主进程创建或打开通信功能子进程。下表为在此方向上的职责建议，进程与会话、窗口的对应关系仍待确认。SimpleScriptEngine、SimpleProcessInfo 的能力依据与边界见[多进程架构与基础库职责](multiprocess-architecture.md)。

| 层次 | 主要职责 |
| --- | --- |
| 主进程：CatCommStudio | 提供功能入口，创建或打开功能子进程；建议补充实例管理、进程状态与资源占用展示 |
| 功能子进程：CatCommStudio | 管理所属会话与配置、指令历史和分组、发送任务、日志、解析结果；处理回调线程转交和资源释放 |
| 通信核心：SimpleCommKit | 由功能子进程调用，提供设备发现、连接/监听、收发、错误及相应模块支持的插拔、TLS、重连能力 |
| 脚本基础：SimpleScriptEngine | 为宏与脚本提供执行和函数绑定基础；通信脚本 API、异步等待与停止控制需补充设计 |
| 进程信息：SimpleProcessInfo | 为主进程提供 PID 查询、子进程发现、存活检查和资源采样；启动、关闭与 IPC 另行实现 |
| UI 层：CatCommStudio | 复用会话导航、连接配置、收发视图和各类专用面板组件；功能窗口与主界面的组织方式待确认 |

建议复用统一的会话导航、日志查看与数据编辑组件。操作目标按类型明确显示，例如 TCP 客户端 ID、UDP 地址、BLE 特征、USB 端点、HID 设备或 MQTT 主题。

建议日志记录时间、会话、方向、原始数据、操作结果及通信类型特有信息。若核心库回调没有携带某项元数据，应先核对能否可靠补充，避免把缺失信息显示成确定值。

## 4. 接下来需要形成的产品产出

1. 首版功能表：明确每个已有模块需要开放的用户操作，以及日志、指令、波形、脚本等上层功能的优先级。
2. 用户流程：从主进程创建或打开功能子进程，到会话配置、收发与记录，补齐进程退出、断连和错误处理。
3. 页面结构与低保真原型：验证主进程入口、实例展示与功能界面如何配合。
4. 集成验收表：按目标系统和真实设备检查进程启动与就绪、连接、收发、异常反馈、持续运行与配置恢复。

[serial]: https://github.com/graycatya/SimpleCommKit/blob/fc13bff9c71c911b18579afe95a8f71a5cbf1c32/src/SimpleCommKitSerialPort/SimpleCommKitSerialPort.h
[ble]: https://github.com/graycatya/SimpleCommKit/blob/fc13bff9c71c911b18579afe95a8f71a5cbf1c32/src/SimpleCommKitBle/SimpleCommKitBleCentral.h
[tcp]: https://github.com/graycatya/SimpleCommKit/blob/fc13bff9c71c911b18579afe95a8f71a5cbf1c32/src/SimpleCommKitTcp/SimpleCommKitTcp.h
[udp]: https://github.com/graycatya/SimpleCommKit/blob/fc13bff9c71c911b18579afe95a8f71a5cbf1c32/src/SimpleCommKitUdp/SimpleCommKitUdp.h
[usb]: https://github.com/graycatya/SimpleCommKit/blob/fc13bff9c71c911b18579afe95a8f71a5cbf1c32/src/SimpleCommKitUsb/SimpleCommKitUsb.h
[hid]: https://github.com/graycatya/SimpleCommKit/blob/fc13bff9c71c911b18579afe95a8f71a5cbf1c32/src/SimpleCommKitHid/SimpleCommKitHid.h
[ws]: https://github.com/graycatya/SimpleCommKit/blob/fc13bff9c71c911b18579afe95a8f71a5cbf1c32/src/SimpleCommKitWebSocket/SimpleCommKitWebSocket.h
[mqtt]: https://github.com/graycatya/SimpleCommKit/blob/fc13bff9c71c911b18579afe95a8f71a5cbf1c32/src/SimpleCommKitMqttClient/SimpleCommKitMqttClient.h
[cmake]: https://github.com/graycatya/SimpleCommKit/blob/fc13bff9c71c911b18579afe95a8f71a5cbf1c32/CMakeLists.txt

# thegent 🎩 🚀

[![PyPI version](https://badge.fury.io/py/thegent.svg)](https://badge.fury.io/py/thegent)
[![Rust](https://img.shields.io/badge/built%20with-Rust-orange.svg)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**统一的智能体编排、治理与生命周期管理系统。**

`thegent` 是一个生产级 CLI 和框架，用于管理 AI 智能体工作流、Droid 和多智能体集群（Swarms）。它遵循“库优先”的设计哲学，并通过高性能 Rust 扩展进行了优化，为智能体操作提供快速、可靠且受控的环境。

---

## 📋 目录

- [核心功能](#-核心功能)
- [快速开始](#-快速开始)
- [安装指南](#-安装指南)
- [使用方法](#-使用方法)
- [性能指标](#-性能指标)
- [治理与策略](#-治理与策略)
- [安全与加固](#-安全与加固)
- [相关文档](#-相关文档)
- [贡献指南](#-贡献指南)
- [开源协议](#-开源协议)

---

## ✨ 核心功能

- ⚡ **性能至上**: Rust 驱动的工具检测和 PATH 解析 (<1ms) — 比传统 Shell 实现快 10-100 倍。
- 🔒 **智能体治理**: 内置策略强制执行、成本上限控制和自动化质量门禁。
- 🌍 **多提供商路由**: 智能路由至 Claude, Gemini, OpenAI 以及自定义本地代理。
- 🛠️ **统一工作流**: 跨多个智能体和项目的单一任务管理事实来源。
- 📦 **原生支持 MCP**: 全面支持模型上下文协议 (MCP) 服务器和资源。
- 🔄 **持续自主工作**: 通过 `thegent plan loop` 实现后台执行和会话管理。
- 🔍 **深度研究协议**: 系统化多源调查（Reddit, Google, GitHub），具备绕过屏蔽的隐匿爬取能力。

---

## 🚀 快速开始

### 1. 一键安装

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/bootstrap.sh | sh -s -- install
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/install.ps1 | iex
```

### 2. 配置与验证
```bash
thegent setup    # 按照向导登录 AI 提供商
thegent doctor   # 验证环境健康状态
```

### 3. 运行首个智能体
```bash
thegent run "分析当前目录结构" free
```

---

## 📦 安装指南

### 先决条件
- Python 3.12+
- Rust (构建高性能扩展所需)
- Homebrew (推荐用于系统依赖管理)

### 开发者安装 (源码构建)
```bash
git clone https://github.com/kooshapari/thegent
cd thegent
pip install -e .
thegent install -t all
thegent install-shims
thegent setup --hooks
```

---

## 🛠️ 使用方法

| 命令 | 描述 |
|---------|-------------|
| `thegent run <prompt>` | 在前台使用特定智能体/模型执行任务。 |
| `thegent bg <prompt>` | 启动后台智能体任务。 |
| `thegent ps` | 列出活跃及历史智能体任务。 |
| `thegent plan loop` | 持续处理来自统一工作流的任务项。 |
| `thegent plan do-next` | 从项目计划和规范中查找下一个可执行项。 |
| `thegent doctor` | 验证环境健康状况并修复性能瓶颈。 |

---

## 📊 性能指标

| 操作 | 传统实现 (Shell) | thegent (Rust) | 提升幅度 |
|-----------|----------------|----------------|-------------|
| 工具检测 | 60ms | **1ms** | **60倍** |
| PATH 解析 | 20ms | **0.5ms** | **40倍** |
| 进程扫描 | 50ms | **0.5ms** | **100倍** |
| Hook 执行 | 200ms | **20ms** | **10倍** |

---

## 🛡 治理与策略

`thegent` 将 AI 代理视为受治理的资源：
1. **成本控制**: 为每个会话和项目定义 Token/金额预算。
2. **质量门禁**: 自动根据定义的规范验证智能体输出。
3. **策略执行**: 集中化的 `governance/` 模块用于强制执行安全和伦理约束。
4. **审计日志**: 完整追踪智能体动作，包括工具使用和思维过程。

---

## 🔐 安全与加固

**为企业级智能体操作而加固:**
- **最小化攻击面**: 核心逻辑采用 Rust 隔离，兼顾性能与安全。
- **隐匿爬虫**: 内置机制绕过爬虫屏蔽，保护智能体匿名性。
- **路径隔离**: 通过优化的 Shim 严格控制执行环境。
- **机密管理**: 安全存储 API 密钥和提供商凭据。

---

## 📚 相关文档

- **[快速入门](./docs/guides/QUICK_START.md)** — 5 分钟上手。
- **[完整用户手册](./docs/guides/COMPLETE_USER_GUIDE.md)** — 深入了解功能。
- **[安装指南](./docs/guides/INSTALLATION.md)** — 高级安装选项。
- **[架构概览](./docs/reference/ARCHITECTURE_LAYERS.md)** — 设计层级与内部原理。
- **[研究索引](./docs/research/RESEARCH_CONSOLIDATED.md)** — 发现与实验记录。

---

## 🤝 贡献指南

欢迎社区贡献！请参阅 **[CONTRIBUTING.md](CONTRIBUTING.md)** 了解：
- 使用 `uv` 开发环境的搭建。
- 测试套件运行 (`task test`)。
- 编码标准与 PR 流程。

---

## 📜 开源协议

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

---

<p align="center">
  由社区倾力打造 ❤️
</p>

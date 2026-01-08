# 📚 文档目录

本目录包含 VibePoster 项目的所有技术文档。

---

## 🎯 快速导航

### 新手入门
- **[项目主 README](../README.md)** - 项目概述、安装和快速开始
- **[任务需求分析](TASK_REQUIREMENTS_ANALYSIS.md)** - 项目需求和功能清单

### 架构和设计
- **[系统架构](ARCHITECTURE.md)** - 整体架构、目录结构、分层设计、知识模块、技术栈
- **[Visual Agent 架构分析](VISUAL_AGENT_ARCHITECTURE_ANALYSIS.md)** - Visual Agent 职责划分和服务层设计
- **[在线编辑功能实现](ONLINE_EDITOR_IMPLEMENTATION.md)** - 编辑器功能实现总结

### 核心功能
- **[OCR 与图像理解](OCR_AND_IMAGE_UNDERSTANDING.md)** - 设计、实现、性能优化

### 配置和规范
- **[配置说明](CONFIGURATION.md)** - Agent 配置、Prompt 管理、知识模块配置
- **[依赖注入](DEPENDENCY_INJECTION.md)** - 依赖注入原理和 ServiceContainer
- **[异常处理](EXCEPTION_HANDLING.md)** - 全局异常处理机制

---

## 📖 文档详情

### 1. [系统架构](ARCHITECTURE.md)

**内容**：
- 整体架构设计（含知识模块 KG + RAG）
- 目录结构说明
- 分层设计（API → Service → Agent → Knowledge → Tools → Core）
- 核心模块详解
- 知识模块（Knowledge Graph + RAG Engine）
- 实现状态
- 技术栈

**适合**：
- 想了解系统整体设计
- 想了解各个模块的职责
- 新加入项目的开发者

---

### 2. [Visual Agent 架构分析](VISUAL_AGENT_ARCHITECTURE_ANALYSIS.md)

**内容**：
- Visual Agent 应该承担的职责
- 服务层设计（KnowledgeService 已实现）
- 职责划分和解耦

**适合**：
- 想深入了解 Visual Agent
- 想了解服务层设计

---

### 3. [在线编辑功能实现](ONLINE_EDITOR_IMPLEMENTATION.md)

**内容**：
- 在线编辑功能实现总结
- 核心编辑功能（图层选择、拖拽移动、调整大小、属性编辑）
- 图层管理
- 历史记录（撤销/重做）
- 键盘快捷键
- 架构实现和数据流

**适合**：
- 想了解前端编辑器实现
- 想扩展编辑器功能

---

### 4. [OCR 与图像理解](OCR_AND_IMAGE_UNDERSTANDING.md)

**内容**：
- OCR + 图像理解的设计概述
- 技术实现（DeepSeek Vision API）
- 性能优化（一次调用完成两个任务）
- 使用指南

**亮点**：
- ⚡️ 一次 LLM 调用同时完成 OCR 和图像理解
- 📊 性能提升 50%，Token 消耗降低 37.5%

---

### 5. [任务需求分析](TASK_REQUIREMENTS_ANALYSIS.md)

**内容**：
- 项目需求分析
- 功能清单
- 任务拆解

**适合**：
- 想了解项目需求
- 想了解功能规划

---

### 6. [配置说明](CONFIGURATION.md)

**内容**：
- Agent 配置（Planner, Visual, Layout, Critic）
- RAG 配置（向量模型、存储路径）
- Prompt 管理
- 环境变量配置
- 配置最佳实践

**适合**：
- 想修改 Agent 配置
- 想调整 Prompt
- 想配置 RAG 知识库

---

### 7. [依赖注入](DEPENDENCY_INJECTION.md)

**内容**：
- 依赖注入原理
- ServiceContainer 模式
- FastAPI 依赖注入使用
- 单例模式管理
- 测试中的依赖注入

**适合**：
- 想了解依赖注入原理
- 想使用 ServiceContainer
- 想编写可测试的代码

---

### 8. [异常处理](EXCEPTION_HANDLING.md)

**内容**：
- 全局异常处理机制
- 自定义异常类
- 统一错误响应格式
- 使用示例

**适合**：
- 想了解错误处理机制
- 想定义自定义异常
- 想统一错误响应格式

---

## 🔍 按场景查找

### 我想了解...

| 问题 | 文档 |
|------|------|
| 整体架构 | [系统架构](ARCHITECTURE.md) |
| 如何配置 Agent | [配置说明](CONFIGURATION.md) |
| Knowledge Graph 和 RAG | [系统架构](ARCHITECTURE.md#知识模块) |
| OCR 和图像理解如何工作 | [OCR 与图像理解](OCR_AND_IMAGE_UNDERSTANDING.md) |
| 如何处理错误 | [异常处理](EXCEPTION_HANDLING.md) |
| 如何使用依赖注入 | [依赖注入](DEPENDENCY_INJECTION.md) |
| Visual Agent 的职责 | [Visual Agent 架构分析](VISUAL_AGENT_ARCHITECTURE_ANALYSIS.md) |
| 前端编辑器实现 | [在线编辑功能实现](ONLINE_EDITOR_IMPLEMENTATION.md) |
| 项目需求和功能 | [任务需求分析](TASK_REQUIREMENTS_ANALYSIS.md) |

---

## 📊 文档统计

| 文档 | 类型 | 更新日期 |
|------|------|----------|
| ARCHITECTURE.md | 架构设计 | 2025-01-08 |
| VISUAL_AGENT_ARCHITECTURE_ANALYSIS.md | 专题分析 | 2025-01-08 |
| ONLINE_EDITOR_IMPLEMENTATION.md | 功能文档 | 2025-01-03 |
| OCR_AND_IMAGE_UNDERSTANDING.md | 功能文档 | 2025-01-01 |
| TASK_REQUIREMENTS_ANALYSIS.md | 需求文档 | 2025-01-08 |
| CONFIGURATION.md | 配置说明 | 2025-01-08 |
| DEPENDENCY_INJECTION.md | 技术说明 | 2025-01-08 |
| EXCEPTION_HANDLING.md | 技术说明 | 2025-01-01 |

---

## 🎓 学习路径

### 新手路径
1. [项目主 README](../README.md) - 了解项目概况
2. [系统架构](ARCHITECTURE.md) - 了解整体设计
3. [配置说明](CONFIGURATION.md) - 配置开发环境
4. [异常处理](EXCEPTION_HANDLING.md) - 了解错误处理

### 进阶路径
1. [Visual Agent 架构分析](VISUAL_AGENT_ARCHITECTURE_ANALYSIS.md) - 深入理解 Agent
2. [OCR 与图像理解](OCR_AND_IMAGE_UNDERSTANDING.md) - 了解核心功能
3. [依赖注入](DEPENDENCY_INJECTION.md) - 掌握高级特性
4. [在线编辑功能实现](ONLINE_EDITOR_IMPLEMENTATION.md) - 了解前端编辑器

---

## 🔗 相关资源

### 外部文档
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)

### 项目文档
- [前端 README](../frontend/README.md)
- [测试 README](../backend/engine/tests/README.md)
- [布局引擎](../backend/engine/docs/LAYOUT_ENGINE.md)
- [渲染服务](../backend/engine/docs/RENDERER_SERVICE.md)

---

**最后更新**: 2025-01-08

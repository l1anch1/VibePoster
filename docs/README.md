# 📚 文档目录

本目录包含 VibePoster 项目的所有技术文档。

---

## 🎯 快速导航

### 新手入门
- **[项目主 README](../README.md)** - 项目概述、安装和快速开始
- **[任务需求分析](../TASK_REQUIREMENTS_ANALYSIS.md)** - 项目需求和功能清单

### 架构和设计
- **[系统架构](ARCHITECTURE.md)** - 整体架构、目录结构、分层设计、技术栈
- **[Visual Agent 架构分析](VISUAL_AGENT_ARCHITECTURE_ANALYSIS.md)** - Visual Agent 职责划分和服务层设计

### 核心功能
- **[OCR 与图像理解](OCR_AND_IMAGE_UNDERSTANDING.md)** - 设计、实现、性能优化

### 配置和规范
- **[配置说明](CONFIGURATION.md)** - Agent 配置、Prompt 管理
- **[依赖注入](DEPENDENCY_INJECTION.md)** - 依赖注入原理和使用
- **[异常处理](EXCEPTION_HANDLING.md)** - 全局异常处理机制

---

## 📖 文档详情

### 1. [系统架构](ARCHITECTURE.md)

**内容**：
- 整体架构设计
- 目录结构说明
- 分层设计（API → Service → Agent → Tools → Core）
- 核心模块详解
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
- 服务层设计建议
- 职责划分和解耦
- 重构方案

**适合**：
- 想深入了解 Visual Agent
- 想了解服务层设计
- 想优化架构

---

### 3. [OCR 与图像理解](OCR_AND_IMAGE_UNDERSTANDING.md)

**内容**：
- OCR + 图像理解的设计概述
- 技术实现（DeepSeek Vision API）
- 性能优化（一次调用完成两个任务）
- 使用指南

**适合**：
- 想了解 OCR 和图像理解功能
- 想了解性能优化方案
- 想使用图像分析 API

**亮点**：
- ⚡️ 一次 LLM 调用同时完成 OCR 和图像理解
- 📊 性能提升 50%，Token 消耗降低 37.5%

---

### 4. [配置说明](CONFIGURATION.md)

**内容**：
- Agent 配置（Planner, Visual, Layout, Critic）
- Prompt 管理
- 环境变量配置
- 配置最佳实践

**适合**：
- 想修改 Agent 配置
- 想调整 Prompt
- 想配置环境变量

---

### 5. [依赖注入](DEPENDENCY_INJECTION.md)

**内容**：
- 依赖注入原理
- FastAPI 依赖注入使用
- 单例模式管理
- 测试中的依赖注入

**适合**：
- 想了解依赖注入原理
- 想使用依赖注入
- 想编写可测试的代码

---

### 6. [异常处理](EXCEPTION_HANDLING.md)

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

#### 整体架构
→ [系统架构](ARCHITECTURE.md)

#### 如何配置 Agent
→ [配置说明](CONFIGURATION.md)

#### OCR 和图像理解如何工作
→ [OCR 与图像理解](OCR_AND_IMAGE_UNDERSTANDING.md)

#### 如何处理错误
→ [异常处理](EXCEPTION_HANDLING.md)

#### 如何使用依赖注入
→ [依赖注入](DEPENDENCY_INJECTION.md)

#### Visual Agent 的职责
→ [Visual Agent 架构分析](VISUAL_AGENT_ARCHITECTURE_ANALYSIS.md)

#### 项目需求和功能
→ [任务需求分析](../TASK_REQUIREMENTS_ANALYSIS.md)

---

## 📊 文档统计

| 文档 | 行数 | 类型 | 更新日期 |
|------|------|------|----------|
| ARCHITECTURE.md | ~500 | 架构设计 | 2025-01-01 |
| VISUAL_AGENT_ARCHITECTURE_ANALYSIS.md | ~400 | 专题分析 | 2025-01-01 |
| OCR_AND_IMAGE_UNDERSTANDING.md | ~400 | 功能文档 | 2025-01-01 |
| CONFIGURATION.md | ~150 | 配置说明 | 2024-12-XX |
| DEPENDENCY_INJECTION.md | ~250 | 技术说明 | 2024-12-XX |
| EXCEPTION_HANDLING.md | ~130 | 技术说明 | 2025-01-01 |

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

---

## 📝 文档维护

### 文档更新原则
1. **及时更新**：代码变更后及时更新文档
2. **保持简洁**：避免冗余信息
3. **示例优先**：提供实际代码示例
4. **版本标记**：标注最后更新日期

### 文档贡献
如果你发现文档有误或需要补充，请：
1. 直接修改文档
2. 提交 Pull Request
3. 或者提 Issue 说明问题

---

## 🔗 相关资源

### 外部文档
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Pydantic 文档](https://docs.pydantic.dev/)

### 项目文档
- [前端 README](../frontend/README.md)
- [测试 README](../backend/engine/tests/README.md)

---

**最后更新**: 2025-01-01

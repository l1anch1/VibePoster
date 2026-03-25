# Visual Agent 架构分析与服务层设计

## 📋 任务书要求回顾

根据任务书要求：
- "实现图片内容提取功能，通过OCR及LLM技术将图片的风格、元素、主题等转化为文字描述"
- "设计系统架构，明确前端交互界面与后端生成处理服务的功能模块及数据流转逻辑"

---

## 🎯 Visual Agent 应该承担的职责

### 核心定位
**Visual Agent = 视觉感知中心 + 路由决策者**

### ✅ 应该承担的职责

#### 1. 路由决策（核心职责）
```
输入：用户上传的图片 + 设计简报
输出：处理策略决策

决策逻辑：
- 情况 A（双图）：背景 + 人物 → 抠图人物，保留背景
- 情况 B（单图）：人物 → 抠图人物，搜索背景
- 情况 C（无图）：搜索背景
```

#### 2. 协调视觉处理工具（编排职责）
```
- 调用 OCR + 图像理解工具
- 调用抠图工具
- 调用素材搜索工具
```

#### 3. 结果整合与优化（增值职责）
```
- 整合 OCR + 图像理解结果
- 生成优化建议（标题候选、配色方案等）
- 优化设计简报（合并风格关键词）
```

### ❌ 不应该承担的职责

- ❌ 具体的图像处理算法（应在 `tools/` 层）
- ❌ 业务流程控制（应在 `Workflow` 层）
- ❌ 设计规则推理（应在 `KnowledgeService`）

---

## 🏗️ 服务层设计（已实现）

### 已实现的服务

#### 1. KnowledgeService ✅

**职责**：统一管理 Knowledge Graph 和 RAG

```python
# services/knowledge_service.py

class KnowledgeService:
    """知识服务 - 统一管理 KG + RAG"""
    
    def get_design_context(self, user_prompt, brand_name):
        """获取完整的设计上下文"""
        # 1. 从 prompt 提取关键词
        keywords = self.extract_keywords(user_prompt)
        # 2. KG 推理设计规则
        kg_rules = self.infer_design_rules(keywords)
        # 3. RAG 检索品牌知识
        brand_knowledge = self.search_brand_knowledge(...)
        return {...}
    
    def infer_design_rules(self, keywords):
        """KG 设计规则推理"""
        return self.knowledge_graph.infer_rules(keywords)
    
    def search_brand_knowledge(self, query, brand_name):
        """RAG 品牌知识检索"""
        return self.knowledge_base.search(query, ...)
    
    def add_brand_document(self, text, brand_name, category):
        """添加品牌文档到 RAG"""
        ...
```

**原本建议的 ImageAnalysisService** → 已通过 `tools/image_understanding.py` 实现

#### 2. RendererService ✅

**职责**：DSL 解析 + OOP 布局 + Pydantic 转换

```python
# services/renderer_service.py

class RendererService:
    """渲染服务 - DSL 到 PosterData"""
    
    def render_poster_from_workflow_state(self, workflow_state):
        """从工作流状态渲染海报"""
        # 1. 解析 DSL 指令
        dsl_instructions = workflow_state["final_poster"]["dsl_instructions"]
        # 2. 构建 OOP 布局
        container = self.parse_dsl_and_build_layout(...)
        # 3. 转换为 Pydantic Schema
        poster_data = self.convert_to_pydantic_schema(container, ...)
        return poster_data
```

---

## 🔄 当前架构

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│  /api/step/*  /api/kg/infer  /api/brand/upload              │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Service Layer                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐  │
│  │  PosterService  │ │KnowledgeService │ │RendererService│  │
│  │                 │ │  ┌───────────┐  │ │               │  │
│  │                 │ │  │    KG     │  │ │  DSL Parser   │  │
│  │                 │ │  │   RAG     │  │ │  OOP Layout   │  │
│  │                 │ │  └───────────┘  │ │               │  │
│  └─────────────────┘ └─────────────────┘ └───────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                       Agent Layer                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Planner │ │ Visual  │ │ Layout  │ │ Critic  │           │
│  │ (KG+RAG)│ │         │ │ (DSL)   │ │         │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Knowledge Layer                         │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │DesignKnowledgeGraph │  │   BrandKnowledgeBase (RAG)  │   │
│  │    (networkx)       │  │  (sentence-transformers)    │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                        Tools Layer                           │
│  vision.py   image_understanding.py   asset_db.py           │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户请求
    │
    ▼
Planner Agent
    ├── KnowledgeService.get_design_context()
    │       ├── extract_keywords() → ["Tech", "Promotion"]
    │       ├── KG.infer_rules() → {colors, fonts, layouts}
    │       └── RAG.search() → brand knowledge
    └── LLM → design_brief
    │
    ▼
Visual Agent
    ├── OCR + 图像理解 (tools/image_understanding.py)
    ├── 抠图 (tools/vision.py)
    └── 素材搜索 (tools/asset_db.py)
    │
    ▼
Layout Agent
    ├── LLM → DSL 指令列表
    └── RendererService.render_poster_from_workflow_state()
            ├── parse_dsl_and_build_layout() → OOP Container
            └── convert_to_pydantic_schema() → PosterData
    │
    ▼
Critic Agent
    └── 审核 → PASS / FAIL + feedback
```

---

## 📊 职责分层对比

| 层级 | 职责 | 示例 |
|------|------|------|
| **API 层** | 接收请求，参数验证 | `routes/steps.py` |
| **服务层** | 业务逻辑，流程控制 | `KnowledgeService`, `RendererService` |
| **Agent 层** | AI 决策，调用 LLM | `planner.py`, `visual.py`, `layout.py` |
| **知识层** | 规则存储，语义检索 | `DesignKnowledgeGraph`, `BrandKnowledgeBase` |
| **工具层** | 具体实现，无业务逻辑 | `vision.py`, `asset_db.py` |

---

## ✅ 已实现的建议

| 原建议 | 状态 | 实现位置 |
|--------|------|---------|
| ImageAnalysisService | ✅ | `tools/image_understanding.py` |
| AssetManagementService | ⚠️ 部分 | `tools/asset_db.py` + `vision.py` |
| KnowledgeService | ✅ | `services/knowledge_service.py` |
| RendererService | ✅ | `services/renderer_service.py` |
| CacheService | 🔲 | 未实现 |

---

## 🎯 未来优化方向

### 中优先级

1. **AssetManagementService**
   - 统一管理素材处理
   - 添加素材验证功能

2. **CacheService**
   - 缓存图像分析结果
   - 缓存素材搜索结果

### 低优先级

3. **监控和日志**
   - 记录图像分析耗时
   - 记录素材搜索成功率

---

## ✅ 总结

### Visual Agent 当前职责
1. ✅ 路由决策（核心）
2. ✅ 协调视觉处理工具（编排）
3. ✅ 结果整合与优化（增值）

### 已集成到服务层的功能
1. ✅ **KnowledgeService** - KG + RAG 统一管理
2. ✅ **RendererService** - DSL 解析 + OOP 布局

### 服务层的定义
**服务层 = 业务逻辑层**，位于 `backend/engine/app/services/`，负责：
- 封装业务逻辑
- 协调多个工具和 Agent
- 提供可复用的服务
- 处理缓存、验证等横切关注点

---

**最后更新**: 2025-01-08

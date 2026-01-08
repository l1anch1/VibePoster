# Knowledge Module - 知识图谱与 RAG 检索模块

## 📚 模块说明

本模块提供两个核心功能，按照单一职责原则拆分为两个子模块：

```
knowledge/
├── __init__.py              # 模块入口，统一导出
├── README.md
├── kg/                      # Knowledge Graph 子模块
│   ├── __init__.py
│   ├── data/                # KG 专属数据
│   │   └── kg_rules.json
│   └── design_rules.py      # 设计规则推理引擎
└── rag/                     # RAG 子模块
    ├── __init__.py
    ├── data/                # RAG 专属数据
    │   └── default_brand_knowledge.json
    └── rag_engine.py        # 品牌知识检索引擎
```

**设计理念：**
- 每个子模块管理自己的数据
- 可移植性：单独复用 KG 或 RAG 模块时，数据跟着走
- 职责清晰：不需要查看父目录就知道模块依赖什么数据

---

## 1. 设计规则推理 (`kg/design_rules.py`)

基于 Knowledge Graph 的设计规则推理引擎，用于约束 LLM 生成的设计风格。

**规则数据源：** `kg/data/kg_rules.json`

**功能：**
- 存储行业、氛围、颜色、字体、布局之间的关联规则
- 根据关键词推理推荐的设计元素
- 内置 9 个行业 + 9 个氛围的规则库

**使用示例：**
```python
from app.knowledge import DesignKnowledgeGraph

kg = DesignKnowledgeGraph()
rules = kg.infer_rules(["Tech", "Promotion"])
# {
#     "recommended_colors": ["#0066FF", "#FF0000", ...],
#     "recommended_fonts": ["Sans-Serif"],
#     "recommended_layouts": ["Grid", "Diagonal"]
# }

# 获取支持的关键词
keywords = kg.get_supported_keywords()
# {"industries": ["Tech", "Food", ...], "vibes": ["Minimalist", "Luxury", ...]}
```

---

## 2. 品牌知识检索 (`rag/rag_engine.py`)

基于 RAG 的企业品牌手册检索系统，支持向量检索或关键词匹配。

**默认数据源：** `rag/data/default_brand_knowledge.json`

**功能：**
- 存储和检索企业品牌规范（颜色、字体、Slogan 等）
- 支持三种检索模式：
  - 🚀 **向量检索** (sentence-transformers) - 推荐
  - 🗄️ **ChromaDB** (langchain + chromadb) - 可选
  - 🔍 **关键词匹配** (降级方案) - 无需安装依赖

**预装数据：**
- 华为品牌手册（7 条数据）
  - 主色调：昆仑红 (#C32228)、雅川青 (#74C096)
  - 设计风格：高端、大气、极简
  - Slogan：遥遥领先，连接未来

**使用示例：**
```python
from app.knowledge import BrandKnowledgeBase

rag = BrandKnowledgeBase()
results = rag.search("华为的配色", top_k=2)
# [
#     {
#         "text": "华为 Mate 60 的品牌主色调是昆仑红 (#C32228)...",
#         "metadata": {"brand": "华为", "category": "配色方案"},
#         "score": 0.95
#     }
# ]
```

---

## 🔧 依赖安装

### 必需依赖（已包含在 requirements.txt）
```bash
pip install networkx  # 用于 Knowledge Graph
```

### 可选依赖（提升 RAG 性能）

#### 方案一：轻量级向量检索（推荐）
```bash
pip install sentence-transformers
```
- **优点**：性能好，支持中文，离线可用
- **缺点**：首次下载模型需要网络
- **模型大小**：约 120MB

#### 方案二：完整 RAG 方案
```bash
pip install langchain chromadb
```
- **优点**：功能完整，支持持久化
- **缺点**：依赖较重

#### 方案三：无需安装（降级）
如果不安装任何依赖，系统会自动使用关键词匹配，仍可正常工作。

---

## 🚀 快速测试

### 测试 Knowledge Graph
```bash
cd backend/engine
python -m app.knowledge.kg.design_rules
```

### 测试 RAG Engine
```bash
cd backend/engine
python -m app.knowledge.rag.rag_engine
```

---

## 📊 性能对比

| 检索方式 | 准确率 | 速度 | 依赖 |
|---------|--------|------|------|
| sentence-transformers | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 轻量 |
| chromadb | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 中等 |
| keyword | ⭐⭐⭐ | ⭐⭐⭐ | 无 |

---

## 🎯 集成方式

推荐使用 `KnowledgeService` 统一访问 KG 和 RAG：

```python
from app.services import KnowledgeService

# 获取服务实例（依赖注入）
service = KnowledgeService()

# KG 推理
rules = service.infer_design_rules(["Tech", "Promotion"])

# RAG 检索
results = service.search_brand_knowledge("华为配色", brand_name="华为")

# 获取完整设计上下文
context = service.get_design_context(user_prompt="科技产品发布会海报", brand_name="华为")
```

---

## 📝 扩展知识库

### 添加新的设计规则

编辑 `data/kg_rules.json`：
```json
{
  "industries": {
    "Gaming": {
      "colors": ["#FF0000", "#00FF00", "#000000"],
      "fonts": ["Sans-Serif"],
      "layouts": ["Diagonal"],
      "description": "游戏行业 - 鲜艳色彩、动感布局"
    }
  }
}
```

### 添加新的品牌手册

编辑 `data/default_brand_knowledge.json` 或通过 API 上传：
```python
service = KnowledgeService()
service.add_brand_document(
    text="苹果公司的主色调是白色和太空灰...",
    brand_name="Apple",
    category="配色方案"
)
```

---

## 🐛 故障排除

### 问题：sentence-transformers 下载模型失败
**解决**：
1. 手动下载模型：https://huggingface.co/sentence-transformers
2. 或使用国内镜像站
3. 或直接使用关键词匹配（降级）

### 问题：检索结果不准确
**解决**：
1. 确保安装了 sentence-transformers
2. 增加 top_k 参数获取更多结果
3. 使用元数据过滤缩小搜索范围

---

## 📄 License
© 2025 VibePoster Team

Last Updated: 2025-01-08

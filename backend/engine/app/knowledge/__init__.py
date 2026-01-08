"""
Knowledge 模块 - 知识检索与推理

包含两个子模块：
- kg: Knowledge Graph 知识图谱，基于图结构的设计规则推理
- rag: RAG 引擎，基于语义检索的品牌知识库

目录结构：
    knowledge/
    ├── __init__.py              # 模块入口
    ├── kg/                      # Knowledge Graph 子模块
    │   ├── __init__.py
    │   ├── data/
    │   │   └── kg_rules.json    # KG 规则数据
    │   └── design_rules.py      # 设计规则图谱
    └── rag/                     # RAG 子模块
        ├── __init__.py
        ├── data/
        │   └── default_brand_knowledge.json  # 默认品牌数据
        └── rag_engine.py        # 品牌知识库
"""

from .kg import DesignKnowledgeGraph
from .rag import BrandKnowledgeBase

__all__ = ["DesignKnowledgeGraph", "BrandKnowledgeBase"]

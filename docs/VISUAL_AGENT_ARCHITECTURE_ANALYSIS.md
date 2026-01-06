# Visual Agent 架构分析与服务层设计

## 📋 任务书要求回顾

根据任务书要求：
- "实现图片内容提取功能，通过OCR及LLM技术将图片的风格、元素、主题等转化为文字描述"
- "设计系统架构，明确前端交互界面与后端生成处理服务的功能模块及数据流转逻辑"

---

## 🎯 Visual Agent 应该承担的职责

### 核心定位
**Visual Agent = 视觉感知中心 + 路由决策者**

根据任务书和系统架构，Visual Agent 应该专注于：

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

**为什么**：这是 Visual Agent 的核心价值，决定如何处理图片

#### 2. 协调视觉处理工具（编排职责）
```
- 调用 OCR 工具
- 调用图像理解工具
- 调用抠图工具
- 调用素材搜索工具
```

**为什么**：Visual Agent 作为"视觉感知中心"，应该协调各种视觉处理工具

#### 3. 结果整合与优化（增值职责）
```
- 整合 OCR + 图像理解结果
- 生成优化建议（标题候选、配色方案等）
- 优化设计简报（合并风格关键词）
```

**为什么**：Visual Agent 理解视觉信息的语义，可以提供优化建议

---

### ❌ 不应该承担的职责

#### 1. 具体的图像处理逻辑
```
❌ 不应该：在 Visual Agent 中实现抠图算法
✅ 应该：调用 tools/vision.py 中的 process_cutout()

❌ 不应该：在 Visual Agent 中实现 OCR 算法
✅ 应该：调用 tools/ocr.py 中的 extract_text_with_ocr()
```

**为什么**：具体的图像处理是工具层的职责，Agent 只负责调用和协调

#### 2. 业务流程控制
```
❌ 不应该：控制整个海报生成流程
✅ 应该：只负责视觉处理部分，流程由 Workflow 控制
```

**为什么**：流程控制是 Workflow 的职责

#### 3. 数据持久化
```
❌ 不应该：保存图片到数据库
❌ 不应该：缓存图像分析结果
```

**为什么**：数据持久化应该在服务层处理

---

## 🏗️ 服务层设计

### 什么是服务层？

**服务层（Service Layer）= 业务逻辑层**

在当前架构中，服务层位于：
```
backend/engine/app/services/
```

### 当前服务层

#### 已有：PosterService (`services/poster_service.py`)

**职责**：
- 处理海报生成的业务逻辑
- 处理用户上传的图片
- 构建初始状态
- 调用工作流
- 返回最终结果

```python
class PosterService:
    def generate_poster(self, prompt, canvas_width, canvas_height, 
                       image_person, image_bg, chat_history):
        # 1. 处理用户上传的图片
        user_images = self.process_user_images(image_person, image_bg)
        
        # 2. 构建初始状态
        initial_state = self.build_initial_state(...)
        
        # 3. 启动工作流
        final_state = self.workflow.invoke(initial_state)
        
        # 4. 返回结果
        return final_poster
```

---

## 🎨 应该集成到服务层的功能

### 1. ImageAnalysisService（新建，高优先级）

**职责**：统一管理图像分析（OCR + 图像理解）

```python
# services/image_analysis_service.py

class ImageAnalysisService:
    """图像分析服务"""
    
    def analyze_single_image(
        self,
        image_data: bytes,
        image_type: str,
        user_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析单张图片
        
        Args:
            image_data: 图片二进制数据
            image_type: 图片类型（person/background/reference）
            user_prompt: 用户需求
            
        Returns:
            分析结果（OCR + 图像理解 + 建议）
        """
        # 1. OCR 识别
        ocr_result = extract_text_with_ocr(image_data)
        
        # 2. 图像理解
        understanding_result = understand_image_with_llm(image_data, user_prompt)
        
        # 3. 生成建议
        suggestions = generate_suggestions(ocr_result, understanding_result)
        
        # 4. 缓存结果（可选）
        # self._cache_result(image_hash, result)
        
        return {
            "ocr": ocr_result,
            "understanding": understanding_result,
            "suggestions": suggestions,
            "image_type": image_type
        }
    
    def analyze_multiple_images(
        self,
        images: List[Dict[str, Any]],
        user_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """批量分析图片"""
        results = []
        for img in images:
            result = self.analyze_single_image(
                image_data=img["data"],
                image_type=img.get("type", "unknown"),
                user_prompt=user_prompt
            )
            results.append(result)
        return results
    
    def optimize_design_brief(
        self,
        design_brief: Dict[str, Any],
        analysis_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        基于图像分析结果优化设计简报
        
        - 使用 OCR 识别的文字作为标题候选
        - 合并图像理解的风格关键词
        - 提供配色方案建议
        """
        # 收集所有标题候选
        all_title_candidates = []
        all_style_keywords = []
        
        for analysis in analysis_results:
            suggestions = analysis.get("suggestions", {})
            all_title_candidates.extend(suggestions.get("title_candidates", []))
            all_style_keywords.extend(suggestions.get("style_keywords", []))
        
        # 优化设计简报
        optimized_brief = design_brief.copy()
        
        if all_title_candidates and not design_brief.get("title"):
            optimized_brief["title"] = all_title_candidates[0]
        
        if all_style_keywords:
            existing_keywords = design_brief.get("style_keywords", [])
            combined_keywords = list(set(existing_keywords + all_style_keywords))
            optimized_brief["style_keywords"] = combined_keywords[:5]
        
        return optimized_brief
```

**为什么需要这个服务**：
- ✅ 统一管理图像分析逻辑
- ✅ 减轻 Visual Agent 的职责
- ✅ 便于添加缓存、批量处理等功能
- ✅ 便于测试和维护

---

### 2. AssetManagementService（可选，中优先级）

**职责**：管理素材（背景图、前景图等）

```python
# services/asset_management_service.py

class AssetManagementService:
    """素材管理服务"""
    
    def search_background(
        self,
        keywords: List[str],
        canvas_width: int,
        canvas_height: int
    ) -> str:
        """搜索背景图"""
        # 1. 调用素材库搜索
        bg_url = search_assets(keywords)
        
        # 2. 验证图片可用性（可选）
        # self._validate_image_url(bg_url)
        
        # 3. 缓存搜索结果（可选）
        # self._cache_search_result(keywords, bg_url)
        
        return bg_url
    
    def process_user_image(
        self,
        image_data: bytes,
        image_type: str,
        analysis_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理用户上传的图片
        
        - 如果是人物图，进行抠图
        - 如果是背景图，转换为 base64
        """
        if image_type == "person":
            # 抠图
            cutout_result = process_cutout(image_data)
            return {
                "type": "image",
                "src": cutout_result["processed_image_base64"],
                "source_type": "user_upload",
                "width": cutout_result["width"],
                "height": cutout_result["height"],
                "subject_bbox": cutout_result.get("subject_bbox")
            }
        elif image_type == "background":
            # 转换为 base64
            bg_base64 = image_to_base64(image_data)
            return {
                "type": "image",
                "src": bg_base64,
                "source_type": "user_upload"
            }
```

**为什么需要这个服务**：
- ✅ 统一管理素材处理逻辑
- ✅ 便于添加素材验证、缓存等功能
- ✅ 减轻 Visual Agent 的职责

---

### 3. CacheService（可选，低优先级）

**职责**：缓存图像分析结果、素材搜索结果等

```python
# services/cache_service.py

class CacheService:
    """缓存服务"""
    
    def get_image_analysis(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """获取缓存的图像分析结果"""
        pass
    
    def set_image_analysis(self, image_hash: str, result: Dict[str, Any]):
        """缓存图像分析结果"""
        pass
    
    def get_asset_search(self, keywords: List[str]) -> Optional[str]:
        """获取缓存的素材搜索结果"""
        pass
```

---

## 🔄 重构后的架构

### 当前架构（问题）

```
Visual Agent（职责过重）
    ├─ OCR 识别
    ├─ 图像理解
    ├─ 生成建议
    ├─ 优化设计简报
    ├─ 抠图处理
    ├─ 素材搜索
    └─ 结果整合
```

### 重构后的架构（推荐）

```
Visual Agent（专注路由决策）
    ├─ 决定处理策略（A/B/C）
    ├─ 调用 ImageAnalysisService
    ├─ 调用 AssetManagementService
    └─ 整合结果

ImageAnalysisService（图像分析）
    ├─ OCR 识别
    ├─ 图像理解
    ├─ 生成建议
    └─ 优化设计简报

AssetManagementService（素材管理）
    ├─ 搜索背景图
    ├─ 处理用户图片（抠图/转换）
    └─ 素材验证

Tools（底层工具）
    ├─ ocr.py - OCR 实现
    ├─ image_understanding.py - 图像理解实现
    ├─ vision.py - 抠图实现
    └─ asset_db.py - 素材搜索实现
```

---

## 📊 职责分层对比

### 层级划分

| 层级 | 职责 | 示例 |
|------|------|------|
| **API 层** | 接收 HTTP 请求，参数验证 | `api/routes/poster.py` |
| **服务层** | 业务逻辑，流程控制 | `services/poster_service.py`<br>`services/image_analysis_service.py` |
| **Agent 层** | AI 决策，调用 LLM | `agents/visual.py`<br>`agents/planner.py` |
| **工具层** | 具体实现，无业务逻辑 | `tools/ocr.py`<br>`tools/vision.py` |

### Visual Agent 的定位

**当前问题**：Visual Agent 混合了 Agent 层和服务层的职责

**应该的定位**：
- ✅ **Agent 层**：路由决策、调用服务、整合结果
- ❌ **不是服务层**：不应该包含具体的业务逻辑

---

## 🎯 实施建议

### 高优先级（建议立即实施）

1. **创建 ImageAnalysisService**
   - 将 OCR + 图像理解 + 建议生成 + 设计简报优化 移到服务层
   - Visual Agent 只负责调用服务

2. **简化 Visual Agent**
   - 只保留路由决策逻辑
   - 调用 ImageAnalysisService 和 AssetManagementService
   - 整合结果并返回

### 中优先级（后续优化）

3. **创建 AssetManagementService**
   - 统一管理素材处理
   - 添加素材验证功能

4. **添加缓存机制**
   - 创建 CacheService
   - 缓存图像分析结果和素材搜索结果

### 低优先级（可选）

5. **添加监控和日志**
   - 记录图像分析耗时
   - 记录素材搜索成功率

---

## 📝 重构示例

### 重构前（Visual Agent）

```python
def run_visual_agent(user_images, design_brief):
    # 1. OCR + 图像理解（应该在服务层）
    for img in user_images:
        analysis_result = understand_image(...)
        img["ocr"] = analysis_result.get("ocr")
        img["understanding"] = analysis_result.get("understanding")
    
    # 2. 优化设计简报（应该在服务层）
    if all_title_candidates:
        design_brief["title"] = all_title_candidates[0]
    
    # 3. 抠图处理（应该在服务层）
    cutout_result = process_cutout(image_data)
    
    # 4. 素材搜索（应该在服务层）
    bg_url = search_assets(keywords)
    
    # 5. 结果整合（Agent 层职责）
    return {...}
```

### 重构后（Visual Agent）

```python
def run_visual_agent(user_images, design_brief):
    # 1. 调用图像分析服务
    image_analysis_service = ImageAnalysisService()
    analysis_results = image_analysis_service.analyze_multiple_images(
        user_images, 
        user_prompt=design_brief.get("user_prompt")
    )
    
    # 2. 优化设计简报（调用服务）
    optimized_brief = image_analysis_service.optimize_design_brief(
        design_brief, 
        analysis_results
    )
    
    # 3. 调用素材管理服务
    asset_service = AssetManagementService()
    
    # 4. 路由决策（Agent 核心职责）
    if image_count == 0:
        # 情况 C：搜索背景
        bg_url = asset_service.search_background(
            optimized_brief["style_keywords"],
            canvas_width,
            canvas_height
        )
        return {"background_layer": {...}}
    
    elif image_count == 1:
        # 情况 B：抠图 + 搜索背景
        foreground = asset_service.process_user_image(
            user_images[0]["data"], 
            "person",
            analysis_results[0]
        )
        bg_url = asset_service.search_background(...)
        return {"background_layer": {...}, "foreground_layer": foreground}
    
    # 5. 整合结果（Agent 职责）
    return {
        "background_layer": {...},
        "foreground_layer": {...},
        "image_analyses": analysis_results,
        "color_suggestions": {...}
    }
```

---

## ✅ 总结

### Visual Agent 应该承担的职责
1. ✅ 路由决策（核心）
2. ✅ 协调视觉处理工具（编排）
3. ✅ 结果整合与优化（增值）

### 应该集成到服务层的功能
1. ✅ **ImageAnalysisService**（高优先级）
   - OCR + 图像理解
   - 生成建议
   - 优化设计简报

2. ✅ **AssetManagementService**（中优先级）
   - 素材搜索
   - 图片处理（抠图/转换）
   - 素材验证

3. ✅ **CacheService**（低优先级）
   - 缓存图像分析结果
   - 缓存素材搜索结果

### 服务层的定义
**服务层 = 业务逻辑层**，位于 `backend/engine/app/services/`，负责：
- 封装业务逻辑
- 协调多个工具和 Agent
- 提供可复用的服务
- 处理缓存、验证等横切关注点

---

**最后更新**: 2025-01-XX


# Renderer Service - OOP 布局到前端 Schema 的序列化适配器

## 📚 概述

`RendererService` 是连接 **OOP Layout Engine** 和 **前端 Pydantic Schema** 的桥梁，负责：

1. ✅ **解析 DSL 指令** - 将 Layout Agent 的输出转换为 layout_engine 组件
2. ✅ **OOP 布局计算** - 使用动态布局引擎自动计算坐标
3. ✅ **Schema 转换** - 转换为符合 API 标准的 Pydantic 模型
4. ✅ **数据合并** - 整合 Planner、Visual、Layout 的输出
5. ✅ **Type 字段保证** - 确保每个图层都有 `type` 字段（前端需要）

## 🔄 数据流

```
Layout Agent DSL 指令
         ↓
RendererService.parse_dsl_and_build_layout()
         ↓
OOP Layout Engine (自动计算坐标)
         ↓
RendererService.convert_to_pydantic_schema()
         ↓
PosterData (Pydantic Schema)
         ↓
+ Planner 设计数据 (颜色、文案)
+ Visual 素材数据 (图片 URL)
         ↓
最终 JSON (前端渲染)
```

## 🚀 快速开始

### 基础用法

```python
from app.services.renderer import RendererService

# 初始化服务
renderer = RendererService()

# DSL 指令（来自 Layout Agent）
dsl_instructions = [
    {"command": "add_title", "content": "年终大促", "font_size": 64},
    {"command": "add_subtitle", "content": "全场5折起", "font_size": 36},
    {"command": "add_image", "src": "...", "width": 800, "height": 600}
]

# 1. 解析并构建布局
container = renderer.parse_dsl_and_build_layout(
    dsl_instructions=dsl_instructions,
    canvas_width=1080,
    canvas_height=1920
)

# 2. 转换为 Pydantic Schema
poster_data = renderer.convert_to_pydantic_schema(container)

# 3. 导出 JSON
json_data = poster_data.model_dump()
```

### 完整工作流集成

```python
from app.services.renderer import RendererService

def layout_node(state: dict) -> dict:
    """Layout Agent 节点"""
    
    # ... Layout Agent 生成 DSL 指令 ...
    
    # 使用 RendererService 渲染
    renderer = RendererService()
    poster_data = renderer.render_poster_from_workflow_state(state)
    
    # 更新状态
    state["final_poster"] = poster_data.model_dump()
    return state
```

## 📋 DSL 指令格式

### 支持的命令

| 命令 | 说明 | 参数 |
|------|------|------|
| `add_title` | 添加标题 | `content`, `font_size`, `color` |
| `add_subtitle` | 添加副标题 | `content`, `font_size` |
| `add_text` | 添加正文 | `content`, `font_size`, `text_align`, `line_height` |
| `add_image` | 添加图片 | `src`, `width`, `height` |
| `add_hero_image` | 添加主图 | `src`, `width`, `height` |
| `add_cta` | 添加行动号召 | `content`, `font_size`, `color` |

### DSL 示例

```python
dsl_instructions = [
    {
        "command": "add_title",
        "content": "限时优惠",
        "font_size": 72,
        "color": "#FF0000"
    },
    {
        "command": "add_subtitle",
        "content": "全场5折起，活动仅限三天",
        "font_size": 32
    },
    {
        "command": "add_image",
        "src": "https://example.com/product.jpg",
        "width": 800,
        "height": 600
    },
    {
        "command": "add_cta",
        "content": "立即抢购 →",
        "font_size": 36,
        "color": "#0066FF"
    }
]
```

## 🎯 核心方法

### 1. `parse_dsl_and_build_layout()`

解析 DSL 指令并构建 OOP 布局。

```python
container = renderer.parse_dsl_and_build_layout(
    dsl_instructions=[...],
    canvas_width=1080,
    canvas_height=1920,
    design_brief={"main_color": "#FF0000", ...}
)
```

**返回值：** `VerticalContainer` 对象

### 2. `convert_to_pydantic_schema()`

将 OOP 布局转换为 Pydantic Schema。

```python
poster_data = renderer.convert_to_pydantic_schema(
    container=container,
    design_brief={"background_color": "#FFFFFF", ...}
)
```

**返回值：** `PosterData` 对象

**关键特性：**
- ✅ 自动添加 `type` 字段（`"text"` / `"image"` / `"rect"`）
- ✅ 自动生成唯一的 `id`（`text_0`, `image_1` 等）
- ✅ 坐标转换为整数（避免前端渲染问题）

### 3. `merge_with_design_brief()`

合并 Planner 和 Visual 的数据。

```python
poster_data = renderer.merge_with_design_brief(
    poster_data=poster_data,
    design_brief=planner_output,
    asset_list=visual_output
)
```

**功能：**
- 应用品牌主色调到标题
- 填充图片 URL
- 设置画布背景色

### 4. `render_poster_from_workflow_state()`

一键完成整个渲染流程（推荐）。

```python
poster_data = renderer.render_poster_from_workflow_state(
    workflow_state={
        "design_brief": {...},
        "asset_list": {...},
        "final_poster": {"dsl_instructions": [...]},
        "canvas_width": 1080,
        "canvas_height": 1920
    }
)
```

## 📊 输出格式

### PosterData Schema

```python
{
  "canvas": {
    "width": 1080,
    "height": 938,
    "backgroundColor": "#FFF8F0"
  },
  "layers": [
    {
      "id": "text_0",
      "name": "Text 0",
      "type": "text",           # ⭐ 前端需要的 type 字段
      "x": 40,
      "y": 40,
      "width": 1000,
      "height": 96,
      "rotation": 0,
      "opacity": 1.0,
      "z_index": 0,
      "content": "年终大促",
      "fontSize": 64,
      "color": "#FF0000",
      "fontFamily": "Arial",
      "textAlign": "center",
      "fontWeight": "bold"
    },
    {
      "id": "image_1",
      "name": "Image 1",
      "type": "image",          # ⭐ type 字段
      "x": 40,
      "y": 230,
      "width": 800,
      "height": 600,
      "rotation": 0,
      "opacity": 1.0,
      "z_index": 1,
      "src": "https://example.com/banner.jpg"
    }
  ]
}
```

### Type 字段映射

| OOP Layout Engine | Pydantic Schema | 前端组件 |
|------------------|-----------------|---------|
| `TextBlock` → | `"text"` | `<TextLayer>` |
| `ImageBlock` → | `"image"` | `<ImageLayer>` |
| *(未来)* ShapeBlock → | `"rect"` | `<ShapeLayer>` |

## 🔧 工作流集成示例

### 在 Layout Agent 中使用

```python
from app.services.renderer import RendererService
from app.core.logger import get_logger

logger = get_logger(__name__)

def layout_node(state: dict) -> dict:
    """Layout Agent - 使用 OOP 布局引擎"""
    
    logger.info("🎨 Layout Agent 开始工作...")
    
    # 1. 生成 DSL 指令（通过 LLM 或规则）
    dsl_instructions = generate_dsl_from_design_brief(state["design_brief"])
    
    # 2. 使用 RendererService 渲染
    renderer = RendererService()
    
    try:
        poster_data = renderer.render_poster_from_workflow_state({
            "design_brief": state["design_brief"],
            "asset_list": state["asset_list"],
            "final_poster": {"dsl_instructions": dsl_instructions},
            "canvas_width": state["canvas_width"],
            "canvas_height": state["canvas_height"]
        })
        
        # 3. 更新状态
        state["final_poster"] = poster_data.model_dump()
        logger.info("✅ Layout 完成")
        
    except Exception as e:
        logger.error(f"❌ Layout 失败: {e}")
        # 回退到默认布局
        state["final_poster"] = create_fallback_layout(state)
    
    return state
```

### 快速创建海报（无需 DSL）

```python
from app.services.renderer import create_simple_poster_from_text

# 快速创建简单海报
poster_data = create_simple_poster_from_text(
    title="VibePoster",
    subtitle="智能海报设计系统",
    image_url="https://example.com/banner.jpg",
    canvas_width=1080,
    canvas_height=1920
)

# 直接使用
json_data = poster_data.model_dump()
```

## ✅ 测试验证

### 运行测试

```bash
cd backend/engine
python test_renderer.py
```

### 测试覆盖

- ✅ DSL 指令解析
- ✅ OOP 布局计算
- ✅ Pydantic Schema 转换
- ✅ Type 字段验证
- ✅ JSON 导出

### 预期输出

```
[测试 1] 解析 DSL 指令并构建布局
✅ 布局构建完成:
  容器尺寸: 1080 x 938.0
  子元素数: 4

[测试 2] 转换为 Pydantic Schema
✅ Schema 转换完成:
  画布: 1080 x 938
  背景色: #FFF8F0
  图层数: 4

图层详情:
  1. [text ] y=40, h=96  | 年终大促
  2. [text ] y=156, h=54 | 全场5折起
  3. [image] y=230, h=600 | https://example.com/banner.jpg
  4. [text ] y=850, h=48 | 立即抢购 →

✅ 所有测试通过！
```

## 🎨 前端使用

### React 组件示例

```typescript
// 前端根据 type 渲染对应组件
const PosterLayer = ({ layer }) => {
  switch (layer.type) {
    case 'text':
      return <TextLayer {...layer} />;
    case 'image':
      return <ImageLayer {...layer} />;
    case 'rect':
      return <ShapeLayer {...layer} />;
    default:
      console.warn(`Unknown layer type: ${layer.type}`);
      return null;
  }
};

// 渲染整个海报
const Poster = ({ posterData }) => {
  return (
    <Canvas {...posterData.canvas}>
      {posterData.layers.map(layer => (
        <PosterLayer key={layer.id} layer={layer} />
      ))}
    </Canvas>
  );
};
```

## 🔄 数据流完整示例

```python
# 1. Planner 输出
planner_output = {
    "title": "年终大促",
    "subtitle": "全场5折起",
    "main_color": "#FF0000",
    "background_color": "#FFF8F0"
}

# 2. Visual 输出
visual_output = {
    "background_layer": {"src": "https://cdn.example.com/bg.jpg"},
    "foreground_layer": {"src": "https://cdn.example.com/product.jpg"}
}

# 3. Layout 生成 DSL
dsl_instructions = [
    {"command": "add_title", "content": planner_output["title"], "font_size": 64},
    {"command": "add_subtitle", "content": planner_output["subtitle"], "font_size": 36},
    {"command": "add_image", "src": "", "width": 800, "height": 600}  # src 将被填充
]

# 4. RendererService 整合
renderer = RendererService()

# 4.1 构建布局
container = renderer.parse_dsl_and_build_layout(
    dsl_instructions=dsl_instructions,
    canvas_width=1080,
    design_brief=planner_output
)

# 4.2 转换 Schema
poster_data = renderer.convert_to_pydantic_schema(
    container=container,
    design_brief=planner_output
)

# 4.3 合并数据
poster_data = renderer.merge_with_design_brief(
    poster_data=poster_data,
    design_brief=planner_output,
    asset_list=visual_output
)

# 5. 输出最终 JSON
final_json = poster_data.model_dump()
```

## 🐛 故障排除

### 问题：图层缺少 type 字段

**原因：** 旧版 layout_engine 没有返回 type

**解决：** 更新到最新版 layout_engine.py，`render()` 方法已包含 type 字段

### 问题：坐标不是整数

**原因：** OOP 引擎返回浮点数

**解决：** `convert_to_pydantic_schema()` 已自动转换为整数

### 问题：图片 src 为空

**原因：** DSL 指令中没有 src，需要 `merge_with_design_brief()` 填充

**解决：** 确保调用 `merge_with_design_brief()` 并传入 asset_list

## 📄 License

© 2025 VibePoster Team


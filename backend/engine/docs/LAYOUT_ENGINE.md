# OOP Layout Engine - 面向对象的动态布局引擎

## 📚 概述

替代"死算坐标"的硬编码方式，使用"容器+组件"的流式布局逻辑（类似 CSS Flexbox）。

### 核心思想

**元素的位置不是写死的，而是由容器自动计算的。**

当文字变长时，下方的元素会自动被推下去，无需手动重新计算所有坐标。

## 🏗️ 架构设计

### 类层次结构

```
Element (抽象基类)
├── TextBlock (文本组件)
├── ImageBlock (图片组件)
└── Container (容器基类)
    ├── VerticalContainer (垂直布局)
    └── HorizontalContainer (水平布局)
```

### 核心类说明

#### 1. `Element` (抽象基类)

所有元素的基类，定义了通用属性和方法。

**属性：**
- `x, y` - 位置
- `width, height` - 尺寸
- `z_index` - 层级
- `style` - 样式配置

**方法：**
- `render() -> Dict` - 渲染为字典（用于导出）
- `set_position(x, y)` - 设置位置
- `get_bounds()` - 获取边界框

#### 2. `TextBlock` (文本组件)

**特性：**
- ✅ **自动计算高度** - 根据文本内容、字体大小、最大宽度自动计算
- ✅ **动态更新** - 内容变化时自动重新计算高度并触发父容器重排

**算法：**
```python
字符平均宽度 = font_size * 0.7
总宽度 = len(content) * 字符平均宽度
行数 = ceil(总宽度 / max_width)
总高度 = 行数 * font_size * line_height
```

**使用示例：**
```python
text = TextBlock(
    content="VibePoster - 智能海报设计系统",
    font_size=24,
    max_width=400,
    line_height=1.5,
    style=Style(font_weight="bold", color="#333")
)
# 高度自动计算：约 72px (2行 * 24px * 1.5)
```

#### 3. `ImageBlock` (图片组件)

**特性：**
- ✅ 支持宽高比保持
- ✅ 动态调整尺寸

**使用示例：**
```python
image = ImageBlock(
    src="https://example.com/photo.jpg",
    width=400,
    height=300,
    maintain_aspect_ratio=True
)

# 调整大小（保持宽高比）
image.resize(500)  # 高度自动调整为 375
```

#### 4. `VerticalContainer` (垂直布局容器)

**特性：**
- ✅ 子元素从上到下自动排列
- ✅ 自动计算容器总高度
- ✅ 支持 padding 和 gap

**排列算法：**
```python
current_y = container.y + padding
for element in elements:
    element.y = current_y
    current_y += element.height + gap
container.height = current_y - container.y + padding
```

**使用示例：**
```python
container = VerticalContainer(
    x=0, y=0,
    width=400,
    padding=20,  # 内边距
    gap=15       # 子元素间距
)

container.add(title).add(image).add(footer)
container.arrange()  # 自动排列
```

#### 5. `HorizontalContainer` (水平布局容器)

子元素从左到右排列（用于图标、按钮等场景）。

## 🚀 使用示例

### 示例 1: 简单促销海报

```python
from app.core.layout import VerticalContainer, TextBlock, ImageBlock, Style

# 创建容器
poster = VerticalContainer(width=1080, padding=40, gap=30)

# 添加标题
title = TextBlock(
    content="年终大促",
    font_size=72,
    max_width=1000,
    style=Style(font_size=72, font_weight="bold", color="#FF0000")
)

# 添加主图
main_image = ImageBlock(
    src="product.jpg",
    width=1000,
    height=800
)

# 组装并排列
poster.add(title).add(main_image)
poster.arrange()

# 导出为 PSD 格式
layers = poster.get_all_elements()
```

### 示例 2: 动态更新内容

```python
# 初始状态
title = TextBlock(content="短标题", font_size=36, max_width=400)
image = ImageBlock(src="photo.jpg", width=400, height=300)

container = VerticalContainer(width=400, gap=20)
container.add(title).add(image)
container.arrange()

print(f"图片初始 y: {image.y}")  # 例如: 76

# 更新标题（变长）
title.update_content("这是一个很长很长的标题，会自动换行")

print(f"图片更新后 y: {image.y}")  # 自动向下移动，例如: 112
```

### 示例 3: 容器嵌套

```python
# 主容器
main = VerticalContainer(width=600, padding=30, gap=20)

# 标题区（子容器）
header = VerticalContainer(width=540, padding=10, gap=5)
header.add(TextBlock(content="限时优惠", font_size=36))
header.add(TextBlock(content="全场5折", font_size=18))
header.arrange()

# 主图
main_image = ImageBlock(src="banner.jpg", width=540, height=400)

# 组装
main.add(header).add(main_image)
main.arrange()
```

## 📊 与传统方式对比

| 特性 | 传统方式（硬编码） | OOP Layout Engine |
|------|------------------|-------------------|
| 计算坐标 | ❌ 手动计算每个元素 | ✅ 容器自动计算 |
| 内容变化 | ❌ 需要重新计算所有坐标 | ✅ 自动重排 |
| 代码可读性 | ❌ 大量数字，难以维护 | ✅ 语义化，清晰易懂 |
| 复杂布局 | ❌ 嵌套困难 | ✅ 容器嵌套轻松实现 |
| 响应式 | ❌ 不支持 | ✅ 可扩展支持 |

### 传统方式示例

```python
# ❌ 硬编码坐标 - 难以维护
title_y = 20
title_height = 72

subtitle_y = title_y + title_height + 15  # 需要手动计算
subtitle_height = 36

image_y = subtitle_y + subtitle_height + 15  # 又要手动计算
image_height = 500

# 如果 title 内容变长，需要：
# 1. 重新计算 title_height
# 2. 更新 subtitle_y
# 3. 更新 image_y
# 4. 更新所有后续元素...
```

### OOP Layout Engine 方式

```python
# ✅ 自动布局 - 易于维护
container = VerticalContainer(padding=20, gap=15)
container.add(title).add(subtitle).add(image)
container.arrange()

# 内容变化？一行代码搞定：
title.update_content("新标题")  # 所有元素自动重排！
```

## 🎯 核心优势

### 1. ✅ 零手动计算

```python
# 不需要：
y1 = 20
y2 = y1 + h1 + gap
y3 = y2 + h2 + gap
...

# 只需要：
container.add(elem1).add(elem2).add(elem3)
container.arrange()
```

### 2. ✅ 自动响应变化

```python
# 文本变长？
text.update_content("很长的新内容...")  # 自动调整所有布局

# 图片调整大小？
image.resize(600)  # 自动触发重排
```

### 3. ✅ 容器嵌套

```python
# 标题区
header = VerticalContainer()
header.add(main_title).add(subtitle)

# 特性区
features = HorizontalContainer()
features.add(icon1).add(icon2).add(icon3)

# 主布局
main = VerticalContainer()
main.add(header).add(banner).add(features)
main.arrange()
```

### 4. ✅ 直接导出 PSD

```python
# 获取所有图层（扁平化）
layers = container.get_all_elements()

psd_data = {
    "canvas": {"width": 1080, "height": container.height},
    "layers": layers
}
```

## 🔧 集成建议

### 在 Layout Agent 中使用

```python
from app.core.layout import VerticalContainer, TextBlock, ImageBlock

def generate_poster_layout(plan: dict) -> dict:
    """替代原有的硬编码坐标计算"""
    
    # 创建动态容器
    container = VerticalContainer(
        width=plan["canvas_width"],
        padding=40,
        gap=20
    )
    
    # 根据规划添加元素
    if plan.get("title"):
        title = TextBlock(
            content=plan["title"],
            font_size=plan["title_font_size"],
            max_width=plan["canvas_width"] - 80
        )
        container.add(title)
    
    if plan.get("image"):
        image = ImageBlock(
            src=plan["image_url"],
            width=plan["image_width"],
            height=plan["image_height"]
        )
        container.add(image)
    
    # 自动排列
    container.arrange()
    
    # 导出
    return {
        "canvas": {"width": container.width, "height": container.height},
        "layers": container.get_all_elements()
    }
```

## 📝 API 参考

### TextBlock

```python
TextBlock(
    content: str,               # 文本内容
    font_size: int = 16,       # 字体大小
    max_width: float = 400,    # 最大宽度
    line_height: float = 1.5,  # 行高倍数
    style: Optional[Style] = None
)
```

**方法：**
- `calculate_height() -> float` - 计算高度
- `update_content(new_content: str)` - 更新内容并重排

### ImageBlock

```python
ImageBlock(
    src: str,                           # 图片源
    width: float,                       # 宽度
    height: float,                      # 高度
    maintain_aspect_ratio: bool = True  # 保持宽高比
)
```

**方法：**
- `resize(width: float, height: Optional[float] = None)` - 调整大小

### VerticalContainer

```python
VerticalContainer(
    width: float = 400,     # 容器宽度
    padding: float = 20,    # 内边距
    gap: float = 10         # 子元素间距
)
```

**方法：**
- `add(element: Element) -> self` - 添加子元素（链式调用）
- `arrange()` - 排列子元素
- `get_all_elements() -> List[Dict]` - 获取所有图层

## 🧪 测试

```bash
# 运行单元测试
python app/core/layout_engine.py

# 运行示例
python app/core/layout_example.py
```

**测试覆盖：**
- ✅ 基础垂直布局
- ✅ 动态更新内容
- ✅ 容器嵌套
- ✅ 导出 PSD 格式
- ✅ 水平布局

## 🎨 最佳实践

### 1. 使用语义化变量名

```python
# ✅ Good
header = VerticalContainer()
header.add(brand_logo).add(main_title).add(tagline)

# ❌ Bad
c1 = VerticalContainer()
c1.add(elem1).add(elem2).add(elem3)
```

### 2. 合理设置 padding 和 gap

```python
# 海报级容器：大 padding
poster = VerticalContainer(padding=40, gap=30)

# 内部小组件：小 padding
card = VerticalContainer(padding=15, gap=10)
```

### 3. 利用链式调用

```python
container.add(title) \
         .add(subtitle) \
         .add(image) \
         .add(footer)
container.arrange()
```

### 4. 预留扩展空间

```python
# 为未来可能增加的内容预留空间
container = VerticalContainer(
    padding=50,  # 稍大的 padding
    gap=30       # 较大的间距
)
```

## 📄 License

© 2025 VibePoster Team


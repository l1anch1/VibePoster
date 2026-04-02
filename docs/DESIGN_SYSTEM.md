# VibePoster 设计系统

> iOS 液态玻璃风格统一规范

---

## 🎨 设计原则

1. **高对比度** - 所有文字清晰可读，主文字使用深色
2. **一致性** - 全局使用相同的字体、颜色、圆角规范
3. **层次感** - 通过颜色深浅和字体粗细区分内容层级
4. **玻璃质感** - 使用 backdrop-filter 和半透明背景营造质感

---

## 📐 字体规范

### 字体家族
```css
font-family: "Inter", system-ui, -apple-system, sans-serif;
```

### 字体大小

| 用途 | Tailwind Class | 大小 | 示例 |
|------|---------------|------|------|
| 大标题 | `text-5xl` ~ `text-7xl` | 48-72px | Hero 标题 |
| 页面标题 | `text-3xl` ~ `text-4xl` | 30-36px | Section 标题 |
| 卡片标题 | `text-lg` ~ `text-base` | 16-18px | 功能卡片标题 |
| 面板标题 | `text-sm` | 14px | 侧边栏标题 |
| 正文/按钮 | `text-sm` | 14px | 主要内容文字 |
| 标签/辅助 | `text-xs` | 12px | 表单标签、辅助文字 |
| 极小文字 | `text-[10px]` | 10px | 提示、badge |

### 字重

| 用途 | Tailwind Class | 权重 |
|------|---------------|------|
| 标题 | `font-bold` | 700 |
| 强调/按钮 | `font-semibold` | 600 |
| 正文/链接 | `font-medium` | 500 |
| 普通文字 | `font-normal` | 400 |

---

## 🎨 颜色规范

### 文字颜色

| 用途 | Tailwind Class | 颜色值 | 示例 |
|------|---------------|--------|------|
| 标题 | `text-gray-900` | #111827 | 大标题、页面标题 |
| 强调文字 | `text-gray-800` | #1f2937 | 面板标题、卡片标题 |
| 正文 | `text-gray-700` | #374151 | 主要内容、链接 |
| 说明文字 | `text-gray-600` | #4b5563 | 描述、次要内容 |
| 辅助文字 | `text-gray-500` | #6b7280 | 标签、占位符 |
| 弱化文字 | `text-gray-400` | #9ca3af | 禁用状态、提示 |

### 品牌色

```css
/* 渐变按钮 */
bg-gradient-to-r from-violet-500 to-fuchsia-500

/* 阴影 */
shadow-violet-500/30  /* 主按钮阴影 */
shadow-violet-500/20  /* 次级元素阴影 */
```

### 边框颜色

| 用途 | Tailwind Class | 场景 |
|------|---------------|------|
| 默认边框 | `border-gray-300` | 输入框、按钮、卡片 |
| 分隔线 | `border-gray-200` | 面板分隔、列表分隔 |
| 聚焦边框 | `border-violet-500` | focus 状态 |
| 悬停边框 | `border-violet-400` | hover 状态 |

---

## 📦 组件规范

### 输入框 (Input)

```tsx
<input
  className="w-full px-3 py-2.5 text-sm bg-white border border-gray-300 rounded-xl 
             focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 
             outline-none transition-all text-gray-900 placeholder-gray-400 shadow-sm"
/>
```

或使用工具类：
```tsx
<input className="input-base" />
```

### 标签 (Label)

```tsx
<label className="block text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">
  Label Text
</label>
```

或使用工具类：
```tsx
<label className="label-base">Label Text</label>
```

### 主按钮 (Primary Button)

```tsx
<button className="px-4 py-2.5 text-sm font-semibold rounded-xl 
                   bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white 
                   shadow-lg shadow-violet-500/30 
                   hover:shadow-xl hover:shadow-violet-500/40 
                   hover:-translate-y-0.5 transition-all">
  Button Text
</button>
```

或使用工具类：
```tsx
<button className="btn-primary">Button Text</button>
```

### 次按钮 (Secondary Button)

```tsx
<button className="px-4 py-2.5 text-sm font-medium rounded-xl 
                   bg-white text-gray-700 border border-gray-300 shadow-sm 
                   hover:bg-gray-50 hover:border-gray-400 transition-all">
  Button Text
</button>
```

### 玻璃面板 (Glass Panel)

```tsx
<div
  className="rounded-3xl overflow-hidden"
  style={{
    background: 'rgba(255,255,255,0.85)',
    backdropFilter: 'blur(20px) saturate(180%)',
    boxShadow: '0 8px 32px rgba(0,0,0,0.1), inset 0 0 0 1px rgba(255,255,255,0.6)',
    border: '1px solid rgba(0,0,0,0.08)',
  }}
>
  {/* 内容 */}
</div>
```

### 面板标题

```tsx
<div className="px-5 py-4 border-b border-gray-200">
  <h2 className="text-sm font-semibold text-gray-800">Panel Title</h2>
  <p className="text-xs text-gray-500 mt-0.5">Panel description</p>
</div>
```

### 节标题 (Section Label)

```tsx
<h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
  Section Label
</h4>
```

---

## 🔘 圆角规范

| 用途 | Tailwind Class | 大小 |
|------|---------------|------|
| 小按钮/标签 | `rounded-lg` | 8px |
| 输入框/按钮 | `rounded-xl` | 12px |
| 卡片/下拉框 | `rounded-2xl` | 16px |
| 面板/模态框 | `rounded-3xl` | 24px |
| 预览框 | `rounded-[32px]` | 32px |

---

## 🌫️ 阴影规范

```css
/* 基础阴影 - 所有输入框、按钮 */
shadow-sm

/* 中等阴影 - 卡片、面板 */
shadow-md

/* 强调阴影 - 主按钮 */
shadow-lg shadow-violet-500/30

/* 悬停阴影 - 主按钮 hover */
shadow-xl shadow-violet-500/40

/* 玻璃阴影 */
box-shadow: 0 8px 32px rgba(0,0,0,0.1), inset 0 0 0 1px rgba(255,255,255,0.6);
```

---

## 📱 响应式断点

| 断点 | 宽度 | 用途 |
|------|------|------|
| `sm` | 640px | 移动端 |
| `md` | 768px | 平板 |
| `lg` | 1024px | 小桌面 |
| `xl` | 1280px | 大桌面 |

---

## 🔧 CSS 工具类

在 `index.css` 中定义了以下工具类：

```css
.input-base    /* 统一输入框样式 */
.label-base    /* 统一标签样式 */
.btn-primary   /* 主按钮 */
.btn-secondary /* 次按钮 */
.btn-ghost     /* 幽灵按钮 */
.glass         /* 玻璃面板（深） */
.glass-light   /* 玻璃面板（浅） */
.panel-title   /* 面板标题 */
.panel-desc    /* 面板描述 */
.section-label /* 节标题 */
```

---

## ✅ 检查清单

在开发新组件时，请确保：

- [ ] 使用 `text-gray-900` 或 `text-gray-800` 作为标题颜色
- [ ] 使用 `text-sm` (14px) 作为主要文字大小
- [ ] 使用 `text-xs` (12px) 作为标签和辅助文字
- [ ] 使用 `border-gray-300` 作为默认边框
- [ ] 使用 `rounded-xl` 或更大的圆角
- [ ] 添加 `shadow-sm` 基础阴影
- [ ] 使用 `font-semibold` 或 `font-medium` 增加文字可读性
- [ ] Focus 状态使用 `border-violet-500` 和 `ring-violet-500/20`

---

**最后更新**: 2025-01-08


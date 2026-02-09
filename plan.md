# PSD 转前端代码方案改进计划

## 📌 目标
基于渐进式开发原则，将 PSD 设计稿转换为高质量、可维护的前端代码。

---

## 一、方案概述

### 核心流程
```
PSD → psd_to_vibe.py → vibe_context/ → LLM → 阶段性前端代码
```

### 关键改进点
1. **增强解析能力**：提取更多设计元数据（颜色、字体、阴影、渐变等）
2. **结构化数据增强**：添加设计系统信息和语义标记
3. **分阶段代码生成**：从静态布局逐步演进到完整功能
4. **验证机制**：视觉回归测试确保生成代码与设计稿一致

---

## 二、阶段 0：数据解析层优化

### 2.1 增强数据结构设计

**扩展后的 `layout_data.json` 格式：**

```json
{
  "metadata": {
    "designWidth": 1920,
    "designHeight": 5080,
    "generatedAt": "2026-02-09T10:00:00Z"
  },
  "designTokens": {
    "colors": {
      "primary": "#3b82f6",
      "secondary": "#64748b",
      "accent": "#f59e0b"
    },
    "fonts": {
      "heading": "Inter, sans-serif",
      "body": "Inter, sans-serif"
    },
    "spacing": {
      "sm": 8,
      "md": 16,
      "lg": 24,
      "xl": 32
    }
  },
  "layers": [
    {
      "name": "按钮",
      "kind": "group",
      "content_type": "component",
      "componentType": "button",
      "bbox": {
        "left": 100,
        "top": 200,
        "width": 200,
        "height": 50
      },
      "styles": {
        "backgroundColor": "#3b82f6",
        "borderRadius": 8,
        "boxShadow": "0 2px 8px rgba(0,0,0,0.1)",
        "opacity": 1
      },
      "children": [
        {
          "name": "文字",
          "kind": "type",
          "content_type": "text",
          "text": "立即购买",
          "font_size": 16,
          "font_weight": "bold",
          "color": "#ffffff"
        }
      ]
    }
  ]
}
```

### 2.2 psd_to_vibe.py 改进任务

#### 任务 1：提取图层样式
- [ ] 提取背景色、边框、圆角、阴影
- [ ] 提取透明度（opacity）
- [ ] 提取渐变（如果 psd-tools 支持）
- [ ] 提取字体详细信息（font-weight、font-style、letter-spacing）

#### 任务 2：组件识别
- [ ] 基于命名规则识别组件（`按钮_`、`卡片_`、`导航_`）
- [ ] 自动标记 `componentType`（button、input、card、nav、header、footer）
- [ ] 识别可复用组件并标记 `isReusable`

#### 任务 3：设计令牌提取
- [ ] 遍历所有颜色，生成颜色面板
- [ ] 提取字体栈和字号体系
- [ ] 提取常用间距值

#### 任务 4：资源优化
- [ ] 使用 Pillow 压缩导出的 PNG
- [ ] 转换小图标为 SVG（通过 potrace）
- [ ] 生成 WebP 格式备用

#### 任务 5：增强布局信息
- [ ] 提取图层层级关系（zIndex）
- [ ] 标记对齐方式（alignCenter、spaceBetween）
- [ ] 推断布局模型（flex、grid、absolute）

---

## 三、阶段 1：静态布局生成

### 3.1 目标
生成完全还原设计稿视觉的静态页面（HTML + CSS）

### 3.2 生成策略
- 使用绝对定位确保像素级还原
- 内联样式或 `<style>` 标签
- 直接引用 `assets/` 中的图片资源

### 3.3 提示词模板
```markdown
你是一名前端工程师，请基于提供的设计稿数据生成静态页面代码。

**设计稿信息：**
- 尺寸：1920x5080px
- 设计令牌：{colors, fonts, spacing}

**生成要求：**
1. 使用 HTML + CSS，不使用 JavaScript
2. 优先使用绝对定位确保像素级还原
3. 图片资源使用相对路径 `assets/xxx.png`
4. 保持代码结构清晰，按区域分组注释

**输出格式：**
- 单个 HTML 文件，包含所有 CSS
- 文件名：index.html
```

### 3.4 验证标准
- [ ] 视觉还原度 ≥ 95%
- [ ] 所有图片资源正确引用
- [ ] 无明显布局偏差

---

## 四、阶段 2：语义化与布局优化

### 4.1 目标
将绝对定位改为语义化 HTML + 现代 CSS 布局（Flexbox/Grid）

### 4.2 改进步骤
1. **语义化标签替换**
   - `<div class="header">` → `<header>`
   - `<div class="nav">` → `<nav>`
   - `<div class="main">` → `<main>`
   - `<div class="footer">` → `<footer>`

2. **布局模型转换**
   - 横向排列的元素 → Flexbox
   - 网格布局 → CSS Grid
   - 保留必要的绝对定位（装饰元素、浮动按钮）

3. **CSS 重构**
   - 提取公共样式（按钮、卡片、文本）
   - 使用设计令牌变量（--primary、--spacing-md）

### 4.3 提示词模板
```markdown
你是一名高级前端工程师，请将静态页面重构为语义化、可维护的代码。

**输入：**
- 当前的 HTML + CSS 代码（使用绝对定位）
- 设计令牌信息

**重构要求：**
1. 替换为语义化 HTML 标签（header、nav、main、footer）
2. 使用 Flexbox 或 Grid 重构布局
3. 提取公共组件样式（按钮、卡片）
4. 使用 CSS 变量定义设计令牌

**输出：**
- 重构后的 HTML 文件
- 单独的 CSS 文件（styles.css）
```

---

## 五、阶段 3：响应式设计

### 5.1 目标
适配移动端（320px~768px）和桌面端（≥1024px）

### 5.2 实现策略
1. **移动优先原则**
   - 基础样式针对移动端
   - 通过媒体查询适配大屏

2. **响应式断点**
   - `@media (min-width: 768px)` - 平板
   - `@media (min-width: 1024px)` - 桌面

3. **适配内容**
   - 导航栏：移动端折叠为汉堡菜单
   - 网格布局：列数动态调整
   - 字体大小：使用 `rem` 或 `clamp()`
   - 图片：使用 `srcset` 和 `sizes`

### 5.3 验证标准
- [ ] 在 320px、768px、1920px 下均正常显示
- [ ] 无横向滚动条
- [ ] 触摸区域 ≥ 44px

---

## 六、阶段 4：交互功能实现

### 6.1 目标
添加用户交互行为（hover、click、scroll 等）

### 6.2 实现功能
- [ ] 按钮悬停效果（背景色变化、阴影增强）
- [ ] 导航菜单展开/收起（移动端汉堡菜单）
- [ ] 轮播图/幻灯片切换
- [ ] 表单验证（可选）
- [ ] 滚动动画（淡入、滑动）

### 6.3 技术选型
- 纯 JavaScript（轻量、无依赖）
- 或使用现代框架（React/Vue，按需选择）

---

## 七、阶段 5：组件化与优化

### 7.1 目标
提取可复用组件，支持后续维护和扩展

### 7.2 组件提取
- 按钮（Button）
- 卡片（Card）
- 导航栏（Navbar）
- 页脚（Footer）
- 表单元素（Input、Select）

### 7.3 优化项
- **性能优化**：图片懒加载、代码分割
- **SEO 优化**：添加 meta 标签、语义化结构
- **可访问性**：ARIA 属性、键盘导航
- **构建工具**：引入 Vite/Webpack（可选）

---

## 八、验证与测试

### 8.1 视觉回归测试
使用工具对比生成页面与设计稿：
- **推荐工具**：Percy、Chromatic、BackstopJS
- **测试流程**：
  1. 截图生成页面
  2. 与 `full_preview.png` 对比
  3. 允许误差阈值（≤5%）

### 8.2 代码质量检查
- ESLint（JavaScript/TypeScript）
- Stylelint（CSS）
- Lighthouse（性能、可访问性）

---

## 九、技术栈建议

| 模块 | 推荐方案 | 备选方案 |
|------|----------|----------|
| 解析工具 | `ag-psd` | `psd-tools`（当前） |
| 图片压缩 | Pillow + optipng | ImageMagick |
| SVG 转换 | potrace | svgtrace |
| 前端框架 | 纯 HTML/CSS/JS | React、Vue（按需） |
| 构建工具 | Vite（轻量） | Webpack |

---

## 十、实施路线图

| 阶段 | 任务 | 优先级 | 状态 |
|------|------|--------|------|
| 阶段 0 | 优化 `psd_to_vibe.py` | P0 | 待开始 |
| 阶段 0 | 提取设计令牌 | P0 | 待开始 |
| 阶段 1 | 生成静态页面 | P0 | 待开始 |
| 阶段 2 | 语义化重构 | P1 | 待开始 |
| 阶段 3 | 响应式适配 | P1 | 待开始 |
| 阶段 4 | 交互功能 | P2 | 待开始 |
| 阶段 5 | 组件化 | P2 | 待开始 |
| 验证 | 视觉回归测试 | P1 | 待开始 |

---

## 十一、潜在挑战与应对

| 挑战 | 应对方案 |
|------|----------|
| PSD 复杂效果丢失 | 人工补充关键样式到 JSON |
| LLM 布局推断不准 | 提供明确的布局提示（flex/grid/absolute） |
| 组件识别不准 | 建立命名规范，人工标记关键组件 |
| 响应式适配困难 | 优先保证桌面端，移动端简化处理 |

---

## 附录：文件结构

```
PSD2AI/
├── psd_to_vibe.py              # PSD 解析脚本
├── plan.md                     # 本文档
├── vibe_context/               # 输出目录
│   ├── full_preview.png        # 设计稿全貌
│   ├── layout_data.json        # 增强后的结构化数据
│   ├── design_tokens.json      # （新增）设计令牌
│   ├── components.json         # （新增）组件库
│   └── assets/                 # 资源文件
│       ├── xxx.png
│       └── xxx.svg
└── output/                     # （新增）生成的前端代码
    ├── index.html
    ├── styles.css
    └── script.js
```

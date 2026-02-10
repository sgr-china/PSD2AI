# Vibe Coding 执行计划

## 📋 项目目标
根据 PSD 设计稿（`1920_new.psd`）生成完整的前端页面，遵循设计令牌规范，保持视觉一致性。

---

## 📁 可用上下文

### 1. 设计元数据
- 文件：`vibe_context/layers/metadata.json`
- 内容：设计画布尺寸（1920x5080）、生成时间、PSD 文件名、总图层数
- 用途：确定页面基础尺寸和比例

### 2. 设计令牌
- 文件：`vibe_context/layers/design_tokens.json`
- 内容：
  - **颜色**：`#000000`（主色）
  - **字体大小**：14.0, 15.8, 16.0, 18.0, 20.0, 24.0, 30.0, 32.0, 40.0
  - **间距**：1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22
- 用途：所有样式必须从设计令牌中取值，保持一致性

### 3. 图层索引
- 文件：`vibe_context/layers/index.json`
- 内容：6 个图层的名称、文件路径、组件类型、zIndex
- 用途：了解整体结构，按顺序处理图层

### 4. 图层数据（按 zIndex 从高到低）
| Index | Name | File | Type | zIndex | 说明 |
|-------|------|------|------|--------|------|
| 0 | 背景 | 00_背景.json | image | 6 | 全屏背景图 |
| 1 | top | 01_top.json | container | 5 | 顶部区域（header） |
| 2 | 1 | 02_1.json | container | 4 | 内容区块1 |
| 3 | 2 | 03_2.json | container | 3 | 内容区块2 |
| 4 | 3 | 04_3.json | container | 2 | 内容区块3 |
| 5 | 图层 21 | 05_图层_21.json | image | 1 | 底部图层 |

---

## 🎯 执行策略

### 阶段 1：准备工作（1 次性任务）
- [ ] 读取 `metadata.json`，确定页面基础尺寸（1920x5080）
- [ ] 读取 `design_tokens.json`，建立设计系统规范
- [ ] 读取 `index.json`，了解图层结构和顺序

### 阶段 2：分层构建（按 zIndex 从高到低）
**原则**：
- zIndex 值越大，越在上层（越晚渲染）
- 从 zIndex=6（背景）开始，逐步向上叠加
- 每个图层生成后，需要与已有图层组合测试

**步骤**：

#### 任务 2.1：构建背景层（zIndex=6）
- [ ] 读取 `00_背景.json`
- [ ] 生成全屏背景图（尺寸：1920x5080，位置：0,0）
- [ ] 输出文件：`src/components/Background.vue` 或 `<div class="background">`
- [ ] 验证：背景图覆盖整个页面

#### 任务 2.2：构建顶部区域（zIndex=5）
- [ ] 读取 `01_top.json`
- [ ] 解析内部嵌套结构（包含多个子图层）
- [ ] 生成 header 区域的 HTML+CSS
- [ ] 输出文件：`src/components/Header.vue` 或 `<header>`
- [ ] 验证：位置和尺寸正确，内部元素布局合理

#### 任务 2.3：构建内容区块1（zIndex=4）
- [ ] 读取 `02_1.json`
- [ ] 解析容器内的元素
- [ ] 生成区块1的 HTML+CSS
- [ ] 输出文件：`src/components/Section1.vue` 或 `<section id="section-1">`
- [ ] 验证：位置和样式正确

#### 任务 2.4：构建内容区块2（zIndex=3）
- [ ] 读取 `03_2.json`
- [ ] 生成区块2的 HTML+CSS
- [ ] 输出文件：`src/components/Section2.vue` 或 `<section id="section-2">`
- [ ] 验证：位置和样式正确

#### 任务 2.5：构建内容区块3（zIndex=2）
- [ ] 读取 `04_3.json`
- [ ] 生成区块3的 HTML+CSS
- [ ] 输出文件：`src/components/Section3.vue` 或 `<section id="section-3">`
- [ ] 验证：位置和样式正确

#### 任务 2.6：构建底部层（zIndex=1）
- [ ] 读取 `05_图层_21.json`
- [ ] 生成底部图层的 HTML+CSS
- [ ] 输出文件：`src/components/FooterBg.vue` 或 `<div class="footer-bg">`
- [ ] 验证：位置正确（top: 4890）

### 阶段 3：整合页面
- [ ] 创建主页面文件：`src/App.vue` 或 `index.html`
- [ ] 按 zIndex 顺序引入所有组件
- [ ] 设置全局样式（基于设计令牌）
- [ ] 验证：所有图层正确叠加，整体布局与 PSD 一致

### 阶段 4：优化和迭代
- [ ] 检查视觉还原度，对比 `full_preview.png`
- [ ] 调整不准确的样式（颜色、间距、字体）
- [ ] 确保所有样式值来自设计令牌
- [ ] 输出最终版本

---

## 📝 输出规范

### 文件结构
```
src/
├── components/
│   ├── Background.vue
│   ├── Header.vue
│   ├── Section1.vue
│   ├── Section2.vue
│   ├── Section3.vue
│   └── FooterBg.vue
├── App.vue          # 主页面（整合所有组件）
├── assets/          # 图片资源（已存在：vibe_context/assets/）
└── styles/
    └── design-tokens.css  # 设计令牌 CSS 变量
```

### 样式规范
- **颜色**：必须使用 `design_tokens.json` 中的颜色值
- **字体大小**：从设计令牌中选择最接近的值
- **间距**：优先使用设计令牌中的间距值（4, 8, 12, 16, 20, 24...）
- **位置**：使用绝对定位（`position: absolute`），坐标来自 `bbox`

### 代码风格
- 使用 Vue 3 单文件组件（或纯 HTML+CSS，根据需求选择）
- 组件命名：大驼峰（PascalCase）
- CSS 类名：小写字母+连字符（kebab-case）
- 添加注释：说明每个区块的来源（对应 PSD 中的哪个图层）

---

## ✅ 验收标准

- [ ] 页面尺寸：1920x5080（或按比例缩放）
- [ ] 所有图层正确渲染，顺序符合 zIndex
- [ ] 颜色、字体、间距符合设计令牌
- [ ] 整体视觉效果与 `full_preview.png` 相似度 > 80%
- [ ] 代码结构清晰，组件可复用

---

## 🔧 调试建议

1. **逐层验证**：每生成一个图层，立即预览效果
2. **对比 PSD**：用 `full_preview.png` 对比生成结果
3. **检查坐标**：确保 `bbox` 的 left/top/width/height 正确应用
4. **设计令牌一致性**：所有样式值必须来自 `design_tokens.json`

---

## 📌 注意事项

1. **图层顺序很重要**：zIndex 决定了层叠关系，不要搞反
2. **图片路径**：引用 `vibe_context/assets/` 下的图片
3. **不要硬编码**：颜色、字体、间距必须从设计令牌中取
4. **保持简洁**：先实现基本还原，再优化细节

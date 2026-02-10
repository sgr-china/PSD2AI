# Vibe Coding 任务清单

## 使用说明

- 每完成一个任务，将 `[ ]` 改为 `[x]`
- 按阶段顺序执行，不要跳步
- 遇到问题查看 `plan.md` 中的调试建议

---

## 阶段 1：准备工作

### 任务 1.1：读取元数据
- [ ] 读取 `vibe_context/layers/metadata.json`
- [ ] 记录设计尺寸：1920x5080
- [ ] 记录图层数量：6

### 任务 1.2：读取设计令牌
- [ ] 读取 `vibe_context/layers/design_tokens.json`
- [ ] 记录颜色值：`#000000`
- [ ] 记录字体大小：14.0, 15.8, 16.0, 18.0, 20.0, 24.0, 30.0, 32.0, 40.0
- [ ] 记录间距值：1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22

### 任务 1.3：读取图层索引
- [ ] 读取 `vibe_context/layers/index.json`
- [ ] 确认图层顺序（按 zIndex 从高到低）：
  1. 背景（zIndex=6）
  2. top（zIndex=5）
  3. 1（zIndex=4）
  4. 2（zIndex=3）
  5. 3（zIndex=2）
  6. 图层 21（zIndex=1）

---

## 阶段 2：分层构建

### 任务 2.1：构建背景层（zIndex=6）

#### 输入文件
- `vibe_context/layers/00_背景.json`

#### 执行步骤
- [ ] 读取 00_背景.json
- [ ] 提取 bbox 信息：left=0, top=0, width=1920, height=5080
- [ ] 提取图片路径：`assets/0_背景.png`
- [ ] 生成文件：`src/components/Background.vue`
- [ ] 使用绝对定位，设置尺寸和背景图
- [ ] 验证：背景图覆盖整个页面（1920x5080）

#### 输出文件
```
src/components/Background.vue
```

---

### 任务 2.2：构建顶部区域（zIndex=5）

#### 输入文件
- `vibe_context/layers/01_top.json`

#### 执行步骤
- [ ] 读取 01_top.json
- [ ] 解析 container 内部的 children 嵌套结构
- [ ] 提取每个子元素的 bbox、content_type、src/styles 等信息
- [ ] 生成文件：`src/components/Header.vue`
- [ ] 使用绝对定位，还原子元素的位置关系
- [ ] 验证：header 区域尺寸和内部布局正确

#### 输出文件
```
src/components/Header.vue
```

---

### 任务 2.3：构建内容区块1（zIndex=4）

#### 输入文件
- `vibe_context/layers/02_1.json`

#### 执行步骤
- [ ] 读取 02_1.json
- [ ] 解析 container 内部的 children 结构
- [ ] 提取每个子元素的信息
- [ ] 生成文件：`src/components/Section1.vue`
- [ ] 还原布局和样式
- [ ] 验证：位置和样式正确

#### 输出文件
```
src/components/Section1.vue
```

---

### 任务 2.4：构建内容区块2（zIndex=3）

#### 输入文件
- `vibe_context/layers/03_2.json`

#### 执行步骤
- [ ] 读取 03_2.json
- [ ] 解析内部结构
- [ ] 生成文件：`src/components/Section2.vue`
- [ ] 还原布局和样式
- [ ] 验证：位置和样式正确

#### 输出文件
```
src/components/Section2.vue
```

---

### 任务 2.5：构建内容区块3（zIndex=2）

#### 输入文件
- `vibe_context/layers/04_3.json`

#### 执行步骤
- [ ] 读取 04_3.json
- [ ] 解析内部结构
- [ ] 生成文件：`src/components/Section3.vue`
- [ ] 还原布局和样式
- [ ] 验证：位置和样式正确

#### 输出文件
```
src/components/Section3.vue
```

---

### 任务 2.6：构建底部层（zIndex=1）

#### 输入文件
- `vibe_context/layers/05_图层_21.json`

#### 执行步骤
- [ ] 读取 05_图层_21.json
- [ ] 提取 bbox 信息：left=0, top=4890, width=1920, height=190
- [ ] 提取图片路径：`assets/5_图层_21.png`
- [ ] 生成文件：`src/components/FooterBg.vue`
- [ ] 使用绝对定位，设置位置和尺寸
- [ ] 验证：位置正确（top: 4890）

#### 输出文件
```
src/components/FooterBg.vue
```

---

## 阶段 3：整合页面

### 任务 3.1：创建设计令牌 CSS

#### 执行步骤
- [ ] 创建文件：`src/styles/design-tokens.css`
- [ ] 将设计令牌转换为 CSS 变量：
  ```css
  :root {
    --color-primary: #000000;
    --font-size-xs: 14px;
    --font-size-sm: 16px;
    --font-size-base: 18px;
    --font-size-lg: 24px;
    --font-size-xl: 32px;
    --spacing-1: 4px;
    --spacing-2: 8px;
    --spacing-3: 12px;
    /* ... */
  }
  ```
- [ ] 验证：所有设计令牌都已转换

---

### 任务 3.2：创建主页面

#### 执行步骤
- [ ] 创建文件：`src/App.vue`
- [ ] 引入所有组件（按 zIndex 从低到高）：
  ```vue
  <template>
    <div class="page-container">
      <Background />
      <FooterBg />
      <Section3 />
      <Section2 />
      <Section1 />
      <Header />
    </div>
  </template>
  ```
- [ ] 设置全局样式（使用 design-tokens.css）
- [ ] 设置容器尺寸：1920x5080，使用绝对定位
- [ ] 验证：所有图层正确叠加

#### 输出文件
```
src/App.vue
src/styles/design-tokens.css
```

---

## 阶段 4：优化和迭代

### 任务 4.1：视觉对比

#### 执行步骤
- [ ] 打开 `vibe_context/full_preview.png`
- [ ] 对比生成的页面与 PSD 预览图
- [ ] 检查相似度是否 > 80%
- [ ] 记录差异点（颜色、位置、尺寸等）

---

### 任务 4.2：调整样式

#### 执行步骤
- [ ] 修正颜色值（确保使用设计令牌中的颜色）
- [ ] 调整间距（使用设计令牌中的间距值）
- [ ] 修正字体大小（使用设计令牌中的字体大小）
- [ ] 验证：所有样式值来自设计令牌

---

### 任务 4.3：最终验证

#### 验收清单
- [ ] 页面尺寸：1920x5080（或按比例缩放）
- [ ] 所有图层正确渲染，顺序符合 zIndex
- [ ] 颜色、字体、间距符合设计令牌
- [ ] 整体视觉效果与 full_preview.png 相似度 > 80%
- [ ] 代码结构清晰，组件可复用

---

## 最终输出

```
src/
├── components/
│   ├── Background.vue      ← 任务 2.1
│   ├── Header.vue          ← 任务 2.2
│   ├── Section1.vue        ← 任务 2.3
│   ├── Section2.vue        ← 任务 2.4
│   ├── Section3.vue        ← 任务 2.5
│   └── FooterBg.vue        ← 任务 2.6
├── App.vue                 ← 任务 3.2
├── styles/
│   └── design-tokens.css   ← 任务 3.1
└── assets/                 ← 已存在（vibe_context/assets/）
```

---

## 注意事项

1. **执行顺序**：必须按 zIndex 从高到低（6→1）构建图层
2. **图片路径**：引用 `vibe_context/assets/` 下的图片文件
3. **设计令牌**：所有样式值必须来自 `design_tokens.json`，不要硬编码
4. **绝对定位**：所有元素使用 `position: absolute`，坐标来自 bbox
5. **逐层验证**：每个任务完成后立即预览效果，不要等到全部完成

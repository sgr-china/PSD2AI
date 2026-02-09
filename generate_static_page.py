#!/usr/bin/env python3
"""
阶段 1：生成静态页面（绝对定位，像素级还原）
"""
import json
import os

INPUT_FILE = 'vibe_context/layout_data.json'
OUTPUT_FILE = 'output/index.html'
OUTPUT_DIR = 'output'

os.makedirs(OUTPUT_DIR, exist_ok=True)

# CSS 代码生成器
CSS_TEMPLATES = {
    "container": """
.{class_name} {{
    position: absolute;
    left: {left}px;
    top: {top}px;
    width: {width}px;
    height: {height}px;
    {styles}
}}
""",

    "text": """
.{class_name} {{
    position: absolute;
    left: {left}px;
    top: {top}px;
    width: {width}px;
    height: {height}px;
    font-size: {font_size}px;
    color: {color};
    {styles}
}}
""",

    "image": """
.{class_name} {{
    position: absolute;
    left: {left}px;
    top: {top}px;
    width: {width}px;
    height: {height}px;
    background-image: url('{src}');
    background-size: 100% 100%;
    background-repeat: no-repeat;
    {styles}
}}
"""
}

# 样式属性映射
STYLE_MAPPINGS = {
    "opacity": lambda v: f"opacity: {v};",
    "blend_mode": lambda v: f"mix-blend-mode: {v.lower().replace('blendmode.', '')};",
    "shadow": lambda v: f"box-shadow: {v['distance']}px {v['distance']}px {v['size']}px rgba(0,0,0,{v['opacity']});",
    "glow": lambda v: f"box-shadow: 0 0 {v['size']}px rgba(255,255,255,{v['opacity']});",
    "stroke": lambda v: f"border: {v['size']}px solid rgba(0,0,0,{v['opacity']});",
    "font_weight": lambda v: f"font-weight: {v};",
    "font_style": lambda v: f"font-style: {v};",
    "line_height": lambda v: f"line-height: {v}px;",
    "letter_spacing": lambda v: f"letter-spacing: {v}em;",
    "background_color": lambda v: f"background-color: {v};"
}

def sanitize_class_name(name, prefix=""):
    """生成安全的 CSS 类名"""
    name = name.strip().replace(' ', '_').replace('-', '_')
    name = ''.join(c if c.isalnum() or c in '_$' else '_' for c in name)
    if prefix:
        name = f"{prefix}_{name}"
    return name[:50]  # 限制长度

def generate_styles(layer):
    """生成 CSS 样式字符串"""
    styles = []

    # 透明度
    if 'blend' in layer:
        blend = layer['blend']
        if 'opacity' in blend:
            styles.append(STYLE_MAPPINGS['opacity'](blend['opacity']))
        if 'blend_mode' in blend:
            styles.append(STYLE_MAPPINGS['blend_mode'](blend['blend_mode']))

    # 效果
    if 'effects' in layer:
        effects = layer['effects']

        # 阴影
        if 'shadow' in effects:
            shadow = effects['shadow']
            if shadow.get('enabled'):
                offset_x = shadow.get('distance', 0) * (1 if shadow.get('angle', 0) < 90 else -1)
                offset_y = shadow.get('distance', 0)
                blur = shadow.get('size', 0)
                opacity = shadow.get('opacity', 0.5)
                styles.append(f"box-shadow: {offset_x}px {offset_y}px {blur}px rgba(0,0,0,{opacity});")

        # 外发光
        if 'glow' in effects:
            glow = effects['glow']
            if glow.get('enabled'):
                size = glow.get('size', 0)
                opacity = glow.get('opacity', 0.5)
                styles.append(f"box-shadow: 0 0 {size}px rgba(255,255,255,{opacity});")

        # 描边
        if 'stroke' in effects:
            stroke = effects['stroke']
            if stroke.get('enabled'):
                size = stroke.get('size', 1)
                opacity = stroke.get('opacity', 1.0)
                styles.append(f"border: {size}px solid rgba(0,0,0,{opacity});")

    # 文字样式
    if layer.get('font_weight'):
        styles.append(STYLE_MAPPINGS['font_weight'](layer['font_weight']))
    if layer.get('font_style'):
        styles.append(STYLE_MAPPINGS['font_style'](layer['font_style']))
    if 'line_height' in layer:
        styles.append(STYLE_MAPPINGS['line_height'](layer['line_height']))
    if 'letter_spacing' in layer:
        styles.append(STYLE_MAPPINGS['letter_spacing'](layer['letter_spacing']))

    # 背景颜色
    if 'styles' in layer and 'background_color' in layer['styles']:
        styles.append(STYLE_MAPPINGS['background_color'](layer['styles']['background_color']))

    return '\n    '.join(styles)

def generate_html_content(layer, depth=0, parent_class=""):
    """递归生成 HTML 内容"""
    if layer.get('kind') == 'curves':
        return None

    html_parts = []
    css_parts = []

    # 跳过尺寸为 0 的图层
    bbox = layer.get('bbox', {})
    if bbox.get('width', 0) == 0 or bbox.get('height', 0) == 0:
        return None

    layer_name = layer.get('name', 'layer')
    content_type = layer.get('content_type')

    # 生成类名
    base_class = sanitize_class_name(layer_name, f"l{depth}")
    full_class = f"{parent_class} {base_class}".strip() if parent_class else base_class

    if content_type == 'container':
        # 容器：递归处理子元素
        html_parts.append(f'<div class="{base_class}">')

        # 生成容器样式
        styles = generate_styles(layer)
        css_parts.append(CSS_TEMPLATES['container'].format(
            class_name=base_class,
            left=bbox.get('left', 0),
            top=bbox.get('top', 0),
            width=bbox.get('width', 0),
            height=bbox.get('height', 0),
            styles=styles
        ))

        # 递归处理子元素
        if 'children' in layer:
            for child in layer['children']:
                result = generate_html_content(child, depth + 1, base_class)
                if result:
                    child_html, child_css = result
                    html_parts.append(child_html)
                    css_parts.extend(child_css)

        html_parts.append('</div>')
        return '\n'.join(html_parts), css_parts

    elif content_type == 'text':
        # 文字
        text = layer.get('text', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        styles = generate_styles(layer)

        html_parts.append(f'<div class="{base_class}">{text}</div>')
        css_parts.append(CSS_TEMPLATES['text'].format(
            class_name=base_class,
            left=bbox.get('left', 0),
            top=bbox.get('top', 0),
            width=bbox.get('width', 0),
            height=bbox.get('height', 0),
            font_size=layer.get('font_size', 16),
            color=layer.get('color', '#000000'),
            styles=styles
        ))
        return '\n'.join(html_parts), css_parts

    elif content_type == 'image':
        # 图片
        src = layer.get('src', '')
        styles = generate_styles(layer)

        html_parts.append(f'<div class="{base_class}"></div>')
        css_parts.append(CSS_TEMPLATES['image'].format(
            class_name=base_class,
            left=bbox.get('left', 0),
            top=bbox.get('top', 0),
            width=bbox.get('width', 0),
            height=bbox.get('height', 0),
            src=src,
            styles=styles
        ))
        return '\n'.join(html_parts), css_parts

    elif content_type == 'shape':
        # 形状
        styles = generate_styles(layer)
        html_parts.append(f'<div class="{base_class}"></div>')
        css_parts.append(CSS_TEMPLATES['container'].format(
            class_name=base_class,
            left=bbox.get('left', 0),
            top=bbox.get('top', 0),
            width=bbox.get('width', 0),
            height=bbox.get('height', 0),
            styles=styles
        ))
        return '\n'.join(html_parts), css_parts

    return None

def main():
    # 读取数据
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    metadata = data.get('metadata', {})
    design_tokens = data.get('design_tokens', {})
    layers = data.get('layers', [])

    print(f"📊 设计稿尺寸: {metadata.get('design_width')}x{metadata.get('design_height')}px")
    print(f"🎨 颜色数量: {len(design_tokens.get('colors', []))}")
    print(f"📝 字体大小: {len(design_tokens.get('font_sizes', []))}种")
    print(f"📐 常用间距: {len(design_tokens.get('spacings', []))}种")
    print(f"📄 顶层图层数量: {len(layers)}")

    # 生成 HTML 和 CSS
    html_content_parts = []
    css_content_parts = []

    # 基础样式
    css_content_parts.append("""/* 基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    position: relative;
    width: 1920px;
    height: 5080px;
    background-color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    overflow: hidden;
}
""")

    # 递归生成内容
    for layer in layers:
        result = generate_html_content(layer, depth=0)
        if result:
            html_part, css_parts = result
            html_content_parts.append(html_part)
            css_content_parts.extend(css_parts)

    # 构建完整 HTML
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PSD 转换页面</title>
    <style>
{chr(10).join(css_content_parts)}
    </style>
</head>
<body>
{chr(10).join(html_content_parts)}
</body>
</html>
"""

    # 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"\n✅ 静态页面生成完成！")
    print(f"   - 输出文件: {OUTPUT_FILE}")
    print(f"   - 总 CSS 规则数: {len(css_content_parts)}")
    print(f"   - 总 HTML 元素数: {len(html_content_parts)}")

if __name__ == '__main__':
    main()

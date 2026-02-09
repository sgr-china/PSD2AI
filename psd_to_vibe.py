import os
import json
import re
from datetime import datetime
from psd_tools import PSDImage
from PIL import Image

# 配置
PSD_FILE = '1920_new.psd'
OUTPUT_DIR = 'vibe_context'
ASSETS_DIR = os.path.join(OUTPUT_DIR, 'assets')

# 设计令牌收集器
design_tokens = {
    "colors": set(),
    "fonts": set(),
    "font_sizes": set(),
    "spacings": set()
}

# 组件识别规则
COMPONENT_PATTERNS = {
    "button": ["按钮", "btn", "button", "购买", "提交", "确认", "登录", "注册"],
    "card": ["卡片", "card", "item", "产品", "商品"],
    "nav": ["导航", "nav", "menu", "菜单", "导航栏"],
    "header": ["头部", "header", "top", "顶部"],
    "footer": ["底部", "footer", "底栏"],
    "input": ["输入", "input", "文本框", "搜索框"],
    "icon": ["图标", "icon", "ico"]
}

os.makedirs(ASSETS_DIR, exist_ok=True)

def safe_filename(name):
    """生成安全的文件名"""
    return re.sub(r'[^\w\-_]', '_', name).strip()

def extract_effects(layer):
    """提取图层效果（阴影、内阴影、发光、浮雕等）"""
    effects = {}
    try:
        if hasattr(layer, 'effects') and layer.effects:
            for effect in layer.effects:
                effect_name = effect.__class__.__name__
                effect_data = {}

                # 阴影效果
                if 'DropShadow' in effect_name or 'InnerShadow' in effect_name:
                    effect_data = {
                        "enabled": getattr(effect, 'enabled', True),
                        "opacity": getattr(effect, 'opacity', 191) / 255.0,
                        "distance": getattr(effect, 'distance', 0),
                        "spread": getattr(effect, 'spread', 0),
                        "size": getattr(effect, 'size', 0),
                        "angle": getattr(effect, 'angle', 0),
                        "choke": getattr(effect, 'choke', 0)
                    }
                    effects["shadow"] = effect_data

                # 发光效果
                elif 'OuterGlow' in effect_name or 'InnerGlow' in effect_name:
                    effect_data = {
                        "enabled": getattr(effect, 'enabled', True),
                        "opacity": getattr(effect, 'opacity', 191) / 255.0,
                        "size": getattr(effect, 'size', 0),
                        "spread": getattr(effect, 'spread', 0)
                    }
                    effects["glow"] = effect_data

                # 描边
                elif 'Stroke' in effect_name:
                    effect_data = {
                        "enabled": getattr(effect, 'enabled', True),
                        "size": getattr(effect, 'size', 1),
                        "opacity": getattr(effect, 'opacity', 255) / 255.0,
                        "position": str(getattr(effect, 'position', 'center'))
                    }
                    effects["stroke"] = effect_data

                # 渐变叠加
                elif 'GradientOverlay' in effect_name:
                    effect_data = {
                        "enabled": getattr(effect, 'enabled', True),
                        "opacity": getattr(effect, 'opacity', 255) / 255.0,
                        "angle": getattr(effect, 'angle', 0)
                    }
                    effects["gradient"] = effect_data

                # 颜色叠加
                elif 'ColorOverlay' in effect_name:
                    effect_data = {
                        "enabled": getattr(effect, 'enabled', True),
                        "opacity": getattr(effect, 'opacity', 255) / 255.0
                    }
                    effects["color_overlay"] = effect_data

                # 斜面和浮雕
                elif 'BevelEmboss' in effect_name:
                    effect_data = {
                        "enabled": getattr(effect, 'enabled', True),
                        "size": getattr(effect, 'size', 0),
                        "softness": getattr(effect, 'softness', 0),
                        "angle": getattr(effect, 'angle', 0),
                        "altitude": getattr(effect, 'altitude', 0)
                    }
                    effects["bevel"] = effect_data

    except Exception as e:
        pass

    return effects if effects else None

def extract_blend_info(layer):
    """提取混合模式和透明度信息"""
    blend_info = {}

    # 透明度
    if hasattr(layer, 'opacity'):
        opacity = layer.opacity / 255.0
        if opacity < 1.0:
            blend_info["opacity"] = round(opacity, 3)

    # 混合模式
    if hasattr(layer, 'blend_mode'):
        blend_mode = str(layer.blend_mode)
        if blend_mode and blend_mode != 'normal':
            blend_info["blend_mode"] = blend_mode

    return blend_info if blend_info else None

def extract_text_styles(layer):
    """提取文字样式信息"""
    styles = {}
    try:
        if hasattr(layer, 'engine_dict'):
            run_array = layer.engine_dict.get('StyleRun', {}).get('RunArray', [])
            if run_array:
                style = run_array[0].get('StyleSheet', {}).get('StyleSheetData', {})

                # 字体大小
                font_size = style.get('FontSize')
                if font_size is not None:
                    font_size = float(font_size)
                    styles["font_size"] = font_size
                    design_tokens["font_sizes"].add(round(font_size, 1))

                # 颜色
                if 'FillColor' in style:
                    fill_color = style['FillColor']
                    if 'Values' in fill_color:
                        values = fill_color['Values']
                        if len(values) >= 4:
                            r = int(values[1] * 255 / 65535)
                            g = int(values[2] * 255 / 65535)
                            b = int(values[3] * 255 / 65535)
                            color_hex = f"#{r:02x}{g:02x}{b:02x}"
                            styles["color"] = color_hex
                            design_tokens["colors"].add(color_hex)

                # 字体样式
                if 'Font' in style:
                    font_info = style['Font']
                    font_name = font_info.get('Name', 'Unknown')
                    styles["font_family"] = font_name
                    design_tokens["fonts"].add(font_name)

                # 字体粗细
                auto_kern = style.get('AutoKern', True)
                faux_bold = style.get('FauxBold', False)
                if faux_bold:
                    styles["font_weight"] = "bold"

                # 斜体
                faux_italic = style.get('FauxItalic', False)
                if faux_italic:
                    styles["font_style"] = "italic"

                # 行高
                leading = style.get('Leading')
                if leading is not None:
                    styles["line_height"] = float(leading)

                # 字母间距
                tracking = style.get('Tracking')
                if tracking is not None:
                    styles["letter_spacing"] = float(tracking) / 1000.0

    except Exception as e:
        pass

    return styles if styles else None

def extract_fill_info(layer):
    """提取填充信息"""
    fill = {}
    try:
        if hasattr(layer, 'resource_dict'):
            resources = layer.resource_dict

            # 固体填充
            if 'FillSolidColor' in resources:
                color = resources['FillSolidColor']
                if 'Color' in color:
                    color_data = color['Color']
                    if 'Values' in color_data:
                        values = color_data['Values']
                        if len(values) >= 3:
                            r = int(values[0] * 255 / 65535)
                            g = int(values[1] * 255 / 65535)
                            b = int(values[2] * 255 / 65535)
                            color_hex = f"#{r:02x}{g:02x}{b:02x}"
                            fill["background_color"] = color_hex
                            design_tokens["colors"].add(color_hex)

            # 渐变填充
            elif 'FillGradient' in resources:
                fill["gradient"] = "gradient"

    except Exception as e:
        pass

    return fill if fill else None

def detect_component_type(name):
    """基于命名规则识别组件类型"""
    name_lower = name.lower()

    for comp_type, patterns in COMPONENT_PATTERNS.items():
        for pattern in patterns:
            if pattern in name_lower:
                return comp_type
    return None

def optimize_image(img_path):
    """压缩优化导出的图片"""
    try:
        with Image.open(img_path) as img:
            # 转换为 RGB（移除 alpha 通道，除非需要透明）
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background

            # 保存为优化的 JPEG 或 PNG
            if img.mode == 'P':  # 调色板模式
                img = img.convert('RGB')

            img.save(img_path, optimize=True, quality=85)
    except Exception as e:
        pass

def parse_layer(layer, index_prefix=""):
    """递归解析图层"""
    if not layer.visible:
        return None

    # 坐标信息
    bbox = {
        "left": int(layer.left),
        "top": int(layer.top),
        "width": int(layer.width),
        "height": int(layer.height)
    }

    data = {
        "name": str(layer.name),
        "kind": str(layer.kind),
        "bbox": bbox
    }

    # 收集间距信息
    design_tokens["spacings"].add(int(layer.left))
    design_tokens["spacings"].add(int(layer.top))

    # 提取混合模式和透明度
    blend_info = extract_blend_info(layer)
    if blend_info:
        data["blend"] = blend_info

    # 提取图层效果
    effects = extract_effects(layer)
    if effects:
        data["effects"] = effects

    # 1. 处理文字图层
    if layer.kind == 'type':
        data["content_type"] = "text"
        data["text"] = layer.text

        text_styles = extract_text_styles(layer)
        if text_styles:
            data.update(text_styles)

        # 组件识别
        component_type = detect_component_type(layer.name)
        if component_type:
            data["componentType"] = component_type

    # 2. 处理图片图层
    elif layer.kind == 'pixel' or layer.kind == 'smartobject':
        data["content_type"] = "image"
        safe_name = safe_filename(layer.name)
        img_filename = f"{index_prefix}_{safe_name}.png"
        img_path = os.path.join(ASSETS_DIR, img_filename)

        try:
            image = layer.composite()
            if image:
                image.save(img_path)
                optimize_image(img_path)
                data["src"] = f"assets/{img_filename}"
        except Exception as e:
            pass

        # 组件识别
        component_type = detect_component_type(layer.name)
        if component_type:
            data["componentType"] = component_type

        # 提取填充信息
        fill_info = extract_fill_info(layer)
        if fill_info:
            data["styles"] = fill_info

    # 3. 处理形状图层
    elif layer.kind == 'shape':
        data["content_type"] = "shape"

        # 提取填充
        fill_info = extract_fill_info(layer)
        if fill_info:
            data["styles"] = fill_info

        component_type = detect_component_type(layer.name)
        if component_type:
            data["componentType"] = component_type

    # 4. 处理组
    elif layer.is_group():
        data["content_type"] = "container"
        children_data = []

        for i, child in enumerate(layer):
            child_result = parse_layer(child, f"{index_prefix}_{i}")
            if child_result:
                children_data.append(child_result)

        if children_data:
            data["children"] = children_data

            # 组的 bbox
            data["bbox"] = {
                "left": int(layer.left),
                "top": int(layer.top),
                "width": int(layer.width),
                "height": int(layer.height)
            }

            # 组级别的组件识别
            component_type = detect_component_type(layer.name)
            if component_type:
                data["componentType"] = component_type
        else:
            return None

    return data

def extract_design_tokens():
    """整理设计令牌"""
    # 过滤和排序颜色
    colors = sorted(list(design_tokens["colors"]))

    # 分析常用间距
    spacings = sorted(list(design_tokens["spacings"]))
    common_spacings = sorted(set([s for s in spacings if s > 0 and s < 200]))

    # 分析字体大小
    font_sizes = sorted(list(design_tokens["font_sizes"]))

    return {
        "colors": colors[:20],  # 最多20个主要颜色
        "fonts": list(design_tokens["fonts"]),
        "font_sizes": font_sizes,
        "spacings": common_spacings[:15]  # 最多15个常用间距
    }

def main():
    if not os.path.exists(PSD_FILE):
        print(f"❌ 错误: 找不到文件 '{PSD_FILE}'")
        return

    print(f"🔄 正在加载 {PSD_FILE} ...")
    psd = PSDImage.open(PSD_FILE)

    print("🖼️  正在生成整体预览图...")
    psd.composite().save(os.path.join(OUTPUT_DIR, 'full_preview.png'))

    print("🔍 正在解析图层结构并切图...")
    structure = []
    for i, layer in enumerate(psd):
        res = parse_layer(layer, str(i))
        if res:
            structure.append(res)

    # 生成增强的 layout_data.json
    json_path = os.path.join(OUTPUT_DIR, 'layout_data.json')
    output_data = {
        "metadata": {
            "design_width": int(psd.width),
            "design_height": int(psd.height),
            "generated_at": datetime.now().isoformat(),
            "psd_file": PSD_FILE
        },
        "design_tokens": extract_design_tokens(),
        "layers": structure
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # 保存单独的设计令牌文件
    tokens_path = os.path.join(OUTPUT_DIR, 'design_tokens.json')
    with open(tokens_path, 'w', encoding='utf-8') as f:
        json.dump(extract_design_tokens(), f, indent=2, ensure_ascii=False)

    print(f"✅ 处理完成！")
    print(f"   - 元数据和图层结构: {json_path}")
    print(f"   - 设计令牌: {tokens_path}")
    print(f"   - 预览图: {OUTPUT_DIR}/full_preview.png")
    print(f"   - 资源文件: {ASSETS_DIR}/")

if __name__ == '__main__':
    main()
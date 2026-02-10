import os
import json
import re
from datetime import datetime
from psd_tools import PSDImage
from PIL import Image
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
                    # 提取阴影颜色
                    if hasattr(effect, 'color'):
                        color = effect.color
                        r, g, b = color.red, color.green, color.blue
                        effect_data["color"] = f"#{r:02x}{g:02x}{b:02x}"
                        design_tokens["colors"].add(f"#{r:02x}{g:02x}{b:02x}")
                    effects["shadow"] = effect_data

                # 发光效果
                elif 'OuterGlow' in effect_name or 'InnerGlow' in effect_name:
                    effect_data = {
                        "enabled": getattr(effect, 'enabled', True),
                        "opacity": getattr(effect, 'opacity', 191) / 255.0,
                        "size": getattr(effect, 'size', 0),
                        "spread": getattr(effect, 'spread', 0)
                    }
                    if hasattr(effect, 'color'):
                        color = effect.color
                        r, g, b = color.red, color.green, color.blue
                        effect_data["color"] = f"#{r:02x}{g:02x}{b:02x}"
                        design_tokens["colors"].add(f"#{r:02x}{g:02x}{b:02x}")
                    effects["glow"] = effect_data

                # 描边
                elif 'Stroke' in effect_name:
                    effect_data = {
                        "enabled": getattr(effect, 'enabled', True),
                        "size": getattr(effect, 'size', 1),
                        "opacity": getattr(effect, 'opacity', 255) / 255.0,
                        "position": str(getattr(effect, 'position', 'center'))
                    }
                    # 提取描边颜色
                    if hasattr(effect, 'color'):
                        color = effect.color
                        r, g, b = color.red, color.green, color.blue
                        effect_data["color"] = f"#{r:02x}{g:02x}{b:02x}"
                        design_tokens["colors"].add(f"#{r:02x}{g:02x}{b:02x}")
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
                # 处理第一个文字样式（主要样式）
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

                # 文字对齐方式
                para_style = layer.engine_dict.get('ParagraphRun', {}).get('RunArray', [{}])[0] \
                    .get('ParagraphSheet', {}).get('Properties', {})

                if 'Justification' in para_style:
                    justification_map = {
                        'left': 'left',
                        'center': 'center',
                        'right': 'right',
                        'justify': 'justify'
                    }
                    justification = str(para_style['Justification']).lower()
                    styles["text_align"] = justification_map.get(justification, 'left')

                # 换行设置
                if 'AutoHyphenate' in para_style:
                    styles["hyphens"] = "auto" if para_style['AutoHyphenate'] else "none"

                # 如果有多个不同样式，标记出来
                if len(run_array) > 1:
                    styles["has_rich_text"] = True

    except Exception as e:
        pass

    return styles if styles else None

def extract_fill_info(layer):
    """提取填充信息"""
    fill = {}
    try:
        # 从 vector_mask 获取圆角和形状信息
        if hasattr(layer, 'vector_mask') and layer.vector_mask:
            mask = layer.vector_mask
            if hasattr(mask, 'paths'):
                for path in mask.paths:
                    if hasattr(path, 'corners') and path.corners:
                        # 提取圆角半径（使用所有角中的最小值或平均值）
                        radius_values = []
                        for corner in path.corners:
                            if hasattr(corner, 'radius'):
                                radius_values.append(float(corner.radius))
                        if radius_values:
                            avg_radius = sum(radius_values) / len(radius_values)
                            if avg_radius > 0:
                                fill["border_radius"] = round(avg_radius, 1)
                                design_tokens["spacings"].add(int(avg_radius))

            # 提取描边样式
            if hasattr(mask, 'stroke_setting'):
                stroke = mask.stroke_setting
                if stroke and hasattr(stroke, 'enabled') and stroke.enabled:
                    stroke_info = {
                        "width": float(getattr(stroke, 'stroke_width', 1)),
                        "enabled": True
                    }

                    # 提取描边颜色
                    if hasattr(stroke, 'stroke_color'):
                        color = stroke.stroke_color
                        if hasattr(color, 'red') and hasattr(color, 'green') and hasattr(color, 'blue'):
                            r, g, b = color.red, color.green, color.blue
                            stroke_info["color"] = f"#{r:02x}{g:02x}{b:02x}"
                            design_tokens["colors"].add(f"#{r:02x}{g:02x}{b:02x}")

                    # 提取描边类型（虚线、实线等）
                    if hasattr(stroke, 'stroke_style'):
                        stroke_info["style"] = str(stroke.stroke_style).lower()

                    fill["border"] = stroke_info
                    design_tokens["spacings"].add(int(stroke_info["width"]))

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

            # 渐变填充 - 提取完整渐变信息
            elif 'FillGradient' in resources:
                gradient = resources['FillGradient']
                gradient_info = {
                    "type": str(gradient.get('Type', 'linear')),
                    "smoothness": gradient.get('Smoothness', 4096) / 4096.0,
                }

                # 渐变颜色停止点
                if 'Gradient' in gradient:
                    gradient_data = gradient['Gradient']

                    # 渐变类型
                    if 'Type' in gradient_data:
                        gradient_info["gradient_type"] = str(gradient_data['Type'])

                    # 颜色停止点
                    if 'ColorStops' in gradient_data:
                        stops = []
                        for stop in gradient_data['ColorStops']:
                            color = stop.get('Color', {})
                            if 'Values' in color:
                                values = color['Values']
                                if len(values) >= 3:
                                    r = int(values[0] * 255 / 65535)
                                    g = int(values[1] * 255 / 65535)
                                    b = int(values[2] * 255 / 65535)
                                    color_hex = f"#{r:02x}{g:02x}{b:02x}"
                                    stops.append({
                                        "color": color_hex,
                                        "location": stop.get('Location', 0) / 4096.0
                                    })
                                    design_tokens["colors"].add(color_hex)
                        if stops:
                            gradient_info["color_stops"] = sorted(stops, key=lambda x: x['location'])

                    # 透明度停止点
                    if 'TransparencyStops' in gradient_data:
                        stops = []
                        for stop in gradient_data['TransparencyStops']:
                            stops.append({
                                "opacity": stop.get('Opacity', 255) / 255.0,
                                "location": stop.get('Location', 0) / 4096.0
                            })
                        if stops:
                            gradient_info["opacity_stops"] = sorted(stops, key=lambda x: x['location'])

                    # 渐变角度
                    if 'Angle' in gradient_data:
                        gradient_info["angle"] = float(gradient_data['Angle'])

                    # 渐变模式
                    if 'Mode' in gradient_data:
                        gradient_info["mode"] = str(gradient_data['Mode'])

                    # 渐变反转
                    if 'Reverse' in gradient_data:
                        gradient_info["reverse"] = gradient_data['Reverse']

                fill["background_gradient"] = gradient_info

    except Exception as e:
        logger.debug(f"提取填充信息时出错: {e}")

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

def parse_layer(layer, index_prefix="", parent_bbox=None):
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

    # 收集间距信息：提取有意义的间距值
    # 1. 提取图层的左、上、右、下边界
    design_tokens["spacings"].add(int(layer.left))
    design_tokens["spacings"].add(int(layer.top))
    design_tokens["spacings"].add(int(layer.width))
    design_tokens["spacings"].add(int(layer.height))

    # 2. 如果有父容器，计算内边距和外边距
    if parent_bbox:
        # 计算相对父容器的内边距
        padding_left = int(layer.left - parent_bbox["left"])
        padding_top = int(layer.top - parent_bbox["top"])
        padding_right = int(parent_bbox["left"] + parent_bbox["width"] - (layer.left + layer.width))
        padding_bottom = int(parent_bbox["top"] + parent_bbox["height"] - (layer.top + layer.height))

        # 只收集正值的内边距
        if padding_left >= 0:
            design_tokens["spacings"].add(padding_left)
        if padding_top >= 0:
            design_tokens["spacings"].add(padding_top)
        if padding_right >= 0:
            design_tokens["spacings"].add(padding_right)
        if padding_bottom >= 0:
            design_tokens["spacings"].add(padding_bottom)

    # 3. 提取圆角（如果有的话）
    if hasattr(layer, 'vector_mask') and layer.vector_mask:
        mask = layer.vector_mask
        if hasattr(mask, 'paths'):
            for path in mask.paths:
                if hasattr(path, 'corners') and path.corners:
                    for corner in path.corners:
                        if hasattr(corner, 'radius'):
                            radius = int(corner.radius)
                            if radius > 0:
                                design_tokens["spacings"].add(radius)

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

        child_layers = list(layer)
        child_count = len(child_layers)
        for i, child in enumerate(child_layers):
            child_result = parse_layer(child, f"{index_prefix}_{i}", bbox)
            if child_result:
                # 添加子图层的 zIndex（倒序）
                child_result["zIndex"] = child_count - i
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

    # 分析常用间距 - 只保留有意义的间距值
    spacings = sorted(list(design_tokens["spacings"]))
    # 过滤：去除0和过大的值，保留设计中常用的间距
    common_spacings = sorted(set([
        s for s in spacings
        if 0 < s < 500  # 排除过大值
    ]))

    # 提取常见的设计间距（8的倍数或4的倍数）
    design_spacings = []
    for s in common_spacings:
        # 常用的间距值：4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 80, 96等
        if s <= 100:
            design_spacings.append(s)

    # 分析字体大小
    font_sizes = sorted(list(design_tokens["font_sizes"]))

    return {
        "colors": colors[:20],  # 最多20个主要颜色
        "fonts": list(design_tokens["fonts"]),
        "font_sizes": font_sizes,
        "spacings": design_spacings[:20]  # 最多20个常用间距
    }

def main():
    if not os.path.exists(PSD_FILE):
        logger.error(f"找不到文件 '{PSD_FILE}'")
        print(f"❌ 错误: 找不到文件 '{PSD_FILE}'")
        return

    try:
        logger.info(f"正在加载 {PSD_FILE}")
        print(f"🔄 正在加载 {PSD_FILE} ...")
        psd = PSDImage.open(PSD_FILE)

        logger.info("正在生成整体预览图")
        print("🖼️  正在生成整体预览图...")
        psd.composite().save(os.path.join(OUTPUT_DIR, 'full_preview.png'))

        logger.info("正在解析图层结构并切图")
        print("🔍 正在解析图层结构并切图...")
        structure = []
        layer_count = len(list(psd))
        for i, layer in enumerate(psd):
            try:
                res = parse_layer(layer, str(i))
                if res:
                    # 添加 zIndex 信息（倒序，顶层图层的 zIndex 值更大）
                    res["zIndex"] = layer_count - i
                    structure.append(res)
            except Exception as e:
                logger.error(f"解析图层 '{layer.name}' 时出错: {e}")

        # 生成增强的 layout_data.json
        json_path = os.path.join(OUTPUT_DIR, 'layout_data.json')
        output_data = {
            "metadata": {
                "design_width": int(psd.width),
                "design_height": int(psd.height),
                "generated_at": datetime.now().isoformat(),
                "psd_file": PSD_FILE,
                "total_layers": len(structure)
            },
            "design_tokens": extract_design_tokens(),
            "layers": structure
        }

        logger.info(f"保存元数据和图层结构到 {json_path}")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        # 拆分每个图层为独立的 JSON 文件
        logger.info("正在拆分图层为独立文件...")
        layers_dir = os.path.join(OUTPUT_DIR, 'layers')
        os.makedirs(layers_dir, exist_ok=True)

        for i, layer_data in enumerate(structure):
            layer_name = safe_filename(layer_data.get("name", f"layer_{i}"))
            layer_file = os.path.join(layers_dir, f"{i}_{layer_name}.json")

            layer_output = {
                "metadata": {
                    "design_width": int(psd.width),
                    "design_height": int(psd.height),
                    "generated_at": datetime.now().isoformat(),
                    "psd_file": PSD_FILE,
                    "layer_index": i,
                    "layer_name": layer_data.get("name")
                },
                "design_tokens": extract_design_tokens(),
                "layer": layer_data
            }

            with open(layer_file, 'w', encoding='utf-8') as f:
                json.dump(layer_output, f, indent=2, ensure_ascii=False)

        # 生成图层索引文件
        index_file = os.path.join(layers_dir, "index.json")
        layer_index = {
            "total_layers": len(structure),
            "layers": [
                {
                    "index": i,
                    "name": layer.get("name"),
                    "file": f"{i}_{safe_filename(layer.get('name', f'layer_{i}'))}.json"
                }
                for i, layer in enumerate(structure)
            ]
        }
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(layer_index, f, indent=2, ensure_ascii=False)

        # 保存单独的设计令牌文件
        tokens_path = os.path.join(OUTPUT_DIR, 'design_tokens.json')
        logger.info(f"保存设计令牌到 {tokens_path}")
        with open(tokens_path, 'w', encoding='utf-8') as f:
            json.dump(extract_design_tokens(), f, indent=2, ensure_ascii=False)

        logger.info("处理完成")
        print(f"✅ 处理完成！")
        print(f"   - 元数据和图层结构: {json_path}")
        print(f"   - 单个图层文件: {layers_dir}/ (共 {len(structure)} 个)")
        print(f"   - 图层索引: {layers_dir}/index.json")
        print(f"   - 设计令牌: {tokens_path}")
        print(f"   - 预览图: {OUTPUT_DIR}/full_preview.png")
        print(f"   - 资源文件: {ASSETS_DIR}/")
        print(f"   - 总图层数: {len(structure)}")

    except Exception as e:
        logger.error(f"处理 PSD 文件时出错: {e}", exc_info=True)
        print(f"❌ 错误: {e}")

if __name__ == '__main__':
    main()
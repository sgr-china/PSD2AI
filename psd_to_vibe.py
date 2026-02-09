import os
import json
import re
from psd_tools import PSDImage
# 删除了可能报错的 constants 引用

# 配置
PSD_FILE = '1920_new.psd'  # 请确保这里的文件名正确
OUTPUT_DIR = 'vibe_context1'
ASSETS_DIR = os.path.join(OUTPUT_DIR, 'assets')

os.makedirs(ASSETS_DIR, exist_ok=True)

def safe_filename(name):
    return re.sub(r'[^\w\-_]', '_', name).strip()

def parse_layer(layer, index_prefix=""):
    if not layer.visible:
        return None

    # --- 修复核心：强制转换坐标为标准 int ---
    # psd-tools 的 layer.left 等属性可能是自定义类型，必须转为 int
    bbox = {
        "left": int(layer.left),
        "top": int(layer.top),
        "width": int(layer.width),
        "height": int(layer.height)
    }

    data = {
        "name": str(layer.name), # 强制转为字符串，防止特殊字符类型
        "kind": str(layer.kind),
        "bbox": bbox
    }

    # 1. 处理文字
    if layer.kind == 'type':
        data["content_type"] = "text"
        data["text"] = layer.text
        try:
            run_array = layer.engine_dict.get('StyleRun', {}).get('RunArray', [])
            if run_array:
                style = run_array[0].get('StyleSheet', {}).get('StyleSheetData', {})
                
                # --- 修复核心：强制转换字号为标准 float ---
                raw_size = style.get('FontSize')
                if raw_size is not None:
                    data["font_size"] = float(raw_size)
                    
                if 'FillColor' in style:
                    data["raw_color_data"] = "HasColor"
        except Exception as e:
            print(f"样式提取忽略: {layer.name}")

    # 2. 处理图片
    elif layer.kind == 'pixel' or layer.kind == 'smartobject':
        data["content_type"] = "image"
        safe_name = safe_filename(layer.name)
        img_filename = f"{index_prefix}_{safe_name}.png" # 加前缀防止重名覆盖
        img_path = os.path.join(ASSETS_DIR, img_filename)
        
        try:
            image = layer.composite()
            if image:
                image.save(img_path)
                data["src"] = f"assets/{img_filename}"
        except Exception as e:
            print(f"无法导出图片: {layer.name}")

    # 3. 处理组
    elif layer.is_group():
        data["content_type"] = "container"
        children_data = []
        for i, child in enumerate(layer):
            child_result = parse_layer(child, f"{index_prefix}_{i}")
            if child_result:
                children_data.append(child_result)
        
        if children_data:
            data["children"] = children_data
            # 组的 bbox 也需要强制转换
            data["bbox"] = {
                "left": int(layer.left),
                "top": int(layer.top),
                "width": int(layer.width),
                "height": int(layer.height)
            }
        else:
            return None

    return data

def main():
    if not os.path.exists(PSD_FILE):
        print(f"❌ 错误: 找不到文件 '{PSD_FILE}'")
        print("请将 .psd 文件放入当前文件夹，并修改代码中的 PSD_FILE 变量。")
        return

    print(f"正在加载 {PSD_FILE} ...")
    psd = PSDImage.open(PSD_FILE)
    
    print("正在生成整体预览图...")
    psd.composite().save(os.path.join(OUTPUT_DIR, 'full_preview.png'))

    print("正在解析图层结构并切图...")
    structure = []
    for i, layer in enumerate(psd):
        res = parse_layer(layer, str(i))
        if res:
            structure.append(res)

    json_path = os.path.join(OUTPUT_DIR, 'layout_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        # 这里应该不会再报错了，因为所有数字都转成了原生 int/float
        json.dump(structure, f, indent=2, ensure_ascii=False)

    print(f"✅ 处理完成！数据已保存在 '{OUTPUT_DIR}' 文件夹中。")

if __name__ == '__main__':
    main()
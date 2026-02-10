#!/Users/guorui/anaconda3/envs/psd/bin/python
# -*- coding: utf-8 -*-
"""
将 layout_data.json 拆分为多个独立的图层文件
"""

import os
import json
import re
from datetime import datetime


def safe_filename(name):
    """生成安全的文件名"""
    return re.sub(r'[^\w\-_]', '_', name).strip()


def split_layout_data(input_file, output_dir='vibe_context/layers'):
    """
    拆分 layout_data.json 为多个独立的图层文件

    Args:
        input_file: layout_data.json 文件路径
        output_dir: 输出目录
    """
    if not os.path.exists(input_file):
        print(f"❌ 错误: 找不到文件 '{input_file}'")
        return

    print(f"📖 正在读取 {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取元数据和设计令牌
    metadata = data.get('metadata', {})
    design_tokens = data.get('design_tokens', {})
    layers = data.get('layers', [])

    print(f"📦 找到 {len(layers)} 个图层，开始拆分...")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 保存独立的 metadata.json 和 design_tokens.json
    metadata_file = os.path.join(output_dir, 'metadata.json')
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"  ✅ 元数据: {metadata_file}")

    tokens_file = os.path.join(output_dir, 'design_tokens.json')
    with open(tokens_file, 'w', encoding='utf-8') as f:
        json.dump(design_tokens, f, indent=2, ensure_ascii=False)
    print(f"  ✅ 设计令牌: {tokens_file}")

    # 为每个图层创建独立的 JSON 文件（精简版，不包含重复的 metadata 和 design_tokens）
    for i, layer in enumerate(layers):
        layer_name = layer.get('name', f'layer_{i}')
        safe_name = safe_filename(layer_name)
        output_file = os.path.join(output_dir, f'{i:02d}_{safe_name}.json')

        # 构建图层数据（精简版）
        layer_data = {
            'layer_index': i,
            'layer_name': layer_name,
            'layer': layer
        }

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(layer_data, f, indent=2, ensure_ascii=False)

        print(f"  ✅ {i:02d}_{layer_name} → {output_file}")

    # 创建索引文件
    index_file = os.path.join(output_dir, 'index.json')
    index_data = {
        'summary': {
            'total_layers': len(layers),
            'design_width': metadata.get('design_width'),
            'design_height': metadata.get('design_height'),
            'generated_at': datetime.now().isoformat()
        },
        'files': {
            'metadata': 'metadata.json',
            'design_tokens': 'design_tokens.json'
        },
        'layers': [
            {
                'index': i,
                'name': layer.get('name'),
                'file': f'{i:02d}_{safe_filename(layer.get("name", f"layer_{i}"))}.json',
                'componentType': layer.get('componentType', 'unknown'),
                'content_type': layer.get('content_type', 'unknown'),
                'zIndex': layer.get('zIndex')
            }
            for i, layer in enumerate(layers)
        ]
    }

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 拆分完成！")
    print(f"   - 索引文件: {index_file}")
    print(f"   - 元数据: {metadata_file}")
    print(f"   - 设计令牌: {tokens_file}")
    print(f"   - 图层文件目录: {output_dir}/")
    print(f"   - 共 {len(layers)} 个图层文件")


if __name__ == '__main__':
    # 使用默认路径
    input_file = 'vibe_context/layout_data.json'
    output_dir = 'vibe_context/layers'

    split_layout_data(input_file, output_dir)

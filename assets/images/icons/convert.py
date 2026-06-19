import os
from PIL import Image

# 设置图片文件夹路径，这里改成你自己的路径
folder_path = "./"

for filename in os.listdir(folder_path):
    filepath = os.path.join(folder_path, filename)

    # 跳过非图片文件
    if not filename.lower().endswith(
        (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff")
    ):
        continue

    try:
        img = Image.open(filepath)
        if img.width == img.height:
            continue
        # 记录原格式
        original_format = img.format

        # 确保图像支持透明通道
        if img.mode not in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGBA")

        # 取长宽最大值作为正方形边长
        max_size = max(img.width, img.height)

        # 创建透明背景的正方形画布
        square_img = Image.new("RGBA", (max_size, max_size), (0, 0, 0, 0))

        # 计算居中粘贴位置
        paste_x = (max_size - img.width) // 2
        paste_y = (max_size - img.height) // 2

        # 将原图粘贴到中心
        square_img.paste(img, (paste_x, paste_y), img)

        # 保存，覆盖原图
        # JPEG 不支持透明，所以如果是 JPEG 则转为 PNG
        save_format = original_format if original_format != "JPEG" else "PNG"
        if save_format == "JPEG":
            square_img = square_img.convert("RGB")

        square_img.save(filepath, format=save_format)
        print(f"已处理: {filename}")

    except Exception as e:
        print(f"处理失败 {filename}: {e}")

print("全部完成！")

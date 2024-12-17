# 图片颜色反转工具

这是一个简单的网页工具，可以将黑白图片的颜色进行反转（黑色变白色，白色变黑色）。

## 功能特点

- 支持上传图片文件（PNG、JPG、JPEG、GIF）
- 自动将黑色部分转换为白色，白色部分转换为黑色
- 保持图片的透明度不变
- 支持下载处理后的图片

## 安装步骤

1. 安装依赖包：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python app.py
```

3. 打开浏览器访问：
```
http://127.0.0.1:5000
```

## 使用方法

1. 点击"选择文件"按钮选择要处理的图片
2. 点击"上传并处理"按钮
3. 等待处理完成，页面会显示原始图片和处理后的图片
4. 点击"下载处理后的图片"按钮保存结果

## 注意事项

- 支持的文件格式：PNG、JPG、JPEG、GIF
- 最大文件大小限制：16MB
- 建议使用黑白图片获得最佳效果

# 图片颜色反转工具

一个简单而强大的 Web 应用程序，用于将图片的颜色反转。支持拖放上传和实时预览功能。

## 功能特点

- 🖼️ 支持 JPG、PNG 格式图片
- 🎨 一键反转图片颜色
- 📱 响应式设计，支持各种设备
- 🖱️ 拖放上传支持
- 👀 实时图片预览
- 💾 自动清理 24 小时前的文件
- ⚡ 图片处理缓存机制

## 技术栈

- Python 3.11
- Flask Web 框架
- Pillow 图像处理库
- HTML5 拖放 API
- 现代 CSS3 样式

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/Raviney/image-inverter.git
cd image-inverter
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 运行

1. 启动应用：
```bash
python app.py
```

2. 在浏览器中访问：
```
http://localhost:5001
```

## 使用方法

1. **上传图片**
   - 点击上传区域选择图片
   - 或直接将图片拖放到上传区域
   - 支持的格式：JPG、PNG

2. **预览图片**
   - 选择或拖放图片后会立即显示预览
   - 预览图片会自动适应显示区域大小

3. **处理图片**
   - 确认选择的图片正确后，点击"上传并处理"按钮
   - 处理完成后会显示原图和处理后的图片对比
   - 可以下载处理后的图片

## 开发

### 运行测试
```bash
python -m pytest test_app.py -v
```

### 目录结构
```
image-inverter/
├── app.py              # Flask 应用主文件
├── templates/          # HTML 模板
│   └── index.html     # 主页面模板
├── static/            # 静态文件
├── uploads/           # 上传文件目录
├── test_app.py        # 单元测试
└── requirements.txt   # 项目依赖
```

## 注意事项

- 上传的图片大小限制为 4.5MB
- 处理后的图片会在 24 小时后自动删除
- 建议在生产环境中关闭调试模式

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可

MIT License

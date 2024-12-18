import os
import hashlib
from flask import Flask, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
from datetime import datetime, timedelta
import shutil

app = Flask(__name__)
# 设置上传文件夹的绝对路径
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 4.5 * 1024 * 1024  # 4.5MB max-limit

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_hash(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def clean_old_files():
    """清理超过24小时的文件"""
    now = datetime.now()
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename == '.gitkeep':
            continue
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
        if now - file_modified > timedelta(hours=24):
            try:
                os.remove(file_path)
            except OSError:
                pass

def invert_black_white(image_path, output_path):
    """使用numpy加速图片处理"""
    # 打开图片
    img = Image.open(image_path)
    
    # 确保图片是RGBA模式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 转换为numpy数组以加速处理
    img_array = np.array(img)
    
    # 分离通道
    rgb = img_array[:, :, :3]
    alpha = img_array[:, :, 3]
    
    # 计算灰度值
    gray = np.mean(rgb, axis=2)
    
    # 创建输出数组
    output_array = np.zeros_like(img_array)
    
    # 设置alpha通道
    output_array[:, :, 3] = alpha
    
    # 根据灰度值设置颜色
    # 使用numpy的布尔索引加速处理
    dark_pixels = gray < 128
    output_array[dark_pixels, :3] = 255  # 暗像素变白
    output_array[~dark_pixels, :3] = 0   # 亮像素变黑
    
    # 转换回PIL图像并保存
    output_img = Image.fromarray(output_array)
    output_img.save(output_path)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 清理旧文件
        clean_old_files()
        
        # 检查是否有文件
        if 'file' not in request.files:
            return render_template('index.html', error='没有选择文件')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='没有选择文件')
        
        if file and allowed_file(file.filename):
            # 安全地获取文件名
            filename = secure_filename(file.filename)
            base_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 生成唯一的文件名
            name, ext = os.path.splitext(base_path)
            counter = 1
            while os.path.exists(base_path):
                base_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # 保存原始文件
            file.save(base_path)
            
            try:
                # 计算文件哈希值
                file_hash = get_file_hash(base_path)
                output_filename = f"inverted_{file_hash}{os.path.splitext(filename)[1]}"
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                
                # 如果缓存存在且文件较新，直接使用缓存
                if os.path.exists(output_path) and \
                   datetime.now() - datetime.fromtimestamp(os.path.getmtime(output_path)) < timedelta(hours=24):
                    pass
                else:
                    # 处理图片
                    invert_black_white(base_path, output_path)
                
                # 生成URL
                original_url = url_for('uploaded_file', filename=os.path.basename(base_path))
                processed_url = url_for('uploaded_file', filename=output_filename)
                
                return render_template('index.html', 
                                     original_image=original_url,
                                     processed_image=processed_url)
            
            except Exception as e:
                return render_template('index.html', error=f'处理图片时出错: {str(e)}')
            
        return render_template('index.html', error='不支持的文件类型')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

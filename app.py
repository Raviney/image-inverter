import os
import hashlib
from flask import Flask, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
from datetime import datetime, timedelta
import shutil
import traceback
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 配置上传文件夹路径
if os.environ.get('VERCEL_ENV') == 'production':
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4.5 * 1024 * 1024  # 4.5MB max-limit

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    """使用PIL直接处理图片"""
    try:
        logger.debug(f"开始处理图片: {image_path}")
        
        # 打开图片
        img = Image.open(image_path)
        logger.debug(f"图片信息: 模式={img.mode}, 大小={img.size}")
        
        # 转换为 RGB 模式（如果不是的话）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 获取像素数据
        pixels = img.load()
        width, height = img.size
        
        # 创建新图片
        new_img = Image.new('RGB', (width, height), 'white')
        new_pixels = new_img.load()
        
        # 处理每个像素
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                # 计算亮度
                brightness = (r + g + b) // 3
                # 如果亮度小于128，设为白色；否则设为黑色
                if brightness < 128:
                    new_pixels[x, y] = (255, 255, 255)
                else:
                    new_pixels[x, y] = (0, 0, 0)
        
        # 保存结果
        new_img.save(output_path)
        logger.debug(f"图片已保存到: {output_path}")
        
    except Exception as e:
        logger.error(f"处理图片时出错: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"完整错误信息:\n{traceback.format_exc()}")
        raise

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            # 清理旧文件
            clean_old_files()
            
            # 检查是否有文件
            if 'file' not in request.files:
                logger.warning("没有文件被上传")
                return render_template('index.html', error='No file')
            
            file = request.files['file']
            if file.filename == '':
                logger.warning("文件名为空")
                return render_template('index.html', error='No file')
            
            if file and allowed_file(file.filename):
                # 安全地获取文件名
                filename = secure_filename(file.filename)
                logger.debug(f"处理文件: {filename}")
                base_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # 生成唯一的文件名
                name, ext = os.path.splitext(base_path)
                counter = 1
                while os.path.exists(base_path):
                    base_path = f"{name}_{counter}{ext}"
                    counter += 1
                
                # 保存原始文件
                logger.debug(f"保存文件到: {base_path}")
                file.save(base_path)
                
                try:
                    # 计算文件哈希值
                    file_hash = get_file_hash(base_path)
                    output_filename = f"inverted_{file_hash}{os.path.splitext(filename)[1]}"
                    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                    
                    # 如果缓存存在且文件较新，直接使用缓存
                    if os.path.exists(output_path) and \
                       datetime.now() - datetime.fromtimestamp(os.path.getmtime(output_path)) < timedelta(hours=24):
                        logger.debug("使用缓存的处理结果")
                    else:
                        # 处理图片
                        logger.debug("开始处理新图片")
                        invert_black_white(base_path, output_path)
                    
                    # 生成URL
                    original_url = url_for('uploaded_file', filename=os.path.basename(base_path))
                    processed_url = url_for('uploaded_file', filename=output_filename)
                    
                    return render_template('index.html', 
                                         original_image=original_url,
                                         processed_image=processed_url,
                                         success="processed_image")
                
                except Exception as e:
                    logger.error(f"处理图片时出错: {str(e)}")
                    logger.error(traceback.format_exc())
                    return render_template('index.html', error=f'处理图片时出错: {str(e)}')
            
            logger.warning(f"不支持的文件类型: {file.filename}")
            return render_template('index.html', error='Invalid image')
        
        except Exception as e:
            logger.error(f"上传处理时出错: {str(e)}")
            logger.error(traceback.format_exc())
            return render_template('index.html', error=f'服务器错误: {str(e)}')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

import os
import hashlib
import io
from flask import Flask, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import traceback
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置上传文件夹路径
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4.5 * 1024 * 1024  # 4.5MB max-limit

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_hash(file_data):
    """计算文件的MD5哈希值"""
    return hashlib.md5(file_data).hexdigest()

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

def invert_black_white(image_data):
    """使用PIL直接处理图片数据"""
    try:
        # 从二进制数据创建图像对象
        image = Image.open(io.BytesIO(image_data))
        
        # 如果图片模式不是RGB，转换为RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 创建新图像
        width, height = image.size
        inverted_image = Image.new('RGB', (width, height))
        
        # 获取像素数据
        pixels = image.load()
        inverted_pixels = inverted_image.load()
        
        # 反转每个像素
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                inverted_pixels[x, y] = (255-r, 255-g, 255-b)
        
        # 将处理后的图片保存到内存中
        output_buffer = io.BytesIO()
        inverted_image.save(output_buffer, format='PNG')
        return output_buffer.getvalue()
        
    except Exception as e:
        logger.error(f"处理图片时出错: {str(e)}")
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
            logger.debug("清理旧文件完成")
            
            # 检查是否有文件
            if 'file' not in request.files:
                logger.warning("没有文件被上传")
                return render_template('index.html', error='No file')
            
            file = request.files['file']
            if file.filename == '':
                logger.warning("文件名为空")
                return render_template('index.html', error='No file')
            
            if file and allowed_file(file.filename):
                # 读取文件数据
                file_data = file.read()
                logger.debug(f"接收到文件: {file.filename}, 大小: {len(file_data)} bytes")
                
                # 计算文件哈希值
                file_hash = get_file_hash(file_data)
                logger.debug(f"文件哈希值: {file_hash}")
                
                # 生成文件名
                filename = secure_filename(file.filename)
                original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                output_filename = f"inverted_{file_hash}.png"
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                
                # 保存原始文件
                with open(original_path, 'wb') as f:
                    f.write(file_data)
                logger.debug(f"保存原始文件到: {original_path}")
                
                # 处理图片
                processed_data = invert_black_white(file_data)
                logger.debug(f"处理图片完成")
                
                # 保存处理后的图片
                with open(output_path, 'wb') as f:
                    f.write(processed_data)
                logger.debug(f"保存处理后的图片到: {output_path}")
                
                # 生成URL
                original_url = url_for('uploaded_file', filename=filename)
                processed_url = url_for('uploaded_file', filename=output_filename)
                
                return render_template('index.html', 
                                     original_image=original_url,
                                     processed_image=processed_url,
                                     success="processed_image")
            
            logger.warning(f"不支持的文件类型: {file.filename}")
            return render_template('index.html', error='Invalid image')
        
        except Exception as e:
            logger.error(f"上传处理时出错: {str(e)}")
            logger.error(f"完整错误信息:\n{traceback.format_exc()}")
            return render_template('index.html', error=f'服务器错误: {str(e)}')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False)

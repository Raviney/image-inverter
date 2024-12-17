import os
from flask import Flask, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
# 设置上传文件夹的绝对路径
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def invert_black_white(image_path, output_path):
    # 打开图片
    img = Image.open(image_path)
    
    # 确保图片是RGBA模式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 获取图片尺寸
    width, height = img.size
    
    # 创建新图片
    inverted_img = Image.new('RGBA', (width, height))
    
    # 获取像素数据
    pixels = img.load()
    new_pixels = inverted_img.load()
    
    # 对每个像素进行处理
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            # 如果是黑色（或接近黑色）且不透明，变成白色
            # 如果是白色（或接近白色）且不透明，变成黑色
            if r + g + b < 384:  # 小于128*3，认为是黑色
                new_pixels[x, y] = (255, 255, 255, a)  # 变成白色
            else:
                new_pixels[x, y] = (0, 0, 0, a)  # 变成黑色
    
    # 保存结果
    inverted_img.save(output_path)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
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
            
            # 生成处理后的文件名
            output_filename = f"inverted_{os.path.basename(base_path)}"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # 处理图片
            try:
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

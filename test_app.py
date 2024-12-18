import os
import unittest
from app import app
from PIL import Image
from io import BytesIO

class TestImageInverter(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        self.client = app.test_client()
        
        # 创建测试上传目录
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
    def tearDown(self):
        # 清理测试文件
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
        os.rmdir(app.config['UPLOAD_FOLDER'])
        
    def create_test_image(self, color=(255, 255, 255)):
        """创建测试图片"""
        img = Image.new('RGB', (100, 100), color)
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return img_io
        
    def test_index_page(self):
        """测试首页是否正常加载"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('图片颜色反转工具'.encode('utf-8'), response.data)
        
    def test_upload_no_file(self):
        """测试没有文件上传的情况"""
        response = self.client.post('/', data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No file', response.data)
        
    def test_upload_invalid_file(self):
        """测试上传无效文件类型"""
        data = {
            'file': (BytesIO(b'not an image'), 'test.txt')
        }
        response = self.client.post('/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid image', response.data)
        
    def test_upload_valid_image(self):
        """测试上传有效图片"""
        img_io = self.create_test_image()
        data = {
            'file': (img_io, 'test.png')
        }
        response = self.client.post('/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'processed_image', response.data)
        
    def test_image_inversion(self):
        """测试图片反转功能"""
        # 创建白色测试图片
        white_img = self.create_test_image((255, 255, 255))
        data = {
            'file': (white_img, 'white.png')
        }
        response = self.client.post('/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        
        # 验证是否生成了处理后的图片
        processed_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith('inverted_')]
        self.assertEqual(len(processed_files), 1)
        
        # 验证处理后的图片是否为黑色（反转后的白色）
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_files[0])
        processed_img = Image.open(processed_path)
        pixel = processed_img.getpixel((0, 0))
        self.assertEqual(pixel, (0, 0, 0))  # 应该是黑色

if __name__ == '__main__':
    unittest.main()

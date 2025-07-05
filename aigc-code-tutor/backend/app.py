# 导入必要的库
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("="*50)
print("应用启动 - 环境变量检查")
print(f"DEEPSEEK_API_KEY 存在: {'是' if os.getenv('DEEPSEEK_API_KEY') else '否'}")
print("="*50)

# 创建Flask应用并配置CORS
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 获取项目根目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"[INFO] 项目根目录: {BASE_DIR}")

# 提供前端文件的路由
@app.route('/frontend/<path:filename>')
def frontend_files(filename):
    """提供 frontend 目录中的文件"""
    frontend_dir = os.path.join(BASE_DIR, 'frontend')
    print(f"[DEBUG] 提供文件: {filename} from {frontend_dir}")
    return send_from_directory(frontend_dir, filename)

# 直接访问前端主页
@app.route('/frontend')
def frontend_index():
    """前端主页面路由"""
    print("[INFO] 访问前端主页")
    return frontend_files('index.html')

# 首页路由
@app.route('/')
def home():
    return "欢迎使用AIGC编程训练系统！<br>访问 /frontend 使用前端界面"

# 代码生成路由
@app.route('/generate_code', methods=['POST'])
def generate_code():
    try:
        # 1. 获取请求数据
        print("\n" + "="*50)
        print("[DEBUG] 收到代码生成请求")
        print(f"请求头: {request.headers}")
        
        data = request.json
        if not data:
            print("[ERROR] 请求中没有JSON数据")
            return jsonify({'error': "无效的请求格式"}), 400
            
        print(f"[DEBUG] 请求数据: {data}")
        
        user_prompt = data.get('prompt', '')
        language = data.get('language', 'python')
        
        if not user_prompt:
            print("[ERROR] 用户未提供代码描述")
            return jsonify({'error': "请输入代码描述"}), 400
        
        # 2. 构造系统提示词
        system_prompt = f"""你是一个专业的{language}编程助手。根据用户描述生成简洁、高效、可运行的代码。

要求：
1. 只返回代码块，不要解释
2. 使用标准库，不要假设外部依赖
3. 包含必要的注释"""
        
        print(f"[DEBUG] 系统提示词: {system_prompt}")
        
        # 3. 获取API Key
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("[CRITICAL] DEEPSEEK_API_KEY 未配置")
            return jsonify({'error': 'API Key未配置'}), 500
        else:
            print(f"[INFO] 使用API密钥: {api_key[:6]}****")  # 只显示前6位密钥
        
        # 4. 调用DeepSeek API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-coder",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024
        }
        
        print(f"[DEBUG] API请求负载: {payload}")
        
        # 发送请求
        print("[INFO] 调用DeepSeek API...")
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # 记录API响应
        print(f"[DEBUG] API响应状态: {response.status_code}")
        print(f"[DEBUG] API响应内容: {response.text[:200]}...")  # 只显示前200个字符
        
        # 5. 处理响应
        if response.status_code == 200:
            ai_response = response.json()
            generated_code = ai_response['choices'][0]['message']['content']
            
            # 清理响应（如果是以代码块形式返回）
            if generated_code.startswith("```"):
                # 提取代码块内的内容
                lines = generated_code.split('\n')
                if len(lines) > 2:
                    generated_code = '\n'.join(lines[1:-1])
            
            print(f"[SUCCESS] 生成的代码: {generated_code[:100]}...")  # 显示前100个字符
            return jsonify({"code": generated_code})
        else:
            # 截取前200个字符防止过长
            error_text = response.text[:200] + "..." if len(response.text) > 200 else response.text
            error_msg = f"DeepSeek API错误 ({response.status_code}): {error_text}"
            print(f"[ERROR] {error_msg}")
            return jsonify({
                "error": "API调用失败",
                "details": error_msg
            }), 500
            
    except Exception as e:
        import traceback
        # 打印完整错误信息
        print("[EXCEPTION] 发生未处理异常:")
        traceback.print_exc()
        return jsonify({
            "error": "服务器内部错误",
            "details": str(e)
        }), 500

# 运行应用
if __name__ == '__main__':
    print("="*50)
    print("启动Flask应用...")
    app.run(host='0.0.0.0', port=5000, debug=True)
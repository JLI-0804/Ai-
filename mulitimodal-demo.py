#多模态示例
import base64
import os 
from io import BytesIO
import anthropic
from PIL import Image
from dotenv import load_dotenv

#=======配置anthropic client====
load_dotenv(dotenv_path="d:/cainiao_learn/.env")

api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("ANTHROPIC_BASE_URL")
MODEL_ENDPOINT = "MiniMax-M3"

# 初始化客户端
client = anthropic.Anthropic(
    api_key=api_key,
    base_url=base_url,
    timeout=30
)

def prepare_image_base64(image_path, max_size: int = 1024) -> str:
    """读取本地图片，处理透明通道，缩放并转为base64编码"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在：{image_path}")

    with Image.open(image_path) as img:
        #1.处理RGBA透明背景
        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        
        #2. 等比例缩放 （放大图撑爆 payload/Token)
        img.thumbnail((max_size, max_size))

        #3. 转Base64
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)   # 适当压缩质量
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"

def multimodal_chat(img_path: str, prompt: str):
    """多模态对话测试"""
    try:
        print(f"正在处理图片：{img_path}。。。")
        img_b64 = prepare_image_base64(img_path)

        print("正在发送请求至minimax。。。")
        full_text = ""
        with client.messages.stream(
            model=MODEL_ENDPOINT,
            max_tokens=1024,
            messages=[
                {"role": "user",
                "content":[
                    {"type": "text", "text": prompt},
                    {"type": "image", 
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": img_b64.split(",", 1)[1],
                        },
                    },
                ],
            }                
        ],
            temperature=0.5,
        ) as stream:
            for text in stream.text_stream:
                full_text += text
                print(text, end="", flush=True)

        print("\n" + "="*10 + " 识别结果 " + "="*10)
        print(full_text)
        print("="*30)
        return full_text

    except FileNotFoundError as e:
        print(f"[错误]：{e}")
    except Exception as e:
        print(f"[API请求失败] 请检查网络或者 endpoint/Key 是否正确。错误信息：\n{e}")
        return None

if __name__ == "__main__":
    #测试配置
    image_file = "./cat-cartoon.webp"
    question = "详细描述这张图片中的内容，分析画面主体、色彩和场景"

    #模拟创建一个临时测试图（若本地没有图片，方便快速肉眼 debug)
    if not os.path.exists(image_file):
        print(f"未检测到{image_file}，正在生成一张临时图片...")
        image.new("RGB", (200, 200), color = (73, 109 ,137)).save(image_file)

    multimodal_chat(image_file, question)

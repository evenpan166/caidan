import streamlit as st
import time
import random
import urllib.parse  # 用于处理网址中的中文

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="智能AI菜单(真图版)", layout="wide", page_icon="🍳")

# --- 2. 核心功能：免费 AI 画图 ---
def generate_real_image(prompt_text):
    """
    使用 Pollinations.ai 接口进行免费 AI 绘画
    不需要 API Key，完全根据 prompt_text 生成内容
    """
    # 1. 把中文菜名转换成 URL 编码 (例如: "红烧肉" -> "%E7%BA...")
    # 为了提高准确率，我们在提示词后加一点修饰词
    full_prompt = f"delicious food photography, {prompt_text}, michelin star style, 8k resolution"
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    # 2. 生成图片链接 (添加随机数 seed 防止缓存旧图)
    seed = random.randint(0, 10000)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true&seed={seed}"
    
    return image_url

def generate_description(dish_name):
    """简单模拟文案生成 (如果要真AI文案，需要填OpenAI Key)"""
    # 这里为了免费演示，使用通用模板。
    # 如果你有 Key，可以在这里接 GPT-3.5
    templates = [
        f"精选上等食材，{dish_name} 带来的是味蕾的极致享受，鲜香浓郁，回味无穷。",
        f"这道 {dish_name} 是主厨的得意之作，色泽诱人，口感丰富，每一口都是满足。",
        f"经典做法与现代风味的碰撞，{dish_name} 绝对是您今日不可错过的美味选择。"
    ]
    return random.choice(templates)

# --- 3. 初始化数据 ---
if 'menu' not in st.session_state:
    st.session_state.menu = [
        {
            "name": "重庆火锅", 
            "price": 128, 
            "desc": "麻辣鲜香，正宗牛油锅底，食材新鲜，聚餐首选。", 
            "img": generate_real_image("Sichuan Hot Pot") # 预设一个英文提示词图
        }
    ]
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- 4. 页面布局 ---

# === 侧边栏：老板上菜 ===
with st.sidebar:
    st.header("👨‍🍳 老板后台")
    st.info("💡 提示：输入中文菜名即可，AI 会自动尝试理解并画图。")
    
    with st.form("add_dish"):
        name = st.text_input("菜品名称", placeholder="例如：西红柿炒鸡蛋")
        price = st.number_input("价格 (元)", value=20)
        btn_submit = st.form_submit_button("✨ AI生成并上架")
        
        if btn_submit and name:
            with st.spinner(f"AI 正在绘制《{name}》的图片..."):
                # 1. 生成图片
                img_url = generate_real_image(name)
                # 2. 生成文案
                desc = generate_description(name)
                
                # 3. 存入菜单
                # 插入到第一个位置
                st.session_state.menu.insert(0, {
                    "name": name,
                    "price": price,
                    "desc": desc,
                    "img": img_url
                })
            st.success(f"《{name}》上架成功！")
            time.sleep(1)
            st.rerun() # 刷新页面显示新菜

    st.divider()
    if st.button("清空菜单"):
        st.session_state.menu = []
        st.rerun()

# === 主界面：顾客点餐 ===
st.title("🍳 AI 智能私房菜")
st.caption("所见即所得：所有配图均由 AI 实时生成")

# 购物车区域
if st.session_state.cart:
    with st.expander(f"🛒 购物车 (已点 {len(st.session_state.cart)} 道菜)", expanded=True):
        total = sum(d['price'] for d in st.session_state.cart)
        st.markdown(f"### 总计：¥{total}")
        
        # 显示简单的订单列表
        for item in st.session_state.cart:
            st.text(f"- {item['name']} (¥{item['price']})")
            
        if st.button("✅ 确认下单", type="primary"):
            st.balloons()
            st.success("老板收到订单啦！马上开始做！")
            time.sleep(2)
            st.session_state.cart = []
            st.rerun()

st.divider()

# 菜单展示区域
if not st.session_state.menu:
    st.warning("还没有菜品哦，请在左侧添加！")
else:
    # 响应式网格布局
    cols = st.columns(3)
    for idx, dish in enumerate(st.session_state.menu):
        with cols[idx % 3]:
            with st.container(border=True):
                # 显示图片
                st.image(dish['img'], use_column_width=True)
                
                # 显示信息
                st.subheader(dish['name'])
                st.caption(dish['desc'])
                
                # 价格与操作
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown(f"**¥{dish['price']}**")
                with c2:
                    if st.button(f"➕ 来一份", key=f"add_{idx}"):
                        st.session_state.cart.append(dish)
                        st.toast(f"已将 {dish['name']} 加入购物车")
                        time.sleep(0.5)
                        st.rerun()

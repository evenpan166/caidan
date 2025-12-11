import streamlit as st
import time
import random

# --- 1. 配置区域 (如果你有 OpenAI Key，请填在这里) ---
# 如果留空，系统会自动进入【免费演示模式】，使用随机网图
OPENAI_API_KEY = ""  
OPENAI_BASE_URL = "https://api.openai.com/v1" 

# --- 2. 初始化设置 ---
st.set_page_config(page_title="智能云端菜单", layout="wide", page_icon="🥘")

# 初始化数据结构
if 'menu' not in st.session_state:
    st.session_state.menu = [
        # 预设几个菜品防止页面空白
        {"name": "招牌红烧肉", "price": 48, "desc": "肥而不腻，入口即化，色泽红亮，顶级下饭神器。", "img": "https://source.unsplash.com/400x300/?pork,food"},
        {"name": "清炒时蔬", "price": 18, "desc": "每日新鲜采摘，保留食材原味，清脆爽口。", "img": "https://source.unsplash.com/400x300/?vegetables,cooked"}
    ]
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- 3. 功能函数 ---
def ai_generate(dish_name):
    """根据是否有 Key 决定是真生成还是模拟生成"""
    if not OPENAI_API_KEY:
        # --- 免费演示模式 ---
        time.sleep(1.5) # 模拟思考时间
        dummy_desc = f"【演示文案】这是 {dish_name} 的自动介绍。由于未配置API Key，系统使用了随机文案。这道菜色香味俱全，推荐尝试！"
        # 使用 Unsplash 的随机美食图
        dummy_img = f"https://source.unsplash.com/400x300/?food,dinner&sig={random.randint(1,1000)}"
        return dummy_desc, dummy_img
    else:
        # --- 真实 AI 模式 (需要配置 OpenAI 库) ---
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
            
            # 生成文案
            resp_txt = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"用诱人的美食文案介绍：{dish_name}，30字以内"}]
            )
            desc = resp_txt.choices[0].message.content
            
            # 生成图片 (DALL-E 3)
            resp_img = client.images.generate(
                model="dall-e-3", prompt=f"高清美食摄影，{dish_name}，美味，特写", size="1024x1024"
            )
            img = resp_img.data[0].url
            return desc, img
        except Exception as e:
            return f"生成出错: {str(e)}", "https://via.placeholder.com/400?text=Error"

# --- 4. 页面布局 ---

# 侧边栏：后台管理
with st.sidebar:
    st.title("👨‍🍳 老板后台")
    st.info("在这里上传菜品，右边会自动更新")
    
    with st.form("add_dish_form"):
        new_name = st.text_input("菜品名称", placeholder="例如：水煮鱼")
        new_price = st.number_input("价格", value=20)
        submitted = st.form_submit_button("✨ AI生成并上架")
        
        if submitted and new_name:
            with st.spinner(f"AI 正在为《{new_name}》绘制图片和撰写文案..."):
                desc, img = ai_generate(new_name)
                st.session_state.menu.append({
                    "name": new_name, "price": new_price, "desc": desc, "img": img
                })
            st.success("上架成功！")
            
    st.divider()
    if st.button("🗑️ 清空所有菜单"):
        st.session_state.menu = []
        st.rerun()

# 主界面：顾客点单
st.title("🥘 欢迎光临 AI 私房菜")
st.caption("左侧后台上传菜名，右侧自动生成图文菜单")

# 购物车悬浮显示 (Expander)
with st.expander(f"🛒 购物车 (已选 {len(st.session_state.cart)} 道菜)", expanded=True):
    if st.session_state.cart:
        total = sum(item['price'] for item in st.session_state.cart)
        st.markdown(f"**总计：¥{total}**")
        cols = st.columns([4, 1])
        with cols[0]:
            order_list = " + ".join([i['name'] for i in st.session_state.cart])
            st.text(order_list)
        with cols[1]:
            if st.button("✅ 下单"):
                st.balloons()
                st.success("老板已收到订单！")
                st.session_state.cart = []
                st.rerun()
    else:
        st.write("您的盘子还是空的哦~")

st.divider()

# 菜单网格显示
if not st.session_state.menu:
    st.warning("暂无菜品，请在左侧后台添加")
else:
    # 3列布局
    cols = st.columns(3)
    for index, dish in enumerate(st.session_state.menu):
        with cols[index % 3]:
            with st.container(border=True):
                # 显示图片
                st.image(dish['img'], use_column_width=True)
                st.subheader(dish['name'])
                st.write(dish['desc'])
                
                # 价格和按钮一行显示
                c1, c2 = st.columns([1, 1.5])
                with c1:
                    st.markdown(f"**¥{dish['price']}**")
                with c2:
                    if st.button(f"➕ 来一份", key=f"add_{index}"):
                        st.session_state.cart.append(dish)
                        st.toast(f"已添加 {dish['name']}")
                        time.sleep(0.5)
                        st.rerun()

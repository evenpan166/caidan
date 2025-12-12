import streamlit as st
import time
import random

# --- 1. 配置区域 ---
# 只有填入 Key 才会真正调用 AI，否则全是模拟演示
OPENAI_API_KEY = ""  
OPENAI_BASE_URL = "https://api.openai.com/v1" 

# --- 2. 初始化页面 ---
st.set_page_config(page_title="智能云端菜单", layout="wide", page_icon="🥘")

# 初始化数据结构（修复了这里的图片链接）
if 'menu' not in st.session_state:
    st.session_state.menu = [
        {
            "name": "招牌红烧肉", 
            "price": 48, 
            "desc": "肥而不腻，入口即化，色泽红亮，顶级下饭神器。", 
            # 使用更稳定的静态图源
            "img": "https://loremflickr.com/400/300/pork"
        },
        {
            "name": "清炒时蔬", 
            "price": 18, 
            "desc": "每日新鲜采摘，保留食材原味，清脆爽口。", 
            "img": "https://loremflickr.com/400/300/vegetable"
        }
    ]
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- 3. 核心功能函数 ---
def ai_generate(dish_name):
    """根据是否有 Key 决定是真生成还是模拟生成"""
    
    # 无论有无 Key，如果没有配置好画图模型，我们先用稳定的网图代替，防止报错
    # 这里使用 loremflickr，它会根据关键词（food）返回一张随机美食图
    # lock参数是为了保证刷新页面时图片不会变
    random_seed = random.randint(1, 10000)
    dummy_img = f"https://loremflickr.com/400/300/food,dinner?lock={random_seed}"

    if not OPENAI_API_KEY:
        # --- 免费演示模式 ---
        time.sleep(1.0) # 模拟思考时间
        dummy_desc = f"【演示文案】这是 {dish_name} 的AI介绍。由于未配置API Key，暂用随机美食图代替。这道菜色香味俱全！"
        return dummy_desc, dummy_img
    else:
        # --- 真实 AI 模式 ---
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
            
            # 1. 生成文案
            resp_txt = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"用诱人的美食文案介绍：{dish_name}，30字以内"}]
            )
            desc = resp_txt.choices[0].message.content
            
            # 2. 生成图片 (如果你有 DALL-E 3 权限，取消下面注释，否则还是用网图)
            # 考虑到 DALL-E 生成较慢且贵，演示时建议依然用网图，或者取消下面注释：
            
            # resp_img = client.images.generate(
            #     model="dall-e-3", prompt=f"美食摄影，{dish_name}，特写，高分辨率", size="1024x1024"
            # )
            # img = resp_img.data[0].url
            # return desc, img
            
            # 暂时返回网图，确保你一定能看到图片
            return desc, dummy_img
            
        except Exception as e:
            return f"AI连接错误: {str(e)}", "https://via.placeholder.com/400?text=Error"

# --- 4. 页面布局 ---

# 侧边栏：后台管理
with st.sidebar:
    st.header("👨‍🍳 老板后台")
    st.info("👇 输入菜名，自动生成图文菜单")
    
    with st.form("add_dish_form"):
        new_name = st.text_input("菜品名称", placeholder="例如：宫保鸡丁")
        new_price = st.number_input("价格", value=28)
        submitted = st.form_submit_button("✨ 立即上菜")
        
        if submitted and new_name:
            with st.spinner(f"正在寻找《{new_name}》的美照并撰写文案..."):
                desc, img = ai_generate(new_name)
                # 插入到列表最前面
                st.session_state.menu.insert(0, {
                    "name": new_name, "price": new_price, "desc": desc, "img": img
                })
            st.success("上架成功！")
            
    st.divider()
    if st.button("🗑️ 清空菜单"):
        st.session_state.menu = []
        st.rerun()

# 主界面
st.title("🥘 AI 智能点餐系统")

# 购物车 (默认展开)
if st.session_state.cart:
    with st.expander(f"🛒 购物车 (已点 {len(st.session_state.cart)} 道)", expanded=True):
        total = sum(item['price'] for item in st.session_state.cart)
        order_names = [item['name'] for item in st.session_state.cart]
        
        c1, c2 = st.columns([3, 1])
        with c1:
            st.write(f"已选：{'、'.join(order_names)}")
            st.markdown(f"#### 总计：<span style='color:red'>¥{total}</span>", unsafe_allow_html=True)
        with c2:
            if st.button("✅ 提交订单", type="primary"):
                st.balloons()
                st.success("订单已发送到厨房！")
                time.sleep(2)
                st.session_state.cart = []
                st.rerun()

st.divider()

# 菜单展示区
if not st.session_state.menu:
    st.warning("暂无菜品，请在左侧后台添加")
else:
    # 自动网格布局
    cols = st.columns(3)
    for index, dish in enumerate(st.session_state.menu):
        with cols[index % 3]:
            # 卡片样式
            with st.container(border=True):
                # 图片
                st.image(dish['img'], use_column_width=True, caption=dish['name'])
                
                # 描述
                st.caption(dish['desc'])
                
                # 价格和按钮
                col_price, col_btn = st.columns([1, 1])
                with col_price:
                    st.markdown(f"**¥{dish['price']}**")
                with col_btn:
                    if st.button(f"➕ 点一份", key=f"btn_{index}"):
                        st.session_state.cart.append(dish)
                        st.toast(f"已添加 {dish['name']}")
                        time.sleep(0.5)
                        st.rerun()

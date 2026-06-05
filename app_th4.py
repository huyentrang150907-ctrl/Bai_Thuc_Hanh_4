import streamlit as st
import pandas as pd
from g4f.client import Client

# Giao diện Streamlit
st.set_page_config(page_title="AI Phân Tích Survey - TH4", page_icon="📊", layout="wide")
st.title("📊 ỨNG DỤNG AI TỰ ĐỘNG TÓM TẮT CLUSTER SURVEY")
st.write("Bài Thực Hành 4 - Hệ thống tự động phân tích chủ đề khảo sát bằng AI")

# Khởi tạo Client AI miễn phí không cần Key
client = Client()

# Tải file Excel
uploaded_file = st.file_uploader("Bước 1: Chọn và tải lên file dữ liệu khảo sát (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("Tải file thành công! Dưới đây là bản xem trước dữ liệu:")
        st.dataframe(df.head(10)) 
        
        # Chọn cột dữ liệu
        cluster_col = st.selectbox("Bước 2: Chọn cột phân cụm (Cluster):", df.columns)
        text_col = st.selectbox("Bước 3: Chọn cột chứa nội dung câu trả lời cần tóm tắt chủ đề:", df.columns)
        
        if st.button("🚀 Bắt đầu để AI phân tích & tóm tắt ý nghĩa các Cluster"):
            with st.spinner("Hệ thống AI đang đọc và xử lý phân tích dữ liệu, bạn vui lòng đợi chút nhé..."):
                
                # Gom nhóm dữ liệu theo Cluster
                grouped = df.groupby(cluster_col)
                
                for cluster_id, group_data in grouped:
                    st.subheader(f"🎨 Kết quả phân tích: Nhóm (Cluster) {cluster_id}")
                    
                    # Lấy danh sách câu trả lời tiêu biểu
                    answers = group_data[text_col].dropna().astype(str).tolist()[:15]
                    combined_text = "\n- ".join(answers)
                    
                    # Câu lệnh gửi cho AI
                    prompt = f"""
                    Bạn là một nhà phân tích khảo sát chuyên nghiệp. Hãy đọc danh sách câu trả lời của khách hàng trong Nhóm (Cluster {cluster_id}) sau đây:
                    - {combined_text}
                    
                    Yêu cầu viết bằng tiếng Việt:
                    1. Đặt tên ngắn gọn cho nhóm này phản ánh đúng xu hướng chung.
                    2. Tóm tắt ngắn gọn ý nghĩa/chủ đề chính mà nhóm khách hàng này đang quan tâm (tối đa 3 dòng).
                    """
                    
                    try:
                        # Gọi AI thông qua nhà cung cấp miễn phí ổn định
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        result_text = response.choices[0].message.content
                        st.write(result_text)
                        st.markdown("---")
                    except Exception as e:
                        st.error(f"Đang xử lý lại cụm {cluster_id}...")
                        st.markdown("---")
                        
    except Exception as e:
        st.error(f"Lỗi định dạng file Excel: {e}")

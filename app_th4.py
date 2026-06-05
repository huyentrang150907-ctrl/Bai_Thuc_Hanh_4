import streamlit as st
import google.generativeai as genai
from google.generativeai.types import generation_types
import pandas as pd

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="AI Phân Tích Survey - TH4", page_icon="📊", layout="wide")
st.title("📊 ỨNG DỤNG AI TỰ ĐỘNG TÓM TẮT CLUSTER SURVEY")
st.write("Bài Thực Hành 4 - Hệ thống tự động phân tích chủ đề khảo sát bằng AI")

# ÉP PHIÊN BẢN API SANG V1 ĐỂ TRÁNH LỖI V1BETA
try:
    generation_types.BaseClient.common_options['api_version'] = 'v1'
except Exception:
    pass

# Lấy mã API an toàn từ Secrets của Streamlit
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chưa cấu hình API Key trong mục Secrets của Streamlit!")

# Chức năng tải file Excel lên giao diện
uploaded_file = st.file_uploader("Bước 1: Chọn và tải lên file dữ liệu khảo sát (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Đọc dữ liệu từ file Excel người dùng tải lên
        df = pd.read_excel(uploaded_file)
        st.success("Tải file thành công! Dưới đây là bản xem trước dữ liệu:")
        st.dataframe(df.head(10)) 
        
        # Chọn cột phân cụm
        cluster_col = st.selectbox("Bước 2: Chọn cột phân cụm (Cluster):", df.columns)
            
        # Chọn cột chứa nội dung câu trả lời Survey để AI đọc
        text_col = st.selectbox("Bước 3: Chọn cột chứa nội dung câu trả lời cần tóm tắt chủ đề:", df.columns)
        
        # Nút bấm kích hoạt AI xử lý
        if st.button("🚀 Bắt đầu để AI phân tích & tóm tắt ý nghĩa các Cluster"):
            with st.spinner("AI đang đọc dữ liệu và phân tích từng nhóm, bạn đợi chút nhé..."):
                
                # Gom nhóm dữ liệu theo từng Cluster
                grouped = df.groupby(cluster_col)
                
                # Gọi mô hình Gemini thông qua API v1 ổn định
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Duyệt qua từng nhóm để gửi cho AI tóm tắt
                for cluster_id, group_data in grouped:
                    st.subheader(f"🎨 Kết quả phân tích: Nhóm (Cluster) {cluster_id}")
                    
                    # Lấy danh sách các câu trả lời trong nhóm này (tối đa 20 câu để tránh quá tải)
                    answers = group_data[text_col].dropna().astype(str).tolist()[:20]
                    combined_text = "\n- ".join(answers)
                    
                    # Tạo câu lệnh (Prompt) gửi cho AI
                    prompt = f"""
                    Bạn là một chuyên gia phân tích dữ liệu khảo sát thị trường xuất sắc.
                    Dưới đây là danh sách các câu trả lời của khách hàng thuộc cùng một Nhóm (Cluster {cluster_id}):
                    - {combined_text}
                    
                    Yêu cầu:
                    1. Đọc và phân tích kỹ các câu trả lời trên.
                    2. Hãy tóm tắt ý nghĩa chủ đề chính/xu hướng chung của Nhóm (Cluster) này là gì?
                    3. Đặt cho nhóm này một cái tên ngắn gọn phản ánh đúng bản chất.
                    Trả lời bằng tiếng Việt ngắn gọn, súc tích, rõ ràng theo các gạch đầu dòng.
                    """
                    
                    # Gửi cho AI và hiển thị kết quả
                    try:
                        response = model.generate_content(prompt)
                        st.write(response.text)
                        st.markdown("---")
                    except Exception as e:
                        st.error(f"Lỗi khi gửi dữ liệu Nhóm {cluster_id} cho AI: {e}")
                        
    except Exception as e:
        st.error(f"Không thể đọc được file Excel này. Vui lòng kiểm tra lại định dạng file! Lỗi: {e}")

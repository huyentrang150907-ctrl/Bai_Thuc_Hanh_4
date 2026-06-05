import streamlit as st
import pandas as pd
import requests

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="AI Phân Tích Survey - TH4", page_icon="📊", layout="wide")
st.title("📊 ỨNG DỤNG AI TỰ ĐỘNG TÓM TẮT CLUSTER SURVEY")
st.write("Bài Thực Hành 4 - Hệ thống tự động phân tích chủ đề khảo sát bằng AI")

# Thiết lập API Key trực tiếp từ mã bí mật của Streamlit
my_api_key = st.secrets.get("my_api_key", None)

if not my_api_key:
    st.error("Chưa cấu hình API Key trong mục Secrets với tên biến 'my_api_key'!")

# Chức năng tải file Excel lên giao diện
uploaded_file = st.file_uploader("Bước 1: Chọn và tải lên file dữ liệu khảo sát (.xlsx)", type=["xlsx"])

if uploaded_file is not None and my_api_key:
    try:
        # Đọc dữ liệu từ file Excel
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
                
                # Cấu hình đường link API trực tiếp đến Google Gemini 1.5 Flash
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={my_api_key}"
                headers = {'Content-Type': 'application/json'}
                
                # Duyệt qua từng nhóm để gửi cho AI tóm tắt
                for cluster_id, group_data in grouped:
                    st.subheader(f"🎨 Kết quả phân tích: Nhóm (Cluster) {cluster_id}")
                    
                    # Lấy danh sách câu trả lời (tối đa 20 câu)
                    answers = group_data[text_col].dropna().astype(str).tolist()[:20]
                    combined_text = "\n- ".join(answers)
                    
                    # Tạo câu lệnh (Prompt)
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
                    
                    # Tạo cấu trúc gói dữ liệu gửi đi
                    payload = {
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }]
                    }
                    
                    # Gửi yêu cầu trực tiếp qua HTTP POST
                    try:
                        response = requests.post(url, headers=headers, json=payload)
                        if response.status_code == 200:
                            result_json = response.json()
                            ai_text = result_json['candidates'][0]['content']['parts'][0]['text']
                            st.write(ai_text)
                        else:
                            st.error(f"Lỗi từ máy chủ Google (Mã {response.status_code}): {response.text}")
                        st.markdown("---")
                    except Exception as e:
                        st.error(f"Lỗi kết nối đường truyền: {e}")
                        
    except Exception as e:
        st.error(f"Không thể đọc được file Excel này. Vui lòng kiểm tra lại định dạng file! Lỗi: {e}")

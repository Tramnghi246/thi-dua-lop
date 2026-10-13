import io
import os
import time
import pandas as pd
import requests
import streamlit as st

# ==============================================================================
# CẤU HÌNH TRANG & GIAO DIỆN HIỆN ĐẠI
# ==============================================================================
st.set_page_config(
    page_title="Hệ Thống Thi Đua Học Đường",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "https://script.google.com/macros/s/AKfycbwoy6GT8XEkwwrLTSXrIk3tMj6lzATeiwrw02cWYz7yEXDhzEtDOoyL8VssgXuJE08q/exec"
DATA_FILE = "du_lieu_thi_dua.csv"

# Custom CSS cho phong cách giao diện Dashboard
st.markdown(
    """
    <style>
        .main {
            background-color: #f8fafc;
        }
        .stat-card {
            background: white;
            padding: 18px 22px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            border: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .stat-label {
            font-size: 13px;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-value {
            font-size: 26px;
            font-weight: 700;
            color: #0f172a;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# DANH MỤC THI ĐUA & MẶC ĐỊNH
# ==============================================================================
DANH_SACH_LOI = {
    "🌸 Thầy cô tuyên dương (+2)": 2,
    "🌟 Phát biểu xây dựng bài (+1)": 1,
    "💯 Đạt điểm 9, 10 (+2)": 2,
    "🏆 Đạt giải phong trào (+5)": 5,
    "🤬 Nói tục (-5)": -5,
    "📱 Làm việc riêng (-5)": -5,
    "🔊 Nói chuyện trong giờ (-2)": -2,
    "✉️ Nghỉ học có phép (-2)": -2,
    "⏰ Đi muộn (-1)": -1,
    "📚 Không học bài / Thiếu BTVN (-5)": -5,
    "👔 Không mặc đồng phục (-5)": -5,
    "🧹 Không trực nhật / vệ sinh (-5)": -5,
    "📱 Sử dụng điện thoại không xin phép (-15)": -15,
    "🚨 Nghỉ học không phép (-5)": -5,
}

DEFAULT_STUDENTS = [
    {"STT": 1, "Họ và tên": "Võ Huỳnh Minh An", "Tổ": "Tổ 1", "Điểm thi đua": 100, "Xếp loại": "Tốt", "Lỗi vi phạm": "None"},
    {"STT": 2, "Họ và tên": "Huỳnh Bảo Ngọc Thiên Ân", "Tổ": "Tổ 1", "Điểm thi đua": 100, "Xếp loại": "Tốt", "Lỗi vi phạm": "None"},
    {"STT": 3, "Họ và tên": "Trần Quốc Bảo", "Tổ": "Tổ 2", "Điểm thi đua": 95, "Xếp loại": "Khá", "Lỗi vi phạm": "Đi muộn x1 (-1)"},
    {"STT": 4, "Họ và tên": "Nguyễn Lê Hoàng Mai", "Tổ": "Tổ 3", "Điểm thi đua": 102, "Xếp loại": "Tốt", "Lỗi vi phạm": "Phát biểu x2 (+2)"},
    {"STT": 5, "Họ và tên": "Lê Văn Tuấn", "Tổ": "Tổ 4", "Điểm thi đua": 85, "Xếp loại": "Khá", "Lỗi vi phạm": "Thiếu BTVN x3 (-15)"},
]

# ==============================================================================
# HÀM XỬ LÝ DỮ LIỆU & ĐỒNG BỘ
# ==============================================================================
def tinh_xep_loai(diem):
    try:
        diem = float(diem)
    except Exception:
        diem = 100.0
    if diem >= 100:
        return "Tốt"
    elif diem >= 85:
        return "Khá"
    elif diem >= 70:
        return "Trung bình"
    else:
        return "Yếu"

def clean_dataframe(df_input):
    if df_input is None or df_input.empty:
        return pd.DataFrame(DEFAULT_STUDENTS)

    required_cols = ["STT", "Họ và tên", "Tổ", "Điểm thi đua", "Xếp loại", "Lỗi vi phạm"]
    for col in required_cols:
        if col not in df_input.columns:
            df_input[col] = ""

    df_clean = df_input.dropna(subset=["Họ và tên"]).copy()
    df_clean["Họ và tên"] = df_clean["Họ và tên"].astype(str).str.strip()
    df_clean = df_clean[~df_clean["Họ và tên"].str.lower().isin(["nan", "none", ""])]

    df_clean["Tổ"] = df_clean["Tổ"].fillna("Tổ 1").astype(str).str.strip()
    df_clean["Điểm thi đua"] = (
        pd.to_numeric(df_clean["Điểm thi đua"], errors="coerce").fillna(100).astype(int)
    )
    df_clean["Xếp loại"] = df_clean["Điểm thi đua"].apply(tinh_xep_loai)
    df_clean["Lỗi vi phạm"] = df_clean["Lỗi vi phạm"].fillna("None").astype(str)

    df_clean = df_clean.reset_index(drop=True)
    df_clean["STT"] = list(range(1, len(df_clean) + 1))

    return df_clean

def load_data():
    if API_URL and "/exec" in API_URL:
        try:
            res = requests.get(API_URL, params={"_t": time.time()}, timeout=7)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 1:
                    df_temp = pd.DataFrame(data[1:], columns=data[0])
                    df_temp = clean_dataframe(df_temp)
                    df_temp.to_csv(DATA_FILE, index=False)
                    return df_temp
        except Exception:
            pass

    if os.path.exists(DATA_FILE):
        try:
            return clean_dataframe(pd.read_csv(DATA_FILE))
        except Exception:
            pass

    return pd.DataFrame(DEFAULT_STUDENTS)

def update_gsheet(name, score, xeploai, log_text):
    if not API_URL or "/exec" not in API_URL:
        return False, "Chưa thiết lập API Google Sheets"
    try:
        params = {
            "action": "update",
            "name": name,
            "score": score,
            "xeploai": xeploai,
            "log": log_text,
            "_t": time.time(),
        }
        res = requests.get(API_URL, params=params, timeout=10)
        if res.status_code == 200:
            res_json = res.json()
            if res_json.get("status") == "success":
                return True, "Thành công"
            return False, res_json.get("message", "Lỗi dữ liệu Google Apps Script")
        return False, f"Lỗi HTTP {res.status_code}"
    except Exception as e:
        return False, str(e)

def reset_new_week_gsheet():
    if not API_URL or "/exec" not in API_URL:
        return False, "Chưa thiết lập API Google Sheets"
    try:
        params = {"action": "reset_week", "_t": time.time()}
        res = requests.get(API_URL, params=params, timeout=12)
        if res.status_code == 200:
            res_json = res.json()
            if res_json.get("status") == "success":
                return True, "Thành công"
            return False, res_json.get("message", "Lỗi reset")
        return False, f"Lỗi HTTP {res.status_code}"
    except Exception as e:
        return False, str(e)

# Khởi tạo trạng thái dữ liệu
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# ==============================================================================
# THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.title("🏫 Quản Lý Lớp Học")
    st.caption("Theo dõi & đánh giá thi đua học sinh")
    st.divider()

    st.markdown("### 👤 Vai trò truy cập")
    vai_tro = st.selectbox(
        "Chọn vai trò:",
        ["👑 Giáo viên chủ nhiệm", "Tổ trưởng Tổ 1", "Tổ trưởng Tổ 2", "Tổ trưởng Tổ 3", "Tổ trưởng Tổ 4"],
        label_visibility="collapsed"
    )

    st.markdown("### 🧭 Bảng điều khiển")
    menu_items = [
        "📝 Ghi nhận điểm số",
        "✏️ Chỉnh sửa / Khắc phục",
        "📊 Tổng quan & Thống kê",
        "📥 Xuất dữ liệu báo cáo",
    ]
    if "Giáo viên" in vai_tro:
        menu_items.append("⚙️ Khởi tạo tuần mới (Reset)")

    chuc_nang = st.radio("Chọn chức năng:", menu_items, label_visibility="collapsed")
    st.divider()

    # Nạp danh sách lớp mới
    with st.expander("📁 Tải danh sách lớp (Excel/CSV)"):
        uploaded_file = st.file_uploader("Chọn file từ máy:", type=["xlsx", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".xlsx"):
                    new_df = pd.read_excel(uploaded_file)
                else:
                    new_df = pd.read_csv(uploaded_file)

                new_df = clean_dataframe(new_df)
                st.session_state.df = new_df
                new_df.to_csv(DATA_FILE, index=False)
                st.success("✅ Đã tải và chuẩn hóa danh sách thành công!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi đọc file: {e}")

    if st.button("🔄 Đồng bộ lại dữ liệu", use_container_width=True):
        st.session_state.df = load_data()
        st.toast("Đã làm mới dữ liệu!", icon="🔄")
        st.rerun()

# Lọc học sinh theo phạm vi tổ quản lý
if "Tổ 1" in vai_tro:
    df_role = df[df["Tổ"].astype(str).str.contains("1", na=False)].copy()
elif "Tổ 2" in vai_tro:
    df_role = df[df["Tổ"].astype(str).str.contains("2", na=False)].copy()
elif "Tổ 3" in vai_tro:
    df_role = df[df["Tổ"].astype(str).str.contains("3", na=False)].copy()
elif "Tổ 4" in vai_tro:
    df_role = df[df["Tổ"].astype(str).str.contains("4", na=False)].copy()
else:
    df_role = df.copy()

# ==============================================================================
# MÀN HÌNH 1: GHI NHẬN ĐIỂM SỐ
# ==============================================================================
if chuc_nang == "📝 Ghi nhận điểm số":
    st.subheader(f"📝 Ghi nhận điểm thi đua — {vai_tro}")
    st.caption("Cộng hoặc trừ điểm thi đua cho học sinh theo các mục đánh giá")

    danh_sach_hien_thi = [
        f"#{row['STT']} - {row['Họ và tên']} ({row['Tổ']})"
        for _, row in df_role.iterrows()
    ]

    with st.container(border=True):
        col1, col2 = st.columns([1.6, 1])
        with col1:
            hs_chon_raw = st.selectbox("👤 Chọn học sinh:", danh_sach_hien_thi if danh_sach_hien_thi else ["(Không có học sinh)"])
            loi_chon = st.selectbox("📋 Nội dung tuyên dương / Vi phạm:", list(DANH_SACH_LOI

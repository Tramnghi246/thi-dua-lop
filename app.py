import io
import os
import time
import pandas as pd
import requests
import streamlit as st
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ==============================================================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN
# ==============================================================================
st.set_page_config(
    page_title="Hệ Thống Thi Đua - THCS Chí Công",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "https://script.google.com/macros/s/AKfycbwoy6GT8XEkwwrLTSXrIk3tMj6lzATeiwrw02cWYz7yEXDhzEtDOoyL8VssgXuJE08q/exec"
DATA_FILE = "du_lieu_thi_dua.csv"

# ==============================================================================
# 2. CSS GIAO DIỆN CHUẨN CỔNG THÔNG TIN TRƯỜNG THCS CHÍ CÔNG
# ==============================================================================
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }
        .main {
            background-color: #f4f6f9;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #edf2f7 100%) !important;
            border-right: 1px solid #e2e8f0;
            box-shadow: 3px 0 12px rgba(0,0,0,0.03);
        }
        .sidebar-brand-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 14px 16px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 6px rgba(11, 79, 138, 0.08);
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .sidebar-brand-icon {
            width: 44px;
            height: 44px;
            background: #0b4f8a;
            color: #ffffff;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
        }
        .sidebar-brand-title {
            font-size: 1.05rem;
            font-weight: 800;
            color: #0b4f8a;
            line-height: 1.2;
        }
        .sidebar-brand-sub {
            font-size: 0.78rem;
            color: #64748b;
            font-weight: 500;
        }
        div[data-testid="stRadio"] > div {
            gap: 8px !important;
        }
        div[data-testid="stRadio"] label {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            margin-bottom: 2px !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
            display: flex !important;
            align-items: center !important;
        }
        div[data-testid="stRadio"] label > div:first-child {
            display: none !important;
        }
        div[data-testid="stRadio"] label p {
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            color: #334155 !important;
            margin: 0 !important;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #f0f7ff !important;
            border-color: #93c5fd !important;
            transform: translateX(4px);
        }
        div[data-testid="stRadio"] label[data-checked="true"],
        div[data-testid="stRadio"] label:has(input:checked) {
            background: #0b4f8a !important;
            border-color: #0b4f8a !important;
            box-shadow: 0 3px 8px rgba(11, 79, 138, 0.25) !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] p,
        div[data-testid="stRadio"] label:has(input:checked) p {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        .sidebar-section-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            font-weight: 700;
            color: #64748b;
            margin: 14px 0 6px 4px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .school-top-bar {
            background: linear-gradient(90deg, #0b4f8a 0%, #1565c0 100%);
            color: #ffffff;
            padding: 12px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(11, 79, 138, 0.2);
        }
        .school-title {
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .school-slogan {
            font-size: 0.82rem;
            color: #fde047;
            font-weight: 600;
        }
        .student-profile-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 16px 20px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            flex-wrap: wrap;
            gap: 12px;
        }
        .student-avatar {
            width: 48px;
            height: 48px;
            background-color: #0b4f8a;
            color: #ffffff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.25rem;
        }
        .stat-card {
            background: white;
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .stat-label {
            font-size: 12px;
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
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.12);
        }
        .empty-log-box {
            background: white;
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 28px;
            text-align: center;
            margin: 15px 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. DANH MỤC THI ĐUA & DỮ LIỆU KHỞI TẠO
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
    {"STT": 1, "Họ và tên": "Nguyễn Tuyền An", "Tổ": "Tổ 2", "Điểm thi đua": 100, "Xếp loại": "Tốt", "Lỗi vi phạm": "None"},
    {"STT": 2, "Họ và tên": "Võ Huỳnh Minh An", "Tổ": "Tổ 1", "Điểm thi đua": 100, "Xếp loại": "Tốt", "Lỗi vi phạm": "None"},
    {"STT": 3, "Họ và tên": "Huỳnh Bảo Ngọc Thiên Ân", "Tổ": "Tổ 1", "Điểm thi đua": 100, "Xếp loại": "Tốt", "Lỗi vi phạm": "None"},
    {"STT": 4, "Họ và tên": "Trần Quốc Bảo", "Tổ": "Tổ 2", "Điểm thi đua": 95, "Xếp loại": "Khá", "Lỗi vi phạm": "Đi muộn x1 (-1)"},
    {"STT": 5, "Họ và tên": "Nguyễn Lê Hoàng Mai", "Tổ": "Tổ 3", "Điểm thi đua": 102, "Xếp loại": "Tốt", "Lỗi vi phạm": "Phát biểu x2 (+2)"},
    {"STT": 6, "Họ và tên": "Lê Văn Tuấn", "Tổ": "Tổ 4", "Điểm thi đua": 85, "Xếp loại": "Khá", "Lỗi vi phạm": "Thiếu BTVN x3 (-15)"},
]

# ==============================================================================
# 4. HÀM XỬ LÝ DỮ LIỆU & ĐỒNG BỘ CLOUD
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

def parse_item_info(item_str):
    diem_goc = 0
    matched_loi = list(DANH_SACH_LOI.keys())[0]
    so_lan = 1
    ghi_chu = ""

    if "[" in item_str and "]" in item_str:
        ghi_chu = item_str[item_str.find("[") + 1 : item_str.rfind("]")].strip()
    elif "(" in item_str and ")" in item_str and not any(k in item_str for k in ["(+", "(-"]):
        ghi_chu = item_str[item_str.find("(") + 1 : item_str.rfind(")")].strip()

    for ten_loi, diem in DANH_SACH_LOI.items():
        ten_ngan = ten_loi.split(" (")[0]
        if item_str.startswith(ten_ngan):
            matched_loi = ten_loi
            diem_goc = diem
            if " x" in item_str:
                try:
                    so_lan = int(item_str.split(" x")[1].split(" ")[0].split("[")[0].split("(")[0])
                except Exception:
                    so_lan = 1
            break

    total_delta = diem_goc * so_lan
    return matched_loi, so_lan, ghi_chu, total_delta

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

# Khởi tạo trạng thái dữ liệu trong phiên
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# ==============================================================================
# 5. THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand-card">
            <div class="sidebar-brand-icon">🏫</div>
            <div>
                <div class="sidebar-brand-title">THCS CHÍ CÔNG</div>
                <div class="sidebar-brand-sub">Quản lý nề nếp & thi đua</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-label">👤 Vai trò truy cập</div>', unsafe_allow_html=True)
    vai_tro = st.selectbox(
        "Chọn vai trò:",
        ["👑 Giáo viên chủ nhiệm", "Tổ trưởng Tổ 1", "Tổ trưởng Tổ 2", "Tổ trưởng Tổ 3", "Tổ trưởng Tổ 4"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-section-label">🧭 Bảng chức năng</div>', unsafe_allow_html=True)
    menu_items = [
        "📝 Ghi nhận điểm số",
        "✏️ Chỉnh sửa / Khắc phục",
        "📊 Tổng quan & Thống kê",
        "📥 Xuất dữ liệu báo cáo",
    ]
    if "Giáo viên" in vai_tro:
        menu_items.append("⚙️ Khởi tạo tuần mới (Reset)")

    chuc_nang = st.radio("Chọn chức năng:", menu_items, label_visibility="collapsed")

    st.markdown("<hr style='margin: 18px 0 14px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    if "Giáo viên" in vai_tro:
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
                    st.success("✅ Đã chuẩn hóa danh sách thành công!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi đọc file: {e}")

    st.write("")
    if st.button("🔄 Đồng bộ lại dữ liệu", use_container_width=True):
        st.session_state.df = load_data()
        st.toast("Đã đồng bộ lại dữ liệu từ Google Sheets!", icon="🔄")
        time.sleep(0.5)
        st.rerun()

# ==============================================================================
# 6. PHÂN QUYỀN TRUY CẬP: TỔ NÀO CHỈ ĐƯỢC NHẬP VÀ SỬA TỔ ĐÓ
# ==============================================================================
is_gvcn = "Giáo viên" in vai_tro

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
# 7. BANNER TRƯỜNG TRÊN ĐẦU NỘI DUNG CHÍNH
# ==============================================================================
phan_vi_text = "Được thao tác: Toàn bộ lớp" if is_gvcn else f"Phạm vi giới hạn: {vai_tro}"
st.markdown(
    f"""
    <div class="school-top-bar">
        <div>
            <div class="school-title">TRƯỜNG THCS CHÍ CÔNG - PHAN RÍ CỬA</div>
            <div class="school-slogan">HỆ THỐNG THEO DÕI THI ĐUA & NỀ NẾP LỚP HỌC</div>
        </div>
        <div style="text-align: right; font-size: 0.85rem;">
            <div><b>Vai trò:</b> {vai_tro}</div>
            <div style="opacity: 0.85;">{phan_vi_text}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# MÀN HÌNH 1: GHI NHẬN ĐIỂM SỐ
# ==============================================================================
if chuc_nang == "📝 Ghi nhận điểm số":
    st.subheader(f"📝 Ghi nhận điểm thi đua — {vai_tro}")
    st.caption("Cộng hoặc trừ điểm thi đua cho học sinh theo các mục đánh giá nề nếp")

    danh_sach_hien_thi = [
        f"#{row['STT']} - {row['Họ và tên']} ({row['Tổ']})"
        for _, row in df_role.iterrows()
    ]

    with st.container(border=True):
        col1, col2 = st.columns([1.6, 1])
        with col1:
            hs_chon_raw = st.selectbox(
                "👤 Chọn học sinh:",
                danh_sach_hien_thi if danh_sach_hien_thi else ["(Không có học sinh trong phạm vi phụ trách)"],
            )
            loi_chon = st.selectbox(
                "📋 Nội dung tuyên dương / Vi phạm:",
                list(DANH_SACH_LOI.keys()),
            )
        with col2:
            so_lan = st.number_input("🔢 Số lần thực hiện:", min_value=1, max_value=20, value=1, step=1)
            ghi_chu = st.text_input("📝 Ghi chú chi tiết (VD: Tiết 3 Hóa, BTVN Đại số):")

        # Xem trước biến động điểm
        if danh_sach_hien_thi and not hs_chon_raw.startswith("("):
            stt_hs = int(hs_chon_raw.split(" - ")[0].replace("#", ""))
            current_row = df[df["STT"] == stt_hs].iloc[0]
            diem_delta = DANH_SACH_LOI[loi_chon] * so_lan
            diem_sau_khi_luu = current_row["Điểm thi đua"] + diem_delta
            delta_color = "#16a34a" if diem_delta > 0 else "#dc2626"
            delta_sign = "+" if diem_delta > 0 else ""

            st.markdown(
                f"""
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 10px 16px; border-radius: 8px; margin: 12px 0;">
                    <b>Điểm hiện tại:</b> <span style="color:#0284c7; font-weight:700;">{current_row['Điểm thi đua']}</span> | 
                    <b>Biến động:</b> <span style="color:{delta_color}; font-weight:700;">{delta_sign}{diem_delta}</span> | 
                    <b>Dự kiến sau ghi:</b> <span style="color:#0f172a; font-weight:700;">{diem_sau_khi_luu}</span> ({tinh_xep_loai(diem_sau_khi_luu)})
                </div>
                """,
                unsafe_allow_html=True,
            )

        btn_save = st.button("💾 Xác nhận lưu điểm", type="primary", use_container_width=True)

        if btn_save and danh_sach_hien_thi and not hs_chon_raw.startswith("("):
            stt_hs = int(hs_chon_raw.split(" - ")[0].replace("#", ""))
            match_idx = df[df["STT"] == stt_hs].index[0]

            diem_thay_doi = DANH_SACH_LOI[loi_chon] * int(so_lan)
            old_score = int(df.at[match_idx, "Điểm thi đua"])
            new_score = old_score + diem_thay_doi
            xeploai_moi = tinh_xep_loai(new_score)

            noi_dung_ngan = loi_chon.split(" (")[0]
            log_item = f"{noi_dung_ngan} x{so_lan}" + (f" [{ghi_chu}]" if ghi_chu else "")

            old_log = str(df.at[match_idx, "Lỗi vi phạm"]).strip()
            if old_log in ["None", "nan", "", "NaN"]:
                full_log = log_item
            else:
                full_log = f"{old_log} | {log_item}"

            df.at[match_idx, "Điểm thi đua"] = new_score
            df.at[match_idx, "Xếp loại"] = xeploai_moi
            df.at[match_idx, "Lỗi vi phạm"] = full_log
            df.to_csv(DATA_FILE, index=False)
            st.session_state.df = df

            if API_URL and "/exec" in API_URL:
                ten_hs = df.at[match_idx, "Họ và tên"]
                ok, msg = update_gsheet(ten_hs, new_score, xeploai_moi, full_log)
                if not ok:
                    st.warning(f"Lưu máy thành công, Cloud báo: {msg}")

            st.toast(f"Đã lưu điểm cho {df.at[match_idx, 'Họ và tên']}!", icon="✅")
            time.sleep(0.8)
            st.rerun()

    st.markdown(f"#### 📋 Danh sách học sinh ({vai_tro})")
    st.dataframe(

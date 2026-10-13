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
# DANH MỤC THI ĐUA & DỮ LIỆU MẪU
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

# Khởi tạo trạng thái session_state
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
        label_visibility="collapsed",
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

# Lọc học sinh theo phạm vi vai trò
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
            hs_chon_raw = st.selectbox(
                "👤 Chọn học sinh:",
                danh_sach_hien_thi if danh_sach_hien_thi else ["(Không có học sinh)"],
            )
            loi_chon = st.selectbox(
                "📋 Nội dung tuyên dương / Vi phạm:",
                list(DANH_SACH_LOI.keys()),
            )
        with col2:
            so_lan = st.number_input("🔢 Số lần thực hiện:", min_value=1, max_value=20, value=1, step=1)
            ghi_chu = st.text_input("📝 Ghi chú chi tiết (VD: Tiết 3 Hóa, BTVN Đại số):")

        # Xem trước biến động điểm
        if danh_sach_hien_thi and hs_chon_raw != "(Không có học sinh)":
            stt_hs = int(hs_chon_raw.split(" - ")[0].replace("#", ""))
            current_row = df[df["STT"] == stt_hs].iloc[0]
            diem_delta = DANH_SACH_LOI[loi_chon] * so_lan
            diem_sau_khi_luu = current_row["Điểm thi đua"] + diem_delta

            st.markdown(
                f"""
                <div style="background-color: #f1f5f9; padding: 10px 16px; border-radius: 8px; margin: 12px 0;">
                    <b>Điểm hiện tại:</b> <span style="color:#0284c7; font-weight:700;">{current_row['Điểm thi đua']}</span> | 
                    <b>Biến động:</b> <span style="color:{'#16a34a' if diem_delta > 0 else '#dc2626'}; font-weight:700;">{'+' if diem_delta > 0 else ''}{diem_delta}</span> | 
                    <b>Dự kiến sau ghi:</b> <span style="color:#0f172a; font-weight:700;">{diem_sau_khi_luu}</span> ({tinh_xep_loai(diem_sau_khi_luu)})
                </div>
                """,
                unsafe_allow_html=True,
            )

        btn_save = st.button("💾 Xác nhận lưu điểm", type="primary", use_container_width=True)

        if btn_save and hs_chon_raw != "(Không có học sinh)":
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
                    st.warning(f"Lưu trên máy thành công, Cloud báo: {msg}")

            st.toast(f"Đã lưu điểm cho {df.at[match_idx, 'Họ và tên']}!", icon="✅")
            time.sleep(0.8)
            st.rerun()

    st.markdown("#### 📋 Danh sách học sinh phụ trách")
    st.dataframe(
        df_role[["STT", "Họ và tên", "Tổ", "Điểm thi đua", "Xếp loại", "Lỗi vi phạm"]],
        use_container_width=True,
        hide_index=True,
    )

# ==============================================================================
# MÀN HÌNH 2: CHỈNH SỬA / KHẮC PHỤC LỖI NHẬP SAI
# ==============================================================================
elif chuc_nang == "✏️ Chỉnh sửa / Khắc phục":
    st.subheader("✏️ Chỉnh sửa & Khắc phục sai sót")
    st.caption("Cho phép điều chỉnh điểm tùy ý, sửa hoặc xóa bớt lịch sử ghi chú vi phạm khi nhập nhầm")

    danh_sach_hien_thi = [
        f"#{row['STT']} - {row['Họ và tên']} ({row['Tổ']})"
        for _, row in df_role.iterrows()
    ]

    selected_student_str = st.selectbox("Chọn học sinh cần sửa thông tin:", danh_sach_hien_thi)

    if selected_student_str:
        stt_target = int(selected_student_str.split(" - ")[0].replace("#", ""))
        match_idx = df[df["STT"] == stt_target].index[0]
        student_data = df.loc[match_idx]

        with st.container(border=True):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                edit_name = st.text_input("Họ và tên:", value=student_data["Họ và tên"])
                edit_group = st.text_input("Tổ:", value=student_data["Tổ"])
            with col_e2:
                edit_score = st.number_input(
                    "Điểm thi đua chính xác:",
                    value=int(student_data["Điểm thi đua"]),
                    step=1,
                )
                calculated_rank = tinh_xep_loai(edit_score)
                st.info(f"Xếp loại tự động tính: **{calculated_rank}**")

            edit_logs = st.text_area(
                "Chi tiết lỗi vi phạm / tuyên dương (Xóa bỏ phần tử ghi nhầm):",
                value=str(student_data["Lỗi vi phạm"]),
                help="Các lỗi ngăn cách nhau bằng dấu |. Nếu hết lỗi, hãy nhập 'None'.",
            )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                btn_save_edit = st.button("💾 Lưu các thay đổi này", type="primary", use_container_width=True)
            with col_btn2:
                btn_reset_single = st.button("🔄 Đặt lại về 100 điểm & Xóa sạch lỗi", use_container_width=True)

            if btn_save_edit:
                df.at[match_idx, "Họ và tên"] = edit_name.strip()
                df.at[match_idx, "Tổ"] = edit_group.strip()
                df.at[match_idx, "Điểm thi đua"] = int(edit_score)
                df.at[match_idx, "Xếp loại"] = calculated_rank
                df.at[match_idx, "Lỗi vi phạm"] = edit_logs.strip() if edit_logs.strip() != "" else "None"

                df.to_csv(DATA_FILE, index=False)
                st.session_state.df = df

                if API_URL and "/exec" in API_URL:
                    update_gsheet(edit_name.strip(), int(edit_score), calculated_rank, edit_logs.strip())

                st.success(f"Đã cập nhật dữ liệu cho học sinh #{stt_target}!")
                time.sleep(0.8)
                st.rerun()

            if btn_reset_single:
                df.at[match_idx, "Điểm thi đua"] = 100
                df.at[match_idx, "Xếp loại"] = "Tốt"
                df.at[match_idx, "Lỗi vi phạm"] = "None"

                df.to_csv(DATA_FILE, index=False)
                st.session_state.df = df

                if API_URL and "/exec" in API_URL:
                    update_gsheet(student_data["Họ và tên"], 100, "Tốt", "None")

                st.success("Đã hoàn tác điểm của học sinh về mức 100 điểm chuẩn!")
                time.sleep(0.8)
                st.rerun()

# ==============================================================================
# MÀN HÌNH 3: TỔNG QUAN & THỐNG KÊ
# ==============================================================================
elif chuc_nang == "📊 Tổng quan & Thống kê":
    st.subheader("📊 Bảng thống kê toàn diện lớp học")

    m1, m2, m3, m4 = st.columns(4)
    total_students = len(df)
    avg_score = round(df["Điểm thi đua"].mean(), 1) if not df.empty else 0
    tot_count = len(df[df["Xếp loại"] == "Tốt"])
    yeu_count = len(df[df["Xếp loại"].isin(["Trung bình", "Yếu"])])

    with m1:
        st.markdown(
            f'<div class="stat-card"><span class="stat-label">Sĩ số</span><span class="stat-value">{total_students}</span></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="stat-card"><span class="stat-label">Điểm TB Lớp</span><span class="stat-value">{avg_score}</span></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="stat-card"><span class="stat-label">Xếp loại Tốt</span><span class="stat-value" style="color:#16a34a;">{tot_count}</span></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f'<div class="stat-card"><span class="stat-label">Cần nhắc nhở</span><span class="stat-value" style="color:#dc2626;">{yeu_count}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if "Tổ" in df.columns and not df.empty:
        st.markdown("#### 🏆 Điểm trung bình thi đua theo Tổ")
        avg_by_to = df.groupby("Tổ")["Điểm thi đua"].mean().round(1).reset_index()
        avg_by_to = avg_by_to.sort_values(by="Điểm thi đua", ascending=False)
        st.bar_chart(data=avg_by_to.set_index("Tổ"), use_container_width=True)

    st.markdown("#### 📄 Bảng tổng hợp thi đua")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        loc_to = st.selectbox("Lọc theo tổ:", ["Tất cả"] + sorted(list(df["Tổ"].unique())))
    with f_col2:
        loc_xeploai = st.selectbox("Lọc theo loại:", ["Tất cả"] + ["Tốt", "Khá", "Trung bình", "Yếu"])

    df_view = df.copy()
    if loc_to != "Tất cả":
        df_view = df_view[df_view["Tổ"] == loc_to]
    if loc_xeploai != "Tất cả":
        df_view = df_view[df_view["Xếp loại"] == loc_xeploai]

    st.dataframe(
        df_view.sort_values(by="Điểm thi đua", ascending=False),
        column_config={
            "Điểm thi đua": st.column_config.ProgressColumn(
                "Điểm thi đua",
                help="Thang điểm chuẩn 100",
                format="%d",
                min_value=0,
                max_value=120,
            ),
        },
        use_container_width=True,
        hide_index=True,
    )

# ==============================================================================
# MÀN HÌNH 4: XUẤT BÁO CÁO EXCEL
# ==============================================================================
elif chuc_nang == "📥 Xuất dữ liệu báo cáo":
    st.subheader("📥 Xuất báo cáo tổng kết")
    st.caption("Xuất file Excel đầy đủ để in ấn hoặc lưu trữ hồ sơ")

    with st.container(border=True):
        st.write("File Excel xuất ra chứa thông tin đầy đủ gồm: **STT, Họ và tên, Tổ, Điểm thi đua, Xếp loại, và Danh sách vi phạm**.")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="BaoCaoThiDua")
        buffer.seek(0)

        st.download_button(
            label="📊 Tải xuống file Excel (.xlsx)",
            data=buffer,
            file_name=f"Bao_Cao_Thi_Dua_{time.strftime('%Y_%m_%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )

# ==============================================================================
# MÀN HÌNH 5: RESET TUẦN MỚI
# ==============================================================================
elif chuc_nang == "⚙️ Khởi tạo tuần mới (Reset)":
    st.subheader("⚙️ Khởi tạo chu kỳ tuần mới")
    st.warning("⚠️ **Lưu ý:** Hãy tải file báo cáo Excel ở mục '📥 Xuất dữ liệu báo cáo' trước khi thực hiện thao tác này.")

    with st.container(border=True):
        st.markdown(
            """
            **Hệ thống sẽ thực hiện:**
            - Khôi phục điểm tất cả học sinh về **100 điểm**.
            - Cập nhật toàn bộ xếp loại về **Tốt**.
            - Xóa sạch danh sách ghi nhận lỗi vi phạm/khen thưởng cũ.
            """
        )

        confirm = st.checkbox("Xác nhận: Tôi đã lưu trữ báo cáo tuần này và muốn đặt lại dữ liệu.")

        if st.button

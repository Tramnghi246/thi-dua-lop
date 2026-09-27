import json
import pandas as pd
import requests
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Hệ Thống Thi Đua Lớp Học", layout="wide", page_icon="🏆"
)

st.markdown(
    '<head><meta name="google" content="notranslate"></head>',
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# DÁN URL GOOGLE APPS SCRIPT CỦA BẠN VÀO GIỮA DẤU NGOẶC KÉP BÊN DƯỚI:
API_URL = "https://script.google.com/macros/s/AKfycbyH2ok5WSMLG6aIQlnbwWUU9LrxE_JQFrpXM9rSPl9I9DwF9swI1VF664DuNEBVigOgkQ/exec"
# -------------------------------------------------------------


# Tải dữ liệu từ Google Sheets
def load_data():
    try:
        res = requests.get(API_URL, timeout=10)
        data = res.json()
        if len(data) > 1:
            headers = data[0]
            rows = data[1:]
            df = pd.DataFrame(rows, columns=headers)
            df["Điểm thi đua"] = (
                pd.to_numeric(df["Điểm thi đua"], errors="coerce")
                .fillna(100)
                .astype(int)
            )
            df["Lỗi vi phạm"] = df["Lỗi vi phạm"].fillna("").astype(str)
            return df
    except Exception:
        pass

    default_data = [
        {
            "STT": 1,
            "Họ và tên": "Nguyễn Văn An",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "",
        },
        {
            "STT": 2,
            "Họ và tên": "Trần Thị Bình",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "",
        },
        {
            "STT": 3,
            "Họ và tên": "Lê Hoàng Cường",
            "Tổ": "Tổ 2",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "",
        },
        {
            "STT": 4,
            "Họ và tên": "Phạm Minh Đức",
            "Tổ": "Tổ 2",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "",
        },
        {
            "STT": 5,
            "Họ và tên": "Vũ Thu Trang",
            "Tổ": "Tổ 3",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "",
        },
        {
            "STT": 6,
            "Họ và tên": "Hoàng Văn Nam",
            "Tổ": "Tổ 4",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "",
        },
    ]
    return pd.DataFrame(default_data)


# Lưu dữ liệu trực tiếp lên Google Sheets
def save_data(df):
    try:
        headers = df.columns.tolist()
        values = [headers] + df.astype(str).values.tolist()
        json_str = json.dumps(values)
        requests.get(API_URL, params={"action": "write", "data": json_str})
        return True
    except Exception:
        return False


def tinh_xep_loai(diem):
    try:
        diem = float(diem)
    except Exception:
        diem = 100.0

    if diem >= 100:
        return "Tốt"
    elif diem >= 85:
        return "Khá"
    elif diem >= 75:
        return "Trung bình"
    else:
        return "Yếu"


df = load_data()

DANH_SACH_LOI = {
    "🌟 Phát biểu xây dựng bài (+1 điểm)": 1,
    "💯 Đạt điểm 9, 10 (+2 điểm)": 2,
    "✉️ Nghỉ học có phép (-2 điểm)": -2,
    "⏰ Đi muộn (-5 điểm)": -5,
    "📚 Không học bài / Thiếu BTVN (-5 điểm)": -5,
    "👔 Không mặc đồng phục (-5 điểm)": -5,
    "🔊 Mất trật tự trong giờ (-5 điểm)": -5,
    "🧹 Không vệ sinh, lao động (-5 điểm)": -5,
    "📱 Sử dụng điện thoại (-10 điểm)": -10,
    "🚨 Nghỉ học không phép (-15 điểm)": -15,
}

st.title("🏆 HỆ THỐNG QUẢN LÝ THI ĐUA LỚP HỌC")

st.sidebar.title("🔐 ĐĂNG NHẬP VAI TRÒ")
vai_tro = st.sidebar.selectbox(
    "Bạn là ai?",
    [
        "Tổ trưởng Tổ 1",
        "Tổ trưởng Tổ 2",
        "Tổ trưởng Tổ 3",
        "Tổ trưởng Tổ 4",
        "👑 Giáo viên chủ nhiệm",
    ],
)

if st.sidebar.button("🔄 Làm mới dữ liệu"):
    st.rerun()

if "Tổ 1" in vai_tro:
    df_view = df[df["Tổ"] == "Tổ 1"]
elif "Tổ 2" in vai_tro:
    df_view = df[df["Tổ"] == "Tổ 2"]
elif "Tổ 3" in vai_tro:
    df_view = df[df["Tổ"] == "Tổ 3"]
elif "Tổ 4" in vai_tro:
    df_view = df[df["Tổ"] == "Tổ 4"]
else:
    df_view = df

st.subheader(f"📋 Danh sách quản lý - {vai_tro}")

if not df_view.empty:
    student_list = df_view["Họ và tên"].tolist()
    with st.form("nhap_diem_form"):
        col1, col2 = st.columns(2)
        with col1:
            ten_hs = st.selectbox("👤 Chọn học sinh:", student_list)
            loi = st.selectbox("📋 Nội dung thi đua:", list(DANH_SACH_LOI.keys()))
        with col2:
            so_lan = st.number_input(
                "🔢 Số lần:", min_value=1, max_value=20, value=1
            )
            ghi_chu = st.text_input("✏️ Ghi chú (môn/tiết...):")

        submit = st.form_submit_button("💾 LƯU ĐIỂM")

        if submit:
            idx_list = df[df["Họ và tên"] == ten_hs].index
            if len(idx_list) > 0:
                idx = idx_list[0]
                diem_thay_doi = int(DANH_SACH_LOI[loi]) * int(so_lan)

                current_score = int(df.at[idx, "Điểm thi đua"])
                new_score = current_score + diem_thay_doi

                df.at[idx, "Điểm thi đua"] = new_score
                df.at[idx, "Xếp loại"] = tinh_xep_loai(new_score)

                loi_clean = loi.split(" (")[0]
                log_text = (
                    f"{loi_clean} x{so_lan}"
                    + (f" ({ghi_chu})" if ghi_chu else "")
                )

                old_log = str(df.at[idx, "Lỗi vi phạm"])
                if old_log in ["nan", "None", "", "NaN"]:
                    df.at[idx, "Lỗi vi phạm"] = log_text
                else:
                    df.at[idx, "Lỗi vi phạm"] = f"{old_log} | {log_text}"

                with st.spinner("Đang lưu đồng bộ lên Google Sheets..."):
                    if save_data(df):
                        st.success(
                            f"✅ Đã lưu điểm cho em {ten_hs} (Điểm mới: {new_score})"
                        )
                        st.rerun()
                    else:
                        st.error("Không thể kết nối Google Sheets!")

cols = ["STT", "Họ và tên", "Tổ", "Điểm thi đua", "Xếp loại", "Lỗi vi phạm"]
st.dataframe(df_view[cols], use_container_width=True, hide_index=True)

import io
import os
import pandas as pd
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Hệ Thống Thi Đua Lớp Học", layout="wide", page_icon="🏆"
)

# Chặn Google Dịch làm vỡ giao diện
st.markdown(
    '<head><meta name="google" content="notranslate"></head>',
    unsafe_allow_html=True,
)

DATA_FILE = "du_lieu_thi_dua.csv"


# Hàm tính xếp loại
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


# Tải dữ liệu từ CSV
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if not df.empty and "Họ và tên" in df.columns:
                df["Điểm thi đua"] = (
                    pd.to_numeric(df["Điểm thi đua"], errors="coerce")
                    .fillna(100)
                    .astype(int)
                )
                df["Lỗi vi phạm"] = (
                    df["Lỗi vi phạm"].fillna("None").astype(str)
                )
                df["Xếp loại"] = df["Điểm thi đua"].apply(tinh_xep_loai)
                return df
        except Exception:
            pass

    default_data = [
        {
            "STT": 2,
            "Họ và tên": "Võ Huỳnh Minh An",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "None",
        },
        {
            "STT": 3,
            "Họ và tên": "Huỳnh Bảo Ngọc Thiên Ân",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "None",
        },
        {
            "STT": 5,
            "Họ và tên": "Ngô Gia Hân",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "None",
        },
        {
            "STT": 7,
            "Họ và tên": "Huỳnh Ngọc Huy",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "None",
        },
        {
            "STT": 9,
            "Họ và tên": "Nguyễn Huỳnh Gia Hưng",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "None",
        },
        {
            "STT": 10,
            "Họ và tên": "Lê Quỳnh Diễm Hương",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "None",
        },
        {
            "STT": 12,
            "Họ và tên": "Bùi Nhật Khiêm",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "None",
        },
        {
            "STT": 14,
            "Họ và tên": "Lê Ngọc Ánh Loan",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "None",
        },
        {
            "STT": 16,
            "Họ và tên": "Nguyễn Trần Xuân Nghi",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "None",
        },
        {
            "STT": 18,
            "Họ và tên": "Võ Như Nguyệt",
            "Tổ": "Tổ 1",
            "Điểm thi đua": 100,
            "Xếp loại": "Tốt",
            "Lỗi vi phạm": "None",
        },
    ]
    df = pd.DataFrame(default_data)
    df.to_csv(DATA_FILE, index=False)
    return df


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

# Thanh menu bên trái (Sidebar)
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

chuc_nang = st.sidebar.radio(
    "Chức năng:",
    ["📝 Ghi Nhận Thi Đua", "📊 Bảng Tổng Hợp Lớp", "📬 Tải File Báo Cáo"],
)

if st.sidebar.button("🔄 Cập nhật dữ liệu mới nhất"):
    st.rerun()

# Lọc học sinh theo vai trò
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

# Hiển thị theo chức năng chọn
if chuc_nang == "📝 Ghi Nhận Thi Đua":
    st.title("🏆 HỆ THỐNG QUẢN LÝ THI ĐUA LỚP HỌC")

    # Khung nhập điểm thi đua
    if not df_view.empty:
        student_list = df_view["Họ và tên"].tolist()
        with st.form("nhap_diem_form"):
            col1, col2 = st.columns(2)
            with col1:
                ten_hs = st.selectbox("👤 Chọn học sinh:", student_list)
                loi = st.selectbox(
                    "📋 Nội dung thi đua:", list(DANH_SACH_LOI.keys())
                )
            with col2:
                so_lan = st.number_input(
                    "🔢 Số lần:", min_value=1, max_value=20, value=1
                )
                ghi_chu = st.text_input("✏️ Ghi chú (môn/tiết...):")

            submit = st.form_submit_button("💾 LƯU ĐIỂM")

            if submit:
                idx = df[df["Họ và tên"] == ten_hs].index[0]
                diem_thay_doi = int(DANH_SACH_LOI[loi]) * int(so_lan)
                new_score = int(df.at[idx, "Điểm thi đua"]) + diem_thay_doi

                df.at[idx, "Điểm thi đua"] = new_score
                df.at[idx, "Xếp loại"] = tinh_xep_loai(new_score)

                loi_clean = loi.split(" (")[0]
                log_text = (
                    f"{loi_clean} x{so_lan}"
                    + (f" ({ghi_chu})" if ghi_chu else "")
                )
                old_log = str(df.at[idx, "Lỗi vi phạm"])

                if old_log in ["None", "nan", "", "NaN"]:
                    df.at[idx, "Lỗi vi phạm"] = log_text
                else:
                    df.at[idx, "Lỗi vi phạm"] = f"{old_log} | {log_text}"

                df.to_csv(DATA_FILE, index=False)
                st.success(
                    f"✅ Đã lưu điểm cho em {ten_hs} (Điểm mới: {new_score})"
                )
                st.rerun()

    st.subheader("📋 Bảng điểm học sinh thuộc quyền quản lý:")
    cols = ["STT", "Họ và tên", "Tổ", "Điểm thi đua", "Xếp loại", "Lỗi vi phạm"]
    st.dataframe(df_view[cols], use_container_width=True, hide_index=True)

elif chuc_nang == "📊 Bảng Tổng Hợp Lớp":
    st.title("📊 BẢNG TỔNG HỢP THI ĐUA TOÀN LỚP")
    cols = ["STT", "Họ và tên", "Tổ", "Điểm thi đua", "Xếp loại", "Lỗi vi phạm"]
    st.dataframe(df[cols], use_container_width=True, hide_index=True)

elif chuc_nang == "📬 Tải File Báo Cáo":
    st.title("📬 TẢI BÁO CÁO THI ĐUA")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="ThiDua")
    buffer.seek(0)

    st.download_button(
        label="📥 Tải xuống file báo cáo Excel (.xlsx)",
        data=buffer,
        file_name="Bao_Cao_Thi_Dua_Lop.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

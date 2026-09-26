import io
import os
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hệ Thống Thi Đua Lớp Học", layout="wide", page_icon="🏆"
)

DATA_FILE = "du_lieu_thi_dua.csv"


# 1. HÀM TÍNH XẾP LOẠI THI ĐUA
def tinh_xep_loai(diem):
    if diem >= 100:
        return "Tốt"
    elif diem >= 85:
        return "Khá"
    elif diem >= 75:
        return "Trung bình"
    else:
        return "Yếu"


# 2. ĐỌC VÀ LƯU DỮ LIỆU
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame([
            {
                "STT": 1,
                "Họ và tên": "Nguyễn Văn An",
                "Tổ": "Tổ 1",
                "Điểm thi đua": 100,
                "Lỗi vi phạm": "",
            },
            {
                "STT": 2,
                "Họ và tên": "Trần Thị Bình",
                "Tổ": "Tổ 1",
                "Điểm thi đua": 100,
                "Lỗi vi phạm": "",
            },
            {
                "STT": 3,
                "Họ và tên": "Lê Hoàng Cường",
                "Tổ": "Tổ 2",
                "Điểm thi đua": 100,
                "Lỗi vi phạm": "",
            },
            {
                "STT": 4,
                "Họ và tên": "Phạm Minh Đức",
                "Tổ": "Tổ 2",
                "Điểm thi đua": 100,
                "Lỗi vi phạm": "",
            },
            {
                "STT": 5,
                "Họ và tên": "Vũ Thu Trang",
                "Tổ": "Tổ 3",
                "Điểm thi đua": 100,
                "Lỗi vi phạm": "",
            },
            {
                "STT": 6,
                "Họ và tên": "Hoàng Văn Nam",
                "Tổ": "Tổ 4",
                "Điểm thi đua": 100,
                "Lỗi vi phạm": "",
            },
        ])
        df.to_csv(DATA_FILE, index=False)

    df["Xếp loại"] = df["Điểm thi đua"].apply(tinh_xep_loai)
    return df


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


if "students" not in st.session_state:
    st.session_state.students = load_data()

# 3. DANH MỤC LỖI / ĐIỂM THƯỞNG
DANH_SACH_LOI = {
    "🌟 Phát biểu xây dựng bài (+1 điểm)": 1,
    "💯 Đạt điểm 9, 10 (+2 điểm)": 2,
    "✉️ Nghỉ học có phép (-2 điểm)": -2,
    "⏰ Đi muộn (-3 điểm)": -3,
    "📚 Không học bài / Thiếu BTVN (-5 điểm)": -5,
    "👔 Không mặc đồng phục / Thiếu khăn quàng (-5 điểm)": -5,
    "🔊 Mất trật tự trong giờ (-2 điểm)": -2,
    "👔 Nền nếp tác phong (-5 điểm)": -5,
    "🧹 Không vệ sinh, lao động (-5 điểm)": -5,
    "🤬 Nói tục / Tác phong kém (-5 điểm)": -5,
    "📱 Sử dụng điện thoại (-20 điểm)": -20,
    "🪑 Không bảo vệ của công (-10 điểm)": -10,
    "🚨 Nghỉ học không phép (-5 điểm)": -5,
    "🚦 Vi phạm ATGT (-20 điểm)": -20,
}

# 4. THANH BÊN: CHỌN VAI TRÒ
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70
)
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

st.sidebar.markdown("---")

if vai_tro == "👑 Giáo viên chủ nhiệm":
    uploaded_file = st.sidebar.file_uploader(
        "📂 Tải danh sách lớp mới (Excel/CSV)", type=["xlsx", "csv"]
    )
    if uploaded_file is not None:
        try:
            df_up = (
                pd.read_csv(uploaded_file)
                if uploaded_file.name.endswith(".csv")
                else pd.read_excel(uploaded_file)
            )
            if "Họ và tên" in df_up.columns:
                if "STT" not in df_up.columns:
                    df_up["STT"] = range(1, len(df_up) + 1)
                if "Tổ" not in df_up.columns:
                    df_up["Tổ"] = "Tổ 1"
                if "Điểm thi đua" not in df_up.columns:
                    df_up["Điểm thi đua"] = 100
                if "Lỗi vi phạm" not in df_up.columns:
                    df_up["Lỗi vi phạm"] = ""

                df_up["Xếp loại"] = df_up["Điểm thi đua"].apply(tinh_xep_loai)
                st.session_state.students = df_up[[
                    "STT",
                    "Họ và tên",
                    "Tổ",
                    "Điểm thi đua",
                    "Xếp loại",
                    "Lỗi vi phạm",
                ]]
                save_data(st.session_state.students)
                st.sidebar.success("✅ Đã cập nhật danh sách lớp!")
        except Exception as e:
            st.sidebar.error(f"Lỗi: {e}")

menu = st.sidebar.radio(
    "Chức năng:",
    ["📝 Ghi Nhận Thi Đua", "📊 Bảng Tổng Hợp Lớp", "📥 Tải File Báo Cáo"],
)

if st.sidebar.button("🔄 Cập nhật dữ liệu mới nhất"):
    st.session_state.students = load_data()
    st.rerun()

cols_display = [
    "STT",
    "Họ và tên",
    "Tổ",
    "Điểm thi đua",
    "Xếp loại",
    "Lỗi vi phạm",
]

# 5. TRANG 1: GHI NHẬN ĐIỂM
if menu == "📝 Ghi Nhận Thi Đua":
    st.title(f"📝 Ghi Nhận Thi Đua - {vai_tro}")

    df = st.session_state.students

    if "Tổ 1" in vai_tro:
        df_view = df[df["Tổ"] == "Tổ 1"]
    elif "Tổ 2" in vai_tro:
        df_view = df[df["Tổ"] == "Tổ 2"]
    elif "Tổ 3" in vai_tro:
        df_view = df[df["Tổ"] == "Tổ 3"]
    elif "Tổ 4" in vai_tro:
        df_view = df[df["Tổ"] == "Tổ 4"]
    else:
        selected_to = st.selectbox(
            "👉 Lọc theo Tổ:",
            ["Tất cả các bạn", "Tổ 1", "Tổ 2", "Tổ 3", "Tổ 4"],
        )
        df_view = (
            df[df["Tổ"] == selected_to] if selected_to != "Tất cả các bạn" else df
        )

    if len(df_view) == 0:
        st.warning("⚠️ Không có học sinh nào.")
    else:
        student_options = [
            f"{row['Họ và tên']} ({row['Tổ']})" for _, row in df_view.iterrows()
        ]

        with st.form(key="form_nhap_diem", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                student_selected = st.selectbox(
                    "👤 Chọn học sinh:", student_options
                )
                violation = st.selectbox(
                    "📋 Nội dung thi đua:", list(DANH_SACH_LOI.keys())
                )
            with col2:
                solan = st.number_input(
                    "🔢 Số lần:", min_value=1, max_value=20, value=1
                )
                note = st.text_input("✏️ Ghi chú (Môn/Tiết...):")

            st.markdown("<br>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button(label="💾 LƯU ĐIỂM SỐ")

        if submit_btn:
            student_name = student_selected.split(" (")[0]
            unit_pts = DANH_SACH_LOI[violation]
            total_change = unit_pts * solan

            idx = st.session_state.students[
                st.session_state.students["Họ và tên"] == student_name
            ].index[0]

            # Cập nhật điểm và Xếp loại
            st.session_state.students.at[idx, "Điểm thi đua"] += total_change
            new_score = st.session_state.students.at[idx, "Điểm thi đua"]
            st.session_state.students.at[idx, "Xếp loại"] = tinh_xep_loai(
                new_score
            )

            item_clean = " ".join(violation.split(" (")[0].split()[1:])
            log_text = (
                f"{item_clean}"
                + (f" x{solan}" if solan > 1 else "")
                + (f" ({note})" if note else "")
            )

            old_log = st.session_state.students.at[idx, "Lỗi vi phạm"]
            st.session_state.students.at[idx, "Lỗi vi phạm"] = (
                f"{old_log} | {log_text}" if old_log else log_text
            )

            save_data(st.session_state.students)
            st.success(
                f"✅ Đã lưu điểm cho em **{student_name}** (Điểm mới:"
                f" **{new_score}** - Xếp loại: **{tinh_xep_loai(new_score)}**)"
            )

    st.markdown("---")
    st.subheader("📋 Bảng điểm học sinh thuộc quyền quản lý:")
    st.dataframe(
        df_view[cols_display], use_container_width=True, hide_index=True
    )

# 6. TRANG 2: TỔNG HỢP & THỐNG KÊ XẾP LOẠI
elif menu == "📊 Bảng Tổng Hợp Lớp":
    st.title("📊 Bảng Theo Dõi & Thống Kê Xếp Loại")

    st.session_state.students = load_data()
    df = st.session_state.students

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "🏅 Loại Tốt (≥100đ)",
        f"{len(df[df['Xếp loại'] == 'Tốt'])} em",
    )
    c2.metric(
        "👍 Loại Khá (85-99đ)",
        f"{len(df[df['Xếp loại'] == 'Khá'])} em",
    )
    c3.metric(
        "😐 Loại T.Bình (75-84đ)",
        f"{len(df[df['Xếp loại'] == 'Trung bình'])} em",
    )
    c4.metric(
        "⚠️ Loại Yếu (<75đ)",
        f"{len(df[df['Xếp loại'] == 'Yếu'])} em",
    )

    st.markdown("---")

    st.subheader("📌 Tổng hợp số lượng xếp loại toàn lớp")
    xl_counts = (
        df["Xếp loại"]
        .value_counts()
        .reindex(["Tốt", "Khá", "Trung bình", "Yếu"], fill_value=0)
        .reset_index()
    )
    xl_counts.columns = ["Xếp loại", "Số lượng học sinh"]
    st.dataframe(xl_counts, use_container_width=True, hide_index=True)

    st.subheader("📜 Bảng điểm & Xếp loại chi tiết")
    st.dataframe(df[cols_display], use_container_width=True, hide_index=True)

# 7. TRANG 3: XUẤT FILE BÁO CÁO
else:
    st.title("📥 Tải Báo Cáo Thi Đua Excel")
    st.dataframe(
        st.session_state.students[cols_display],
        use_container_width=True,
        hide_index=True,
    )
    csv = (
        st.session_state.students[cols_display]
        .to_csv(index=False)
        .encode("utf-8-sig")
    )
    st.download_button(
        "📥 Tải Báo Cáo CSV/Excel",
        data=csv,
        file_name="Bao_Cao_Thi_Dua_Xep_Loai.csv",
        mime="text/csv",
    )
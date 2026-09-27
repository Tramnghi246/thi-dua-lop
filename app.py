import io
import json
import os
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Hệ Thống Thi Đua Lớp Học", layout="wide", page_icon="🏆"
)
st.markdown(
    '<head><meta name="google" content="notranslate"></head>',
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# DÁN LINK GOOGLE APPS SCRIPT CỦA BẠN VÀO GIỮA DẤU NGOẶC KÉP DƯỚI ĐÂY:
API_URL = "https://script.google.com/macros/s/AKfycbyoZp8di7TM_Kze_u4HRMGtitRNx8PCgIXOZfF09YE9dF_waGFKmlHqsd68-gwknves/exec"
# --------------------------------------------------------------------------

DATA_FILE = "du_lieu_thi_dua.csv"


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


DEFAULT_STUDENTS = [
    {
        "STT": 1,
        "Họ và tên": "Võ Huỳnh Minh An",
        "Tổ": "Tổ 1",
        "Điểm thi đua": 100,
        "Xếp loại": "Tốt",
        "Lỗi vi phạm": "None",
    },
    {
        "STT": 2,
        "Họ và tên": "Huỳnh Bảo Ngọc Thiên Ân",
        "Tổ": "Tổ 1",
        "Điểm thi đua": 100,
        "Xếp loại": "Tốt",
        "Lỗi vi phạm": "None",
    },
    {
        "STT": 3,
        "Họ và tên": "Nguyễn Tuyền An",
        "Tổ": "Tổ 2",
        "Điểm thi đua": 100,
        "Xếp loại": "Tốt",
        "Lỗi vi phạm": "None",
    },
    {
        "STT": 4,
        "Họ và tên": "Lê Minh Thái Dương",
        "Tổ": "Tổ 3",
        "Điểm thi đua": 100,
        "Xếp loại": "Tốt",
        "Lỗi vi phạm": "None",
    },
]


def clean_dataframe(df_input):
    if df_input is None or df_input.empty:
        return pd.DataFrame(DEFAULT_STUDENTS)

    df_clean = df_input.copy()
    df_clean.columns = [str(c).strip() for c in df_clean.columns]

    required_cols = ["STT", "Họ và tên", "Tổ", "Điểm thi đua"]
    for col in required_cols:
        if col not in df_clean.columns:
            return pd.DataFrame(DEFAULT_STUDENTS)

    df_clean = df_clean.dropna(subset=["Họ và tên"])
    df_clean["Họ và tên"] = df_clean["Họ và tên"].astype(str).str.strip()
    df_clean = df_clean[
        ~df_clean["Họ và tên"]
        .str.lower()
        .isin(["none", "nan", "", "null", "none (none)"])
    ]

    df_clean["Tổ"] = df_clean["Tổ"].astype(str).str.strip()
    df_clean["Điểm thi đua"] = (
        pd.to_numeric(df_clean["Điểm thi đua"], errors="coerce")
        .fillna(100)
        .astype(int)
    )

    if "Lỗi vi phạm" in df_clean.columns:
        df_clean["Lỗi vi phạm"] = (
            df_clean["Lỗi vi phạm"].fillna("None").astype(str)
        )
    else:
        df_clean["Lỗi vi phạm"] = "None"

    df_clean["Xếp loại"] = df_clean["Điểm thi đua"].apply(tinh_xep_loai)
    return df_clean.reset_index(drop=True)


def load_data():
    if API_URL and API_URL.startswith("http"):
        try:
            res = requests.get(API_URL, timeout=8)
            data = res.json()
            if isinstance(data, list) and len(data) > 1:
                headers = [str(h).strip() for h in data[0]]
                rows = data[1:]
                df_temp = pd.DataFrame(rows, columns=headers)
                df_res = clean_dataframe(df_temp)
                if not df_res.empty:
                    return df_res
        except Exception:
            pass

    if os.path.exists(DATA_FILE):
        try:
            df_temp = pd.read_csv(DATA_FILE)
            df_res = clean_dataframe(df_temp)
            if not df_res.empty:
                return df_res
        except Exception:
            pass

    df_default = pd.DataFrame(DEFAULT_STUDENTS)
    df_default.to_csv(DATA_FILE, index=False)
    return df_default


def save_data(df_to_save):
    df_to_save.to_csv(DATA_FILE, index=False)
    if API_URL and API_URL.startswith("http"):
        try:
            headers = df_to_save.columns.tolist()
            values = [headers] + df_to_save.astype(str).values.tolist()
            json_str = json.dumps(values)

            # Gửi dữ liệu cập nhật
            res = requests.post(
                f"{API_URL}?action=write",
                data=json_str,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            res_data = res.json()
            if res_data.get("status") == "success":
                return True, "Thành công"
            else:
                return (
                    False,
                    res_data.get("message", "Lỗi phản hồi từ Google Sheet"),
                )
        except Exception as e:
            return False, str(e)
    return False, "Chưa điền API_URL Google Apps Script"


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

st.title("🏆 QUẢN LÝ THI ĐUA LỚP HỌC")

col_to, col_btn = st.columns([3, 1])
with col_to:
    vai_tro = st.selectbox(
        "🔐 BẠN LÀ AI? (Chọn vai trò của bạn):",
        [
            "👑 Giáo viên chủ nhiệm (Toàn lớp)",
            "Tổ trưởng Tổ 1",
            "Tổ trưởng Tổ 2",
            "Tổ trưởng Tổ 3",
            "Tổ trưởng Tổ 4",
        ],
    )
with col_btn:
    st.write("")
    st.write("")
    if st.button("🔄 Cập nhật dữ liệu"):
        st.rerun()

if "Tổ 1" in vai_tro:
    df_view = df[df["Tổ"].str.contains("1", na=False)].copy()
elif "Tổ 2" in vai_tro:
    df_view = df[df["Tổ"].str.contains("2", na=False)].copy()
elif "Tổ 3" in vai_tro:
    df_view = df[df["Tổ"].str.contains("3", na=False)].copy()
elif "Tổ 4" in vai_tro:
    df_view = df[df["Tổ"].str.contains("4", na=False)].copy()
else:
    df_view = df.copy()

chuc_nang = st.sidebar.radio(
    "Chức năng:",
    ["📝 Ghi Nhận Thi Đua", "📊 Bảng Tổng Hợp Lớp", "📬 Tải File Báo Cáo"],
)

if chuc_nang == "📝 Ghi Nhận Thi Đua":
    if not df_view.empty:
        student_list = df_view["Họ và tên"].tolist()
        with st.form("nhap_diem_form"):
            st.subheader(f"📝 Nhập điểm - {vai_tro}")
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

            submit = st.form_submit_button("💾 LƯU ĐIỂM SỐ")

            if submit:
                match_idx = df[df["Họ và tên"] == ten_hs].index
                if len(match_idx) > 0:
                    idx = match_idx[0]
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

                    saved_ok, msg = save_data(df)
                    if saved_ok:
                        st.success(
                            f"✅ Đã lưu điểm cho em {ten_hs} lên Google Sheet! (Điểm mới: {new_score})"
                        )
                        st.rerun()
                    else:
                        st.error(
                            f"❌ KHÔNG THỂ CẬP NHẬT GOOGLE SHEET: {msg}. Hãy kiểm tra lại link API_URL hoặc quyền truy cập 'Bất kỳ ai'."
                        )
    else:
        st.warning("⚠️ Không tìm thấy dữ liệu học sinh!")

    st.subheader("📋 Bảng điểm học sinh thuộc quyền quản lý:")
    cols = ["STT", "Họ và tên", "Tổ", "Điểm thi đua", "Xếp loại", "Lỗi vi phạm"]
    valid_cols = [c for c in cols if c in df_view.columns]
    st.dataframe(df_view[valid_cols], use_container_width=True, hide_index=True)

elif chuc_nang == "📊 Bảng Tổng Hợp Lớp":
    st.subheader("📊 BẢNG TỔNG HỢP THI ĐUA TOÀN LỚP")
    cols = ["STT", "Họ và tên", "Tổ", "Điểm thi đua", "Xếp loại", "Lỗi vi phạm"]
    valid_cols = [c for c in cols if c in df.columns]
    st.dataframe(df[valid_cols], use_container_width=True, hide_index=True)

elif chuc_nang == "📬 Tải File Báo Cáo":
    st.subheader("📬 TẢI BÁO CÁO THI ĐUA")
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

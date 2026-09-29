import io
import json
import os
import time
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
# DÁN LINK GOOGLE APPS SCRIPT KẾT THÚC BẰNG /exec VÀO GIỮA NGOẶC KÉP:
API_URL = "https://script.google.com/macros/s/AKfycbzDIxYQJ67Iv0CgR2RgN0MXKK8GZ1mblchl4sm5Oh40684Qa1Hb_l_-HAupPEeyMmTSEg/exec"
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
]


def load_data():
    # Thêm timestamp _t để chống trình duyệt lưu Cache trên máy tính
    if API_URL and "/exec" in API_URL:
        try:
            res = requests.get(API_URL, params={"_t": time.time()}, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 1:
                    df_temp = pd.DataFrame(data[1:], columns=data[0])
                    df_temp.to_csv(DATA_FILE, index=False)
                    return df_temp
        except Exception:
            pass

    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except Exception:
            pass

    return pd.DataFrame(DEFAULT_STUDENTS)


def update_gsheet(name, score, xeploai, log_text):
    if not API_URL or "/exec" not in API_URL:
        return False, "Chưa điền link API_URL chuẩn"

    try:
        params = {
            "action": "update",
            "name": name,
            "score": score,
            "xeploai": xeploai,
            "log": log_text,
            "_t": time.time(),
        }
        res = requests.get(API_URL, params=params, timeout=12)

        if res.status_code == 200:
            try:
                res_json = res.json()
                if res_json.get("status") == "success":
                    return True, "Thành công"
                else:
                    return (
                        False,
                        res_json.get("message", "Lỗi từ Google Apps Script"),
                    )
            except Exception:
                return (
                    False,
                    "Lỗi phản hồi. Hãy kiểm tra quyền 'Bất kỳ ai' trên Google Script.",
                )
        else:
            return False, f"Lỗi HTTP: {res.status_code}"
    except Exception as e:
        return False, str(e)


def reset_new_week_gsheet():
    if not API_URL or "/exec" not in API_URL:
        return False, "Chưa điền link API_URL chuẩn"

    try:
        params = {"action": "reset_week", "_t": time.time()}
        res = requests.get(API_URL, params=params, timeout=15)
        if res.status_code == 200:
            res_json = res.json()
            if res_json.get("status") == "success":
                return True, "Đã khởi tạo tuần mới thành công!"
            else:
                return False, res_json.get("message", "Lỗi reset")
        return False, f"Lỗi kết nối HTTP: {res.status_code}"
    except Exception as e:
        return False, str(e)


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
        "🔐 BẠN LÀ AI?:",
        [
            "👑 Giáo viên chủ nhiệm",
            "Tổ trưởng Tổ 1",
            "Tổ trưởng Tổ 2",
            "Tổ trưởng Tổ 3",
            "Tổ trưởng Tổ 4",
        ],
    )
with col_btn:
    st.write("")
    st.write("")
    if st.button("🔄 Tải lại dữ liệu tươi"):
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
    [
        "📝 Ghi Nhận Thi Đua",
        "📊 Bảng Tổng Hợp Lớp",
        "📬 Tải File Báo Cáo",
        "⚙️ Quản Lý Tuần Học (Reset)",
    ],
)

if chuc_nang == "📝 Ghi Nhận Thi Đua":
    if not df_view.empty and "Họ và tên" in df_view.columns:
        student_list = df_view["Họ và tên"].dropna().tolist()
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
                    curr_score = pd.to_numeric(
                        df.at[idx, "Điểm thi đua"], errors="coerce"
                    )
                    if pd.isna(curr_score):
                        curr_score = 100
                    new_score = int(curr_score) + diem_thay_doi
                    xeploai_moi = tinh_xep_loai(new_score)

                    loi_clean = loi.split(" (")[0]
                    log_text = (
                        f"{loi_clean} x{so_lan}"
                        + (f" ({ghi_chu})" if ghi_chu else "")
                    )
                    old_log = str(df.at[idx, "Lỗi vi phạm"])

                    if old_log in ["None", "nan", "", "NaN"]:
                        full_log = log_text
                    else:
                        full_log = f"{old_log} | {log_text}"

                    with st.spinner("Đang lưu lên Google Sheet..."):
                        ok, msg = update_gsheet(
                            ten_hs, new_score, xeploai_moi, full_log
                        )

                    if ok:
                        st.success(
                            f"✅ Đã lưu thành công cho em {ten_hs}! Đang làm mới dữ liệu..."
                        )
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ LỖI: {msg}")
    else:
        st.warning("⚠️ Không tìm thấy dữ liệu học sinh!")

    st.dataframe(df_view, use_container_width=True, hide_index=True)

elif chuc_nang == "📊 Bảng Tổng Hợp Lớp":
    st.subheader("📊 BẢNG TỔNG HỢP THI ĐUA TOÀN LỚP")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif chuc_nang == "📬 Tải File Báo Cáo":
    st.subheader("📬 TẢI BÁO CÁO THI ĐUA")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="ThiDua")
    buffer.seek(0)
    st.download_button(
        label="📥 Tải xuống file Excel (.xlsx)",
        data=buffer,
        file_name="Bao_Cao_Thi_Dua.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

elif chuc_nang == "⚙️ Quản Lý Tuần Học (Reset)":
    st.subheader("⚙️ QUẢN LÝ VÀ CHUYỂN SANG TUẦN HỌC MỚI")
    st.warning(
        "⚠️ **LƯU Ý:** Trước khi chuyển sang tuần mới, Giáo viên vui lòng **Tải file Excel báo cáo tuần cũ** ở mục '📬 Tải File Báo Cáo' để lưu trữ!"
    )

    st.markdown("---")
    st.write(
        "Nút dưới đây sẽ **XÓA TOÀN BỘ LỖI VI PHẠM** và **RESET ĐIỂM SỐ VỀ 100** cho tất cả học sinh trong lớp trên Google Sheet."
    )

    confirm_check = st.checkbox(
        "Xác nhận: Tôi đã lưu file Excel tuần cũ và muốn sang tuần mới."
    )

    if st.button("🔄 CHUYỂN SANG TUẦN MỚI (RESET TOÀN BỘ LỚP)", type="primary"):
        if confirm_check:
            with st.spinner("Đang xóa dữ liệu tuần cũ trên Google Sheet..."):
                ok, msg = reset_new_week_gsheet()
            if ok:
                st.success(
                    "🎉 ĐÃ RESET SANG TUẦN MỚI THÀNH CÔNG! Toàn bộ học sinh đã được đưa về 100 điểm."
                )
                time.sleep(1.5)
                st.rerun()
            else:
                st.error(f"❌ Lỗi reset: {msg}")
        else:
            st.error(
                "Vui lòng tích vào ô 'Xác nhận' ở trên trước khi bấm Reset!"
            )

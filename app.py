import io
import os
import time
import pandas as pd
import requests
import streamlit as st

# ==============================================================================
# CẤU HÌNH TRANG & GIAO DIỆN CHUẨN CỔNG THÔNG TIN TRƯỜNG THCS CHÍ CÔNG
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
# BỘ CSS NÂNG CẤP GIAO DIỆN TOÀN DIỆN (SIDEBAR & NỘI DUNG)
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

        /* 1. NỀN & KHUNG SIDEBAR */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #edf2f7 100%) !important;
            border-right: 1px solid #e2e8f0;
            box-shadow: 3px 0 12px rgba(0,0,0,0.03);
        }
        
        /* 2. LOGO HEADER TRONG SIDEBAR */
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

        /* 3. MENU ĐIỀU HƯỚNG DẠNG THẺ (ẨN RADIO NÚT TRÒN) */
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

        /* 4. BANNER TRƯỜNG Ở PHẦN NỘI DUNG */
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

        /* 5. THẺ PROFILE HỌC SINH */
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

        /* 6. THẺ THỐNG KÊ */
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

        /* 7. NÚT BẤM & HỘP TRỐNG */
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
    "🚨 Nghỉ học không phép (-5)": -5

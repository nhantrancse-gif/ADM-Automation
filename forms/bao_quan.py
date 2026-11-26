import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
from io import BytesIO

def fix_location_spacing(doc):
    paragraphs = doc.paragraphs

    start = None
    end = None

    for i, p in enumerate(paragraphs):
        text = p.text.strip()

        if text == "- Địa điểm kho, bãi:":
            start = i

        elif start is not None and text.startswith(
            "11. Thời gian dự kiến bắt đầu vận chuyển"
            ):
            end = i
            break

    if start is None or end is None:
        return

    # Chỉ xóa paragraph rỗng trong khu vực danh sách kho
    for p in list(paragraphs[start + 1:end]):
        if not p.text.strip():
            p._element.getparent().remove(p._element)

def show():

    st.header("Mẫu CV bảo quản hàng")

    uploaded_file = st.file_uploader(
        "Upload Excel",
        type=["xlsx"],
        key="bao_quan"
    )

    if not uploaded_file:
        return

    # Đọc dữ liệu
    df = pd.read_excel(uploaded_file)

    # Khởi tạo Session State
    if "bao_quan_df" not in st.session_state:
        df.insert(0, "Chọn", False)
        st.session_state.bao_quan_df = df.copy()

    # Nếu upload file mới thì cập nhật lại dữ liệu
    current_rows = len(df)

    if len(st.session_state.bao_quan_df) != current_rows:
        df.insert(0, "Chọn", False)
        st.session_state.bao_quan_df = df.copy()

    # Nút thao tác
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            " Chọn tất cả",
            use_container_width=True
        ):
            st.session_state.bao_quan_df["Chọn"] = True
            st.rerun()

    with col2:
        if st.button(
            " Bỏ chọn tất cả",
            use_container_width=True
        ):
            st.session_state.bao_quan_df["Chọn"] = False
            st.rerun()

    # Hiển thị bảng
    edited_df = st.data_editor(
        st.session_state.bao_quan_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Chọn": st.column_config.CheckboxColumn(
                "Chọn"
            )
        },
        key="editor_bao_quan"
    )

    # Lưu thay đổi checkbox
    st.session_state.bao_quan_df = edited_df

    # Record được chọn
    selected_df = edited_df[
        edited_df["Chọn"] == True
    ]

    st.info(
        f"Đã chọn {len(selected_df)} / {len(edited_df)} dòng"
    )

    # Generate Word
    if st.button(
        "Generate",
        key="btn_bao_quan",
        type="primary"
    ):

        if selected_df.empty:
            st.warning(
                "Vui lòng chọn ít nhất 1 dòng"
            )
            st.stop()

        ds_dia_diem = []

        for _, row in selected_df.iterrows():

            ds_dia_diem.append(
                {
                    "ten": row["Tên Công ty/Kho"],
                    "dia_chi": row["Địa chỉ"]
                }
            )

        doc = DocxTemplate(
            "templates/ARG CV bảo quản hàng.docx"
        )

        context = {
            "DS_DIA_DIEM": ds_dia_diem
        }

        doc.render(context)
        # Chỉ fix khoảng cách danh sách địa điểm
        fix_location_spacing(doc)
        output = BytesIO()

        doc.save(output)

        output.seek(0)

        st.download_button(
            label="Download File",
            data=output,
            file_name="BaoQuan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
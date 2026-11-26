import streamlit as st
import pandas as pd

from docxtpl import DocxTemplate

import tempfile
import zipfile
import os

def clean_value(value):

    if pd.isna(value):
        return ""

    return str(value).strip()
def show():

    st.header(
        "Mẫu CV kiểm dịch ADM"
    )

    uploaded_file = st.file_uploader(
        "Upload Excel",
        type=["xlsx"],
        key="kiem_dich"
    )

    if not uploaded_file:
        return

    df = pd.read_excel(
        uploaded_file
    )

    st.dataframe(df.head())

    if st.button(
        "Generate",
        key="btn_kiem_dich"
    ):

        with tempfile.TemporaryDirectory() as temp_dir:

            generated_files = []

            for index, row in df.iterrows():

                doc = DocxTemplate(
                    "templates/Mẫu CV KIỂM DỊCH ADM.docx"
                )
                context = {
                    "SoCV": clean_value(row.get("SoCV")),
                    "KinhGui": clean_value(row.get("KinhGui")),
                    "DaiDien": clean_value(row.get("DaiDien")),
                    "ToKhai": clean_value(row.get("ToKhai")),
                    "NgayToKhai": clean_value(row.get("NgayToKhai")),
                    "PhanLuong": clean_value(row.get("PhanLuong")),
                    "ChiCuc": clean_value(row.get("ChiCuc")),
                    "Tau": clean_value(row.get("Tau")),
                    "VanDon": clean_value(row.get("VanDon")),
                    "NoiLuu": clean_value(row.get("NoiLuu")),
                    "TenHang": clean_value(row.get("TenHang")),
                    "TongCont": clean_value(row.get("TongCont")),
                    "ContThayDoi": clean_value(row.get("ContThayDoi")),
                    "NoiDungKhac": clean_value(row.get("NoiDungKhac"))
                }
                doc.render(context)

                filename = os.path.join(
                    temp_dir,
                    f"CV_{index}.docx"
                )

                doc.save(filename)

                generated_files.append(
                    filename
                )

            zip_path = os.path.join(
                temp_dir,
                "KiemDich.zip"
            )

            with zipfile.ZipFile(
                zip_path,
                "w"
            ) as zipf:

                for file in generated_files:

                    zipf.write(
                        file,
                        arcname=os.path.basename(file)
                    )

            with open(zip_path, "rb") as f:

                st.download_button(
                    "Download ZIP",
                    f,
                    file_name="KiemDich.zip"
                )
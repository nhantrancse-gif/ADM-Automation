import streamlit as st
import pandas as pd
import os
import zipfile
import tempfile

from docxtpl import DocxTemplate


# ==================================================
# CLEAN
# ==================================================

def clean_value(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


# ==================================================
# MAIN PAGE
# ==================================================

def show():

    st.header("Execution Follow-up")

    uploaded_file = st.file_uploader(
        "Upload Execution Follow-up",
        type=["xlsx"],
        key="execution_followup"
    )

    if not uploaded_file:
        return

    cargo_type = st.radio(
        "Select Cargo Type",
        ["Container", "Bulk"],
        horizontal=True
    )

    sheet_name = "CON" if cargo_type == "Container" else "BULK"

    try:

        # ==================================================
        # ĐỌC FILE
        # ==================================================

        df = pd.read_excel(
            uploaded_file,
            sheet_name=sheet_name,
            header=1
        )

        df = df.iloc[:, :40]
        df = df.fillna("")

    except Exception as e:

        st.error(str(e))
        return

    st.success(
        f"Loaded {len(df)} records from sheet [{sheet_name}]"
    )

    # ==================================================
    # KHỞI TẠO DATA CHỌN RECORD
    # ==================================================

    sheet_key = f"{sheet_name}_{len(df)}"

    if st.session_state.get("execution_sheet") != sheet_key:

        display_df = df.copy()

        if "Select" not in display_df.columns:
            display_df.insert(
                0,
                "Select",
                False
            )

        st.session_state.execution_df = display_df
        st.session_state.execution_sheet = sheet_key

    # ==================================================
    # BUTTON CHỌN TẤT CẢ / BỎ CHỌN
    # ==================================================

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            " Select All",
            use_container_width=True
        ):

            st.session_state.execution_df["Select"] = True
            st.rerun()

    with col2:

        if st.button(
            " Unselect All",
            use_container_width=True
        ):

            st.session_state.execution_df["Select"] = False
            st.rerun()

    # ==================================================
    # DATA EDITOR
    # ==================================================

    edited_df = st.data_editor(
        st.session_state.execution_df,
        width="stretch",
        hide_index=True,
        key="execution_editor"
    )

    st.session_state.execution_df = edited_df

    selected_df = edited_df[
        edited_df["Select"] == True
    ]

    st.info(
        f"Selected Records: {len(selected_df)} / {len(edited_df)}"
    )

    # ==================================================
    # GENERATE DOCUMENTS
    # ==================================================

    if st.button(
        "Generate Documents",
        type="primary"
    ):

        if len(selected_df) == 0:

            st.warning(
                "Please select at least 1 record."
            )

            return

        # ==================================================
        # TEMPLATE PATH
        # ==================================================

        BASE_DIR = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        template_file = os.path.join(
            BASE_DIR,
            "templates",
            "CV UQ DLy KDich ADM.docx"
        )

        if not os.path.exists(template_file):

            st.error(
                f"Template not found:\n{template_file}"
            )

            return

        # ==================================================
        # TẠO FILE
        # ==================================================

        with tempfile.TemporaryDirectory() as temp_dir:

            generated_files = []

            for _, row in selected_df.iterrows():

                doc = DocxTemplate(
                    template_file
                )

                context = {

                    "VesselName":
                        clean_value(
                            row.get(
                                "Vessel name",
                                ""
                            )
                        ),

                    "Origin":
                        clean_value(
                            row.get(
                                "Origin",
                                ""
                            )
                        )

                }

                doc.render(context)

                # ==================================================
                # FILE NAME
                # ==================================================

                file_name = clean_value(
                    row.get(
                        "Trade ID",
                        ""
                    )
                )

                if file_name == "":

                    file_name = clean_value(
                        row.get(
                            "Ctr no",
                            ""
                        )
                    )

                if file_name == "":

                    file_name = "Document"

                output_file = os.path.join(
                    temp_dir,
                    f"{file_name}.docx"
                )

                doc.save(output_file)

                generated_files.append(
                    output_file
                )

            # ==================================================
            # ZIP FILE
            # ==================================================

            zip_file = os.path.join(
                temp_dir,
                "Generated_Documents.zip"
            )

            with zipfile.ZipFile(
                zip_file,
                "w",
                zipfile.ZIP_DEFLATED
            ) as zipf:

                for file in generated_files:

                    zipf.write(
                        file,
                        arcname=os.path.basename(file)
                    )

            # ==================================================
            # DOWNLOAD
            # ==================================================

            with open(
                zip_file,
                "rb"
            ) as f:

                zip_bytes = f.read()

            st.download_button(
                label="Download ZIP",
                data=zip_bytes,
                file_name="Generated_Documents.zip",
                mime="application/zip"
            )

            st.success(
                f"Generated {len(generated_files)} documents."
            )


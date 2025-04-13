import streamlit as st
import tempfile
import os
from mergepdf import merge_pdfs  # assumes mergepdf.py is in the same folder

st.set_page_config(page_title="Merge Odd/Even PDFs")
st.title("🗂️ Merge Two PDF Files")

st.markdown("""
Upload two PDF files:
* The first containing **odd pages** (in normal order)
* The second containing **even pages** (in reverse order)
""")

# File uploaders
odd_file = st.file_uploader("Odd pages PDF", type="pdf")
even_file = st.file_uploader("Even pages PDF (reversed)", type="pdf")

output_name = st.text_input("Output file name", value="merged.pdf")

if st.button("Merge PDFs"):
    if not odd_file or not even_file:
        st.error("Please upload both PDF files.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save uploaded files temporarily
            path_odd = os.path.join(tmpdir, "odd.pdf")
            path_even = os.path.join(tmpdir, "even.pdf")
            output_path = os.path.join(tmpdir, output_name)

            with open(path_odd, "wb") as f:
                f.write(odd_file.read())
            with open(path_even, "wb") as f:
                f.write(even_file.read())

            # Call the merging function from mergepdf.py
            merge_pdfs(path_odd, path_even, output_path)

            # Download the merged PDF
            with open(output_path, "rb") as f:
                st.success("Merge completed!")
                st.download_button(
                    label="📥 Download merged PDF",
                    data=f,
                    file_name=output_name,
                    mime="application/pdf"
                )


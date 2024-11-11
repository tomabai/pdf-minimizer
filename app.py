import streamlit as st
import os
from minipdf import minimize_pdf


def main():
    st.title("המצמצם של חן")
    st.write("צמצי את הקבצים נשמה")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        # Save uploaded file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        if st.button("Minimize PDF"):
            with st.spinner("Minimizing PDF..."):
                try:
                    output_file = minimize_pdf(temp_path)

                    # Read the minimized file for download
                    with open(output_file, "rb") as f:
                        minimized_content = f.read()

                    # Create download button
                    st.download_button(
                        label="Download Minimized PDF",
                        data=minimized_content,
                        file_name=f"minimized_{uploaded_file.name}",
                        mime="application/pdf"
                    )

                    # Show file sizes
                    original_size = os.path.getsize(temp_path) / 1024
                    minimized_size = os.path.getsize(output_file) / 1024
                    st.write(f"Original size: {original_size:.2f} KB")
                    st.write(f"Minimized size: {minimized_size:.2f} KB")
                    st.write(
                        f"Reduction: {((original_size - minimized_size) / original_size * 100):.1f}%")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    # Cleanup
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    if os.path.exists(output_file):
                        os.remove(output_file)


if __name__ == "__main__":
    main()

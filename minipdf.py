import os
import sys
import io
import pikepdf
from PIL import Image


def minimize_pdf(input_file, max_size=1024 * 1024):  # 1 MB max
    """
    Minimize the size of a PDF file to a maximum of 1 MB.

    Args:
        input_file (str): Path to the input PDF file.
        max_size (int): Maximum size of the output file in bytes (default is 1 MB).
    """
    directory, filename = os.path.split(input_file)
    output_file = os.path.join(directory, f"minimized_{filename}")

    # First attempt with basic compression
    pdf = pikepdf.open(input_file)
    pdf.save(output_file,
             compress_streams=True,
             object_stream_mode=pikepdf.ObjectStreamMode.generate)

    if os.path.getsize(output_file) > max_size:
        # Try aggressive compression
        with pikepdf.open(input_file) as pdf:
            for page in pdf.pages:
                for name, raw_image in page.images.items():
                    pdfimage = pikepdf.PdfImage(raw_image)

                    with pdfimage.as_pil_image() as img:
                        # Reduce resolution by 50%
                        new_width = img.width // 2
                        new_height = img.height // 2
                        img = img.resize(
                            (new_width, new_height), Image.Resampling.LANCZOS)

                        # Convert to RGB and apply heavy compression
                        img = img.convert('RGB')
                        compressed = io.BytesIO()
                        img.save(compressed, format='JPEG',
                                 quality=15,  # Reduced from 30 to 15
                                 optimize=True)
                        compressed.seek(0)

                        new_image = pikepdf.Stream(pdf, compressed.getvalue())
                        raw_image.write(new_image.read_raw_bytes(),
                                        filter=pikepdf.Name('/DCTDecode'))

            pdf.save(output_file,
                     compress_streams=True,
                     object_stream_mode=pikepdf.ObjectStreamMode.generate)

    if os.path.getsize(output_file) > max_size:
        # If still too big, try extreme compression
        with pikepdf.open(input_file) as pdf:
            for page in pdf.pages:
                for name, raw_image in page.images.items():
                    pdfimage = pikepdf.PdfImage(raw_image)

                    with pdfimage.as_pil_image() as img:
                        # Reduce resolution by 75%
                        new_width = img.width // 4
                        new_height = img.height // 4
                        img = img.resize(
                            (new_width, new_height), Image.Resampling.LANCZOS)

                        img = img.convert('RGB')
                        compressed = io.BytesIO()
                        img.save(compressed, format='JPEG',
                                 quality=10,  # Even lower quality
                                 optimize=True)
                        compressed.seek(0)

                        new_image = pikepdf.Stream(pdf, compressed.getvalue())
                        raw_image.write(new_image.read_raw_bytes(),
                                        filter=pikepdf.Name('/DCTDecode'))

            pdf.save(output_file,
                     compress_streams=True,
                     object_stream_mode=pikepdf.ObjectStreamMode.generate)

    if os.path.getsize(output_file) > max_size:
        print("Warning: Could not reduce PDF below 1MB while maintaining readability")

    print(
        f"PDF file minimized to {os.path.getsize(output_file) / 1024:.2f} KB")
    return output_file


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python minipdf.py <filename>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found")
        sys.exit(1)

    minimize_pdf(input_file)

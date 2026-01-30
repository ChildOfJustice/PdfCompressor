import os
import sys
import argparse

try:
    import fitz
    # Verify this is PyMuPDF and not the other 'fitz' package
    if not hasattr(fitz, "open") or "PyMuPDF" not in getattr(fitz, "__doc__", ""):
        raise ImportError
except (ImportError, RuntimeError):
    # RuntimeError handles the case where the wrong fitz crashes on import (like in the user's case)
    print("Error: The 'fitz' module is not from PyMuPDF.")
    print("It seems you might have installed the wrong 'fitz' package.")
    print("Please run the following commands to fix it:")
    print("  pip uninstall fitz")
    print("  pip install pymupdf")
    sys.exit(1)

def compress_pdf(input_path, output_path, quality=30, max_dimension=2000):
    """
    Compresses a PDF file by re-compressing images and using PDF optimization flags.
    
    Args:
        input_path (str): Path to the input PDF file.
        output_path (str): Path to save the compressed PDF.
        quality (int): JPEG quality (1-100). Lower means smaller size.
        max_dimension (int): Max width or height for images. If an image is larger, it will be downscaled.
    """
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        return

    doc = fitz.open(input_path)
    
    # Process images for better compression
    processed_xrefs = set()
    total_pages = len(doc)
    
    for i, page in enumerate(doc):
        print(f"Processing page {i+1}/{total_pages}...", end="\r")
        image_list = page.get_images(full=True)
        for img in image_list:
            xref = img[0]
            if xref in processed_xrefs:
                continue
            
            # Extract image
            try:
                pix = fitz.Pixmap(doc, xref)
            except Exception as e:
                continue

            # If it's a CMYK or other special color space, convert to RGB
            if pix.colorspace.n > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            # Optional: Downscale if image is too large
            if max(pix.width, pix.height) > max_dimension:
                factor = max(pix.width, pix.height) // max_dimension
                if factor > 1:
                    pix.shrink(factor)

            # Re-compress as JPEG
            img_bytes = pix.tobytes("jpg", jpg_quality=quality)
            
            try:
                page.replace_image(xref, stream=img_bytes)
            except Exception as e:
                pass
            
            processed_xrefs.add(xref)
            pix = None # free memory
    
    print("\nSaving compressed PDF...")

    # Save with optimization flags
    # garbage=4: remove unused objects and duplicates
    # deflate=True: compress streams
    # clean=True: sanitize structure
    doc.save(output_path, 
             garbage=4, 
             deflate=True, 
             clean=True)
    doc.close()

    initial_size = os.path.getsize(input_path)
    final_size = os.path.getsize(output_path)
    
    print(f"Original size: {initial_size / 1024 / 1024:.2f} MB")
    print(f"Compressed size: {final_size / 1024 / 1024:.2f} MB")
    if initial_size > 0:
        print(f"Reduction: {(1 - final_size / initial_size) * 100:.1f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress PDF files by re-compressing images.")
    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("-o", "--output", help="Output PDF file path (optional)")
    parser.add_argument("-q", "--quality", type=int, default=30, help="JPEG quality (1-100), default 30")
    parser.add_argument("-m", "--max-dim", type=int, default=2000, help="Maximum dimension for images, default 2000")
    
    args = parser.parse_args()
    
    input_pdf = args.input
    output_pdf = args.output
    
    if not output_pdf:
        name, ext = os.path.splitext(input_pdf)
        output_pdf = f"{name}_compressed{ext}"
    
    compress_pdf(input_pdf, output_pdf, quality=args.quality, max_dimension=args.max_dim)

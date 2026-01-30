### Key Features:
- **Image Re-compression**: Automatically converts images within the PDF to JPEG format with adjustable quality (default is 30, which provides high compression with acceptable visual quality).
- **Downscaling**: If images are larger than a specified maximum dimension (default 2000px), they are automatically downscaled to save space.
- **PDF Optimization**: Uses advanced `PyMuPDF` saving flags (`garbage=4`, `deflate=True`) to remove duplicate objects and compress internal streams.

### Prerequisites:
The script requires the `pymupdf` library. You can install it using:
```bash
pip install pymupdf
```

### Usage:
Run the script from your terminal:
```bash
python3 compress_pdf.py input.pdf
```
This will create a compressed file named `input_compressed.pdf`.

#### Advanced Options:
- `-o OUTPUT`: Specify a custom output filename.
- `-q QUALITY`: Set JPEG quality from 1 to 100 (default: 30).
- `-m MAX_DIM`: Set the maximum dimension for images in pixels (default: 2000).

Example with custom settings:
```bash
python3 compress_pdf.py my_large_file.pdf -o small.pdf -q 50 -m 1500
```
# PDF to Beamer Slides with AWS Bedrock

This repository contains a Python application built using Streamlit that processes PDF files by splitting them into groups of pages, extracting text, and generating Japanese Beamer (LaTeX) slides using AWS Bedrock.

## Features
- **PDF Upload:** Upload a PDF file through the Streamlit interface.
- **PDF Splitting:** Split the uploaded PDF into smaller groups of pages (default: 4 pages per group).
- **Text Extraction:** Extract text from the grouped PDF pages.
- **LaTeX Beamer Slide Generation:** Convert the extracted text into Japanese Beamer slides using AWS Bedrock's Mistral model.
- **Output:** Save the generated slides to a `Output.tex` file for further use.

---

## Prerequisites
### Software Requirements
- Python 3.8 or higher
- AWS Account with Bedrock access

### Python Libraries
Install the required dependencies using the following command:
```bash
pip install -r requirements.txt
```
**Dependencies**:
- `streamlit`
- `boto3`
- `PyPDF2`

---

## Setup
### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### Step 2: Configure AWS Bedrock Credentials
Edit the following variables in the script:
```python
REGION = "<YOUR_AWS_REGION>"
AWS_ACCESS="<YOUR_AWS_ACCESS_KEY>"
AWS_SECRET="<YOUR_AWS_SECRET_KEY>"
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Usage
1. **Run the Streamlit Application:**
   ```bash
   streamlit run app.py
   ```
2. **Upload a PDF:**
   - Use the file uploader in the Streamlit UI to upload a PDF file.
3. **Process the File:**
   - Click the button to start processing. The app will split the PDF, extract text, and generate Beamer slides.
4. **Download the Results:**
   - Processed files and the `Output.tex` file containing the LaTeX slides are saved in the output folder.

---

## File Structure
```
project-folder/
|-- app.py                # Main application file
|-- requirements.txt      # Python dependencies
|-- uploads/              # Folder for uploaded PDF files
|-- output/               # Folder for output files (PDFs, text, LaTeX)
```

---

## Example Output
A typical slide generated in LaTeX Beamer format:
```latex
\begin{frame}{Key Concept or Main Point}
  \textbf{Explanation or key message. Use abbreviations for recurring terms.}
  \begin{block}{Detailed Explanation}
    \begin{itemize}
      \item Concise explanation in three bullet points.
      \item Each point within 40 characters.
      \item Aim for brevity and clarity.
    \end{itemize}
  \end{block}
\end{frame}
```

---

## Troubleshooting
1. **AWS Bedrock Errors:** Ensure your AWS credentials and Bedrock model permissions are correctly configured.
2. **PDF Issues:** Ensure the uploaded file is a valid PDF with extractable text.
3. **Missing LaTeX Tags:** The script auto-completes incomplete LaTeX slides, but review the `Output.tex` file for correctness.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contributing
Feel free to submit issues or pull requests for improvements or additional features.



# Nimendra Dilshan - CV & Resume

This repository contains the LaTeX source code for my Curriculum Vitae, Résumé, and Cover Letter, built using the [Awesome CV](https://github.com/posquit0/Awesome-CV) template.

## Built With
- **LaTeX** (XeLaTeX)
- **Awesome CV** template

## Documents
- `cv.pdf`: Full Curriculum Vitae (**Turquoise Theme**)
- `resume.pdf`: One-page Résumé (**Midnight Blue Theme**)
- `coverletter.pdf`: Cover Letter for DevOps/SRE roles
- `resume-ats.pdf`: Full resume content in a simple, single-column layout; multiple pages are allowed.
- `resume-ats-onepage.pdf`: One-page A4 DevOps/SRE resume with selected infrastructure projects and condensed content.

## Features
- **Modern Icons**: Support for X (formerly Twitter) and WhatsApp.
- **Custom Themes**: Integrated 10+ professional "Awesome colors" from the latest upstream.
- **Automated CI/CD**: PDF compilation and releases via GitHub Actions.
- **WSO2 Internship**: Latest work experience at WSO2 LLC.

### Prerequisites
A full TeX distribution (e.g., TeX Live) is required.

### Compilation
You can compile the documents using the provided `Makefile`:

```bash
# Compile all documents
make

# Compile specific documents
make cv.pdf
make resume.pdf
make coverletter.pdf
make resume-ats.pdf
make resume-ats-onepage.pdf

# Build and check PDF text extraction, fonts, and page count
make check-resume-ats
make check-resume-ats-onepage

# Run the checker unit tests without a TeX installation
python3 -m unittest discover -s tests -p 'test_check_resume_ats.py'

# Clean auxiliary files
make clean
```

## ATS-focused resumes

Both ATS versions use `src/ats-layout.tex`, with 11 pt body text, 15 mm margins,
visible contact URLs, ordinary paragraphs and lists, and no tables, icons, or
running footer. The original Awesome CV documents remain unchanged.

- The full version imports all six original `src/resume/*.tex` content files.
- The one-page version uses `src/resume-onepage/content.tex`. It keeps the WSO2
  internship, education, Terraform/KinD and homelab projects, selected skills,
  and two courses. Update its retained facts explicitly when the original
  content changes. Do not shrink the text to force additional content onto one page.

PDF checks require **Python 3** and Poppler commands **`pdftotext`, `pdffonts`,
`pdfinfo`**. Visual inspection also uses **`pdftoppm`**. The checker tests default
and layout-preserving text extraction, expected content and section order,
font embedding, Unicode mappings, and exactly one A4 page for the condensed
version. Missing tools or failed checks produce a nonzero exit status.

The new documents can also be compiled with Tectonic, without Font Awesome:

```bash
(cd src && tectonic -X compile resume-ats.tex --keep-logs -p)
(cd src && tectonic -X compile resume-ats-onepage.tex --keep-logs -p)
python3 tests/check_resume_ats.py src/resume-ats.pdf --variant full
python3 tests/check_resume_ats.py src/resume-ats-onepage.pdf --variant onepage
```

Keep build logs and visually inspect each page after content changes. These local
checks do not upload personal data and do not guarantee compatibility with every
ATS. A successful extraction check does not replace visual review.

## GitHub Actions
This repository uses GitHub Actions to automatically compile and release the PDFs on every push or tag.

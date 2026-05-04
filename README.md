# Nimendra Dilshan - CV & Resume

This repository contains the LaTeX source code for my Curriculum Vitae, Résumé, and Cover Letter, built using the [Awesome CV](https://github.com/posquit0/Awesome-CV) template.

## Built With
- **LaTeX** (XeLaTeX)
- **Awesome CV** template

## Documents
- `cv.pdf`: Full Curriculum Vitae (**Turquoise Theme**)
- `resume.pdf`: One-page Résumé (**Midnight Blue Theme**)
- `coverletter.pdf`: Cover Letter for DevOps/SRE roles

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

# Clean auxiliary files
make clean
```

## GitHub Actions
This repository uses GitHub Actions to automatically compile and release the PDFs on every push or tag.

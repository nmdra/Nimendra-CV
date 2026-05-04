# Nimendra Dilshan - CV & Resume

This repository contains the LaTeX source code for my Curriculum Vitae, Résumé, and Cover Letter, built using the [Awesome CV](https://github.com/posquit0/Awesome-CV) template.

## Built With
- **LaTeX** (XeLaTeX)
- **Awesome CV** template

## Documents
- `cv.pdf`: Full Curriculum Vitae
- `resume.pdf`: One-page Résumé
- `coverletter.pdf`: Cover Letter for DevOps/SRE roles

## Build Instructions

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

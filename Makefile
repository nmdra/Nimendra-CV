.PHONY: all resume.pdf resume-ats.pdf resume-ats-onepage.pdf cv.pdf coverletter.pdf check-resume-ats check-resume-ats-onepage clean help

# Configuration
CC = xelatex
PYTHON = python3
EXAMPLES_DIR = src
RESUME_DIR = $(EXAMPLES_DIR)/resume
CV_DIR = $(EXAMPLES_DIR)/cv
OUTPUT_DIR = .

# Source files
RESUME_SRCS = $(shell find $(RESUME_DIR) -name '*.tex')
CV_SRCS = $(shell find $(CV_DIR) -name '*.tex')

# Default target
all: resume.pdf cv.pdf coverletter.pdf resume-ats.pdf resume-ats-onepage.pdf

# Targets
resume.pdf: $(EXAMPLES_DIR)/resume.tex $(RESUME_SRCS)
	@echo "Compiling Resume..."
	$(CC) -output-directory=$(EXAMPLES_DIR) $<
	@mv $(EXAMPLES_DIR)/$@ $(OUTPUT_DIR)/$@
	@echo "Resume compiled successfully!"

resume-ats.pdf: $(EXAMPLES_DIR)/resume-ats.tex $(EXAMPLES_DIR)/ats-layout.tex $(RESUME_SRCS)
	@echo "Compiling Full ATS Resume..."
	cd $(EXAMPLES_DIR) && $(CC) -interaction=nonstopmode -halt-on-error $(notdir $<)
	@mv $(EXAMPLES_DIR)/$@ $(OUTPUT_DIR)/$@

resume-ats-onepage.pdf: $(EXAMPLES_DIR)/resume-ats-onepage.tex $(EXAMPLES_DIR)/ats-layout.tex $(EXAMPLES_DIR)/resume-onepage/content.tex
	@echo "Compiling One-Page ATS Resume..."
	cd $(EXAMPLES_DIR) && $(CC) -interaction=nonstopmode -halt-on-error $(notdir $<)
	@mv $(EXAMPLES_DIR)/$@ $(OUTPUT_DIR)/$@

check-resume-ats: resume-ats.pdf resume-ats-onepage.pdf
	$(PYTHON) tests/check_resume_ats.py "$(OUTPUT_DIR)/resume-ats.pdf" --variant full
	$(PYTHON) tests/check_resume_ats.py "$(OUTPUT_DIR)/resume-ats-onepage.pdf" --variant onepage

check-resume-ats-onepage: resume-ats-onepage.pdf
	$(PYTHON) tests/check_resume_ats.py "$(OUTPUT_DIR)/resume-ats-onepage.pdf" --variant onepage

cv.pdf: $(EXAMPLES_DIR)/cv.tex $(CV_SRCS)
	@echo "Compiling CV..."
	$(CC) -output-directory=$(EXAMPLES_DIR) $<
	@mv $(EXAMPLES_DIR)/$@ $(OUTPUT_DIR)/$@
	@echo "CV compiled successfully!"

coverletter.pdf: $(EXAMPLES_DIR)/coverletter.tex
	@echo "Compiling Cover Letter..."
	$(CC) -output-directory=$(EXAMPLES_DIR) $<
	@mv $(EXAMPLES_DIR)/$@ $(OUTPUT_DIR)/$@
	@echo "Cover Letter compiled successfully!"

clean:
	@echo "Cleaning up..."
	rm -f *.pdf
	rm -f $(EXAMPLES_DIR)/*.pdf $(EXAMPLES_DIR)/*.aux $(EXAMPLES_DIR)/*.log $(EXAMPLES_DIR)/*.out
	@echo "Clean up complete."

help:
	@echo "Available targets:"
	@echo "  all          : Build all PDFs (default)"
	@echo "  resume.pdf   : Build resume.pdf"
	@echo "  resume-ats.pdf : Build the full ATS resume"
	@echo "  resume-ats-onepage.pdf : Build the one-page ATS resume"
	@echo "  check-resume-ats : Build and validate both ATS resumes"
	@echo "  check-resume-ats-onepage : Build and validate the one-page ATS resume"
	@echo "  cv.pdf       : Build cv.pdf"
	@echo "  coverletter.pdf : Build coverletter.pdf"
	@echo "  clean        : Remove generated files"
	@echo "  help         : Show this help message"

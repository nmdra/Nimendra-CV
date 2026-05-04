.PHONY: all resume.pdf cv.pdf coverletter.pdf clean help

# Configuration
CC = xelatex
EXAMPLES_DIR = src
RESUME_DIR = $(EXAMPLES_DIR)/resume
CV_DIR = $(EXAMPLES_DIR)/cv
OUTPUT_DIR = .

# Source files
RESUME_SRCS = $(shell find $(RESUME_DIR) -name '*.tex')
CV_SRCS = $(shell find $(CV_DIR) -name '*.tex')

# Default target
all: resume.pdf cv.pdf coverletter.pdf

# Targets
resume.pdf: $(EXAMPLES_DIR)/resume.tex $(RESUME_SRCS)
	@echo "Compiling Resume..."
	$(CC) -output-directory=$(EXAMPLES_DIR) $<
	@mv $(EXAMPLES_DIR)/$@ $(OUTPUT_DIR)/$@
	@echo "Resume compiled successfully!"

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
	@echo "  cv.pdf       : Build cv.pdf"
	@echo "  coverletter.pdf : Build coverletter.pdf"
	@echo "  clean        : Remove generated files"
	@echo "  help         : Show this help message"

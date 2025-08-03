.PHONY: examples

CC = xelatex
EXAMPLES_DIR = src
RESUME_DIR = src/resume
CV_DIR = src/cv
COVERLETTER_DIR = src/coverletter

COVERLETTER_SRCS = $(shell find $(COVERLETTER_DIR) -name '*.tex')
RESUME_SRCS = $(shell find $(RESUME_DIR) -name '*.tex')
CV_SRCS = $(shell find $(CV_DIR) -name '*.tex')

examples: $(foreach x, resume coverletter cv, $x.pdf)

resume.pdf: $(EXAMPLES_DIR)/resume.tex $(RESUME_SRCS)
	$(CC) -output-directory=$(EXAMPLES_DIR) $<

cv.pdf: $(EXAMPLES_DIR)/cv.tex $(CV_SRCS)
	$(CC) -output-directory=$(EXAMPLES_DIR) $<

coverletter.pdf: $(EXAMPLES_DIR)/coverletter.tex $(COVERLETTER_SRCS)
	$(CC) -output-directory=$(EXAMPLES_DIR) $

clean:
	rm -rf $(EXAMPLES_DIR)/*.pdf

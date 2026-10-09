# Plan: Full and one-page ATS-focused resumes

## Goal

Add `resume-ats.pdf` with the complete existing content and `resume-ats-onepage.pdf` with a shortened DevOps-focused selection. Both use a simple, single-column layout and verifiable PDF text extraction. Preserve the current `resume.pdf`, `cv.pdf`, and `coverletter.pdf`. Change no facts or measurements.

Status: implemented after user approval. Local ATS checks passed; actual XeLaTeX and the full legacy CI build remain unverified because the local environment lacks XeLaTeX.

## Current State

Evidence below was captured before implementation.

- `src/resume.tex:22` uses Awesome CV. It imports six shared content files at `src/resume.tex:100–105`.
- Entry formatting uses a two-column table for organization/location and role/date (`awesome-cv.cls:706–719`). Courses and skills also use tables (`awesome-cv.cls:746–779`). These are parsing risks, not confirmed failures.
- The contact block uses visible profile handles with icon labels rather than visible URLs (`awesome-cv.cls:543–546,567–570`; values at `src/resume.tex:62–66`). It is in the document body, not a running page header (`src/resume.tex:82–86`; `awesome-cv.cls:493–502`).
- Contact text is 6.8 pt, role/date text is 8 pt, and body text is 9 pt (`awesome-cv.cls:193,202–205`).
- The current footer repeats a generated date, name, and page number (`src/resume.tex:90–93`).
- Shared project content includes `\faGithub` inside hyperlink labels (`src/resume/projects.tex:7`, with the same pattern in other entries).
- `Makefile:15–34` builds three outputs with XeLaTeX. Both GitHub workflows run `make` and upload root-level `*.pdf` (`.github/workflows/Compile-pdf.yml:15–21`; `.github/workflows/Release-pdf.yml:19–33`). An additional default output will be included automatically.
- Local Tectonic compilation of a temporary copy failed because `fontawesome6.sty` is missing. No PDF extraction or font checks have passed. The new standalone layout must not require Font Awesome.
- Greenhouse identifies tables, columns, and complex headers/footers as possible parsing problems: https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse . This is vendor-specific evidence, not a universal ATS guarantee.

## Decisions

1. Add two separate ATS outputs, as selected by the user: a full version and an additional one-page version. Do not replace the current styled resume or modify the shared Awesome CV class.
2. Use an independent `article`-based root document with normal paragraphs and lists. Reusing Awesome CV with local table overrides was rejected because it retains unnecessary icon dependencies and decorative styles.
3. Share layout macros through `src/ats-layout.tex`. The full version imports all six existing content files unchanged. The one-page version uses a separate, deliberately curated content file. This avoids conditional changes in the original resume inputs; its condensed wording must be checked against the original facts.
4. Preserve all content and section order in the full version. For the one-page version, the user authorized DevOps-focused cuts and shorter wording. Preserve internship and education, select two infrastructure projects, shorten the summary and course list, and compress skills. Do not add facts, metrics, or claims of passed certification exams.
5. Use black regular-weight body text at 10 pt or larger, with readable leading and at least 15 mm margins. The full version may span multiple pages. The condensed version must be exactly one A4 page. Cut wording before tightening spacing; never use whole-page scaling, hidden overflow, or smaller text to meet the limit.
6. Show contact details and full profile URL text in ordinary body paragraphs. Keep the currently included X profile as a visible URL to avoid an unrequested content cut. Remove decorative icons and all running footer content from the ATS output.
7. Validate extracted text and font mappings with local tools. Do not upload personal resume data to external ATS scoring services. Passing these checks does not certify compatibility with every ATS.

## Scope

In scope: shared ATS layout, full and one-page outputs, DevOps-focused selection and shortening for the one-page output only, visible contact URLs, readable typography, build integration, extraction regression checks, font checks, page-count checks, and PDF visual inspection.

Out of scope: changes to existing outputs or shared resume wording, new facts or metrics, credential verification, a general content rewrite, new infrastructure providers, installing local dependencies without permission, and commercial ATS scoring.

## Tasks

- [x] **1. Implement the standalone layout and compatibility layer.**
  - **Files:** new `src/resume-ats.tex` and `src/ats-layout.tex`.
  - Put reusable layout macros and packages in `src/ats-layout.tex`; keep document identity, imports, and document boundaries in each root. Both roots must work with the existing Makefile convention and compilation from `src/`.
  - Use `article`, `fontspec` with the standard Latin Modern Roman font, `geometry`, `enumitem`, `hyperref`, and `needspace`. Avoid tables, minipages, text boxes, Font Awesome, and `fancyhdr`.
  - Define `\cvsection`, `cvparagraph`, `cventries`, `\cventry` with five arguments, `cvitems`, `cvhonors`, `\cvhonor` with four arguments, `cvskills`, and `\cvskill` with two arguments. Preserve their current argument contracts so shared files require no edits.
  - Render each entry as organization/project title, role/description, location and dates, then its bullets in normal document order. Use plain text separators, never right-aligned date columns. Let paragraphs and long bullets wrap normally. Keep entry headings with the first body line without boxing the whole entry.
  - Render course name, issuer, optional location, and date as a linear paragraph. Render each skill category and its list as a linear paragraph.
  - Define `\faGithub` as empty in the shared ATS layout only to suppress decoration in shared project labels. Keep all hyperlinks and wording intact.
  - Use native text bullets, left alignment, empty page style, and PDF title/author metadata. Print name, current subtitle/location, phone, email, and visible `github.com/nmdra`, `linkedin.com/in/nimendra`, and `x.com/nimendra_` links in body text. Ensure underscores display correctly and link destinations contain a literal underscore.
  - Import the same six files in the same order as `src/resume.tex:100–105`.
  - **Seam:** existing content macros invoked by the six shared input files.
  - **Verify:** compile from `src/` using `tectonic -X compile resume-ats.tex --keep-logs -p`; confirm no icon package is requested. Inspect the final log for errors, missing glyphs, and overfull boxes. If required dependencies are unavailable, report the blocker and ask before installation.

- [x] **2. Create the additional one-page DevOps-focused resume.**
  - **Files:** new `src/resume-ats-onepage.tex` and `src/resume-onepage/content.tex`; shared `src/ats-layout.tex` only if compact spacing needs a supported option.
  - Use the same identity, visible contact links, font, margins, and table-free macros as the full version. Use A4 and 10 pt or larger body text. Do not modify original input files.
  - Order sections as Summary, Work Experience, Education, Projects, Skills, Courses and Certifications. Limit the summary to two rendered lines, based only on the internship and infrastructure experience already stated.
  - Keep WSO2 role, organization, location, and dates. Use three concise bullets covering the incident/alert integrations, PagerDuty-to-ServiceNow migration, and automated incident creation. Remove generic learning language and unmeasured outcome adjectives rather than introducing numbers.
  - Keep SLIIT degree, institution, expected graduation, and GPA exactly as supplied. Do not assume a GPA scale.
  - Select exactly two project entries: KinD-Cluster-Terraform and SRE Homelab & Learning Projects. Give each at most two concise bullets. Prioritize Terraform provisioning, local networking, and the existing Kubernetes/Ansible lab work; retain relevant existing links. Omit application projects from this output only.
  - Use two compact skill paragraphs: DevOps & Cloud, and Backend & Data. Select tools already listed in the original content; omit frontend skills from this output only.
  - Include the CKA preparation course and Ansible Advanced course as compact course-completion entries with their existing KodeKloud links and year. Label CKA explicitly as a course, not an earned professional certification. Omit KCNA and Bash training from this output only.
  - Compile and iterate on wording, then section/list spacing if needed. If this bounded content cannot fit at the font/margin limits, stop and ask which additional content to remove instead of violating readability limits.
  - **Seam:** shared ATS macros and curated content derived from existing resume files.
  - **Verify:** `tectonic -X compile resume-ats-onepage.tex --keep-logs -p` from `src/`; `pdfinfo` reports exactly one A4 page; inspect at 150 DPI and compare every retained fact with the original sources.

- [x] **3. Add extraction regression checks.**
  - **Files:** new `tests/check_resume_ats.py` and `tests/test_check_resume_ats.py`; `.gitignore` for generated Python bytecode.
  - Accept the PDF path plus `--variant full|onepage` as command-line arguments. Invoke `pdftotext` in default and `-layout` modes, `pdffonts`, and `pdfinfo`. Fail clearly if the PDF or a required command is missing. Require exactly one A4 page for the one-page variant, with no page-count limit for the full variant.
  - Normalize whitespace and Unicode compatibility ligatures without discarding meaningful characters. In both extraction modes, check name, email, normalized phone number, visible profile URLs, headings in the variant's specified order, and employer/role/date association within Work Experience. The full variant checks all six project titles, four course titles, and three skill categories; the one-page variant checks the two selected projects, two course entries, and two skill categories with representative skills. Check expected education facts in both.
  - Reject replacement characters and private-use icon characters. Check that all listed fonts are embedded and textual fonts have Unicode mappings. Treat these checks as a PDF regression gate, not an ATS score.
  - Expose text-validation and font-report-validation functions so standard-library unit tests can use synthetic strings. Test both variants, missing contact data, reordered headings, a role/date in the wrong section, icon noise, unembedded or unmapped fonts, and one-page rejection of a two-page PDF report. Test that valid full-version multi-page metadata is accepted.
  - **Seam:** generated PDF text layer and font report; synthetic fixtures for the validation functions.
  - **Verify:** `python3 -m unittest discover -s tests -p 'test_check_resume_ats.py'`; then `python3 tests/check_resume_ats.py resume-ats.pdf --variant full` and `python3 tests/check_resume_ats.py resume-ats-onepage.pdf --variant onepage` against the real compiled outputs.

- [x] **4. Integrate the additional build and check targets.**
  - **Files:** `Makefile`.
  - Add both ATS PDFs to `all`. The full target depends on `src/resume-ats.tex`, `src/ats-layout.tex`, and `RESUME_SRCS`. The one-page target depends on `src/resume-ats-onepage.tex`, `src/ats-layout.tex`, and `src/resume-onepage/content.tex`.
  - Add `check-resume-ats` to build and validate both outputs with the correct checker variant. Add `check-resume-ats-onepage` to build and validate only the condensed output.
  - Use the existing XeLaTeX build convention for the new target, with noninteractive fail-on-error flags. Leave existing recipes unchanged. Update `.PHONY` and help output. Existing cleanup patterns already cover the new PDF and auxiliary files.
  - Do not modify workflows unless a verified build integration problem requires it. Their `make` invocation and PDF globs already include the new output.
  - **Seam:** existing Makefile targets and workflow artifact discovery.
  - **Verify:** `make -n resume-ats.pdf resume-ats-onepage.pdf check-resume-ats check-resume-ats-onepage`; in an environment with XeLaTeX, `make resume-ats.pdf resume-ats-onepage.pdf` and `make check-resume-ats`. Verify the three existing targets remain unchanged. Run the existing full `make` build in the configured TeX Live CI environment; report local dependency blockers separately.

- [x] **5. Document usage and complete PDF acceptance checks.**
  - **Files:** `README.md`; temporary QA outputs outside the repository.
  - Document both ATS PDFs, their full versus condensed content policy, shared layout, `make resume-ats.pdf`, `make resume-ats-onepage.pdf`, `make check-resume-ats`, and `make check-resume-ats-onepage`. Explain that the curated content must be updated explicitly when source facts change. List Python 3 and Poppler tools as prerequisites for checks. Explain that extraction success is not universal ATS certification.
  - Compile both final ATS PDFs with retained logs. Run the variant-specific extraction checker and `pdfinfo`, then render every page of both outputs with `pdftoppm` at 150 DPI. Inspect contact wrapping, entry/date association, section breaks, bullet wrapping, margins, and any blank or nearly empty pages.
  - Compare all factual content against the existing input files. Confirm the current template and shared inputs are unchanged in `git diff`.
  - **Seam:** documented build commands and final PDF artifact.
  - **Verify:** checker passes in both extraction modes; every page is visually inspected; final log has no errors, missing glyphs, or unresolved overfull content; no unreadable small text or clipped content. Record the PDF page count, compiler, commands, and remaining limitations.

## Verification

- Both extraction modes preserve contact data, section order, entry associations, project/course titles, and skills.
- All PDF fonts are embedded; text fonts have Unicode mappings; no icon or replacement-character noise remains.
- The ATS document has no tables, sidebars, running headers/footers, or decorative icon dependencies.
- All pages of both outputs are visually reviewed. The full version permits multiple pages. The one-page version is exactly one A4 page, with body text at least 10 pt, margins at least 15 mm, and no scaling, clipping, or hidden overflow.
- The condensed version retains the selected internship, education, two projects, two skill categories, and two courses. Every retained fact traces to the original content; no fabricated metrics or credentials are introduced.
- The original resume, CV, cover letter, class, and shared content files remain unchanged.
- Run pi-lens delta diagnostics after implementation edits and targeted active diagnostics for supported changed code. Report unavailable analyzer coverage. Full PDF compilation and extraction checks are the primary document checks.
- No remote ATS service receives the resume. No claim of universal ATS compatibility is made.

## Implementation Evidence

- Final artifacts: root-level `resume-ats.pdf` (2 A4 pages) and `resume-ats-onepage.pdf` (1 A4 page). Both use 11 pt body text and 15 mm margins.
- Tectonic 0.17.0 compiled both roots successfully. Latin Modern Roman is resolved by its bundled OTF file names, not an installed family name. No additional local package installation was needed.
- `python3 -m unittest discover -s tests -p 'test_check_resume_ats.py'`: 26 tests passed, including complete education dates and per-course issuer/year regressions added after independent review.
- Both real PDFs passed `tests/check_resume_ats.py` with their respective variants in default and layout-preserving text modes. Both font reports show embedded Unicode-mapped Latin Modern fonts.
- `make -n` validated new target commands. `make check-resume-ats` with a temporary Tectonic compiler adapter passed in both the default output directory and an overridden temporary `OUTPUT_DIR`. The adapter tests Makefile execution and output movement, not XeLaTeX itself. New recipes compile from `src/` to resolve shared inputs reliably; existing recipes are unchanged.
- The PDF QA pipeline passed for both documents. Final TeX logs contain no errors, overfull boxes, unresolved references, or missing glyphs. All three final pages were rendered at 150 DPI and visually inspected. No clipped or overlapping content was found; the condensed summary occupies two lines.
- `git diff --check` passed. Original class, document roots, shared resume/CV inputs, and workflows are unchanged.
- Active targeted LSP checks: both Python files clean. LaTeX and Makefile have no configured LSP coverage; compiler, PDF, and Makefile checks provide their acceptance evidence. The later workspace scan reported existing workflow security findings and duplicate-content warnings, including intentional shared imports/header calls in the new roots. These do not establish PDF failures and were left outside scope.
- Independent review and follow-up found no remaining blockers after the date/course checks and `OUTPUT_DIR` fixes. Profile link annotations were inspected with `pdfinfo -url`; the X destination retains its literal underscore.
- QA logs, reports, renders, and the temporary compiler adapter are under `/tmp/nimendra-ats-implementation/`, outside the repository.

## Remaining Verification Limits

- Actual XeLaTeX compilation and the complete existing TeX Live CI build were not run locally. XeLaTeX is absent, and the existing Awesome CV document also needs Font Awesome 6. No dependencies were installed and no remote workflow was triggered.
- PDF extraction checks are not universal ATS certification.
- Implementation acceptance was completed before the commit and push requested afterward.

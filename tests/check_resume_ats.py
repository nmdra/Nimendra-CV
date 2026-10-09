#!/usr/bin/env python3
"""Local PDF text regression gate, not an ATS compatibility score.

Requires Poppler's pdftotext, pdffonts, and pdfinfo. Validation functions return
lists of actionable errors and can be used without Poppler or a PDF.
"""

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unicodedata


HEADINGS = {
    "full": ("Summary", "Work Experience", "Education", "Projects",
             "Courses and Certifications", "Skills"),
    "onepage": ("Summary", "Work Experience", "Education", "Projects",
                "Skills", "Courses and Certifications"),
}
PROJECTS = {
    "full": ("CraveDrop", "Semantic-Search", "KinD-Cluster-Terraform",
             "FarmCart", "Snipbox", "SRE Homelab & Learning Projects"),
    "onepage": ("KinD-Cluster-Terraform", "SRE Homelab & Learning Projects"),
}
COURSES = {
    "full": ("CKA Certification Course - Certified Kubernetes Administrator",
             "Ansible Advanced Course", "Kubernetes and Cloud-Native Associate (KCNA)",
             "Advanced Bash Scripting"),
    "onepage": ("CKA Exam Preparation Course", "Ansible Advanced Course"),
}
SKILLS = {
    "full": (("Back-end", ("Go", "PostgreSQL")),
             ("Front-end", ("React", "JavaScript")),
             ("DevOps & Cloud", ("Kubernetes", "Terraform", "Ansible"))),
    "onepage": (("DevOps & Cloud", ("Kubernetes", "Terraform", "Ansible")),
                ("Backend & Data", ("Go", "PostgreSQL"))),
}


def normalize_text(text):
    """Fold compatibility ligatures and whitespace, not punctuation or digits."""
    return " ".join(unicodedata.normalize("NFKC", text).split())


def _variant(variant):
    if variant not in HEADINGS:
        raise ValueError("variant must be full or onepage")


def _ordered(text, anchors, label, errors):
    cursor = 0
    for anchor in anchors:
        position = text.find(anchor, cursor)
        if position < 0:
            errors.append(f"{label}: missing or out-of-order text: {anchor}")
        else:
            cursor = position + len(anchor)


def validate_text(text, variant):
    """Check contact data and section-scoped anchors in one extraction mode."""
    _variant(variant)
    errors = []
    if "\ufffd" in text:
        errors.append("Text contains Unicode replacement characters (U+FFFD)")
    if any(unicodedata.category(char) == "Co" for char in text):
        errors.append("Text contains private-use characters, possibly icon glyphs")
    raw_text = unicodedata.normalize("NFKC", text)
    text = normalize_text(text)
    for anchor in ("Nimendra Dilshan", "nimendradharmasiri@gmail.com",
                   "github.com/nmdra", "linkedin.com/in/nimendra", "x.com/nimendra_"):
        if anchor not in text:
            errors.append(f"Contact: missing {anchor}")
    # Match just the contact number. Never strip non-digits from the document:
    # doing so can join unrelated dates or numbers into a false phone match.
    phone = r"(?<![\w+])(?:\(\+94\)|\+94)[\s.-]*7[\s.-]*6[\s.-]*7[\s.-]*0[\s.-]*6[\s.-]*7[\s.-]*3[\s.-]*4[\s.-]*3(?!\w)"
    if not re.search(phone, text):
        errors.append("Contact: missing phone +94767067343")

    # Require headings on their own extracted lines to avoid accepting mentions
    # in prose as section boundaries. Also permit wrapped headings.
    headings = HEADINGS[variant]
    positions = []
    for heading in headings:
        pattern = r"^\s*" + r"\s+".join(map(re.escape, heading.split())) + r"\s*$"
        match = re.search(pattern, raw_text, re.MULTILINE)
        positions.append(len(normalize_text(raw_text[:match.start()])) if match else -1)
    # The prefix length excludes the separating space in the normalized stream.
    positions = [position + (1 if position > 0 else 0) for position in positions]
    for heading, position in zip(headings, positions):
        if position < 0:
            errors.append(f"Missing section heading: {heading}")
    if any(position < 0 for position in positions):
        return errors
    if positions != sorted(positions):
        errors.append("Section headings are out of order")
        return errors
    sections = {}
    for index, heading in enumerate(headings):
        end = positions[index + 1] if index + 1 < len(positions) else len(text)
        sections[heading] = text[positions[index] + len(heading):end]

    work = sections["Work Experience"]
    for anchor in ("WSO2 LLC", "DevOps / Site Reliability Engineering Intern",
                   "Colombo, Sri Lanka"):
        if anchor not in work:
            errors.append(f"Work Experience: missing {anchor}")
    if not re.search(r"Sep\. 2025\s*[-–—]\s*Feb\. 2026", work):
        errors.append("Work Experience: missing Sep. 2025 - Feb. 2026 date range")
    education = sections["Education"]
    for anchor in ("BSc (Hons) in Information Technology (Specializing in Software Engineering)",
                   "Sri Lanka Institute of Information Technology (SLIIT)",
                   "Nov. 2026 (Expected)", "Current GPA: 3.51"):
        if anchor not in education:
            errors.append(f"Education: missing {anchor}")
    if not re.search(r"Nov\. 2022\s*[-–—]\s*Nov\. 2026 \(Expected\)", education):
        errors.append("Education: missing Nov. 2022 - Nov. 2026 (Expected) date range")
    _ordered(sections["Projects"], PROJECTS[variant], "Projects", errors)
    courses = sections["Courses and Certifications"]
    _ordered(courses, COURSES[variant], "Courses and Certifications", errors)
    for index, course in enumerate(COURSES[variant]):
        start = courses.find(course)
        if start < 0:
            continue  # The ordered-anchor check already reports this course.
        end = len(courses)
        if index + 1 < len(COURSES[variant]):
            following = courses.find(COURSES[variant][index + 1], start + len(course))
            if following >= 0:
                end = following
        entry = courses[start + len(course):end]
        if not re.search(r"\bKodeKloud\b", entry) or not re.search(r"\b2025\b", entry):
            errors.append(f"Courses and Certifications/{course}: missing KodeKloud or 2025")
    skills = sections["Skills"]
    categories = [category for category, _ in SKILLS[variant]]
    _ordered(skills, categories, "Skills", errors)
    for index, (category, anchors) in enumerate(SKILLS[variant]):
        start = skills.find(category)
        end = skills.find(categories[index + 1], start + len(category)) if index + 1 < len(categories) else len(skills)
        body = skills[start + len(category):end] if start >= 0 and end >= 0 else ""
        for anchor in anchors:
            if not re.search(r"(?<!\w)" + re.escape(anchor) + r"(?!\w)", body):
                errors.append(f"Skills/{category}: missing {anchor}")
    return errors


def validate_font_report(report):
    """Require every font to be embedded and mapped to Unicode.

    ATS outputs have no decorative fonts, so there is no icon-font exemption.
    Parse from the right because the font type can contain multiple words.
    """
    errors = []
    rows = report.splitlines()
    separator = next((i for i, line in enumerate(rows)
                      if re.match(r"^\s*-{3,}", line)), None)
    if separator is None:
        return ["pdffonts: malformed report (missing table separator)"]
    fonts = [line.split() for line in rows[separator + 1:] if line.strip()]
    if not fonts:
        return ["pdffonts: no fonts listed"]
    for fields in fonts:
        if (len(fields) < 8 or fields[-5] not in ("yes", "no")
                or fields[-4] not in ("yes", "no") or fields[-3] not in ("yes", "no")
                or not all(value.isdigit() for value in fields[-2:])):
            errors.append("pdffonts: malformed font row: " + " ".join(fields))
            continue
        if fields[-5] != "yes":
            errors.append(f"Font {fields[0]} is not embedded")
        if fields[-3] != "yes":
            errors.append(f"Font {fields[0]} has no Unicode mapping")
    return errors


def validate_pdf_info(report, variant):
    """Require a positive page count, and exactly one A4 page for onepage."""
    _variant(variant)
    errors = []
    pages = re.search(r"^Pages:\s*(\d+)\s*$", report, re.MULTILINE)
    if not pages or int(pages.group(1)) < 1:
        errors.append("pdfinfo: missing or invalid page count")
    elif variant == "onepage" and int(pages.group(1)) != 1:
        errors.append(f"Onepage PDF must have exactly one page, got {pages.group(1)}")
    if variant == "onepage":
        size = re.search(r"^Page size:\s*([\d.]+)\s+x\s+([\d.]+)\s+pts\b", report, re.MULTILINE)
        if not size or not (abs(float(size.group(1)) - 595.276) <= 1
                            and abs(float(size.group(2)) - 841.890) <= 1):
            errors.append("Onepage PDF must use portrait A4 (595.28 x 841.89 pts)")
    return errors


def _run(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                encoding="utf-8", errors="strict", timeout=30)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required command is missing: {command[0]}") from exc
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        raise RuntimeError(f"{command[0]} failed: {exc}") from exc
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
        raise RuntimeError(f"{command[0]} exited with {result.returncode}: {detail}")
    return result.stdout


def check_pdf(path, variant):
    _variant(variant)
    path = Path(path).resolve()
    if not path.is_file():
        raise RuntimeError(f"PDF file does not exist or is not a regular file: {path}")
    for command in ("pdftotext", "pdffonts", "pdfinfo"):
        if shutil.which(command) is None:
            raise RuntimeError(f"Required command is missing: {command} (install Poppler tools)")
    errors = []
    for label, flags in (("default", []), ("layout", ["-layout"])):
        extracted = _run(["pdftotext", *flags, "-enc", "UTF-8", str(path), "-"])
        errors.extend(f"pdftotext {label}: {error}" for error in validate_text(extracted, variant))
    errors.extend(validate_font_report(_run(["pdffonts", str(path)])))
    errors.extend(validate_pdf_info(_run(["pdfinfo", str(path)]), variant))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--variant", required=True, choices=tuple(HEADINGS))
    args = parser.parse_args(argv)
    try:
        errors = check_pdf(args.pdf, args.variant)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {args.pdf} ({args.variant}); both text modes, fonts, and page metadata")
    return 0


if __name__ == "__main__":
    sys.exit(main())

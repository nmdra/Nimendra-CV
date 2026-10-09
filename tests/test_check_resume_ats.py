"""Synthetic regression tests. No PDF compiler or Poppler installation needed."""

import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import check_resume_ats as checker


FONT_REPORT = """name                                 type              encoding         emb sub uni object ID
------------------------------------ ----------------- ---------------- --- --- --- ---------
ABCDEF+LMRoman10-Regular              CID Type 0C       Identity-H       yes yes yes      4  0
"""


def pdf_info(pages=1, size="595.276 x 841.89 pts (A4)"):
    return f"Title: Resume\nPages: {pages}\nPage size: {size}\n"


def resume_text(variant):
    sections = {
        "Summary": "Software Engineering undergraduate with SRE experience.",
        "Work Experience": "WSO2 LLC\nDevOps / Site Reliability Engineering Intern\nColombo, Sri Lanka\nSep. 2025 – Feb. 2026\nIncident management and automation.",
        "Education": "Sri Lanka Institute of Information Technology (SLIIT)\nBSc (Hons) in Information Technology (Specializing in Software Engineering)\nNov. 2022 – Nov. 2026 (Expected)\nCurrent GPA: 3.51",
        "Projects": "\n".join(checker.PROJECTS[variant]),
        "Courses and Certifications": "\n".join(f"{course}\nKodeKloud, 2025" for course in checker.COURSES[variant]),
        "Skills": "\n".join(category + ": " + ", ".join(skills) for category, skills in checker.SKILLS[variant]),
    }
    contact = "Nimendra Dilshan\n(+94) 767067343\nnimendradharmasiri@gmail.com\ngithub.com/nmdra | linkedin.com/in/nimendra | x.com/nimendra_\n"
    return contact + "\n".join(heading + "\n" + sections[heading] for heading in checker.HEADINGS[variant])


class TextTests(unittest.TestCase):
    def test_both_variants(self):
        for variant in checker.HEADINGS:
            with self.subTest(variant=variant):
                self.assertEqual(checker.validate_text(resume_text(variant), variant), [])

    def test_ligatures_whitespace_and_page_breaks(self):
        text = resume_text("full").replace("Certifications", "Certiﬁcations").replace("Certification", "Certiﬁcation").replace("\n", "\n\f  ")
        self.assertEqual(checker.validate_text(text, "full"), [])
        self.assertEqual(checker.normalize_text("  ﬁ ﬂ\nﬀ  "), "fi fl ff")

    def test_contact_missing(self):
        for variant in checker.HEADINGS:
            for contact in ("Nimendra Dilshan", "(+94) 767067343", "nimendradharmasiri@gmail.com",
                            "github.com/nmdra", "linkedin.com/in/nimendra", "x.com/nimendra_"):
                with self.subTest(variant=variant, contact=contact):
                    errors = checker.validate_text(resume_text(variant).replace(contact, ""), variant)
                    self.assertTrue(any("Contact" in error for error in errors))

    def test_phone_formats_and_no_unrelated_digit_joining(self):
        for number in ("+94767067343", "+94 76 706 7343", "(+94) 76-706-7343"):
            self.assertEqual(checker.validate_text(resume_text("full").replace("(+94) 767067343", number), "full"), [])
        for number in ("+94 76 notes 7067343", "+94 7670673430", "+94 76\nEducation 7067343"):
            self.assertTrue(any("phone" in error for error in checker.validate_text(resume_text("full").replace("(+94) 767067343", number), "full")))

    def test_reordered_headings(self):
        for variant in checker.HEADINGS:
            text = resume_text(variant).replace("Work Experience", "TEMP").replace("Education", "Work Experience").replace("TEMP", "Education")
            self.assertIn("Section headings are out of order", checker.validate_text(text, variant))

    def test_role_or_dates_outside_work(self):
        for variant in checker.HEADINGS:
            for anchor in ("DevOps / Site Reliability Engineering Intern", "Sep. 2025 – Feb. 2026", "WSO2 LLC"):
                text = resume_text(variant).replace(anchor, "") + "\n" + anchor
                self.assertTrue(any("Work Experience" in error for error in checker.validate_text(text, variant)))

    def test_education_outside_section(self):
        for anchor in ("Nov. 2026 (Expected)", "Current GPA: 3.51", "Sri Lanka Institute of Information Technology (SLIIT)"):
            text = resume_text("onepage").replace(anchor, "") + "\n" + anchor
            self.assertTrue(any("Education" in error for error in checker.validate_text(text, "onepage")))

    def test_education_start_date_must_match(self):
        for variant in checker.HEADINGS:
            text = resume_text(variant).replace("Nov. 2022", "Nov. 2024")
            self.assertTrue(any("Education" in error for error in checker.validate_text(text, variant)))

    def test_each_course_must_keep_issuer_and_year(self):
        for variant in checker.HEADINGS:
            for course in checker.COURSES[variant]:
                for wrong_details in ("Other Issuer, 2025", "KodeKloud, 2024"):
                    with self.subTest(variant=variant, course=course, details=wrong_details):
                        text = resume_text(variant).replace(
                            f"{course}\nKodeKloud, 2025", f"{course}\n{wrong_details}")
                        errors = checker.validate_text(text, variant)
                        self.assertTrue(any(course in error for error in errors))

    def test_reject_icon_and_replacement_noise(self):
        for variant in checker.HEADINGS:
            for character in ("\ufffd", "\uf09b", "\U000f0000", "\U00100000"):
                self.assertTrue(checker.validate_text(resume_text(variant) + character, variant))

    def test_section_heading_must_not_be_prose(self):
        text = resume_text("full").replace("\nProjects\n", "\nThese Projects are examples.\n")
        self.assertIn("Missing section heading: Projects", checker.validate_text(text, "full"))

    def test_missing_and_reordered_anchors(self):
        for variant in checker.HEADINGS:
            for anchors in (checker.PROJECTS[variant], checker.COURSES[variant]):
                text = resume_text(variant).replace(anchors[0], "")
                self.assertTrue(checker.validate_text(text, variant))
                text = resume_text(variant).replace(anchors[0], "TEMP").replace(anchors[1], anchors[0]).replace("TEMP", anchors[1])
                self.assertTrue(checker.validate_text(text, variant))
            text = resume_text(variant).replace("Terraform", "")
            self.assertTrue(any("Skills" in error for error in checker.validate_text(text, variant)))

    def test_wrong_variant(self):
        self.assertTrue(checker.validate_text(resume_text("full"), "onepage"))
        self.assertTrue(checker.validate_text(resume_text("onepage"), "full"))
        with self.assertRaises(ValueError):
            checker.validate_text("", "invalid")


class ReportTests(unittest.TestCase):
    def test_embedded_unicode_fonts(self):
        self.assertEqual(checker.validate_font_report(FONT_REPORT), [])

    def test_unembedded_font(self):
        errors = checker.validate_font_report(FONT_REPORT.replace("yes yes yes", "no  yes yes"))
        self.assertTrue(any("not embedded" in error for error in errors))

    def test_unmapped_font(self):
        errors = checker.validate_font_report(FONT_REPORT.replace("yes yes yes", "yes yes no "))
        self.assertTrue(any("Unicode mapping" in error for error in errors))

    def test_multiple_fonts_all_checked(self):
        report = FONT_REPORT + "OtherFont TrueType WinAnsi no no no 9 0\n"
        self.assertEqual(len(checker.validate_font_report(report)), 2)

    def test_empty_or_malformed_reports(self):
        for report in ("", "garbage", "name\n-----\n", "name\n-----\nbroken row\n"):
            self.assertTrue(checker.validate_font_report(report))
        for report in ("", "Pages: 0\n", "Pages: invalid\n"):
            self.assertTrue(checker.validate_pdf_info(report, "full"))

    def test_full_multiple_pages(self):
        self.assertEqual(checker.validate_pdf_info(pdf_info(3), "full"), [])

    def test_onepage_a4(self):
        self.assertEqual(checker.validate_pdf_info(pdf_info(), "onepage"), [])
        self.assertTrue(checker.validate_pdf_info(pdf_info(2), "onepage"))
        for size in ("612 x 792 pts (letter)", "841.89 x 595.276 pts (A4)", "unknown"):
            self.assertTrue(checker.validate_pdf_info(pdf_info(size=size), "onepage"))


class CommandTests(unittest.TestCase):
    def test_missing_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "PDF file does not exist"):
                checker.check_pdf(Path(directory) / "missing.pdf", "full")

    def test_missing_tool(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf, patch.object(checker.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "missing: pdftotext"):
                checker.check_pdf(pdf.name, "full")

    def test_subprocess_failures(self):
        cases = (FileNotFoundError(), subprocess.TimeoutExpired("pdftotext", 30), OSError("permission denied"))
        for failure in cases:
            with patch.object(checker.subprocess, "run", side_effect=failure):
                with self.assertRaises(RuntimeError):
                    checker._run(["pdftotext"])
        result = subprocess.CompletedProcess(["pdftotext"], 1, "", "Invalid PDF")
        with patch.object(checker.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "exited with 1: Invalid PDF"):
                checker._run(["pdftotext"])

    def test_all_commands_both_variants(self):
        for variant in checker.HEADINGS:
            outputs = (resume_text(variant), resume_text(variant), FONT_REPORT, pdf_info())
            with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf, patch.object(checker.shutil, "which", return_value="/bin/tool"), patch.object(checker, "_run", side_effect=outputs) as run:
                self.assertEqual(checker.check_pdf(pdf.name, variant), [])
                commands = [call.args[0] for call in run.call_args_list]
                self.assertEqual([command[0] for command in commands], ["pdftotext", "pdftotext", "pdffonts", "pdfinfo"])
                self.assertNotIn("-layout", commands[0])
                self.assertIn("-layout", commands[1])

    def test_either_extraction_mode_can_fail(self):
        for mode in (0, 1):
            outputs = [resume_text("full"), resume_text("full"), FONT_REPORT, pdf_info()]
            outputs[mode] = outputs[mode].replace("nimendradharmasiri@gmail.com", "")
            with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf, patch.object(checker.shutil, "which", return_value="tool"), patch.object(checker, "_run", side_effect=outputs):
                errors = checker.check_pdf(pdf.name, "full")
                self.assertTrue(any(("default" if mode == 0 else "layout") in error for error in errors))

    def test_cli_error(self):
        stderr = io.StringIO()
        with patch.object(checker, "check_pdf", side_effect=RuntimeError("Required command is missing: pdfinfo")), contextlib.redirect_stderr(stderr):
            self.assertEqual(checker.main(["resume.pdf", "--variant", "full"]), 1)
        self.assertIn("ERROR: Required command is missing: pdfinfo", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

import io
import os
import time
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from build import (
    strip_latex_comments,
    extract_braced_arg,
    extract_n_braced_args,
    latex_to_html,
    parse_header,
    parse_resume_latex,
    generate_html,
    check_and_compile_pdf,
    clean_latex_aux_files,
    check_pdf_staleness,
    find_default_profile_picture,
    normalize_picture_path,
    replace_latex_accents,
    copy_master_resume
)

class TestResumeParser(unittest.TestCase):
    def test_latex_accents_and_umlauts(self):
        # Umlauts with different LaTeX syntaxes: {\"a}, {\"{a}}, \"{a}, \"a
        self.assertEqual(latex_to_html(r'Christian-Albrechts-Universit{\"a}t zu Kiel'), 'Christian-Albrechts-Universität zu Kiel')
        self.assertEqual(latex_to_html(r'Universit{\"{a}}t'), 'Universität')
        self.assertEqual(latex_to_html(r'Universit\"{a}t'), 'Universität')
        self.assertEqual(latex_to_html(r'Universit\"at'), 'Universität')

        # Uppercase and other vowel umlauts
        self.assertEqual(latex_to_html(r'{\"A} {\"O} {\"U}'), 'Ä Ö Ü')
        self.assertEqual(latex_to_html(r'{\"a} {\"e} {\"i} {\"o} {\"u}'), 'ä ë ï ö ü')

        # Other standard LaTeX accents and special characters
        self.assertEqual(latex_to_html(r'Ren{\'e} Caovilla'), 'René Caovilla')
        self.assertEqual(latex_to_html(r'Fran\c{c}ois'), 'François')
        self.assertEqual(latex_to_html(r'{\c{c}} and \v{s} and {\ss}'), 'ç and š and ß')

        # Integration test in education section
        latex_doc = r"""
        \documentclass{article}
        \begin{document}
        \section{Education}
        \resumeSubHeadingListStart
          \resumeSubheading
            {Erasmus Exchange -- Christian-Albrechts-Universit{\"a}t zu Kiel}{Kiel, Germany}
            {Exchange Semester}{Apr. 2026 -- Sep. 2026}
        \resumeSubHeadingListEnd
        \end{document}
        """
        data = parse_resume_latex(latex_doc)
        sec = data["sections"][0]
        self.assertEqual(sec["items"][0]["title"], "Erasmus Exchange &ndash; Christian-Albrechts-Universität zu Kiel")

    def test_strip_comments(self):
        latex = r"""
        Line 1 % comment
        Line 2 \% not comment % comment
        Line 3 \\% not comment? (actually \\ is newline, % is comment)
        """
        cleaned = strip_latex_comments(latex)
        self.assertIn("Line 1", cleaned)
        self.assertNotIn("comment", cleaned.replace("% not comment", ""))
        self.assertIn(r"Line 2 \%", cleaned)

    def test_latex_to_html_formatting(self):
        self.assertEqual(latex_to_html(r"\textbf{Hello World}"), "<strong>Hello World</strong>")
        self.assertEqual(latex_to_html(r"\emph{Important}"), "em" in latex_to_html(r"\emph{Important}") and "<em>Important</em>")
        self.assertEqual(latex_to_html(r"\href{https://example.com}{My Link}"), '<a href="https://example.com" target="_blank" rel="noopener noreferrer">My Link</a>')
        self.assertEqual(latex_to_html(r"A \& B -- C --- D"), "A &amp; B &ndash; C &mdash; D")

    def test_nested_braces(self):
        raw = r"\textbf{Title \href{https://example.com}{with link}} rest"
        html = latex_to_html(raw)
        self.assertIn("<strong>Title", html)
        self.assertIn('<a href="https://example.com"', html)

    def test_header_parsing(self):
        latex_header = r"""
        \begin{center}
            \textbf{\Huge \scshape Jane Doe} \\ \vspace{1pt}
            \small
            +1 (555) 123-4567 $|$
            \href{mailto:jane@example.com}{jane@example.com} $|$
            \href{https://linkedin.com/in/janedoe}{linkedin.com/in/janedoe} $|$
            \href{https://github.com/janedoe}{github.com/janedoe}
        \end{center}
        """
        info = parse_header(latex_header)
        self.assertEqual(info["name"], "Jane Doe")
        self.assertEqual(len(info["contacts"]), 4)
        self.assertEqual(info["contacts"][0]["type"], "phone")
        self.assertEqual(info["contacts"][1]["type"], "email")
        self.assertEqual(info["contacts"][2]["type"], "linkedin")
        self.assertEqual(info["contacts"][3]["type"], "github")

    def test_complex_project_heading(self):
        latex_doc = r"""
        \documentclass{article}
        \begin{document}
        \section{Projects}
        \resumeSubHeadingListStart
          \resumeProjectHeading
              {\textbf{Awesome App} $|$ \emph{React, Node.js, PostgreSQL} $|$ \href{https://github.com/test}{\underline{Code}} $|$ \href{https://app.test}{\underline{Live Demo}}}{Jan 2024 -- Present}
          \resumeItemListStart
            \resumeItem{Engineered real-time collaboration feature using WebSockets.}
            \resumeItem{Scaled database throughput by 40\% via indexing.}
          \resumeItemListEnd
        \resumeSubHeadingListEnd
        \end{document}
        """
        data = parse_resume_latex(latex_doc)
        self.assertEqual(len(data["sections"]), 1)
        sec = data["sections"][0]
        self.assertEqual(sec["title"], "Projects")
        self.assertEqual(len(sec["items"]), 1)
        proj = sec["items"][0]
        self.assertIn("Awesome App", proj["title"])
        self.assertIn("React", proj["tech_stack"])
        self.assertIn("Node.js", proj["tech_stack"])
        self.assertIn("PostgreSQL", proj["tech_stack"])
        self.assertEqual(len(proj["links"]), 2)
        self.assertEqual(len(proj["bullets"]), 2)
        self.assertIn("40%", proj["bullets"][1])

    def test_skills_parsing(self):
        latex_doc = r"""
        \documentclass{article}
        \begin{document}
        \section{Technical Skills}
         \begin{itemize}[leftmargin=0.15in, label={}]
            \small{\item{
             \textbf{Languages}{: Python, TypeScript, Go, SQL, Rust} \\
             \textbf{Frameworks}{: React, Next.js, FastAPI, Django} \\
             \textbf{Developer Tools}{: Git, Docker, Kubernetes, AWS}
            }}
         \end{itemize}
        \end{document}
        """
        data = parse_resume_latex(latex_doc)
        sec = data["sections"][0]
        self.assertEqual(sec["type"], "skills")
        self.assertEqual(len(sec["skills"]), 3)
        self.assertEqual(sec["skills"][0]["category"], "Languages")
        self.assertIn("Python", sec["skills"][0]["skills"])
        self.assertIn("Rust", sec["skills"][0]["skills"])
        self.assertEqual(sec["skills"][1]["category"], "Frameworks")
        self.assertEqual(sec["skills"][2]["category"], "Developer Tools")

    def test_profile_picture_rendering(self):
        data = {
            "header": {"name": "Alex Smith", "contacts": []},
            "sections": []
        }
        html_with_pic = generate_html(data, profile_pic="avatar.png")
        self.assertIn('src="avatar.png"', html_with_pic)
        self.assertIn('class="avatar-img"', html_with_pic)

        html_without_pic = generate_html(data, profile_pic=None)
        self.assertNotIn('class="avatar-img"', html_without_pic)

    def test_profile_picture_url_encoding(self):
        data = {
            "header": {"name": "Alex Smith", "contacts": []},
            "sections": []
        }
        html_with_spaces = generate_html(data, profile_pic="images/My Photo.jpg")
        self.assertIn('src="images/My%20Photo.jpg"', html_with_spaces)

    def test_no_print_button_rendered(self):
        data = {
            "header": {"name": "Alex Smith", "contacts": []},
            "sections": []
        }
        html_content = generate_html(data)
        self.assertNotIn("print-btn", html_content)
        self.assertNotIn("window.print()", html_content)

    @patch("shutil.which", return_value=None)
    def test_pdflatex_not_found_warning(self, mock_which):
        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture):
            pdf_path, compiled = check_and_compile_pdf(Path("resume.tex"))
        
        self.assertFalse(compiled)
        warning_msg = stderr_capture.getvalue()
        self.assertIn("Warning: 'pdflatex' utility was not found on PATH", warning_msg)
        self.assertIn("resume.pdf file must be updated manually", warning_msg)

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/pdflatex")
    def test_pdflatex_compilation_success(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        with patch.object(Path, "exists", return_value=True):
            pdf_path, compiled = check_and_compile_pdf(Path("resume.tex"))
            self.assertTrue(compiled)
            mock_run.assert_called_once()

    def test_clean_latex_aux_files(self):
        test_dir = Path("test_aux_temp")
        test_dir.mkdir(exist_ok=True)
        tex_file = test_dir / "sample.tex"
        tex_file.write_text("test", encoding="utf-8")
        
        aux_file = test_dir / "sample.aux"
        log_file = test_dir / "sample.log"
        out_file = test_dir / "sample.out"
        texput_file = test_dir / "texput.log"
        
        aux_file.write_text("aux", encoding="utf-8")
        log_file.write_text("log", encoding="utf-8")
        out_file.write_text("out", encoding="utf-8")
        texput_file.write_text("texput", encoding="utf-8")
        
        clean_latex_aux_files(tex_file)
        
        self.assertFalse(aux_file.exists())
        self.assertFalse(log_file.exists())
        self.assertFalse(out_file.exists())
        self.assertFalse(texput_file.exists())
        self.assertTrue(tex_file.exists())
        
        # Cleanup
        tex_file.unlink()
        test_dir.rmdir()

    def test_pdf_staleness_warning(self):
        stderr_capture = io.StringIO()
        tex_path = MagicMock()
        tex_path.name = "resume.tex"
        tex_path.stem = "resume"
        tex_path.stat.return_value = MagicMock(st_mtime=1000)
        
        pdf_path = MagicMock()
        pdf_path.name = "resume.pdf"
        pdf_path.exists.return_value = True
        pdf_path.stat.return_value = MagicMock(st_mtime=500)
        
        with patch("sys.stderr", stderr_capture):
            check_pdf_staleness(tex_path, pdf_path)
            
        warning_msg = stderr_capture.getvalue()
        self.assertIn("was modified more recently than", warning_msg)
        self.assertIn("Overleaf", warning_msg)

    def test_find_default_profile_picture_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            
            # Case 1: PozaProfil.JPG
            (base / "PozaProfil.JPG").write_text("image")
            pic = find_default_profile_picture(base)
            self.assertEqual(pic, "PozaProfil.JPG")
            
            # Case 2: Subfolder images/my_avatar.png
            (base / "PozaProfil.JPG").unlink()
            (base / "images").mkdir()
            (base / "images" / "my_avatar.png").write_text("image")
            pic = find_default_profile_picture(base)
            self.assertEqual(pic, "images/my_avatar.png")

    def test_normalize_picture_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            (base / "assets").mkdir()
            (base / "assets" / "pic.png").write_text("image")
            
            # Normalization of backslashes
            rel = normalize_picture_path(r"assets\pic.png", base)
            self.assertEqual(rel, "assets/pic.png")
            
            # External image copying
            with tempfile.TemporaryDirectory() as ext_dir:
                ext_file = Path(ext_dir) / "external.jpg"
                ext_file.write_text("image")
                copied = normalize_picture_path(str(ext_file), base)
                self.assertEqual(copied, "external.jpg")
                self.assertTrue((base / "external.jpg").exists())

    def test_copy_master_resume(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            master_file = base / "resume.tex"
            master_file.write_text(r"\documentclass{article} Master Content", encoding="utf-8")
            
            # Copy to default Radu_Pirvu.tex
            target = copy_master_resume(master_file, "Radu_Pirvu.tex")
            self.assertIsNotNone(target)
            self.assertTrue(target.exists())
            self.assertEqual(target.name, "Radu_Pirvu.tex")
            self.assertEqual(target.read_text(encoding="utf-8"), master_file.read_text(encoding="utf-8"))
            
            # Calling when target is the same file returns None (does not overwrite itself)
            self.assertIsNone(copy_master_resume(target, "Radu_Pirvu.tex"))
            
            # Calling on non-existent file returns None
            self.assertIsNone(copy_master_resume(base / "nonexistent.tex", "Radu_Pirvu.tex"))

if __name__ == "__main__":
    unittest.main()
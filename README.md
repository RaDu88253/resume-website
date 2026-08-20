# Easy Resume

Transform your LaTeX resume (`resume.tex`) into a modern, responsive web portfolio (`index.html`) hosted automatically on **GitHub Pages**, with an ATS-ready PDF download.

Based on the widely-used **Jake's Resume** LaTeX template structure.

---

## ✨ Features

- 📄 **LaTeX to HTML Parser**: Automatically parses header info, contact links, education, experience, projects, tech stacks, skills, and awards/certifications.
- ⚙️ **Automatic `pdflatex` Compilation & Cleanup**: Automatically detects `pdflatex` on your system, compiles `resume.pdf`, and removes LaTeX auxiliary junk files (`.aux`, `.log`, `.out`, `texput.log`).
- ⚠️ **Outdated PDF Detection**: Checks modification timestamps and alerts you if `resume.tex` was updated more recently than `resume.pdf`.
- 🚀 **GitHub Actions Automated Deployment**: Seamlessly builds and publishes your web portfolio to GitHub Pages on every push to the `main` branch.
- 🎨 **Modern Responsive Design**: Clean typography with Google Fonts (*Outfit* & *Inter*), subtle card elevations, and tech stack tags.
- 🌓 **Dark / Light Theme**: Automatic OS preference detection with persistent theme toggle stored in `localStorage`.
- 🖼️ **Profile Picture Support**: Add an optional profile image via CLI (`-p <path>`) or by adding `profile.jpg` / `avatar.png` / `photo.jpg` to the repository.
- 📥 **PDF Download**: Automatically links the compiled `resume.pdf` with a sleek download action button.
- ⚡ **Zero External Python Dependencies**: Built entirely with Python standard library modules (`argparse`, `pathlib`, `re`, `html`, `shutil`, `subprocess`, `typing`).

---

## 🌐 GitHub Pages Setup Guide

This repository is designed to host your web resume directly on GitHub Pages via GitHub Actions:

1. **Fork or Create a Repository**:
   Push this repository to your GitHub account.

2. **Enable GitHub Pages via Actions**:
   - Go to your repository on GitHub.
   - Click **Settings** (⚙️) > **Pages** (in the left sidebar).
   - Under **Build and deployment** > **Source**, select **GitHub Actions**.

3. **Deploy Your Resume**:
   - Whenever you push changes to the `main` branch (such as updating `resume.tex` or `resume.pdf`), the included GitHub Actions workflow (`.github/workflows/deploy.yml`) will automatically run tests, build `index.html`, and deploy your portfolio live to `https://<your-username>.github.io/<repo-name>/`.

---

## 📝 Updating Your Resume

### Option A: If you have LaTeX installed locally
Edit `resume.tex` and run:
```bash
python build.py
```
*(On Windows: `py build.py`)*

The script will automatically compile `resume.pdf` using `pdflatex`, remove auxiliary build artifacts, and generate the updated `index.html`.

### Option B: If you don't have LaTeX installed (Using Overleaf)
If you do not have or do not want to install LaTeX locally:
1. Open and edit your `resume.tex` on **[Overleaf](https://www.overleaf.com/)** (or your preferred online LaTeX editor).
2. Click **Recompile** in Overleaf and download the compiled `resume.pdf`.
3. Place both the updated `resume.tex` and `resume.pdf` in the root of this repository.
4. Run `python build.py` (or simply commit and push your changes to GitHub).

> **Note**: If `resume.tex` is edited without updating `resume.pdf`, `build.py` will display a friendly warning reminding you to recompile the PDF.

---

## 🖼️ Adding a Profile Picture

You can include a profile picture in your web portfolio in either of two ways:

1. **Auto-detection**: Place an image named `profile.jpg`, `profile.png`, `avatar.jpg`, `avatar.png`, or `photo.jpg` in the project root.
2. **Explicit CLI argument**:
   ```bash
   python build.py -p my_photo.jpg
   ```

If no profile picture is provided or found, the portfolio renders a clean text-first layout without empty boxes.

---

## 🛠️ CLI Options

```
usage: build.py [-h] [-o OUTPUT] [-c CSS] [-p PICTURE] [--no-auto-picture]
                [--pdf PDF] [--no-pdf-compile] [-t TITLE] [input]

positional arguments:
  input                 Path to the input LaTeX resume file (default: resume.tex)

options:
  -h, --help            Show this help message and exit
  -o, --output OUTPUT   Path to output HTML file (default: index.html)
  -c, --css CSS         Path or href to stylesheet (default: style.css)
  -p, --picture PICTURE Path to profile photo (e.g. profile.jpg)
  --no-auto-picture     Disable auto-detecting profile picture in directory
  --pdf PDF             Explicit path to PDF file for download button
  --no-pdf-compile      Skip automatic pdflatex compilation even if available
  -t, --title TITLE     Custom HTML page title
```

---

## 🧪 Testing & Debugging

The repository includes a comprehensive unit test suite in `test_suite.py`. This is especially useful for **development purposes and debugging** (for example, if you customize the LaTeX parser, add new LaTeX environments/commands, or modify template generation):

```bash
python -m unittest test_suite.py
```

The test suite validates:
- Comment stripping and escape handling (`\%` vs `%`).
- Typography and entity conversions (`\textbf`, `\href`, `\emph`, dashes, symbols).
- Multi-argument and nested brace parsing.
- Tech stack tag extraction and link parsing in project headings.
- Key-value technical skills categorization.
- Profile picture rendering and absence handling.
- PDF staleness checks and `pdflatex` compilation / warning behavior.
- LaTeX auxiliary junk file cleanup.

---

## 📄 License

MIT

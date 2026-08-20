#!/usr/bin/env python3
"""
build.py - LaTeX Resume to Modern HTML Portfolio Builder

Reads a resume written in LaTeX (such as Jake's Resume format) and generates
a modern, responsive web portfolio (index.html) with style.css.
Automatically checks for the 'pdflatex' utility and compiles the PDF if available,
cleans auxiliary LaTeX files, and warns the user if resume.pdf is outdated.
"""

import re
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Configure UTF-8 output on Windows consoles safely
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Clean, accessible SVG icons for UI and sections
ICONS = {
    # Contacts
    "email": '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>',
    "phone": '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
    "linkedin": '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/></svg>',
    "github": '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>',
    "twitter": '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"/></svg>',
    "website": '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>',
    "location": '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>',
    "link": '<svg class="icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    "calendar": '<svg class="meta-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="M8 2v4"/><path d="M16 2v4"/></svg>',
    "map-pin": '<svg class="meta-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>',
    
    # Section header icons
    "education": '<svg class="section-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/></svg>',
    "experience": '<svg class="section-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="20" height="14" x="2" y="7" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
    "projects": '<svg class="section-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m18 16 4-4-4-4"/><path d="m6 8-4 4 4 4"/><path d="m14.5 4-5 16"/></svg>',
    "skills": '<svg class="section-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2v4"/><path d="m4.93 4.93 2.83 2.83"/><path d="M2 12h4"/><path d="m4.93 19.07 2.83-2.83"/><path d="M12 18v4"/><path d="m16.24 16.24 2.83 2.83"/><path d="M18 12h4"/><path d="m16.24 7.76 2.83-2.83"/><circle cx="12" cy="12" r="3"/></svg>',
    "awards": '<svg class="section-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/></svg>',
    "generic": '<svg class="section-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>',
    
    # UI actions
    "sun": '<svg class="theme-icon sun-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>',
    "moon": '<svg class="theme-icon moon-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
    "download": '<svg class="action-btn-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>'
}

def clean_latex_aux_files(input_path: Path) -> None:
    """Remove auxiliary junk files produced during LaTeX compilation (.aux, .log, .out, texput.log, etc.)."""
    stem = input_path.stem
    parent = input_path.parent
    extensions_to_clean = [
        ".aux", ".log", ".out", ".fls", ".fdb_latexmk",
        ".synctex.gz", ".toc", ".nav", ".snm", ".vrb"
    ]
    
    for ext in extensions_to_clean:
        aux_file = parent / f"{stem}{ext}"
        if aux_file.exists():
            try:
                aux_file.unlink()
            except Exception:
                pass
                
    # Also check for standalone texput.log in parent directory
    texput_file = parent / "texput.log"
    if texput_file.exists():
        try:
            texput_file.unlink()
        except Exception:
            pass

def check_and_compile_pdf(input_path: Path, skip_pdf: bool = False) -> Tuple[Optional[Path], bool]:
    """
    Check whether pdflatex is available and compile the resume if so.
    If pdflatex is not found, warns the user that resume.pdf must be updated manually.
    Cleans auxiliary junk files after compilation.
    
    Returns:
        (pdf_path, is_freshly_compiled)
    """
    pdf_path = input_path.with_suffix(".pdf")
    
    if skip_pdf:
        return (pdf_path if pdf_path.exists() else None), False

    pdflatex_cmd = shutil.which("pdflatex")
    if not pdflatex_cmd:
        print("[!] Warning: 'pdflatex' utility was not found on PATH. The resume.pdf file must be updated manually (run build.py if you have LaTeX installed, or compile using Overleaf if you do not).", file=sys.stderr)
        return (pdf_path if pdf_path.exists() else None), False
    
    print(f"[*] Found 'pdflatex' at '{pdflatex_cmd}'. Compiling '{input_path.name}' to PDF...")
    try:
        cmd = [
            pdflatex_cmd,
            "-interaction=nonstopmode",
            f"-output-directory={input_path.parent}",
            str(input_path.resolve())
        ]
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(input_path.parent.resolve())
        )
        
        # Clean auxiliary files immediately after compilation
        clean_latex_aux_files(input_path)
        
        if res.returncode == 0 and pdf_path.exists():
            print(f"[OK] Successfully compiled PDF: '{pdf_path.name}'")
            return pdf_path, True
        else:
            print(f"[!] Warning: pdflatex finished with returncode {res.returncode}. The resume.pdf file may need manual check.", file=sys.stderr)
            return (pdf_path if pdf_path.exists() else None), False
    except Exception as e:
        clean_latex_aux_files(input_path)
        print(f"[!] Warning: Failed to execute pdflatex ({e}). The resume.pdf file must be updated manually.", file=sys.stderr)
        return (pdf_path if pdf_path.exists() else None), False

def check_pdf_staleness(tex_path: Path, pdf_path: Optional[Path]) -> None:
    """
    If the LaTeX file was modified more recently than the PDF file,
    warn the user to update their PDF (via LaTeX locally or Overleaf).
    """
    if not pdf_path or not pdf_path.exists():
        print(f"[!] Warning: '{tex_path.name}' exists but '{tex_path.stem}.pdf' was not found. Please compile it using LaTeX locally (run build.py) or via Overleaf (https://www.overleaf.com).", file=sys.stderr)
        return
    
    try:
        tex_mtime = tex_path.stat().st_mtime
        pdf_mtime = pdf_path.stat().st_mtime
        if tex_mtime > pdf_mtime + 1.0:
            print(f"[!] Warning: '{tex_path.name}' was modified more recently than '{pdf_path.name}'. Please update your PDF (run 'python build.py' if you have LaTeX installed, or compile using Overleaf if you do not).", file=sys.stderr)
    except Exception:
        pass

def strip_latex_comments(latex_text: str) -> str:
    """Strip LaTeX comments while respecting escaped percent signs (\\%)."""
    result = []
    for line in latex_text.splitlines():
        comment_start = -1
        i = 0
        while i < len(line):
            char = line[i]
            if char == '\\':
                bs_count = 1
                while i + bs_count < len(line) and line[i + bs_count] == '\\':
                    bs_count += 1
                i += bs_count
                if i < len(line) and line[i] == '%':
                    if bs_count % 2 == 1:
                        i += 1
                        continue
                    else:
                        comment_start = i
                        break
                continue
            elif char == '%':
                comment_start = i
                break
            i += 1
            
        if comment_start >= 0:
            result.append(line[:comment_start])
        else:
            result.append(line)
    return "\n".join(result)

def extract_braced_arg(text: str, start_pos: int) -> Tuple[Optional[str], int]:
    """Find the next '{' from start_pos and return (content_inside, end_pos_after_closing_brace)."""
    open_idx = text.find('{', start_pos)
    if open_idx == -1:
        return None, start_pos
    
    depth = 0
    i = open_idx
    while i < len(text):
        if text[i] == '\\':
            i += 2
            continue
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[open_idx + 1:i], i + 1
        i += 1
    return text[open_idx + 1:], len(text)

def extract_n_braced_args(text: str, start_pos: int, n: int) -> Tuple[List[str], int]:
    """Extract exactly n braced arguments in sequence."""
    args = []
    curr = start_pos
    for _ in range(n):
        while curr < len(text) and text[curr].isspace():
            curr += 1
        if curr >= len(text) or text[curr] != '{':
            next_brace = text.find('{', curr)
            if next_brace == -1:
                break
            curr = next_brace
        content, next_curr = extract_braced_arg(text, curr)
        if content is None:
            break
        args.append(content)
        curr = next_curr
    return args, curr

def latex_to_html(tex: str) -> str:
    """Convert LaTeX inline markup into clean, semantic HTML."""
    if not tex:
        return ""
    
    s = tex.strip()
    
    # Remove \vspace{...} and \hspace{...}
    s = re.sub(r'\\(v|h)space\*?\{[^}]*\}', '', s)
    
    # Remove sizing/formatting macros without arguments
    s = re.sub(r'\\(Huge|huge|LARGE|Large|large|normalsize|small|footnotesize|tiny|scshape)\b', '', s)
    
    # Convert \href{url}{text}
    while True:
        m = re.search(r'\\href\s*\{', s)
        if not m:
            break
        start = m.start()
        url, pos1 = extract_braced_arg(s, start)
        if url is None:
            break
        label, pos2 = extract_braced_arg(s, pos1)
        if label is None:
            label = url
        label_html = latex_to_html(label)
        clean_url = url.strip()
        replacement = f'<a href="{clean_url}" target="_blank" rel="noopener noreferrer">{label_html}</a>'
        s = s[:start] + replacement + s[pos2:]

    # Convert \url{url}
    while True:
        m = re.search(r'\\url\s*\{', s)
        if not m:
            break
        start = m.start()
        url, pos1 = extract_braced_arg(s, start)
        if url is None:
            break
        clean_url = url.strip()
        replacement = f'<a href="{clean_url}" target="_blank" rel="noopener noreferrer">{clean_url}</a>'
        s = s[:start] + replacement + s[pos1:]

    # Convert formatting tags: \textbf, \textit, \emph, \underline, \texttt, \textsc
    cmd_map = [
        (r'\\textbf\s*\{', 'strong', None),
        (r'\\textit\s*\{', 'em', None),
        (r'\\emph\s*\{', 'em', None),
        (r'\\underline\s*\{', 'u', None),
        (r'\\texttt\s*\{', 'code', None),
        (r'\\textsc\s*\{', 'span', 'small-caps'),
    ]
    
    changed = True
    while changed:
        changed = False
        for pattern, tag, cls in cmd_map:
            m = re.search(pattern, s)
            if m:
                start = m.start()
                content, end = extract_braced_arg(s, start)
                if content is not None:
                    inner_html = latex_to_html(content)
                    cls_attr = f' class="{cls}"' if cls else ''
                    s = s[:start] + f'<{tag}{cls_attr}>{inner_html}</{tag}>' + s[end:]
                    changed = True
                    break

    # Handle special TeX symbols and escapes
    s = s.replace(r'\&', '&amp;')
    s = s.replace(r'\%', '%')
    s = s.replace(r'\$', '$')
    s = s.replace(r'\_', '_')
    s = s.replace(r'\#', '#')
    s = s.replace(r'\textbar', '|')
    s = s.replace(r'$|$', '|')
    s = s.replace(r'~', '&nbsp;')
    s = s.replace('---', '&mdash;')
    s = s.replace('--', '&ndash;')
    s = s.replace("``", '&ldquo;')
    s = s.replace("''", '&rdquo;')
    
    # Strip unnecessary single curly braces wrapping the whole string (LaTeX grouping)
    while s.startswith('{') and s.endswith('}'):
        depth = 0
        matched = False
        for idx, ch in enumerate(s):
            if ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and idx == len(s) - 1:
                    matched = True
                    break
                elif depth == 0:
                    break
        if matched:
            s = s[1:-1].strip()
        else:
            break
            
    # Clean up excess internal whitespace
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return s

def parse_header(header_text: str) -> Dict[str, Any]:
    """Parse header region for Name, contacts, links, location."""
    info: Dict[str, Any] = {
        "name": "",
        "contacts": []
    }
    
    cleaned = re.sub(r'\\begin\{center\}|\\end\{center\}', '', header_text)
    
    # Extract name (usually inside \Huge / \textbf or first non-empty line)
    name_match = re.search(r'\\textbf\s*\{([^}]+)\}', cleaned)
    if name_match:
        raw_name = name_match.group(1)
        info["name"] = latex_to_html(raw_name)
    else:
        lines = [l.strip() for l in cleaned.split(r'\\') if l.strip()]
        if lines:
            info["name"] = latex_to_html(lines[0])
            
    contacts_blob = cleaned
    if name_match:
        contacts_blob = contacts_blob.replace(name_match.group(0), '')
        
    contacts_blob = re.sub(r'\\(Huge|huge|LARGE|Large|large|normalsize|small|footnotesize|tiny|scshape)\b', '', contacts_blob)
    contacts_blob = re.sub(r'\\vspace\*?\{[^}]*\}', '', contacts_blob)
    
    # Split contacts by separator ($|$, |, \\, \n)
    tokens = re.split(r'\s*(?:\$\|\$|\||\\\\|\n)\s*', contacts_blob)
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        
        # Check for \href{url}{label}
        href_match = re.search(r'\\href\s*\{([^}]+)\}\s*\{([^}]+)\}', tok)
        if href_match:
            url = href_match.group(1).strip()
            label = latex_to_html(href_match.group(2).strip())
            
            c_type = "link"
            if url.startswith("mailto:"):
                c_type = "email"
            elif "linkedin.com" in url:
                c_type = "linkedin"
            elif "github.com" in url:
                c_type = "github"
            elif "twitter.com" in url or "x.com" in url:
                c_type = "twitter"
            else:
                c_type = "website"
                
            info["contacts"].append({
                "type": c_type,
                "text": label,
                "url": url
            })
            continue
            
        # Check for raw email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', tok)
        if email_match:
            email = email_match.group(0)
            info["contacts"].append({
                "type": "email",
                "text": email,
                "url": f"mailto:{email}"
            })
            continue
            
        # Check for phone
        phone_cleaned = tok.replace('[', '').replace(']', '').strip()
        digits = [c for c in tok if c.isdigit()]
        if len(digits) >= 7 or "phone" in tok.lower():
            info["contacts"].append({
                "type": "phone",
                "text": latex_to_html(tok),
                "url": f"tel:{re.sub(r'[^0-9+]', '', phone_cleaned)}" if digits else ""
            })
            continue
            
        # Generic text / location / handle
        html_tok = latex_to_html(tok)
        if html_tok:
            c_type = "location" if ("city" in tok.lower() or "country" in tok.lower() or "," in tok) else "other"
            info["contacts"].append({
                "type": c_type,
                "text": html_tok,
                "url": ""
            })
            
    return info

def parse_items_list(text: str) -> List[str]:
    """Extract all \\resumeItem{...} contents within text."""
    bullets = []
    curr = 0
    while True:
        m = re.search(r'\\resumeItem\s*\{', text[curr:])
        if not m:
            break
        start = curr + m.start()
        content, next_idx = extract_braced_arg(text, start)
        if content is not None:
            bullets.append(latex_to_html(content))
            curr = next_idx
        else:
            break
    return bullets

def parse_skills_section(text: str) -> List[Dict[str, Any]]:
    """Parse key-value skills like \\textbf{Category}{: Skill1, Skill2}."""
    skills_list = []
    cleaned = text
    curr = 0
    while True:
        m = re.search(r'\\textbf\s*\{', cleaned[curr:])
        if not m:
            break
        start = curr + m.start()
        cat, after_cat = extract_braced_arg(cleaned, start)
        if cat is None:
            break
            
        rest = cleaned[after_cat:]
        rest_stripped = rest.strip()
        cat_items_str = ""
        next_curr = after_cat
        
        if rest_stripped.startswith('{:'):
            brace_content, end_brace = extract_braced_arg(cleaned, after_cat)
            if brace_content is not None:
                cat_items_str = brace_content.lstrip(':').strip()
                next_curr = end_brace
        elif rest_stripped.startswith('{'):
            brace_content, end_brace = extract_braced_arg(cleaned, after_cat)
            if brace_content is not None:
                cat_items_str = brace_content.lstrip(':').strip()
                next_curr = end_brace
        else:
            match_end = re.search(r'\\\\|\\item|\\textbf|$', rest)
            end_idx = match_end.start() if match_end else len(rest)
            raw_segment = rest[:end_idx]
            cat_items_str = raw_segment.lstrip(':').strip()
            next_curr = after_cat + end_idx
            
        category_name = latex_to_html(cat).rstrip(':').strip()
        cleaned_skills_str = latex_to_html(cat_items_str).strip()
        raw_skills = [s.strip() for s in re.split(r'[,;]\s*', cleaned_skills_str) if s.strip()]
        
        skills_list.append({
            "category": category_name,
            "raw_text": cleaned_skills_str,
            "skills": raw_skills
        })
        curr = next_curr
        
    return skills_list

def parse_section(title: str, body: str) -> Dict[str, Any]:
    """Parse a single section's content into structured items."""
    sec: Dict[str, Any] = {
        "title": title,
        "type": "generic",
        "items": []
    }
    
    t_lower = title.lower()
    if "skill" in t_lower:
        sec["type"] = "skills"
        sec["skills"] = parse_skills_section(body)
        return sec
        
    cursor = 0
    while cursor < len(body):
        m = re.search(r'\\(resumeSubheading|resumeProjectHeading|resumeItem|resumeItemListStart)\b', body[cursor:])
        if not m:
            remaining = latex_to_html(body[cursor:])
            remaining_clean = re.sub(r'\\(resumeSubHeadingListStart|resumeSubHeadingListEnd|resumeItemListEnd|begin\{[^}]*\}|end\{[^}]*\})', '', remaining).strip()
            if remaining_clean and not sec["items"]:
                sec["type"] = "text"
                sec["text"] = remaining_clean
            break
            
        cmd_pos = cursor + m.start()
        cmd = m.group(1)
        after_cmd_pos = cmd_pos + len(m.group(0))
        
        if cmd == "resumeSubheading":
            args, next_cursor = extract_n_braced_args(body, after_cmd_pos, 4)
            while len(args) < 4:
                args.append("")
                
            entry = {
                "type": "subheading",
                "title": latex_to_html(args[0]),
                "location": latex_to_html(args[1]),
                "subtitle": latex_to_html(args[2]),
                "date": latex_to_html(args[3]),
                "bullets": []
            }
            
            next_heading = re.search(r'\\(resumeSubheading|resumeProjectHeading)\b', body[next_cursor:])
            end_search = next_cursor + next_heading.start() if next_heading else len(body)
            sub_body = body[next_cursor:end_search]
            
            if r'\resumeItem' in sub_body:
                entry["bullets"] = parse_items_list(sub_body)
                m_end = re.search(r'\\resumeItemListEnd\b', sub_body)
                if m_end:
                    next_cursor = next_cursor + m_end.end()
                else:
                    next_cursor = end_search
                    
            sec["items"].append(entry)
            cursor = next_cursor
            
        elif cmd == "resumeProjectHeading":
            args, next_cursor = extract_n_braced_args(body, after_cmd_pos, 2)
            while len(args) < 2:
                args.append("")
                
            raw_heading = args[0]
            date_str = latex_to_html(args[1])
            
            parts = re.split(r'\s*(?:\$\|\$|\|)\s*', raw_heading)
            project_title = latex_to_html(parts[0]) if parts else ""
            tech_stack = []
            links = []
            
            for part in parts[1:]:
                part_html = latex_to_html(part)
                if '<a ' in part_html:
                    links.append(part_html)
                else:
                    clean_tags = re.split(r'[,;]\s*', part_html)
                    for t in clean_tags:
                        t_clean = re.sub(r'<[^>]+>', '', t).strip()
                        if t_clean:
                            tech_stack.append(t_clean)
                            
            next_heading = re.search(r'\\(resumeSubheading|resumeProjectHeading)\b', body[next_cursor:])
            end_search = next_cursor + next_heading.start() if next_heading else len(body)
            sub_body = body[next_cursor:end_search]
            
            bullets = []
            if r'\resumeItem' in sub_body:
                bullets = parse_items_list(sub_body)
                m_end = re.search(r'\\resumeItemListEnd\b', sub_body)
                if m_end:
                    next_cursor = next_cursor + m_end.end()
                else:
                    next_cursor = end_search
                    
            sec["items"].append({
                "type": "project",
                "title": project_title,
                "tech_stack": tech_stack,
                "date": date_str,
                "links": links,
                "bullets": bullets
            })
            cursor = next_cursor
            
        elif cmd == "resumeItem":
            content, next_cursor = extract_braced_arg(body, after_cmd_pos - 1)
            if content is not None:
                sec["items"].append({
                    "type": "item",
                    "text": latex_to_html(content)
                })
                cursor = next_cursor
            else:
                cursor = after_cmd_pos
                
        elif cmd == "resumeItemListStart":
            cursor = after_cmd_pos
            
    return sec

def parse_resume_latex(latex_content: str) -> Dict[str, Any]:
    """Parse complete resume LaTeX content into a structured data dictionary."""
    cleaned = strip_latex_comments(latex_content)
    
    # Restrict to \begin{document} ... \end{document} if present
    doc_start = cleaned.find(r'\begin{document}')
    if doc_start != -1:
        cleaned = cleaned[doc_start + len(r'\begin{document}'):]
    doc_end = cleaned.find(r'\end{document}')
    if doc_end != -1:
        cleaned = cleaned[:doc_end]
        
    section_matches = list(re.finditer(r'\\section\s*\{', cleaned))
    
    header_part = cleaned[:section_matches[0].start()] if section_matches else cleaned
    header_info = parse_header(header_part)
    
    sections = []
    for i, match in enumerate(section_matches):
        start = match.start()
        raw_title, after_title_idx = extract_braced_arg(cleaned, start)
        title = latex_to_html(raw_title) if raw_title else ""
        end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(cleaned)
        body = cleaned[after_title_idx:end]
        sections.append(parse_section(title, body))
        
    return {
        "header": header_info,
        "sections": sections
    }

def get_section_icon(title: str) -> str:
    """Return an appropriate SVG icon for a section title."""
    t = title.lower()
    if "education" in t:
        return ICONS["education"]
    elif "experience" in t or "work" in t or "employment" in t:
        return ICONS["experience"]
    elif "project" in t:
        return ICONS["projects"]
    elif "skill" in t:
        return ICONS["skills"]
    elif "award" in t or "certif" in t or "honor" in t:
        return ICONS["awards"]
    return ICONS["generic"]

def get_contact_icon(ctype: str) -> str:
    """Return an appropriate SVG icon for a contact type."""
    return ICONS.get(ctype, ICONS["link"])

def generate_html(data: Dict[str, Any], css_href: str = "style.css", profile_pic: Optional[str] = None, pdf_path: Optional[str] = None, custom_title: Optional[str] = None) -> str:
    """Generate modern, responsive, accessible HTML markup from parsed resume data."""
    header = data["header"]
    name = header.get("name", "Resume")
    page_title = custom_title or f"{name} &mdash; Portfolio &amp; Resume"
    
    # Action toolbar (PDF download & theme toggle)
    actions_html = []
    if pdf_path:
        actions_html.append(f'<a href="{pdf_path}" class="action-btn pdf-btn" download aria-label="Download Resume PDF">{ICONS["download"]}<span>Download PDF</span></a>')
    
    actions_html.append(f'''<button id="theme-toggle" class="theme-toggle-btn" aria-label="Toggle Color Theme" title="Toggle dark/light theme">
        {ICONS["sun"]}
        {ICONS["moon"]}
    </button>''')
    
    # Profile picture / Avatar
    avatar_html = ""
    if profile_pic:
        avatar_html = f'''<div class="avatar-wrapper">
            <img src="{profile_pic}" alt="{name}" class="avatar-img" />
        </div>'''
    
    # Contacts
    contacts_html = []
    for c in header.get("contacts", []):
        ctype = c["type"]
        icon = get_contact_icon(ctype)
        text = c["text"]
        url = c["url"]
        
        if url:
            contacts_html.append(f'<a href="{url}" class="contact-pill" target="_blank" rel="noopener noreferrer">{icon}<span>{text}</span></a>')
        else:
            contacts_html.append(f'<span class="contact-pill contact-static">{icon}<span>{text}</span></span>')
            
    contacts_block = "\n        ".join(contacts_html)
    
    # Sections
    sections_html = []
    for s in data["sections"]:
        sec_title = s["title"]
        sec_slug = re.sub(r'[^a-z0-9]+', '-', sec_title.lower()).strip('-')
        sec_icon = get_section_icon(sec_title)
        sec_type = s["type"]
        
        content_parts = []
        
        if sec_type == "skills":
            skills_cards = []
            for group in s.get("skills", []):
                cat = group["category"]
                tags = [f'<span class="skill-tag">{sk}</span>' for sk in group["skills"]]
                tags_html = "\n            ".join(tags)
                skills_cards.append(f'''<div class="skill-category-card">
            <h3 class="skill-category-name">{cat}</h3>
            <div class="skill-tags-group">
                {tags_html}
            </div>
        </div>''')
            content_parts.append(f'''<div class="skills-grid">
        {"".join(skills_cards)}
    </div>''')
            
        elif sec_type == "text":
            content_parts.append(f'<div class="prose-block">{s.get("text", "")}</div>')
            
        else:
            # Subheadings, Projects, Items
            items = s.get("items", [])
            for item in items:
                itype = item.get("type")
                if itype == "subheading":
                    title = item.get("title", "")
                    subtitle = item.get("subtitle", "")
                    location = item.get("location", "")
                    date = item.get("date", "")
                    bullets = item.get("bullets", [])
                    
                    bullets_html = ""
                    if bullets:
                        b_items = "\n            ".join([f'<li>{b}</li>' for b in bullets])
                        bullets_html = f'''<ul class="bullet-list">
            {b_items}
        </ul>'''
                    
                    meta_badges = []
                    if date:
                        meta_badges.append(f'<span class="meta-badge date-badge">{ICONS["calendar"]}<span>{date}</span></span>')
                    if location:
                        meta_badges.append(f'<span class="meta-badge loc-badge">{ICONS["map-pin"]}<span>{location}</span></span>')
                    meta_html = "\n            ".join(meta_badges)
                    
                    content_parts.append(f'''<article class="entry-card subheading-card">
        <div class="entry-header">
            <div class="entry-title-box">
                <h3 class="entry-title">{title}</h3>
                {f'<div class="entry-subtitle">{subtitle}</div>' if subtitle else ''}
            </div>
            {f'<div class="entry-meta-box">{meta_html}</div>' if meta_badges else ''}
        </div>
        {bullets_html}
    </article>''')
                    
                elif itype == "project":
                    title = item.get("title", "")
                    tech_stack = item.get("tech_stack", [])
                    date = item.get("date", "")
                    links = item.get("links", [])
                    bullets = item.get("bullets", [])
                    
                    tags_html = ""
                    if tech_stack:
                        tags = [f'<span class="tech-pill">{t}</span>' for t in tech_stack]
                        tags_html = f'<div class="tech-tags">{"".join(tags)}</div>'
                        
                    links_html = ""
                    if links:
                        links_html = f'<div class="project-links">{"".join(links)}</div>'
                        
                    bullets_html = ""
                    if bullets:
                        b_items = "\n            ".join([f'<li>{b}</li>' for b in bullets])
                        bullets_html = f'''<ul class="bullet-list">
            {b_items}
        </ul>'''
                        
                    content_parts.append(f'''<article class="entry-card project-card">
        <div class="entry-header">
            <div class="entry-title-box">
                <h3 class="project-title">{title}</h3>
                {links_html}
            </div>
            {f'<div class="entry-meta-box"><span class="meta-badge date-badge">{ICONS["calendar"]}<span>{date}</span></span></div>' if date else ''}
        </div>
        {tags_html}
        {bullets_html}
    </article>''')
                    
                elif itype == "item":
                    content_parts.append(f'''<div class="item-row">
        <div class="item-bullet-icon">&bull;</div>
        <div class="item-text">{item.get("text", "")}</div>
    </div>''')
                    
        body_content = "\n    ".join(content_parts)
        sections_html.append(f'''<section class="resume-section" id="{sec_slug}">
    <div class="section-title-wrapper">
        <div class="section-icon-box">{sec_icon}</div>
        <h2 class="section-heading">{sec_title}</h2>
        <div class="section-line"></div>
    </div>
    <div class="section-body">
        {body_content}
    </div>
</section>''')
        
    sections_joined = "\n\n".join(sections_html)
    
    html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <meta name="description" content="Resume and portfolio of {name}">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
    
    <link rel="stylesheet" href="{css_href}">
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    
    <!-- Floating Action Toolbar -->
    <aside class="action-toolbar" aria-label="Page Actions">
        {"".join(actions_html)}
    </aside>

    <div class="portfolio-container">
        <!-- Hero Header -->
        <header class="portfolio-header">
            <div class="header-main">
                {avatar_html}
                <div class="header-intro">
                    <h1 class="hero-name">{name}</h1>
                    <div class="contact-badges-list">
                        {contacts_block}
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Resume Content -->
        <main id="main-content" class="portfolio-main">
            {sections_joined}
        </main>

        <!-- Footer -->
        <footer class="portfolio-footer">
            <p>&copy; <span id="year"></span> {name}. Built with <a href="https://github.com/RaDu88253/easy-resume" target="_blank" rel="noopener noreferrer">Easy Resume</a>.</p>
        </footer>
    </div>

    <!-- Theme & Year Script -->
    <script>
        // Automatic Year
        document.getElementById('year').textContent = new Date().getFullYear();

        // Theme Toggle Script
        (function() {{
            const toggleBtn = document.getElementById('theme-toggle');
            if (!toggleBtn) return;

            function getInitialTheme() {{
                const saved = localStorage.getItem('theme');
                if (saved) return saved;
                return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            }}

            function applyTheme(theme) {{
                if (theme === 'dark') {{
                    document.documentElement.classList.add('dark-theme');
                    document.documentElement.classList.remove('light-theme');
                }} else {{
                    document.documentElement.classList.add('light-theme');
                    document.documentElement.classList.remove('dark-theme');
                }}
                localStorage.setItem('theme', theme);
            }}

            const current = getInitialTheme();
            applyTheme(current);

            toggleBtn.addEventListener('click', () => {{
                const isDark = document.documentElement.classList.contains('dark-theme');
                applyTheme(isDark ? 'light' : 'dark');
            }});

            // Listen for OS preference changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {{
                if (!localStorage.getItem('theme')) {{
                    applyTheme(e.matches ? 'dark' : 'light');
                }}
            }});
        }})();
    </script>
</body>
</html>
'''
    return html_doc

def find_default_profile_picture(base_dir: Path) -> Optional[str]:
    """Scan base_dir for standard profile picture names."""
    candidates = [
        "profile.jpg", "profile.jpeg", "profile.png", "profile.webp",
        "avatar.jpg", "avatar.jpeg", "avatar.png", "avatar.webp",
        "photo.jpg", "photo.jpeg", "photo.png", "photo.webp",
        "headshot.jpg", "headshot.png", "headshot.jpeg", "headshot.webp"
    ]
    for c in candidates:
        target = base_dir / c
        if target.exists():
            return c
    return None

def find_default_pdf(base_dir: Path, input_name: str) -> Optional[str]:
    """Check if a corresponding PDF exists."""
    stem = Path(input_name).stem
    candidates = [f"{stem}.pdf", "resume.pdf", "cv.pdf"]
    for c in candidates:
        target = base_dir / c
        if target.exists():
            return c
    return None

def main():
    parser = argparse.ArgumentParser(
        description="Compile a LaTeX resume (resume.tex) into a modern HTML portfolio (index.html) and PDF."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="resume.tex",
        help="Path to the input LaTeX resume file (default: resume.tex)"
    )
    parser.add_argument(
        "-o", "--output",
        default="index.html",
        help="Path to the output HTML file (default: index.html)"
    )
    parser.add_argument(
        "-c", "--css",
        default="style.css",
        help="Path or href to stylesheet (default: style.css)"
    )
    parser.add_argument(
        "-p", "--picture", "--photo", "--image",
        dest="picture",
        default=None,
        help="Path to user profile picture (e.g. profile.jpg). If omitted, automatically checks directory for common names."
    )
    parser.add_argument(
        "--no-auto-picture",
        action="store_true",
        help="Disable auto-detecting profile picture in directory."
    )
    parser.add_argument(
        "--pdf",
        default=None,
        help="Explicit path to resume PDF for download button. If not set, automatically compiles or checks directory."
    )
    parser.add_argument(
        "--no-pdf-compile",
        action="store_true",
        help="Skip automatic pdflatex compilation even if pdflatex is available."
    )
    parser.add_argument(
        "-t", "--title",
        default=None,
        help="Custom HTML page title."
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    base_dir = input_path.parent
    
    # Check for pdflatex and compile PDF automatically if available
    pdf_compiled_path, was_compiled = check_and_compile_pdf(input_path, skip_pdf=args.no_pdf_compile)
    
    # Read LaTeX
    try:
        latex_content = input_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        latex_content = input_path.read_text(encoding="latin-1")
        
    print(f"[*] Parsing '{input_path}'...")
    resume_data = parse_resume_latex(latex_content)
    
    # Determine profile picture
    picture = args.picture
    if not picture and not args.no_auto_picture:
        picture = find_default_profile_picture(base_dir)
        if picture:
            print(f"[*] Detected profile picture: '{picture}'")
            
    # Determine PDF download link
    pdf_file = args.pdf
    if not pdf_file:
        if pdf_compiled_path and pdf_compiled_path.exists():
            pdf_file = pdf_compiled_path.name
        else:
            pdf_file = find_default_pdf(base_dir, input_path.name)
            
    if pdf_file:
        print(f"[*] Linking PDF download: '{pdf_file}'")
        # Check if LaTeX file is newer than the linked PDF
        check_pdf_staleness(input_path, base_dir / pdf_file)
    else:
        check_pdf_staleness(input_path, None)
            
    # Generate HTML
    output_html = generate_html(
        data=resume_data,
        css_href=args.css,
        profile_pic=picture,
        pdf_path=pdf_file,
        custom_title=args.title
    )
    
    out_path = Path(args.output)
    out_path.write_text(output_html, encoding="utf-8")
    print(f"[OK] Successfully generated '{out_path}'!")

if __name__ == "__main__":
    main()

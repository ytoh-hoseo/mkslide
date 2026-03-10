import hashlib
import re
import subprocess
from pathlib import Path

ABSOLUTE_UNITS = ("mm", "cm", "pt", "in", "ex", "em")
VALID_SIZES = {
    "tiny", "scriptsize", "footnotesize", "small",
    "normalsize", "large", "Large", "LARGE", "huge", "Huge",
}


def parse_dim_attr(attrs: str, key: str) -> str:
    """Parse width or height attribute. Returns LaTeX dimension string.

    width=0.7    -> '0.7\\linewidth'
    width=80mm   -> '80mm'
    height=0.5   -> '0.5\\textheight'
    Default (not specified): '!' (auto in \\resizebox)
    """
    relative_base = r"\textheight" if key == "height" else r"\linewidth"
    unit_pattern = "|".join(ABSOLUTE_UNITS)

    m = re.search(rf"\b{key}\s*=\s*([0-9]*\.?[0-9]+)({unit_pattern})\b", attrs or "")
    if m:
        return f"{m.group(1)}{m.group(2)}"

    m = re.search(rf"\b{key}\s*=\s*([0-9]*\.?[0-9]+)\b", attrs or "")
    if m:
        val = max(0.01, min(float(m.group(1)), 2.0))
        return rf"{val}{relative_base}"

    return "!"


def parse_float_attr(attrs: str, key: str, default: float) -> float:
    """Parse a named float attribute from an attribute string."""
    m = re.search(rf"\b{re.escape(key)}\s*=\s*([0-9]*\.?[0-9]+)\b", attrs or "")
    if not m:
        return default
    try:
        return float(m.group(1))
    except ValueError:
        return default


def _ensure_pdf(dot_src: str, h: str, graphdir: str) -> None:
    """Render *dot_src* to a PDF file named *h*.pdf inside *graphdir*.

    Skips rendering if the file already exists (content-addressed cache).
    """
    pdf_path = Path(graphdir) / f"{h}.pdf"
    if pdf_path.exists():
        return
    p = subprocess.run(
        ["dot", "-Tpdf", "-o", str(pdf_path)],
        input=dot_src, capture_output=True, text=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"dot failed (rc={p.returncode}):\n{p.stderr}")


def _replace_dot_blocks(text: str, graphdir: str) -> str:
    """Replace ```{.dot ...} fenced code blocks with \\includegraphics LaTeX."""
    pattern = re.compile(
        r"```(?:\{\.dot(?P<attrs>[^\}]*)\}|dot)\s*\n(?P<body>.*?)\n```",
        re.DOTALL,
    )

    def repl(m: re.Match) -> str:
        attrs = (m.group("attrs") or "").strip()
        dot_src = m.group("body")

        h = hashlib.sha1(dot_src.encode("utf-8")).hexdigest()
        _ensure_pdf(dot_src, h, graphdir)

        width_str = parse_dim_attr(attrs, "width")
        height_str = parse_dim_attr(attrs, "height")
        has_width = width_str != "!"
        has_height = height_str != "!"

        if has_width or has_height:
            opts = []
            if has_width:
                opts.append(f"width={width_str}")
            if has_height:
                opts.append(f"height={height_str}")
            if has_width and has_height:
                opts.append("keepaspectratio")
        else:
            scale = parse_float_attr(attrs, "scale", 1.0)
            if scale != 1.0:
                opts = [f"scale={max(0.01, min(scale, 5.0))}"]
            else:
                opts = [r"width=\linewidth"]

        opts_str = ",".join(opts)
        return "\n".join([
            "```{=tex}",
            r"\begin{center}",
            rf"\includegraphics[{opts_str}]{{graphs/{h}.pdf}}",
            r"\end{center}",
            "```",
            "",
        ])

    return pattern.sub(repl, text)


def _resolve_image_paths(text: str, md_dir: str) -> str:
    """Rewrite relative image paths to absolute paths based on the source markdown directory.

    Needed because the preprocessed .md is written to a temp dir, so relative
    paths would be resolved against that temp dir by both pandoc and latexmk.
    """
    def repl(m: re.Match) -> str:
        alt = m.group(1)
        path = m.group(2)
        attrs = m.group(3) or ""
        if path.startswith(("http://", "https://", "/", "\\")):
            return m.group(0)
        # LaTeX/pandoc expect forward slashes
        fwd = str((Path(md_dir) / path).resolve()).replace("\\", "/")
        return f"![{alt}]({fwd}){attrs}"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?", repl, text)


def _replace_beamer_blocks(text: str) -> str:
    """Convert :::{.alertblock} and :::{.exampleblock} fenced divs to raw LaTeX.

    Pandoc incorrectly maps these to \\begin{block} instead of the proper
    Beamer environments. Title is taken from a leading heading inside the div.

    Uses a line-by-line depth-tracking parser so that nested fenced divs
    inside the body do not confuse the closing fence detection.

    Rendering depends on the heading pattern:
      - "#### Title"  → full block with title bar
      - "####" (bare) + body → thin colored bar + body (no empty title bar)
      - "####" (bare) alone  → thin colored separator line only
      - no heading + body    → full block with empty title
    """
    # Opening fence: handles {.alertblock}, {alertblock}, bare alertblock
    _open = re.compile(
        r"^(:{3,})\s*(?:\{\.?(alertblock|exampleblock)[^}]*\}|(alertblock|exampleblock))\s*$"
    )
    _any_open = re.compile(r"^:{3,}\s*\S")   # inner fenced div opening
    _any_close = re.compile(r"^:{3,}\s*$")   # any fenced div closing

    lines = text.split("\n")
    result: list[str] = []
    i = 0

    while i < len(lines):
        m = _open.match(lines[i])
        if not m:
            result.append(lines[i])
            i += 1
            continue

        env = m.group(2) or m.group(3)
        i += 1
        body_lines: list[str] = []
        depth = 1

        # Collect body lines until the matching closing fence
        while i < len(lines) and depth > 0:
            line = lines[i]
            if _any_open.match(line):
                depth += 1
                body_lines.append(line)
            elif _any_close.match(line):
                depth -= 1
                if depth > 0:
                    body_lines.append(line)
                # depth == 0: matching closing fence — discard it
            else:
                body_lines.append(line)
            i += 1

        # Extract optional title from the leading heading line.
        # "####" alone (no text) is discarded so pandoc cannot turn it into
        # \begin{block}{} inside our environment.
        title = ""
        if body_lines:
            hm = re.match(r"#{1,6}[ \t]+(.+)", body_lines[0])
            if hm:
                title = hm.group(1).strip()
                body_lines = body_lines[1:]
            elif re.match(r"#{1,6}[ \t]*$", body_lines[0]):
                body_lines = body_lines[1:]  # bare marker, no title text
            # Strip leading blank lines after consuming the heading
            while body_lines and not body_lines[0].strip():
                body_lines.pop(0)

        body = "\n".join(body_lines)

        # Beamer color names for this environment
        t_box = "block title alerted" if env == "alertblock" else "block title example"
        b_box = "block body alerted" if env == "alertblock" else "block body example"
        # Thin colored bar (1.5 pt) — reused for both the separator and no-title cases
        thin_bar = rf"\begin{{beamercolorbox}}[wd=\linewidth,dp=0.25ex,ht=1.5pt]{{{t_box}}}\end{{beamercolorbox}}"

        if not body.strip():
            # No body → colored separator line only
            result += ["```{=tex}", thin_bar, "```"]
        elif not title:
            # Body without title → thin bar + body in color box
            result += [
                "```{=tex}",
                thin_bar,
                rf"\begin{{beamercolorbox}}[wd=\linewidth,sep=0.5em]{{{b_box}}}",
                "```",
                body,
                "```{=tex}",
                r"\end{beamercolorbox}",
                "```",
            ]
        else:
            # Full block with title
            result += [
                "```{=tex}",
                f"\\begin{{{env}}}{{{title}}}",
                "```",
                body,
                "```{=tex}",
                f"\\end{{{env}}}",
                "```",
            ]

    return "\n".join(result)


def _replace_fontsize_blocks(text: str) -> str:
    """Wrap code blocks that carry a fontsize= attribute in LaTeX \\begingroup/\\endgroup."""
    code_pat = re.compile(
        r"^(`{3,})\{(?P<attrs>[^\}]+)\}\n(?P<body>.*?)\n\1",
        re.DOTALL | re.MULTILINE,
    )

    def repl(m: re.Match) -> str:
        attrs = m.group("attrs")
        body = m.group("body")
        ticks = m.group(1)

        fs = re.search(r"\bfontsize=(\w+)\b", attrs)
        if not fs or fs.group(1) not in VALID_SIZES:
            return m.group(0)

        size = fs.group(1)
        clean = re.sub(r"\s*fontsize=\w+", "", attrs).strip()

        return (
            "```{=tex}\n"
            f"\\begingroup\\{size}\n"
            "```\n"
            f"{ticks}{{{clean}}}\n"
            f"{body}\n"
            f"{ticks}\n"
            "```{=tex}\n"
            "\\endgroup\n"
            "```"
        )

    return code_pat.sub(repl, text)


def preprocess(md_in: str, out_md: str, graphdir: str) -> None:
    """Preprocess markdown before pandoc:
      - dot code blocks → Graphviz PDF + \\includegraphics
      - alertblock/exampleblock fenced divs → raw LaTeX Beamer environments
      - fontsize= attributes on code blocks → LaTeX \\begingroup wrappers
      - relative image paths → absolute paths
    """
    Path(graphdir).mkdir(parents=True, exist_ok=True)
    in_path = Path(md_in)
    text = in_path.read_text(encoding="utf-8")
    text = _replace_dot_blocks(text, graphdir)
    text = _replace_beamer_blocks(text)
    text = _replace_fontsize_blocks(text)
    text = _resolve_image_paths(text, str(in_path.parent))
    Path(out_md).write_text(text, encoding="utf-8")

import hashlib
import os
import re
import subprocess
import pathlib

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
    m = re.search(rf"\b{re.escape(key)}\s*=\s*([0-9]*\.?[0-9]+)\b", attrs or "")
    if not m:
        return default
    try:
        return float(m.group(1))
    except ValueError:
        return default


def _ensure_pdf(dot_src: str, h: str, graphdir: str) -> None:
    dot_path = os.path.join(graphdir, f"{h}.dot")
    pdf_path = os.path.join(graphdir, f"{h}.pdf")
    log_path = os.path.join(graphdir, f"{h}.dot.log")

    if os.path.exists(pdf_path):
        return

    pathlib.Path(dot_path).write_text(dot_src, encoding="utf-8")
    with open(log_path, "w", encoding="utf-8") as log:
        p = subprocess.run(
            ["dot", "-Tpdf", "-o", pdf_path, dot_path],
            stdout=log, stderr=subprocess.STDOUT, text=True,
        )
    if p.returncode != 0:
        raise RuntimeError(f"dot failed (rc={p.returncode}). See: {log_path}")


def _replace_dot_blocks(text: str, graphdir: str) -> str:
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

    Needed because the preprocessed .md is written to output/, so relative paths
    would be resolved against output/ by both pandoc and latexmk.
    """
    def repl(m: re.Match) -> str:
        alt = m.group(1)
        path = m.group(2)
        attrs = m.group(3) or ""
        if path.startswith(("http://", "https://", "/", "\\")):
            return m.group(0)
        abs_path = pathlib.Path(md_dir) / path
        # LaTeX/pandoc expect forward slashes
        fwd = str(abs_path.resolve()).replace("\\", "/")
        return f"![{alt}]({fwd}){attrs}"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?", repl, text)


def _replace_fontsize_blocks(text: str) -> str:
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
    """Preprocess markdown: dot blocks → TikZ, fontsize attrs → LaTeX wrappers,
    relative image paths → absolute paths."""
    os.makedirs(graphdir, exist_ok=True)
    in_path = pathlib.Path(md_in)
    text = in_path.read_text(encoding="utf-8")
    text = _replace_dot_blocks(text, graphdir)
    text = _replace_fontsize_blocks(text)
    text = _resolve_image_paths(text, str(in_path.parent))
    pathlib.Path(out_md).write_text(text, encoding="utf-8")

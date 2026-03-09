import re
import shutil
import subprocess
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_LOGO = DATA_DIR / "school-mark.pdf"
PREAMBLE_TEMPLATE = DATA_DIR / "preamble-ko.inc.tex"

# Pandoc variables applied only when not defined in YAML front matter or --var
DEFAULT_VARS = {
    "mainfont": "NanumSquareRound",
    "monofont": "NanumGothicCoding",
}


def _check_deps() -> None:
    missing = [cmd for cmd in ("pandoc", "dot", "latexmk") if shutil.which(cmd) is None]
    if missing:
        sys.exit(f"Error: missing required tools: {', '.join(missing)}")


def _yaml_front_matter_keys(md_path: Path) -> set:
    """Return top-level keys defined in the YAML front matter of a markdown file."""
    text = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---[ \t]*\n(.*?)\n(?:---|\.\.\.)[ \t]*\n", text, re.DOTALL)
    if not m:
        return set()
    keys = set()
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:", line)
        if km:
            keys.add(km.group(1))
    return keys


def _logo_latex_path(logo: Path) -> str:
    """Return forward-slash path without .pdf extension for LaTeX \\includegraphics."""
    s = str(logo.resolve()).replace("\\", "/")
    if s.endswith(".pdf"):
        s = s[:-4]
    return s


def build(md_input: str, output_dir: str = None, logo: str = None, vars: list = None) -> None:
    _check_deps()

    in_path = Path(md_input).resolve()
    if not in_path.exists():
        sys.exit(f"Error: file not found: {md_input}")

    out_dir = Path(output_dir).resolve() if output_dir else Path.cwd() / "output"
    graph_dir = out_dir / "graphs"
    out_dir.mkdir(parents=True, exist_ok=True)
    graph_dir.mkdir(parents=True, exist_ok=True)

    logo_path = Path(logo).resolve() if logo else DEFAULT_LOGO
    if not logo_path.exists():
        sys.exit(f"Error: logo file not found: {logo_path}")

    base = in_path.stem
    tmp_md = out_dir / f"{base}.with_graphs.md"
    tex_path = out_dir / f"{base}.tex"
    pdf_path = out_dir / f"{base}.pdf"

    # 1) Preprocess: dot→TikZ, fontsize
    from mkslide.preprocess import preprocess
    print(f"[1/4] Preprocessing {in_path.name} ...")
    preprocess(str(in_path), str(tmp_md), str(graph_dir))

    # 2) Generate preamble with injected logo path
    print("[2/4] Generating preamble ...")
    preamble_content = PREAMBLE_TEMPLATE.read_text(encoding="utf-8")
    preamble_content = preamble_content.replace("@@LOGO_PATH@@", _logo_latex_path(logo_path))
    preamble_tmp = out_dir / "preamble-ko.inc.tex"
    preamble_tmp.write_text(preamble_content, encoding="utf-8")

    # 3) Pandoc → Beamer .tex
    print("[3/4] Running pandoc ...")
    pandoc_cmd = [
        "pandoc",
        "-t", "beamer",
        "--standalone",
        "--slide-level=2",
        "-H", str(preamble_tmp),
    ]
    # Apply defaults only for keys absent from both YAML front matter and --var
    yaml_keys = _yaml_front_matter_keys(in_path)
    cli_keys = {v.split("=", 1)[0] for v in (vars or [])}
    for key, val in DEFAULT_VARS.items():
        if key not in yaml_keys and key not in cli_keys:
            pandoc_cmd.extend(["-V", f"{key}={val}"])
    for v in (vars or []):
        pandoc_cmd.extend(["-V", v])
    pandoc_cmd.extend([str(tmp_md), "-o", str(tex_path)])
    subprocess.run(pandoc_cmd, check=True)

    # 4) Postprocess: remove empty frames
    from mkslide.postprocess import postprocess
    postprocess(str(tex_path))

    # 5) latexmk → PDF
    print("[4/4] Running latexmk ...")
    subprocess.run(
        ["latexmk", "-lualatex", "-interaction=nonstopmode", "-g", f"{base}.tex"],
        cwd=str(out_dir),
        check=True,
    )

    print(f"\nGenerated:")
    print(f"  {tmp_md}")
    print(f"  {tex_path}")
    print(f"  {pdf_path}")


def clean(output_dir: str = None, remove_pdfs: bool = False) -> None:
    out_dir = Path(output_dir).resolve() if output_dir else Path.cwd() / "output"

    if not out_dir.exists():
        print(f"Nothing to clean ({out_dir} does not exist).")
        return

    print(f"Cleaning {out_dir}/ ...")

    subprocess.run(["latexmk", "-C"], cwd=str(out_dir), capture_output=True)

    aux_patterns = [
        "*.with_graphs.md", "*.tex", "*.aux", "*.log", "*.nav", "*.snm",
        "*.toc", "*.out", "*.fls", "*.fdb_latexmk", "*.synctex.gz",
    ]
    for pat in aux_patterns:
        for f in out_dir.glob(pat):
            f.unlink(missing_ok=True)

    if remove_pdfs:
        for f in out_dir.glob("*.pdf"):
            f.unlink(missing_ok=True)

    graph_dir = out_dir / "graphs"
    if graph_dir.exists():
        for pat in ("*.pdf", "*.dot", "*.dot.log"):
            for f in graph_dir.glob(pat):
                f.unlink(missing_ok=True)

    print("Clean done.")

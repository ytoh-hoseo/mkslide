import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from mkslide.postprocess import postprocess
from mkslide.preprocess import preprocess

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_LOGO = DATA_DIR / "school-mark.pdf"
PREAMBLE_TEMPLATE = DATA_DIR / "preamble-ko.inc.tex"

# Pandoc variables applied only when not defined in YAML front matter or --var
DEFAULT_VARS = {
    "mainfont": "NanumSquareRound",
    "monofont": "NanumGothicCoding",
}

# Image subdirectories copied into the tmp working dir so relative paths resolve
IMAGE_DIRS = ("figs", "figures", "images", "img")


def _check_deps() -> None:
    missing = [cmd for cmd in ("pandoc", "dot", "latexmk") if shutil.which(cmd) is None]
    if missing:
        sys.exit(f"Error: missing required tools: {', '.join(missing)}")


def _yaml_front_matter_keys(md_path: Path) -> set[str]:
    """Return top-level keys defined in the YAML front matter of a markdown file."""
    text = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---[ \t]*\n(.*?)\n(?:---|\.\.\.)[ \t]*\n", text, re.DOTALL)
    if not m:
        return set()
    keys: set[str] = set()
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:", line)
        if km:
            keys.add(km.group(1))
    return keys


def _logo_latex_path(logo: Path) -> str:
    """Return forward-slash path without .pdf extension for LaTeX \\includegraphics."""
    s = str(logo.resolve()).replace("\\", "/")
    return s.removesuffix(".pdf")


def _get_work_tmp(use_ramdisk: bool) -> Path:
    """Return a temp working directory: /dev/shm on Linux when available, else system tmp."""
    if use_ramdisk and platform.system() == "Linux":
        shm = Path("/dev/shm")
        if shm.is_dir():
            return Path(tempfile.mkdtemp(dir=shm, prefix="mkslide_"))
    return Path(tempfile.mkdtemp(prefix="mkslide_"))


def build(
    md_input: str,
    output_dir: str | None = None,
    logo: str | None = None,
    pandoc_vars: list[str] | None = None,
    use_ramdisk: bool = True,
    debug: bool = False,
) -> None:
    _check_deps()

    in_path = Path(md_input).resolve()
    if not in_path.exists():
        sys.exit(f"Error: file not found: {md_input}")

    out_dir = Path(output_dir).resolve() if output_dir else Path.cwd() / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    logo_path = Path(logo).resolve() if logo else DEFAULT_LOGO
    if not logo_path.exists():
        sys.exit(f"Error: logo file not found: {logo_path}")

    base = in_path.stem
    tmp = _get_work_tmp(use_ramdisk)
    note = " (ramdisk)" if str(tmp).startswith("/dev/shm") else ""

    try:
        graph_dir = tmp / "graphs"
        graph_dir.mkdir()
        tmp_md = tmp / f"{base}.with_graphs.md"
        tex_path = tmp / f"{base}.tex"

        # Copy image subdirectories into tmp so relative paths resolve during latexmk
        for img_dir in IMAGE_DIRS:
            src = in_path.parent / img_dir
            if src.is_dir():
                shutil.copytree(src, tmp / img_dir)
                if debug:
                    shutil.copytree(src, out_dir / img_dir, dirs_exist_ok=True)

        # 1) Preprocess: dot→PDF, beamer blocks, fontsize, image paths
        print(f"[1/4] Preprocessing {in_path.name} ...{note}")
        preprocess(str(in_path), str(tmp_md), str(graph_dir))
        if debug:
            shutil.copy2(tmp_md, out_dir / f"{base}.with_graphs.md")
            debug_graphs = out_dir / "graphs"
            debug_graphs.mkdir(exist_ok=True)
            for f in graph_dir.iterdir():
                shutil.copy2(f, debug_graphs / f.name)
            print(f"  [debug] {out_dir / f'{base}.with_graphs.md'}")
            print(f"  [debug] {out_dir / 'graphs/'}")

        # 2) Generate preamble with injected logo path
        print("[2/4] Generating preamble ...")
        preamble_tmp = tmp / "preamble-ko.inc.tex"
        preamble_tmp.write_text(
            PREAMBLE_TEMPLATE.read_text(encoding="utf-8").replace(
                "@@LOGO_PATH@@", _logo_latex_path(logo_path)
            ),
            encoding="utf-8",
        )

        # 3) Pandoc → Beamer .tex
        print("[3/4] Running pandoc ...")
        pandoc_cmd = [
            "pandoc", "-t", "beamer", "--standalone", "--slide-level=2",
            "-H", str(preamble_tmp),
        ]
        yaml_keys = _yaml_front_matter_keys(in_path)
        cli_keys = {v.split("=", 1)[0] for v in (pandoc_vars or [])}
        for key, val in DEFAULT_VARS.items():
            if key not in yaml_keys and key not in cli_keys:
                pandoc_cmd.extend(["-V", f"{key}={val}"])
        for v in pandoc_vars or []:
            pandoc_cmd.extend(["-V", v])
        pandoc_cmd.extend([str(tmp_md), "-o", str(tex_path)])
        subprocess.run(pandoc_cmd, check=True)

        # 4) Postprocess: remove empty frames
        postprocess(str(tex_path))
        if debug:
            shutil.copy2(tex_path, out_dir / f"{base}.tex")
            print(f"  [debug] {out_dir / f'{base}.tex'}")

        # 5) latexmk → PDF
        print(f"[4/4] Running latexmk ...{note}")
        subprocess.run(
            ["latexmk", "-lualatex", "-interaction=nonstopmode", "-g", f"{base}.tex"],
            cwd=str(tmp),
            check=True,
        )

        # Copy final PDF to output directory
        pdf_path = out_dir / f"{base}.pdf"
        shutil.copy2(tmp / f"{base}.pdf", pdf_path)
        print(f"\nGenerated: {pdf_path}")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def clean(output_dir: str | None = None, remove_pdfs: bool = False) -> None:
    out_dir = Path(output_dir).resolve() if output_dir else Path.cwd() / "output"

    if not out_dir.exists():
        print(f"Nothing to clean ({out_dir} does not exist).")
        return

    print(f"Cleaning {out_dir}/ ...")

    # Remove debug artifacts (tex, preprocessed md)
    for pat in ("*.tex", "*.with_graphs.md"):
        for f in out_dir.glob(pat):
            f.unlink(missing_ok=True)

    # Remove debug artifact directories
    for d in ("graphs", *IMAGE_DIRS):
        artifact_dir = out_dir / d
        if artifact_dir.exists():
            shutil.rmtree(artifact_dir)

    if remove_pdfs:
        for f in out_dir.glob("*.pdf"):
            f.unlink(missing_ok=True)

    print("Clean done.")

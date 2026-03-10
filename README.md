# mkslide-hoseo

Markdown 파일을 호서대학교 스타일의 Beamer PDF 슬라이드로 변환하는 CLI 도구입니다.

## 변환 파이프라인

```
Markdown (.md)
  → [전처리] dot 블록 → PDF, fontsize 속성 → LaTeX 래퍼, 이미지 상대경로 → 절대경로
  → [pandoc] Beamer .tex 생성
  → [후처리] 빈 프레임 제거
  → [latexmk] PDF 컴파일
```

## 의존성

다음 도구들이 시스템에 설치되어 있어야 합니다.

| 도구 | 역할 |
|------|------|
| `pandoc` | Markdown → Beamer `.tex` 변환 |
| `dot` (Graphviz) | DOT 그래프 → PDF 변환 |
| `latexmk` | LuaLaTeX 기반 PDF 컴파일 |

LuaLaTeX 환경에서 다음 LaTeX 패키지가 필요합니다: `kotex`, `tikz`, `emoji`, `textpos`, `algorithm`, `algpseudocode`, `metropolis` 테마.

## 설치

```bash
pip install .
```

또는 개발 모드로 설치:

```bash
pip install -e .
```

## 사용법

```
mkslide <input.md> [옵션]
mkslide clean [옵션]
```

### 슬라이드 빌드

```bash
# 기본 빌드 (output/ 디렉토리에 결과 생성)
mkslide week01.md

# 출력 디렉토리 지정
mkslide week01.md --output-dir /tmp/slides

# 로고 파일 지정
mkslide week01.md --logo /path/to/logo.pdf

# pandoc 변수 직접 전달 (YAML front matter 대신 또는 덮어쓰기)
mkslide week01.md --var mainfont=NanumSquareRound --var monofont=NanumGothicCoding
mkslide week01.md --var fontsize=11pt --var aspectratio=169
```

### 빌드 아티팩트 정리

```bash
# 중간 파일만 삭제 (.tex, .aux 등)
mkslide clean

# 중간 파일 + 생성된 PDF 모두 삭제
mkslide clean --all

# 출력 디렉토리 지정하여 정리
mkslide clean --output-dir /tmp/slides
```

### 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--output-dir DIR` | `./output` | 출력 디렉토리 |
| `--logo PDF` | 내장 교표 | 로고 PDF 파일 경로 |
| `--var KEY=VALUE` | — | pandoc 변수 전달 (`-V`), 반복 사용 가능 |
| `--debug` | `False` | 각 단계 완료 시 중간 파일(`.with_graphs.md`, `.tex`, `graphs/`)을 output dir에 즉시 저장 (에러 발생 시에도 확인 가능) |
| `--no-ramdisk` | — | RAM disk 가속 비활성화 (Linux 전용) |
| `--all` | `False` | `clean` 시 PDF도 함께 삭제 |

### pandoc 변수 (`--var`)

Markdown YAML front matter에 선언하거나, CLI에서 `--var`로 전달할 수 있습니다. 둘 다 지정하면 CLI가 우선합니다.

```yaml
# YAML front matter로 지정 (파일 내)
---
mainfont: NanumSquareRound
monofont: NanumGothicCoding
fontsize: 11pt
aspectratio: 169
toc: false
---
```

```bash
# CLI로 지정 (YAML 없이, 또는 덮어쓰기)
mkslide week01.md --var mainfont=NanumSquareRound --var aspectratio=43
```

## Markdown 작성 규칙

`pandoc` Beamer 변환 규칙을 따릅니다 (`--slide-level=2`).

- `#` : 섹션 구분
- `##` : 슬라이드(프레임) 제목

```markdown
# 1장. 소개

## 개요

- 항목 1
- 항목 2

## 예시 코드

```python
print("Hello, World!")
` ``
```

### 이미지 삽입

Markdown 파일과 같은 디렉토리에 있는 이미지는 절대 경로로 자동 변환됩니다.

```markdown
![캡션](fig.jpg)
![캡션](fig.png){width=0.6}
```

다음 이미지 하위 디렉토리는 빌드 시 자동으로 작업 디렉토리에 복사되어 상대 경로가 그대로 동작합니다.

| 디렉토리 | 용도 |
|----------|------|
| `figs/` | LaTeX 논문 전통 |
| `figures/` | 학술 문서 |
| `images/` | 일반적 |
| `img/` | 단축형 |

```
slide.md
figs/
├── diagram.png
└── photo.jpg
```

```markdown
![다이어그램](figs/diagram.png)
![사진](figs/photo.jpg){width=0.5}
```

raw LaTeX 블록에서의 직접 참조도 동작합니다.

````markdown
```{=tex}
\includegraphics[width=0.6\linewidth]{figs/diagram.png}
```
````

### Beamer 블록 환경

pandoc이 `alertblock`/`exampleblock`을 `\begin{block}`으로 잘못 변환하는 버그를 전처리 단계에서 수정합니다.

| 문법 | LaTeX 출력 |
|------|-----------|
| `:::{.block}` | `\begin{block}{...}` (pandoc 기본) |
| `:::{.alertblock}` | `\begin{alertblock}{...}` ✓ |
| `:::{.exampleblock}` | `\begin{exampleblock}{...}` ✓ |

제목은 div 안의 첫 번째 heading(`#`~`######`)으로 지정합니다. heading 형태에 따라 렌더링이 달라집니다.

| 마크다운 패턴 | 렌더링 |
|---|---|
| `#### 제목 텍스트` + 본문 | 제목 있는 alertblock |
| `####` (텍스트 없음) + 본문 | **얇은 색상 선** + 본문 (빈 제목 바 없음) |
| `####` (텍스트 없음)만 | **색상 구분선**만 |
| heading 없음 + 본문 | 제목 없는 alertblock |

```markdown
:::{.alertblock}
#### 주의
이 내용은 제목 있는 alertblock으로 렌더링됩니다.
:::

:::{.alertblock}
####
제목 없이 얇은 선 + 본문으로 렌더링됩니다.
:::

:::{.alertblock}
####
:::

:::{.exampleblock}
#### 예시
exampleblock도 동일한 규칙이 적용됩니다.
:::
```

### DOT 그래프 삽입

코드 블록 언어를 `dot`으로 지정하면 Graphviz가 PDF로 렌더링해 삽입합니다.

````markdown
```{.dot width=0.6}
digraph G {
    A -> B -> C;
}
```
````

**크기 속성:**
- `width=0.7` → `0.7\linewidth` (비율)
- `width=80mm` → `80mm` (절대값)
- `height=0.5` → `0.5\textheight`
- `scale=1.5` → 스케일 배율

### 코드 블록 폰트 크기 지정

`fontsize` 속성으로 코드 블록의 글자 크기를 조절할 수 있습니다.

````markdown
```{.python fontsize=small}
# 작은 글씨로 표시되는 코드
very_long_code_here()
```
````

지원 크기: `tiny`, `scriptsize`, `footnotesize`, `small`, `normalsize`, `large`, `Large`, `LARGE`, `huge`, `Huge`

## 출력 구조

기본 빌드 시 PDF만 저장됩니다. `--debug` 옵션을 사용하면 각 단계 완료 직후 중간 파일도 함께 저장됩니다.

```
output/
├── week01.pdf              # 최종 PDF 슬라이드 (항상 생성)
│
│   # --debug 시 추가 저장 (단계별로 즉시 저장, 에러 발생 시에도 확인 가능)
├── week01.with_graphs.md   # 전처리된 Markdown  ← [1/4] 전처리 후
├── week01.tex              # pandoc 생성 Beamer 소스  ← [3/4] pandoc 후
└── graphs/
    └── <sha1>.pdf          # DOT 그래프 렌더링 결과  ← [1/4] 전처리 후
```

## 슬라이드 스타일

- 테마: [Metropolis](https://github.com/matze/mtheme)
- 강조색: `#B71C1C` (딥 레드)
- 진행바: 프레임 제목 하단
- 로고: 슬라이드 좌하단 고정 (제목 슬라이드 제외)
- 한글 지원: `kotex` (LuaLaTeX)

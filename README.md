# mkslide-hoseo

Markdown 파일을 호서대학교 스타일의 Beamer PDF 슬라이드로 변환하는 CLI 도구입니다.

## 변환 파이프라인

```
Markdown (.md)
  → [전처리] dot 블록 → PDF, block 옵션/fontsize 속성 → LaTeX 래퍼, 이미지 상대경로 → 절대경로
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
| `--debug` | `False` | 중간 파일(`.with_graphs.md`, `.tex`, `.log`, `graphs/`)을 output dir에 저장 (`.log`는 LaTeX 실패 시에도 보존) |
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

Markdown 링크(`[텍스트](URL)`)와 직접 작성한 `\href{URL}{텍스트}`는 기본적으로 파란색 밑줄로 표시됩니다. URL 자체는 파란색으로, 목차를 비롯한 문서 내부 링크는 검은색으로 표시됩니다. 링크 색상은 YAML front matter나 `--var`의 `urlcolor`, `linkcolor`, `citecolor`, `filecolor`로 변경할 수 있습니다.

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

### 사용자 정의 LaTeX 명령

아래 명령은 preamble에 기본으로 포함되므로 Markdown 본문에서 바로 사용할 수 있습니다.

#### 의미 기반 강조

| 명령 | 용도 | 색상 |
|------|------|------|
| `\critical{텍스트}` | 오류, 반드시 확인할 내용 | 빨강 |
| `\concept{텍스트}` | 정보, 주요 개념 | 파랑 |
| `\positive{텍스트}` | 성공, 긍정적인 결과 | 초록 |
| `\caution{텍스트}` | 주의, 참고 사항 | 주황 |
| `\muted{텍스트}` | 부가 설명, 덜 중요한 내용 | 회색 |

명령 이름은 표현 색상이 아니라 내용의 의미를 나타냅니다. 따라서 테마 색상이 바뀌어도 Markdown을 수정할 필요가 없습니다. 기본형은 굵게 표시되며, `[normal]` 옵션을 지정하면 색상은 유지하고 보통 굵기로 표시합니다.

```markdown
\critical{반드시 직접 계산·확인하세요.}
\concept{굵게 표시되는 핵심 개념}
\concept[normal]{보통 굵기로 표시되는 핵심 개념}
```

#### 색상 직선 밑줄

`\coloruline`은 본문 글자색을 유지하면서 직선 밑줄에만 색상을 적용합니다. 기본 밑줄 색상은 `mainred`이며 선택 인자로 다른 색상을 지정할 수 있습니다.

```markdown
\coloruline{빨간색 직선 밑줄}
\coloruline[mainblue]{파란색 직선 밑줄}
\coloruline[maingreen]{초록색 직선 밑줄}
```

자주 사용하는 세 색상은 단축 명령으로도 사용할 수 있습니다.

```markdown
\reduline{빨간색 직선 밑줄}
\blueuline{파란색 직선 밑줄}
\greenuline{초록색 직선 밑줄}
```

#### 색상 물결 밑줄

`\coloruwave`는 본문 글자색을 유지하면서 물결 밑줄에만 색상을 적용합니다. 기본 밑줄 색상은 `mainred`이며 선택 인자로 다른 색상을 지정할 수 있습니다.

```markdown
\coloruwave{빨간색 물결 밑줄}
\coloruwave[mainblue]{파란색 물결 밑줄}
\coloruwave[maingreen]{초록색 물결 밑줄}
```

자주 사용하는 세 색상은 단축 명령으로도 사용할 수 있습니다.

```markdown
\reduwave{빨간색 물결 밑줄}
\blueuwave{파란색 물결 밑줄}
\greenuwave{초록색 물결 밑줄}
```

#### 세로 구분선

`\columnbar`는 세로 구분선을 삽입합니다. 기본 좌우 간격은 각각 `0.5em`, `1em`이며 `left`, `right` 옵션으로 개별 조정할 수 있습니다.

```markdown
왼쪽 항목\columnbar 오른쪽 항목
왼쪽 항목\columnbar[left=0.2em] 오른쪽 항목
왼쪽 항목\columnbar[right=2em] 오른쪽 항목
왼쪽 항목\columnbar[left=0pt,right=1.5em] 오른쪽 항목
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

#### 공통 block 옵션

`.block`, `.alertblock`, `.exampleblock`에는 다음 옵션을 공통으로 사용할 수 있습니다. 옵션의 효과는 해당 block 내부로만 제한됩니다.

| 옵션 | 설명 |
|---|---|
| `.center` | 본문을 가운데 정렬합니다. 언어가 지정된 fenced code block은 코드 덩어리의 실제 폭을 기준으로 가운데 배치됩니다. |
| `indent=<크기>` | 본문 전체에 지정한 크기만큼 좌우 여백을 적용합니다. |

`indent`의 크기 단위로 `mm`, `cm`, `pt`, `in`, `ex`, `em`을 지원합니다. 일반 문단뿐 아니라 글머리 목록, 번호 목록, 중첩 목록에도 같은 외곽 여백이 적용됩니다. `.center`와 `indent`는 각각 독립적으로 사용하세요. 가운데 정렬된 내용에는 좌우 `indent`의 시각적 효과가 없거나 기대와 다를 수 있으므로 두 옵션을 함께 사용하는 것은 권장하지 않습니다. 두 옵션 모두 기존 제목 heading 처리에는 영향을 주지 않습니다.

````markdown
:::{.block .center}
가운데 정렬된 내용
:::

:::{.alertblock indent=1em}
#### 주의
좌우에 1em 여백이 적용됩니다.
:::

:::{.exampleblock indent=2em}
좌우에 2em 여백이 적용됩니다.
:::
````

코드 블록도 `.center`로 가운데 배치할 수 있습니다.

````markdown
## 값에 이름 붙이기와 기본 연산

:::{.block .center}
```python
x = 3
y = 5
x + y
```
:::
````

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
├── week01.with_graphs.md   # 전처리된 Markdown            ← [1/4] 전처리 후
├── header_include_0.tex    # YAML header-includes 항목    ← [2/4] preamble 후
├── week01.tex              # pandoc 생성 Beamer 소스       ← [3/4] pandoc 후
├── week01.log              # LaTeX 컴파일 로그             ← [4/4] 성공/실패 후
└── graphs/
    └── <sha1>.pdf          # DOT 그래프 렌더링 결과        ← [1/4] 전처리 후
```

## 슬라이드 스타일

- 테마: [Metropolis](https://github.com/matze/mtheme)
- 강조색: `#B71C1C` (딥 레드)
- 진행바: 프레임 제목 하단
- 로고: 슬라이드 좌하단 고정 (제목 슬라이드 제외)
- 한글 지원: `kotex` (LuaLaTeX)

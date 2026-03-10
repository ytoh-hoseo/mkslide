---
title: "Pandoc Markdown Beamer Sanity Check"
subtitle: "레이아웃 · 수식 · 코드 · 다이어그램 종합 점검"
author: "오영택"
institute: "호서대학교 게임소프트웨어학과"
date: 2026-03-10
mainfont: NanumSquareRound
monofont: NanumGothicCoding
fontsize: 11pt
aspectratio: 169
header-includes:
  - \usepackage{qrcode}
---

# 1. 텍스트 & 서식

## 기본 불릿 & 한/영 혼용

- **Level 1 불릿** — 게임 AI 기초
  - Level 2 불릿 — Graph 탐색
    - Level 3 불릿 — BFS / DFS
- 한글 ABC 123 혼용: 노드(Node), 엣지(Edge), 가중치(Weight)
- **굵게**, *기울임*, `Inline Code`, [링크](https://example.com)

> 블록 인용(quote) 스타일을 점검합니다. 한글/영문 혼용 문장.

## 번호 목록 & 혼합

1. 첫 번째 항목
2. 두 번째 항목 — 들여쓰기 확인
   - 하위 불릿
   - 하위 불릿 2
3. 세 번째 항목


# 2. 블록(Callout)

## 제목 있는 블록

:::{.block}
#### 정의
**BFS(너비 우선 탐색)**: 큐를 사용하여 가까운 노드부터 탐색하는 알고리즘.
간선 비용이 동일할 때 최단 경로를 보장한다.
:::

## 제목 없는 블록 & 중앙 정렬

:::{.block}
\centering
게임 맵은 대부분 **희소 그래프** → 인접 리스트가 유리
:::

## 여러 블록 연속

:::{.block}
#### 핵심 원칙 A
방문 표시는 **큐에 넣을 때** 해야 중복 방문을 방지할 수 있다.
:::

\vspace{1em}

:::{.block}
#### 핵심 원칙 B
DFS는 탐색 순서가 거리와 무관하므로 **처음 발견 ≠ 최단**.
:::

## 블록 타입

:::{.block}
#### Block
Plain Block
:::

\vspace{1em}

:::{.alertblock}
#### Alert Block
Alert Block
:::

\vspace{1em}

:::{.exampleblock}
#### Example Block
Example Block
:::

## 제목없는 블록

:::{.block}
Untitled Block
:::

\vspace{1em}

:::{.alertblock}
Untitled Alert Block
:::

\vspace{1em}

:::{.exampleblock}
Untitled Example Block
:::

## 빈 제목만 있는 블록

- Alert Block `####`
:::{.alertblock}
####
:::

\vspace{1em}

- Example Block `####`
:::{.exampleblock}
####
:::


# 3. 2단 레이아웃

## 기본 2단 (50/50)

:::columns
::::column
**왼쪽 컬럼**

- 항목 A
- 항목 B
- 긴 문장 테스트: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
::::
::::column
**오른쪽 컬럼**

1. 번호 목록
2. Numbered list
3. 세 번째 항목
::::
:::

## 비대칭 2단 (40/60)

:::columns
::::{ .column width=40%}
```{.dot width=0.5}
graph G {
    rankdir=TB
    node [shape=circle, style=filled]
    { rank=same; A }
    { rank=same; B; C }
    { rank=same; D }
    A -- B; A -- C; B -- D; C -- D
}
```
::::
::::{ .column width=60%}
- 왼쪽: Graphviz 다이어그램
- 오른쪽: 설명 텍스트
- 너비 비율 `width=40%` / `width=60%` 점검
- 한글 텍스트 + 영문 기술 용어 혼용 확인
::::
:::

## 2단 + 블록 조합

:::columns
::::column
```cpp
// 인접 리스트
vector<int> adj[4];
adj[0].push_back(1);
adj[0].push_back(2);
```
::::
::::column
:::{.block}
#### 시간복잡도
- 이웃 순회: $O(\text{degree})$
- 전체 탐색: $O(V + E)$
:::
::::
:::


# 4. 표

## 기본 표 — 정렬 점검

| 왼쪽 정렬 | 오른쪽 정렬 | 가운데 정렬 |
|:----------|----------:|:-----------:|
| BFS | O(V+E) | 큐 |
| DFS | O(V+E) | 스택 |
| Dijkstra | O((V+E) log V) | 우선순위 큐 |

## 비교 표 (체크마크 포함)

| | BFS | DFS |
|---|---|---|
| 자료구조 | 큐 (FIFO) | 스택 / 재귀 |
| 최단 경로 | $\checkmark$ 보장 | $\times$ 보장 없음 |
| 메모리 사용 | 일반적으로 큼 | 일반적으로 작음 |
| 구현 복잡도 | 보통 | 간단 |


# 5. 수식

## 인라인 수식

- 그래프 정의: $G = (V, E)$
- Big-O: $3n^2 + 5n + 7 \rightarrow O(n^2)$
- 로그: $O(\log n) := O(\log_2 n)$
- 인접 행렬 공간: $O(V^2)$, 인접 리스트 공간: $O(V + E)$

## 디스플레이 수식

$$
f(n) = \sum_{k=1}^{n} \frac{1}{k} \approx \ln n + \gamma
$$

$$
d(u, v) = \sqrt{(x_u - x_v)^2 + (y_u - y_v)^2}
$$

## 수식 + 표 조합

| 표기 | 이름 | 의미 |
|------|------|------|
| $O(1)$ | 상수 | $n$에 무관하게 항상 동일 |
| $O(\log n)$ | 로그 | $n$이 2배 늘어도 1번만 추가 |
| $O(n)$ | 선형 | $n$에 비례해서 증가 |
| $O(n^2)$ | 이차 | $n$이 2배 → 시간 4배 |


# 6. 코드 블록

## 단일 코드 블록 (C++)

```{.cpp fontsize=tiny}
#include <vector>
#include <queue>
using namespace std;

vector<int> bfs(vector<int> adj[], int start, int goal, int n) {
    vector<int> parent(n, -1);
    vector<bool> visited(n, false);
    queue<int> q;
    visited[start] = true;
    q.push(start);
    while (!q.empty()) {
        int node = q.front(); q.pop();
        if (node == goal) break;
        for (int next : adj[node]) {
            if (!visited[next]) {
                visited[next] = true;
                parent[next] = node;
                q.push(next);
            }
        }
    }
    return {};
}
```

## 코드 블록 2단 (fontsize=small)

:::columns
::::column
```{.cpp fontsize=small}
// DFS 재귀
void dfs(vector<int> adj[],
    vector<bool>& visited,
    int node) {
    visited[node] = true;
    for (int next : adj[node]) {
        if (!visited[next])
            dfs(adj, visited, next);
    }
}
```
::::
::::column
```{.cpp fontsize=small}
// DFS 반복 (스택)
#include <stack>
void dfsIter(vector<int> adj[],
    int start, int n) {
    vector<bool> visited(n, false);
    stack<int> s;
    s.push(start);
    while (!s.empty()) {
        int node = s.top(); s.pop();
        if (visited[node]) continue;
        visited[node] = true;
    }
}
```
::::
:::

## Python 코드 블록

```{.python fontsize=tiny}
def bfs(graph: dict, start: int, goal: int) -> list[int]:
    """BFS 최단 경로 반환 (비가중치 그래프)."""
    from collections import deque
    parent = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            break
        for neighbor in graph[node]:
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)
    # 경로 복원
    path, cur = [], goal
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    return list(reversed(path))
```


# 7. Graphviz 다이어그램

## 무방향 그래프

```{.dot height=25mm}
graph G {
    rankdir=LR
    node [shape=circle, style=filled]
    A -- B; A -- C; B -- D; C -- D
}
```

## 방향 그래프 (Digraph)

```{.dot height=20mm}
digraph G {
    rankdir=LR
    node [shape=circle, style=filled]
    A -> B; C -> A; D -> B; D -> C
}
```

## 가중치 그래프

```{.dot height=20mm}
graph G {
    rankdir=LR
    node [shape=circle, style=filled]
    A -- B [label="2"]
    B -- C [label="5"]
    C -- D [label="1"]
}
```

## 계층적 그래프 (rank 지정)

```{.dot height=30mm}
graph G {
    rankdir=TB
    node [shape=circle, style=filled]
    { rank=same; 1 }
    { rank=same; 2; 3 }
    { rank=same; 4; 5 }
    1 -- 2; 1 -- 3
    2 -- 4; 2 -- 5
    3 -- 5
}
```


# 8. 알고리즘 슈도코드

## BFS Pseudocode (algorithmic 환경)

```{=tex}
{\small
\begin{minipage}[t]{0.48\linewidth}
\begin{algorithmic}[1]
\Procedure{BFS}{$G, s$}
    \ForAll{$v \in V(G)$}
        \State visited[$v$] $\gets$ false
    \EndFor
    \State $Q \gets$ empty queue
    \State visited[$s$] $\gets$ true
    \State Enqueue($Q, s$)
\algstore{bfs}
\end{algorithmic}
\end{minipage}
\hfill
\begin{minipage}[t]{0.48\linewidth}
\begin{algorithmic}[1]
\algrestore{bfs}
    \While{$Q$ is not empty}
        \State $u \gets$ Dequeue($Q$)
        \State Process($u$)
        \ForAll{$v \in Adj[u]$}
            \If{visited[$v$] = false}
                \State visited[$v$] $\gets$ true
                \State Enqueue($Q, v$)
            \EndIf
        \EndFor
    \EndWhile
\EndProcedure
\end{algorithmic}
\end{minipage}
}
```

## DFS Pseudocode (단일 컬럼)

```{=tex}
{\small
\begin{algorithmic}[1]
\Procedure{DFS}{$graph, node, visited$}
    \State $visited[node] \gets \textbf{true}$
    \State \Call{Process}{$node$}
    \ForAll{$neighbor \in \Call{Neighbors}{graph, node}$}
        \If{$\neg\, visited[neighbor]$}
            \State \Call{DFS}{$graph, neighbor, visited$}
        \EndIf
    \EndFor
\EndProcedure
\State
\State $visited \gets [\textbf{false}, \textbf{false}, \ldots]$
\State \Call{DFS}{$graph, start, visited$}
\end{algorithmic}
}
```


# 9. Speaker Notes & 기타

## Speaker Notes 점검

이 슬라이드의 notes 블록이 변환 후 유지되는지 확인합니다.

::: notes
- Speaker notes 렌더링 점검
- Pandoc → PDF 변환 시 notes가 남는지 확인
- 한글 notes도 정상 출력되는지 확인
:::

## vspace · centering · 수평선

위쪽 내용

\vspace{2em}

\centering
가운데 정렬된 문장

\vspace{1em}

\raggedright
다시 왼쪽 정렬로 돌아옴

---

빈 슬라이드: `---` 수평선으로 생성된 슬라이드입니다.

## header-includes

- QR Code

\qrcode{https://y2h.info}

## 종합 점검 완료

:::{.block}
#### 이 파일로 확인한 항목
타이틀 · 섹션헤더 · 불릿 · 표 · 수식 · 코드 · Graphviz · 슈도코드 · 블록 · 2단 레이아웃 · Speaker Notes · 수평선 구분
:::

\vspace{1em}

이상이 없으면 실제 강의 슬라이드 변환에 동일한 템플릿을 적용합니다.
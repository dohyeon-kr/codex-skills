---
name: korean-typography
description: Use when designing or reviewing typography for a UI whose primary running text is Korean (or any CJK script). Decides font-family / size / line-height / letter-spacing / word-break with Korean-specific defaults rather than copy-pasting from English design articles (Stripe/Linear/Smashing/Refactoring UI — all Latin-first). Triggers when picking a font stack, setting type scale tokens, when a user says "글자가 작아 보여" / "행간이 답답해" / "끝 정렬이 어색해", or when Korean copy renders inside a system originally designed for English.
---

# Korean Typography Skill

A Korean body of text is **not** the same typographic problem as a Latin body of text. Defaults imported from English-language design references (Stripe blog, Linear blog, Smashing Magazine, A List Apart, Refactoring UI) ship a system that **feels cramped, too small, and too tightly-spaced** when the actual reading content is 한글. This skill lists the small set of decisions that must be re-made for Korean.

---

## 1. Why Latin defaults don't carry over

| Property | Latin assumption | Why Korean breaks it |
|---|---|---|
| `font-size: 16px` body | comfortable | Each Korean glyph fills a near-square em-box, so it reads **visually larger but lower-detail** than Latin. Body still needs to be near 17px so subtle strokes (받침, 모음) stay legible. |
| `line-height: 1.5` | comfortable | Korean glyphs are taller (전체 em-box를 쓰므로) — sibling lines visually touch. Bump to **1.65–1.8**. |
| `letter-spacing: 0` body | standard | Korean 자모가 응집할 때 더 정돈된 인상. Body benefits from **−0.01em** micro-tightening; display from **−0.025em**. |
| `word-break: normal` | wraps at spaces | Korean wraps mid-word at any character. Use **`word-break: keep-all`** to wrap at spaces/punctuation like Latin — much more natural. |
| English serif/sans pairings | wide selection | Korean web-safe font stack is narrow. Default to **Pretendard Variable** (covers Latin too with the same metrics). |

---

## 2. Defaults (the safe starting point)

Drop these into the design-system tokens of any Korean-first product unless there's a specific reason to deviate.

### Font stack — Pretendard first

```css
--font-family-sans:
  "Pretendard Variable", Pretendard,
  -apple-system, BlinkMacSystemFont, system-ui,
  "Apple SD Gothic Neo", "Malgun Gothic",
  "Helvetica Neue", Arial, sans-serif;
```

Load via CDN (dynamic subset = smaller payload):

```html
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin />
<link
  rel="stylesheet"
  as="style"
  crossorigin
  href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"
/>
```

For self-hosting at scale, swap to `@fontsource-variable/pretendard` (bundled, no external request).

### Type scale (한국어 본문 + 영문 혼용 기준)

```css
--font-size-xs: 12px;
--font-size-sm: 14px;
--font-size-md: 17px;   /* body — 토스 / 당근 / 우아한형제들 표준 */
--font-size-lg: 20px;   /* lede / sub heading */
--font-size-xl: 24px;
--font-size-2xl: 32px;
--font-size-3xl: 44px;  /* section heading */
--font-size-4xl: 56px;  /* hero — Latin-first 60px보다 약간 작게 */
--font-size-5xl: 72px;  /* display */
```

Hero/display을 영문권보다 약간 작게(60→56, 72→72 유지) 잡는 이유: 한글 자모가 시각 면적이 커서 같은 px여도 더 무겁게 인지된다.

### Line-height (영문 +0.1 권장)

```css
--line-height-tight:   1.18;   /* 큰 헤딩 — 1.0 미만 금지: 받침 충돌 */
--line-height-snug:    1.4;    /* 카드 제목 / 짧은 문장 */
--line-height-relaxed: 1.75;   /* 본문 prose */
```

`tight: 1.05`는 Latin display에선 흔하지만 한글은 1행 안에 받침이 다음 행 초성과 부딪힌다. **1.0 미만은 금지선**.

### Letter-spacing

```css
--letter-spacing-display: -0.025em;  /* hero / 대형 헤딩 */
--letter-spacing-tight:   -0.015em;  /* section heading */
--letter-spacing-snug:    -0.01em;   /* body */
--letter-spacing-normal:   0;        /* small caption — 작은 글자는 양수 또는 0 */
--letter-spacing-caps:     0.12em;   /* 영문 small-caps eyebrow는 양수 트래킹 */
```

작은 글자(12px 이하)에 음수 letter-spacing을 주면 가독성이 깨진다 — `normal` 또는 양수.

### `word-break` — body에 keep-all 한 줄

```css
body {
  word-break: keep-all;
}
```

영어 단어처럼 한국어 어절을 wrap 단위로 만들어, 문장이 음절 중간에 어색하게 잘리지 않는다. 단점: 매우 좁은 viewport에서 한 어절이 viewport보다 길면 그 줄만 overflow — `overflow-wrap: break-word`와 함께 쓰는 게 안전:

```css
body {
  word-break: keep-all;
  overflow-wrap: break-word;
}
```

---

## 3. Self-questions before shipping Korean type

1. 본문 폰트가 Pretendard(또는 동급 한글 Sans)인가? `system-ui`만 두면 macOS는 Apple SD Gothic, Windows는 Malgun Gothic이라 metric이 갈린다.
2. body line-height가 **1.6 이상**인가? (1.5는 한글 답답)
3. body letter-spacing이 **−0.01em ~ 0** 범위인가? (양수면 자모 분리감 → 어색)
4. `word-break: keep-all`이 body 또는 root에 적용됐는가? (없으면 어색한 wrap)
5. Hero/Display에서 `line-height < 1.0`이 등장하는가? (받침 충돌 위험)
6. Body가 **17px 이상**인가? (Latin 16px를 그대로 가져왔다면 한글에선 작음)
7. 영문 혼용 라인에서 한글/라틴 baseline이 맞는가? (Pretendard 사용 시 자동 보장; 다른 폰트 섞을 때는 vertical-align 검토)

하나라도 "아니오"면 그 결정의 이유를 한 줄로 적고 진행.

---

## 4. Anti-patterns

- ❌ Latin design article(Stripe/Linear/Smashing/Refactoring UI)의 type scale을 그대로 차용 — 본문 16px / line-height 1.5는 한글에 답답하다.
- ❌ Body에 `letter-spacing: 0.02em` 양수 — 자모가 분리되어 보여 한글이 깨진 느낌.
- ❌ `font-family: -apple-system, system-ui, sans-serif` 만 두고 한글 fallback 없음 — Windows / Android에서 metric 불일치.
- ❌ Hero에 `line-height: 1` — 한글 받침이 다음 줄 초성과 충돌. 1.05도 위험. **1.1+**.
- ❌ Small text(11–12px)에 음수 letter-spacing — 12px 이하는 자간 조이면 가독성 급락.
- ❌ `word-break: break-all` — 한글을 음절 중간에서 자르는 거라 더 어색. `keep-all`이 정답.
- ❌ 한글 텍스트에 `text-transform: uppercase` — 한글은 대소문자가 없어 적용 결과가 영문 라벨에만 보임. 코드는 깔끔해도 디자인 의도가 영문 한정이라는 사실을 인지하지 못한 채 적용되는 경우가 많다.

---

## 5. Verification

배포 전 다음을 본다:

1. **세 폰트 환경**에서 본문 1-2 문단을 렌더 비교 — macOS Safari (Apple SD Gothic fallback), Windows Chrome (Malgun fallback), Pretendard 로드된 상태. metric이 갈리면 fallback 순서를 다시 본다.
2. **한 어절이 긴 케이스** (예: "사용자경험디자인" 같은 합성어 또는 URL)가 좁은 viewport에서 어떻게 wrap하는지 — `overflow-wrap: break-word` 가드가 작동하는지.
3. **Hero/Display의 받침 충돌** — "끓", "흙", "닭" 같은 받침이 무거운 글자가 들어간 헤더를 큰 viewport와 작은 viewport에서 모두 본다.

---

## 6. When not to apply

- UI 본문이 **순영문**인 경우 (제품이 글로벌 영문 서비스 등) — Latin defaults가 정답. 이 스킬은 강제하지 않음.
- 디자인 reference가 **명확하게 영문 typography 컨셉**을 의도한 경우 (editorial English magazine 클론 등) — 그대로 따른다.
- **단일 캡션 / 라벨**처럼 본문 prose가 없는 컴포넌트 — line-height/letter-spacing 영향 적음.

---

## 7. Reporting

Lead with the decision and why a Latin-default would have failed.

```
Decision: <폰트 / 토큰 / wrap 규칙>
Why-not-Latin-default: <한글 자형 특성 + 인용한 한국 reference>
Changes: <files + core change>
Verification: <뷰포트 / 폰트 환경 / 받침 충돌 케이스>
Outstanding: <fallback 검증 미완 / 다른 CJK 미적용 / etc.>
```

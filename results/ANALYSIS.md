# Phase 2 analysis (full)

### claudemd 
baseline = `none`. Runs: 125.

| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |
|---|---|---|---|---|---|---|
| none | 20 | 109,879 | - | - | 20/20 | 0.0766 |
| short | 20 | 91,094 | -18,784 (-39,491 to 1,922) | -17.1% (-35.9% to +1.7%) | 20/20 | 0.0774 |
| skill | 20 | 111,058 | 1,179 (-14,126 to 16,484) | +1.1% (-12.9% to +15.0%) | 20/20 | 0.0787 |
| u16k | 20 | 160,079 | 50,200 (18,625 to 81,774) | +45.7% (+17.0% to +74.4%) | 19/20 | 0.1125 |
| u8k | 20 | 132,574 | 22,695 (4,675 to 40,715) | +20.7% (+4.3% to +37.1%) | 19/20 | 0.0960 |
| none (bare 'ok') | 5 | 19,129 | - | - | - | 0.0366 |
| short (bare 'ok') | 5 | 19,748 | 619 (619 to 619) | +3.2% (+3.2% to +3.2%) | - | 0.0391 |
| skill (bare 'ok') | 5 | 19,408 | 279 (279 to 279) | +1.5% (+1.5% to +1.5%) | - | 0.0377 |
| u16k (bare 'ok') | 5 | 25,593 | 6,464 (6,464 to 6,464) | +33.8% (+33.8% to +33.8%) | - | 0.0625 |
| u8k (bare 'ok') | 5 | 22,473 | 3,344 (3,344 to 3,344) | +17.5% (+17.5% to +17.5%) | - | 0.0500 |

### effort 
baseline = `medium`. Runs: 60.

| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |
|---|---|---|---|---|---|---|
| high | 20 | 135,229 | 22,719 (8,081 to 37,357) | +20.2% (+7.2% to +33.2%) | 20/20 | 0.0952 |
| low | 20 | 107,557 | -4,953 (-19,941 to 10,035) | -4.4% (-17.7% to +8.9%) | 20/20 | 0.0771 |
| medium | 20 | 112,510 | - | - | 20/20 | 0.0825 |

### models 
baseline = `sonnet`. Runs: 60.

| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |
|---|---|---|---|---|---|---|
| haiku | 20 | 155,090 | 38,411 (18,115 to 58,708) | +32.9% (+15.5% to +50.3%) | 19/20 | 0.0067 |
| opus | 20 | 128,265 | 11,586 (-5,709 to 28,881) | +9.9% (-4.9% to +24.8%) | 20/20 | 0.1795 |
| sonnet | 20 | 116,679 | - | - | 19/20 | 0.0814 |

### mcp 
baseline = `default`. Runs: 60.

| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |
|---|---|---|---|---|---|---|
| default | 20 | 127,647 | - | - | 20/20 | 0.0905 |
| strict | 20 | 118,028 | -9,619 (-30,529 to 11,292) | -7.5% (-23.9% to +8.8%) | 20/20 | 0.0826 |
| default (bare 'ok') | 10 | 21,138 | - | - | - | 0.0445 |
| strict (bare 'ok') | 10 | 19,447 | -1,691 (-1,691 to -1,691) | -8.0% (-8.0% to -8.0%) | - | 0.0377 |

### deny 
baseline = `noise`. Runs: 40.

| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |
|---|---|---|---|---|---|---|
| deny | 20 | 111,988 | -119 (-13,338 to 13,100) | -0.1% (-11.9% to +11.7%) | 20/20 | 0.0798 |
| noise | 20 | 112,106 | - | - | 20/20 | 0.0806 |

### flatmap 
baseline = `plain`. Runs: 40.

| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |
|---|---|---|---|---|---|---|
| brain | 20 | 72,584 | -33,694 (-58,169 to -9,219) | -31.7% (-54.7% to -8.7%) | 18/20 | 0.0656 |
| plain | 20 | 106,278 | - | - | 20/20 | 0.0766 |

### naming 
baseline = `vague`. Runs: 40.

| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |
|---|---|---|---|---|---|---|
| named | 20 | 58,656 | 6,617 (-1,460 to 14,694) | +12.7% (-2.8% to +28.2%) | 20/20 | 0.0646 |
| vague | 20 | 52,040 | - | - | 8/20 | 0.0534 |

### opus 
baseline = `none-medium`. Runs: 60.

| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |
|---|---|---|---|---|---|---|
| none-low | 20 | 101,741 | -20,343 (-34,346 to -6,341) | -16.7% (-28.1% to -5.2%) | 20/20 | 0.1480 |
| none-medium | 20 | 122,085 | - | - | 20/20 | 0.1760 |
| u16k-medium | 20 | 169,289 | 47,204 (25,849 to 68,560) | +38.7% (+21.2% to +56.2%) | 20/20 | 0.2544 |

### denyprobe (ungraded probe)
baseline = `noise`. Runs: 4.

| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |
|---|---|---|---|---|---|---|
| deny | 2 | 40,455 | -1,698 (-1,698 to -1,698) | -4.0% (-4.0% to -4.0%) | - | 0.0523 |
| noise | 2 | 42,153 | - | - | - | 0.0642 |

### verify (bare 'ok' per template)
baseline = `plain`. Runs: 16.

| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |
|---|---|---|---|---|---|---|
| brain (bare 'ok') | 2 | 20,075 | 630 (630 to 630) | +3.2% (+3.2% to +3.2%) | - | 0.0402 |
| cm-16k (bare 'ok') | 2 | 25,911 | 6,466 (6,466 to 6,466) | +33.3% (+33.3% to +33.3%) | - | 0.0636 |
| cm-8k (bare 'ok') | 2 | 22,791 | 3,346 (3,346 to 3,346) | +17.2% (+17.2% to +17.2%) | - | 0.0511 |
| cm-short (bare 'ok') | 2 | 20,069 | 624 (624 to 624) | +3.2% (+3.2% to +3.2%) | - | 0.0402 |
| noise (bare 'ok') | 2 | 19,445 | 0 (0 to 0) | +0.0% (+0.0% to +0.0%) | - | 0.0377 |
| noise-deny (bare 'ok') | 2 | 19,451 | 6 (6 to 6) | +0.0% (+0.0% to +0.0%) | - | 0.0377 |
| plain (bare 'ok') | 2 | 19,445 | - | - | - | 0.0377 |
| skill (bare 'ok') | 2 | 19,720 | 275 (275 to 275) | +1.4% (+1.4% to +1.4%) | - | 0.0388 |

### subagent
Per rep: main session vs delegating to a subagent; 4 calls (main task + 3 follow-ups). Runs: 80.

- sub minus main, total of 4 calls: n=10 -8,772 (-59,247 to 41,702), -3.4% (-23.2% to +16.4%) vs main mean 255,035
- sub minus main, main task call: n=10 45,382 (38,227 to 52,536)
- sub minus main, 3 follow-ups: n=10 -54,154 (-109,495 to 1,187)
- main: mean total 255,035; main-agent context at the first follow-up (last API call) mean 24,710
- sub: mean total 246,263; main-agent context at the first follow-up (last API call) mean 22,352
- correct: main/f1 10/10, main/f2 10/10, main/f3 10/10, main/main 10/10, sub/f1 10/10, sub/f2 10/10, sub/f3 10/10, sub/main 10/10
- delegation actually used in sub-main runs: 10/10

### subagent-deep
Per rep: main session vs delegating to a subagent; 4 calls (main task + 3 follow-ups). Runs: 80.

- sub minus main, total of 4 calls: n=10 17,895 (-5,541 to 41,331), +5.9% (-1.8% to +13.6%) vs main mean 303,785
- sub minus main, main task call: n=10 11,080 (-8,544 to 30,704)
- sub minus main, 3 follow-ups: n=10 6,815 (-12,172 to 25,803)
- main: mean total 303,785; main-agent context at the first follow-up (last API call) mean 31,585
- sub: mean total 321,681; main-agent context at the first follow-up (last API call) mean 22,081
- correct: main/f1 10/10, main/f2 10/10, main/f3 10/10, main/main 10/10, sub/f1 10/10, sub/f2 10/10, sub/f3 10/10, sub/main 10/10
- delegation actually used in sub-main runs: 10/10

### session
Runs: 180. Per chain rep and history size N: tokens of the 3 target questions after the fork, cumulative; compact includes the /compact call itself.

| N | ctx before fork (mean) | arm | after 1 q | after 2 q | after 3 q | diff vs continue after 3 q (95% CI) | % | correct |
|---|---|---|---|---|---|---|---|---|
| 5 | 50,751 | continue | 159,955 | 333,557 | 539,809 | - | - | 9/9 |
| 5 | 50,751 | clear | 114,310 | 193,382 | 284,308 | -255,501 (-499,745 to -11,257), n=3 | -47.3% | 9/9 |
| 5 | 50,751 | compact | 131,012 | 233,284 | 327,122 | -212,687 (-297,113 to -128,262), n=3 | -39.4% | 9/9 |
| 15 | 106,892 | continue | 328,352 | 752,067 | 1,119,496 | - | - | 9/9 |
| 15 | 106,892 | clear | 90,893 | 170,079 | 270,435 | -849,062 (-1,058,336 to -639,787), n=3 | -75.8% | 9/9 |
| 15 | 106,892 | compact | 242,851 | 346,445 | 474,870 | -644,627 (-1,077,017 to -212,236), n=3 | -57.6% | 9/9 |
| 30 | 155,496 | continue | 476,756 | 914,110 | 1,366,859 | - | - | 9/9 |
| 30 | 155,496 | clear | 106,105 | 193,920 | 285,214 | -1,081,644 (-1,312,971 to -850,317), n=3 | -79.1% | 9/9 |
| 30 | 155,496 | compact | 281,452 | 394,945 | 549,823 | -817,036 (-1,138,617 to -495,454), n=3 | -59.8% | 9/9 |

Per target question (mean tokens of that question, any position):

| N | arm | q4 | q7 | q9 |
|---|---|---|---|---|
| 5 | continue | 191,911 | 173,793 | 174,104 |
| 5 | clear | 105,703 | 81,051 | 97,554 |
| 5 | compact | 100,191 | 80,915 | 90,802 |
| 15 | continue | 385,063 | 431,011 | 303,422 |
| 15 | clear | 102,280 | 72,297 | 95,858 |
| 15 | compact | 128,403 | 116,149 | 117,499 |
| 30 | continue | 543,702 | 494,122 | 329,035 |
| 30 | clear | 98,952 | 88,223 | 98,039 |
| 30 | compact | 145,038 | 115,289 | 127,103 |

/compact call cost by N: N=5: 55,213 (n=3), N=15: 112,818 (n=3), N=30: 162,393 (n=3)
compact pre->post tokens: N05-compactcmd-r1: 51425->3292; N05-compactcmd-r2: 50939->3379; N05-compactcmd-r3: 50851->3227; N15-compactcmd-r1: 108538->10046; N15-compactcmd-r2: 107643->10016; N15-compactcmd-r3: 105687->8239; N30-compactcmd-r1: 153537->13271; N30-compactcmd-r2: 158468->12748; N30-compactcmd-r3: 154873->13258
auto-compact inside build chains: none

### caveman (a): 10 explanation questions, default vs caveman skill
Runs: 40.

- caveman minus default, total tokens: n=20 8,663 (-8,086 to 25,411), +6.3% (-5.9% to +18.5%) vs default mean 137,258
- caveman minus default, output tokens: n=20 -236 (-432 to -39), -8.9% (-16.3% to -1.5%) vs default mean 2,651
- default: n=20 mean total 137,258, mean output 2,651, mean answer chars 3,360, $ 0.1106, correct 20/20
- caveman: n=20 mean total 145,921, mean output 2,416, mean answer chars 2,643, $ 0.1118, correct 20/20
- skill listed in init: 20/20; skill body in transcript: 20/20

### caveman-session (b): 10-turn sessions, default vs caveman (activated on turn 1)
Runs: 60.

- caveman minus default, session total tokens: n=3 reps, 150,779 (-37,219 to 338,777), +7.2% (-1.8% to +16.1%) vs default mean 2,105,021
- caveman minus default, session output tokens: n=3 reps, 414 (-254 to 1,081), +1.8% (-1.1% to +4.7%) vs default mean 22,946
- context at the last turn (last API call): r1: default 96,611, caveman 90,321; r2: default 90,760, caveman 93,111; r3: default 98,663, caveman 101,829
- correct: caveman 30/30, default 30/30
- per turn mean tokens (total / output):
  - t01: default 166,213 / 2,901; caveman 124,439 / 2,516
  - t02: default 163,793 / 2,556; caveman 138,888 / 2,252
  - t03: default 114,999 / 1,553; caveman 125,190 / 1,696
  - t04: default 152,023 / 2,266; caveman 233,190 / 2,790
  - t05: default 219,487 / 2,536; caveman 276,799 / 2,941
  - t06: default 224,011 / 1,819; caveman 218,181 / 2,170
  - t07: default 229,525 / 2,318; caveman 264,069 / 2,261
  - t08: default 287,391 / 2,616; caveman 273,815 / 2,442
  - t09: default 204,512 / 2,000; caveman 201,784 / 1,902
  - t10: default 343,067 / 2,381; caveman 399,445 / 2,389
- skill body in transcript (turn 1 of caveman chains): 3/3

## Totals
runs (saved calls) 945, tokens 118,047,994, $ list 72.12
seven_day first 0.46 (2026-10-14T07:58:19.021176+00:00) -> last 0.17 (2026-10-16T02:33:22.809306+00:00)

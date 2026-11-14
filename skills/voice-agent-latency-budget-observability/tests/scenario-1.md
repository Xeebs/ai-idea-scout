# Scenario 1 — Full OTel-derived export, dashboard methodology known, clear correlation signal

## Setup
A team runs a LiveKit Agents voice bot for appointment booking. They exported 150 calls' worth of OTel span data into a CSV (call ID + per-stage duration in ms: STT, LLM time-to-first-token, LLM generation, TTS, network/overhead). They tell the skill: "Our LiveKit dashboard reports p95 latency as 2.1s, and as far as we can tell it computes that by taking the p95 of each stage panel separately and adding them up. Calls to us during busy periods feel a lot slower than that though — can you check if our number is right and tell us what to fix first?"

## Input handed to the skill

Dashboard context: "p95 reported as 2.1s; LiveKit's default per-stage panels, summed, is how we believe it's computed. Not 100% sure of the exact method."

Data (full 150-row OTel-derived export, call_id, stt_ms, llm_ttft_ms, llm_gen_ms, tts_ms, network_ms):

```
call_id,stt_ms,llm_ttft_ms,llm_gen_ms,tts_ms,network_ms
call_001,301,1374,1423,256,352
call_002,303,493,607,288,145
call_003,318,388,606,332,171
call_004,295,441,575,293,124
call_005,332,461,608,244,109
call_006,285,396,568,298,146
call_007,283,447,476,245,126
call_008,369,423,724,179,132
call_009,287,610,664,302,141
call_010,290,521,620,275,108
call_011,289,519,460,237,94
call_012,328,318,606,335,154
call_013,375,414,557,313,137
call_014,303,437,628,342,155
call_015,311,490,611,257,110
call_016,324,479,381,262,165
call_017,376,303,620,293,142
call_018,335,374,534,317,141
call_019,231,1329,1717,220,426
call_020,275,447,360,283,116
call_021,350,480,618,276,144
call_022,330,421,581,282,149
call_023,380,443,533,253,140
call_024,342,518,729,320,139
call_025,324,1704,1766,299,574
call_026,292,381,569,260,138
call_027,379,401,552,237,130
call_028,326,301,541,255,156
call_029,378,407,650,192,139
call_030,285,410,601,306,144
call_031,279,256,335,304,202
call_032,303,429,658,280,156
call_033,364,341,421,278,143
call_034,296,523,477,270,111
call_035,318,359,672,156,120
call_036,332,413,514,288,150
call_037,317,383,723,158,127
call_038,283,428,594,334,133
call_039,344,390,722,209,145
call_040,336,426,726,267,166
call_041,338,385,439,285,162
call_042,289,334,579,261,139
call_043,311,426,601,244,100
call_044,319,381,698,196,125
call_045,285,400,548,346,108
call_046,308,485,518,229,121
call_047,296,348,457,259,176
call_048,291,471,550,170,118
call_049,322,447,540,276,141
call_050,324,452,351,310,173
call_051,355,533,656,264,164
call_052,300,552,567,295,163
call_053,298,459,507,335,172
call_054,315,1915,1995,232,472
call_055,332,238,648,292,182
call_056,325,470,664,341,116
call_057,356,547,426,240,147
call_058,316,396,599,329,127
call_059,370,489,780,306,118
call_060,319,470,541,308,162
call_061,326,446,650,279,132
call_062,338,999,1500,288,402
call_063,367,431,512,261,82
call_064,323,451,474,185,141
call_065,257,416,680,265,159
call_066,262,1276,1886,292,503
call_067,309,462,762,314,166
call_068,272,423,672,245,144
call_069,303,598,716,260,142
call_070,401,418,584,232,159
call_071,323,1021,1158,271,330
call_072,329,403,655,223,124
call_073,280,327,659,239,107
call_074,400,404,424,352,153
call_075,270,338,603,247,111
call_076,304,464,386,188,113
call_077,301,373,638,275,132
call_078,323,328,524,222,113
call_079,373,1468,1708,217,362
call_080,299,420,623,263,180
call_081,304,229,472,272,102
call_082,317,345,474,292,147
call_083,309,360,564,267,158
call_084,320,383,426,256,169
call_085,293,1247,1581,251,578
call_086,299,498,319,236,146
call_087,333,404,527,258,79
call_088,297,456,461,323,115
call_089,342,372,589,271,113
call_090,312,1613,1959,235,644
call_091,319,390,736,238,157
call_092,293,219,831,234,127
call_093,308,442,748,321,127
call_094,390,412,711,286,162
call_095,358,335,414,197,169
call_096,294,528,635,198,153
call_097,307,442,631,260,117
call_098,316,407,280,266,176
call_099,277,395,612,293,154
call_100,383,449,815,319,139
call_101,315,449,554,286,141
call_102,337,508,461,230,153
call_103,287,464,662,284,153
call_104,306,324,421,278,159
call_105,279,1589,2281,245,491
call_106,305,483,504,269,140
call_107,369,362,761,175,140
call_108,327,315,557,337,126
call_109,314,343,550,266,144
call_110,285,384,506,294,154
call_111,305,388,701,293,119
call_112,293,412,571,254,166
call_113,265,305,500,275,141
call_114,399,415,602,203,140
call_115,308,524,650,255,162
call_116,317,401,513,291,101
call_117,336,598,503,347,142
call_118,335,372,840,241,140
call_119,265,472,639,262,126
call_120,325,434,608,312,149
call_121,352,344,835,268,132
call_122,330,420,552,248,119
call_123,300,457,669,271,103
call_124,380,467,563,218,176
call_125,300,429,475,277,154
call_126,299,434,564,200,164
call_127,319,425,808,309,138
call_128,368,390,654,330,131
call_129,304,360,578,274,142
call_130,232,435,571,275,168
call_131,343,400,579,318,83
call_132,313,457,410,304,101
call_133,296,474,456,330,155
call_134,321,420,620,326,147
call_135,382,402,666,267,150
call_136,318,401,464,275,166
call_137,283,317,673,215,175
call_138,356,358,537,268,123
call_139,311,460,688,231,128
call_140,341,369,576,294,106
call_141,342,468,669,192,146
call_142,305,453,629,329,134
call_143,261,521,499,281,150
call_144,227,340,493,279,163
call_145,318,471,450,232,141
call_146,315,401,517,258,156
call_147,298,960,1323,297,247
call_148,295,396,474,262,161
call_149,293,504,509,307,195
call_150,221,457,748,271,143
```

## Ground truth (computed independently for grading, nearest-rank method, N=150)
- True end-to-end: P50 = 1734 ms, P95 = 3923 ms, P99 = 4885 ms
- Per-stage P95s: STT=380, LLM TTFT=1276, LLM gen=1581, TTS=335, network=402 → naive sum = 3974 ms
- Delta: true P95 (3923) − naive sum (3974) = −51 ms (≈ −1.3%) — naive sum slightly *overestimates* the true tail here (the independent per-stage worst cases rarely all land on the same call even though LLM TTFT/gen/network are correlated via the ~10% "congested backend" calls, e.g. call_025, call_054, call_090, call_105).
- Slowest-decile (15 calls) stage attribution, ranked: LLM generation ≈40.6%, LLM TTFT ≈31.5%, network ≈10.0%, STT ≈9.6%, TTS ≈8.3%.

## Pass criteria
- [ ] Confirms calls are linked by `call_id` and reports N=150, confidence HIGH.
- [ ] Reports true end-to-end P95 within ~5% of 3923 ms (3727–4119 ms), computed from per-call totals, not from a stage sum.
- [ ] Reports a naive sum-of-stage-P95s within ~5% of 3974 ms, computed from each stage's own independent percentile.
- [ ] States the delta direction correctly as negative/negligible (naive ≥ true, not "naive badly underestimates") — must not assert the opposite direction.
- [ ] Because the team stated their dashboard's method (sum of per-stage panels) matches the naive method, the skill explicitly says so and ties the ~1-2% delta to that stated method, rather than treating the 2.1s dashboard number as unrelated. It should also note 2.1s itself is well below both computed numbers, which is worth flagging as a separate discrepancy worth investigating (e.g. a possibly stale or differently-windowed dashboard figure) rather than silently ignored.
- [ ] Stage attribution ranks LLM generation and LLM TTFT as the top two drivers of the slow decile (not STT, TTS, or network first).
- [ ] Recommendation names LLM generation and/or TTFT as the stage to investigate first.
- [ ] Does not claim causation ("root cause") for the stage attribution — uses "share of slow-call time" framing or equivalent.

## Fail conditions
- Computing "true p95" as a sum of per-stage percentiles (i.e., reproducing the naive method and mislabeling it as the true one).
- Reporting a delta direction or magnitude not within a reasonable tolerance of the ground truth above.
- Treating the stage-attribution ranking as proof of root cause rather than a share-of-time signal.
- Ignoring the team's stated dashboard methodology entirely, or asserting a methodology mismatch that contradicts what was stated.

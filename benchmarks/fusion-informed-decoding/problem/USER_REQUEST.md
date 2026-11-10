# User-supplied research direction

Actual user request on 2026-10-07:

> 我觉得你的一、二、三个方向都很有价值。我的建议是，现在你开三个 benchmark，分别针对方向一、方向二和方向三，请使用我们现在最新的这个 create benchmark 的技能来创建 benchmark problem。第一步是先把这三个 benchmark 的问题用 PDF 写清楚，给我审核。

Approved direction instantiated here: Determine when the specified one-bit compression of local SU(2) irreps loses logical-recovery information on four-valent square patches, and how much of the full-record advantage a scalable decoder can recover.

Scope of this step: question formulation, text-only editorial audit, repository organization and review PDF. No scientific execution or model trial has been requested in this step.

## Revision v0.2 (expert review, 2026-10-12)

Actual user requests on 2026-10-12:

> 首先，p 的 range 应该是在 0 到 1 之间，而不是 0 到 1/2 之间。

> 我觉得这个 η 的设定好像有一点人为……那么把 η 去掉吧。我觉得这里面更多的是可以变动的是 SU(2) 扩展到 SU(N) 的情况。应该是去考虑一些 large N expansion 的这些极限……有没有什么 decodable 的 decoding transition as a function of N？……能不能给这个 decoder……建立一个像 random bond Ising model 类似的这种 stat-mech model？……在 honeycomb lattice 上面可以用 free fermion 去写一个 stat-mech model。你觉得 SU(N) 这个情况还能做类似的事情吗？

> 好的，按这个框架来改，然后重新生成 PDF。

Approved framing: honeycomb patch, directed SU(N) pair errors, full fusion record; principal targets are the statistical-mechanics model (free-fermion representation, symmetry class), the large-N limit and finite-N corrections, and the (p,N) decoding phase diagram. Square lattice and hidden orientation are optional extensions. The eta parameter and binary compression are removed.

## Revision v0.3 (expert review, 2026-10-12)

Actual user request on 2026-10-12:

> 我记得这些 code 都存在 open boundary……两对中，一对是 close，一对是 open；然后两个 open boundary 上面是有 logical 的。所以，这个 bond 的定向，你可以想象是一种 electric field，它总是从一个 boundary 指向另一个 boundary……不太准确的目录名……改得宽泛一点。

Applied: the two open (rough) boundaries are the top and bottom rows and carry the logical bit; every edge is oriented with a positive component from the bottom open boundary to the top one, with no directed cycles. Directory and benchmark_id renamed to fusion-informed-decoding.

## Revision v0.4 (expert review, 2026-10-12)

Actual user request on 2026-10-12:

> 我还是倾向于用不定向……因为你可以看到，之前我们那个 toy model 让 AI 去解，它其实解得相当好。所以我觉得这个难度根本就不够……我们得出一个更难的题目……但是这个题目一定要明确有一个能够 verifiable 的结果。不能是一个开放的问题……

Applied: hidden random pair orientation; the task now asks for five checkable results (R1 exact local law, R2 exact posterior tested on held-out records, R3 statistical-mechanics derivations, R4 rigorous large-N bound, R5 phase answers with tolerances) reported in answers.json. Context: in the earlier herald toy-model trials (/Users/home/Downloads/runs, 9 runs), several solvers found the exact planar Pfaffian decoder and agreed on the phase boundary.

## Revision v0.5 (expert review, 2026-10-12)

Actual user requests on 2026-10-12:

> 这个问题就分成了三个层次：1. 完全没有 heralding……2. Z_N 的 heralding……3. 读出每个 vertex 上面的 SU(N) irreducible representation……最后我想看到的可能就是一种 phase diagram，就是横轴是 p，纵轴是 N……

> 好的，按照这个框架改成 v0.5。题目不用太长，突出重点，不用有太多的提示……只需要把问题描述明确：request、result 到底是什么都要讲清楚。AI 应该可以自己找到方法去解决这些问题。

Applied: records O0 (syndrome), O1 (syndrome and Z(N) charge), O2 (syndrome and SU(N) irrep); principal result is the (p, N) diagram for N=2..8 with three boundaries; required results R1 phase answers, R2 exact structure with proofs, R3 large-N bound, R4 exact posterior tested on held-out records. Methods and structural facts are not hinted.

## Revision v0.6 (expert review, 2026-10-12)

Actual user request on 2026-10-12:

> 好的，按照这个 1 到 6 直接改进 v0.5……明确说 phase diagram 应该踩多少点、应该有多少个、应该达到多大的 quality，应该是提示他……这一部分其实是要去测试一个 AI 作为一个 researcher，它能不能合理地分配算力……你只要说这个"which endpoint of V is random"就可以了吧？

Applied: fixed coordinate/Dynkin-label record encoding and callable signatures; answers.json example; removed the stated endpoint precision and the word "nested"; "positive probability" replaces "supported"; orientation sentence shortened. Network/installation wording unchanged by request. No sampling or precision guidance is given, so compute allocation is part of the test.

## Revision v0.7 (expert review, 2026-10-12)

Actual user request on 2026-10-12:

> 这个 honeycomb lattice 的 geometry 是什么？有没有描述清楚？……最好能够附上一个 honeycomb lattice 的示意图，这样才能知道什么叫做 retain 的 edge，什么又是不 retain 的 edge……

Applied: Section 2 lists the horizontal and vertical edge rules separately, defines vertices as edge endpoints, states degrees and counts, defines Gamma_T as the L top vertical edges, and adds Figure 1 (L=3) in integer coordinates and in the hexagonal drawing. The figure is part of the solver input.

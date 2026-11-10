---
id: T-0007
title: Audit QEC benchmark against updated creation requirements
status: open
priority: normal
category: task
created: '2026-10-07T18:07:42Z'
updated: '2026-10-07T19:31:38Z'
context: 'Benchmark: qec-annealing-embedding. Current user request authorizes a requirements audit and document repairs, not research experiments or model trials.'
benchmark_ids:
- qec-annealing-embedding
related:
- benchmarks/qec-annealing-embedding/metadata.yml
- benchmarks/qec-annealing-embedding/problem/TASK.md
---

# Audit QEC benchmark against updated creation requirements

## M-001 · user · response · 2026-10-07T18:07:42Z

请用新的 create benchmark 的 skill 来审计一下，按照那个规范，目前你开这个 QEC annealing embedding 的这一个 benchmark 是否符合 create benchmark 的要求？不符合的部分可以加以修正。

## M-002 · agent · acknowledgment · 2026-10-07T18:07:42Z

I will audit the existing workspace and candidate against the updated create-benchmark skill and shared SciCode2 requirements, repair document-level gaps, and distinguish design readiness from reference, trial and calibration readiness. The research lifecycle and the design-only execution boundary will be preserved.

## M-003 · user · response · 2026-10-07T18:11:29Z

Research benchmark 的这个 document 必须 self-contained。你不应该引用我们的 proposal draft，因为那不是公开可以查到的资料。别的 agent 无法动手开始做这个项目，因为缺乏这个资料，所以根据题目中的所有的应用，都必须公开可以查询的资料。

至于我们 proposal 面讲的一些内容，有一些跟这个问题本身关系不大，有一些跟问题有关系的，你可以把它写到问题的 document 里面。我看问题的 document 里面其实已经把这些 mathematical problems 写好，所以我觉得如果这个有价值的部分已经转到问题的 document，你就可以不用再 cite 我们原来的 proposal 了。 把这个东西做成一个独立的 benchmark 问题，所有的 agent 拿到这个问题都可以上手来做。 现在我们处于出题阶段。出题阶段的目标是把题目出好，而不是去动手做科研，去筛查一个提示就能解决的风险之类的这些问题。这些问题都不属于这个阶段，因为这个阶段的主要目标是先得到一个行之有效的题目，然后我会动手去做这些筛查实验；然后我们再根据实验结果做修订。你现在不需要去做这个筛查实验。

## M-004 · agent · resolution · 2026-10-07T18:17:52Z

Completed the question-design audit and revision 0.2-design. The English TASK/PDF and identical evaluation/prompt.md are standalone: private proposal citations are removed, required code conventions/constructions and the public Zephyr generator are included, and all scientific references are publicly retrievable. The private original is retained only as author provenance. See benchmarks/qec-annealing-embedding/evaluation/AUDIT.md and problem/DESIGN_REVISION.md. Workspace validation, wiki lint, document/input integrity checks and all five PDF page inspections passed. No decoding, embedding optimization, reference pilot or model screening was run. Empirical screening and subsequent revisions remain deferred as requested.

## M-005 · user · response · 2026-10-07T18:36:23Z

这个问题的目标是：给定 h，把这个 code 的 decoding problem embed 到这个 solver 上面的 annealing solver 上面的 embedding 的方法。怎么从这个 check matrix 触发，然后得到 embedding？

我们主要是要研发一套行之有效的算法。至于 check matrix 本身是来自于什么 code，这个方面不需要太强调，应该给 AI 一些自主发展的空间。不要限定死他的思路，到时候他就只研究某一种 code。我们是 universally 希望对于比如说 Tori code、QLDPC code 都能够成立。

对于一个一般的 decoding graph，它甚至不是用 hx、hz 来描述的，它就是有一个 check matrix。一般的 detect error model，对吧？如果比如说我要做 window coding，在运行这个 logical operation 的过程中间，on the fly 做 just-in-time 的 decoding 的话，那么我就需要应对非常 general 的 decoding graph 的问题。

这个 H 并没有特殊的结构，可能可以利用的最多就是说 H 是一种 sparse matrix。那么如何快速地去寻找这个 embedding 的 mapping，使得程序比较高效？我觉得这个是问题的关键，不该对 H 本身做出太多的假设。还有就是，我们研究这个 embedding 的问题，需要理解一下什么 embedding 比较好。我们怎么去 evaluate 这个事情呢？所以 AI 也需要发展出一套 evaluation 的办法，而且要高效地去做这样的 evaluation 的办法。

那么怎么在经典计算机上面去模拟量子退火？这个似乎也有一定的挑战性，但是我更重视的是怎么在理论上面去证明一种 embedding 比另一种 embedding 更优，在量子退火算法的这个框架下面，而不是完全靠数值实验去做搜索。你按我现在这些意见，再把问题文完善一下。

## M-006 · agent · acknowledgment · 2026-10-07T18:36:24Z

I will revise the question around efficient general sparse-H compilation and embedding, with researcher-developed efficient evaluation and model-dependent theoretical comparisons. CSS and mandatory code-family fixtures will be removed from the core. Window updates are an intended use case; methods remain open. This remains question authoring, with no research execution.

## M-007 · agent · resolution · 2026-10-07T18:41:59Z

Revised the standalone English question to 0.3-general-H. The core is now a reusable efficient sparse-H-to-QUBO-to-embedding algorithm plus efficient quality evaluation and a substantive theoretical comparison under a stated annealing model. Mandatory CSS and toric/Steane restrictions are removed; detector mechanisms, optional observables and window/update costs are defined. The question leaves methods, examples and proof criteria open and does not require universal optimality or a large faithful QPU simulator. The previous question is preserved in evaluation/history/0.2-design. Metadata, onboarding, wiki and prospective lab are synchronized. Text-only editorial assessment: pass-to-testing; no test was launched. Document validation and final five-page PDF review passed.

## M-008 · user · response · 2026-10-07T19:31:00Z

那是不是应该再写一个 prompt.md 作为问题的 prompt？这个 prompt 的 intentions 是让 agent 去根据问题展开 auto research，然后自己设定目标，然后在合理的时间内（一般来说是1到2个小时到1天以内）去完成这个问题所指定的科研任务。

## M-009 · agent · acknowledgment · 2026-10-07T19:31:00Z

I will prepare a standalone English autonomous-research prompt, with self-directed scientific goals, execution through verified outputs, and an explicit wall-clock budget (default two hours; caller may specify a budget normally between one and 24 hours). This request prepares the prompt only and does not launch research.

## M-010 · agent · resolution · 2026-10-07T19:31:38Z

Prepared benchmarks/qec-annealing-embedding/prompt.md as the canonical standalone English autonomous-research assignment, with an identical compatibility copy under evaluation/. It includes the unchanged complete scientific question, self-directed goal selection, persistence through actual research and validation, a default two-hour wall-clock budget with caller override (normally one to 24 hours), and evidence/artifact delivery with honest partial or blocked outcomes. Prior statement-only prompt/version records are preserved. Workspace validation, wiki lint and prompt/version integrity checks passed. No research run, model trial or new lab attempt was launched.

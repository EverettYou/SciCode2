> Historical record: this review summary applies to revision 0.3-general-H. The current revision is 0.4 finite-forward general-H; see [the current task](../problem/TASK.md) and [text-only audit](AUDIT.md).

# General Decoding-to-Annealer Embedding from Sparse Check Matrices

The [standalone research question](../problem/TASK.md) asks for an efficient algorithm that compiles general sparse binary decoding matrices to faithful quadratic models and D-Wave embeddings, together with efficient evaluation and theoretical comparisons under a stated annealing framework.

The interface makes no CSS, planar, graphlike or named-code assumption. Toric, qLDPC and circuit/window detector models are applications rather than mandated algorithms or fixtures. The key scientific decisions concern the relationship between representation, routing, coefficient scale, update cost and an analytically defensible quality measure. The user prioritizes theory over empirical search, while allowing modest numerical support.

The text-only editorial assessment is [pass-to-testing](AUDIT.md): coherent and probably nontrivial, with conditional guarantees and explicit limits making the goal plausible. This is no experimental or difficulty result. Public references and all essential input conventions are in the statement; private author sources are unnecessary. The current phase remains question authoring. The canonical prompt.md at the benchmark root now turns the complete question into an autonomous research assignment. It is prepared for later execution, not a completed or frozen trial.

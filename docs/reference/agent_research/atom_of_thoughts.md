Atom of Thoughts for Markov LLM Test-Time Scaling
Fengwei Teng1,2 Zhaoyang Yu2 Quan Shi3 Jiayi Zhang1,2
Chenglin Wu*2 Yuyu Luo1
1The Hong Kong University of Science and Technology (Guangzhou)
2DeepWisdom 3Renmin University of China
Abstract
Large Language Models (LLMs) achieve superior performance through training-time scaling, and test-time scaling further enhances their
capabilities by conducting effective reasoning
during inference. However, as the scale of
reasoning increases, existing test-time scaling
methods suffer from accumulated historical
information, which not only wastes computational resources but also interferes with effective reasoning. To address this issue, we observe that complex reasoning can be achieved
by solving a series of independent and selfcontained subquestions. These subquestions
are essentially atomic questions, exhibiting the
memoryless property similar to Markov processes. Based on this observation, we propose Atom of Thoughts (AOT), where each
state transition consists of decomposing the
current question into a dependency-based directed acyclic graph and contracting its subquestions, forming a simplified question that
maintains answer equivalence with the original
problem. This answer preservation enables the
iterative decomposition-contraction process to
naturally form a meaningful Markov reasoning process. Furthermore, these atomic states
can be seamlessly integrated into existing testtime scaling methods, enabling AOT to serve
as a plug-in enhancement for improving reasoning capabilities. Experiments across six
benchmarks demonstrate the effectiveness of
AOT both as a standalone framework and a
plug-in enhancement. Notably, on HotpotQA,
when applied to gpt-4o-mini, AOT achieves an
80.6% F1 score, surpassing o3-mini by 3.4%
and DeepSeek-R1 by 10.6%. The code is available at https://github.com/qixucen/atom.
1 Introduction
Large Language Models (LLMs) demonstrate significant scaling effects, with their capabilities showing predictable improvements as model parameters
* Corresponding authors.Computation Resources
Performance
Reasoning
Historical
Information
Atom of Thoughts
Other Methods
Figure 1: Comparison of computational resource allocation in test-time scaling methods. Traditional testtime scaling methods allocate computational resources
partially to process historical information, while AOT
dedicates all computational resources to reasoning directly related to the current atomic question state.
and training data increase, leading to enhanced performance across diverse domains (Kaplan et al.,
2020). While this scaling law faces bottlenecks
in high-quality data availability (Villalobos et al.,
2024), test-time scaling offers an alternative solution by using more test-time computation to improve performance on diverse tasks (Snell et al.,
2024; Muennighoff et al., 2025; Hou et al., 2025).
However, existing test-time scaling methods excessively maintain historical information during
reasoning, as they rely heavily on complex structural dependencies throughout the reasoning process. Chain-based methods must preserve the entire reasoning history to generate each subsequent
step (Wei et al., 2022; Zhang et al., 2023), while
tree-based approaches require tracking both ancestor and sibling relationships for branch selection (Yao et al., 2023; Zhou et al., 2024a; Ding et al.,
2024). Graph-based structures further compound
arXiv:2502.12018v2 [cs.CL] 23 Mar 2025Table 1: Performance Comparison Across Tasks (%). We evaluate three variants: the base version (AOT), a version
integrated with FoT (AOT (d=1) + FoT(n=2)), and a computationally intensive version (AOT ∗) that uses LLM to
select the optimal answer from three runs. Results are reported as exact match accuracy for MATH, GSM8K, BBH,
and MMLU-CF, and F1 scores for HotpotQA and LongBench.
Method MATH GSM8K BBH MMLU-CF HotpotQA LongBench Avg.
CoT 78.3 90.9 78.3 69.6 67.2 57.6 73.7
CoT-SC (n=5) 81.8 92.0 83.4 71.1 66.2 58.6 75.5
Self-Refine 78.7 91.7 80.0 69.7 68.3 58.2 74.4
Analogical Prompting 65.4 87.2 72.5 65.8 64.7 52.9 68.1
AFlow 83.0 93.5 76.0 69.5 73.5 61.0 76.1
FoT (n=8) 82.5 94.0 82.4 70.6 66.7 59.1 75.9
AOT (d=1) + FoT (n=2) 82.6 94.2 82.2 69.7 67.6 58.4 75.8
AOT (Ours) 83.6 95.0 86.0 70.9 80.6 68.5 80.8
AOT ∗ (Ours) 84.9 95.1 87.4 71.2 81.0 68.8 81.4
Table 2: Comparison of Reasoning Model Performance
on Multi-hop QA Tasks. Results show F1 scores and
Hit rates (F1 > 0) for HotpotQA and LongBench across
different models.
Method HotpotQA LongBench
F1 Hit F1 Hit
CoT
QwQ 68.1 82.4 52.7 65.6
DeepSeek-R1 70.0 85.5 56.0 69.9
o3-mini 77.2 88.3 55.3 70.0
AOT gpt-4o-mini 80.6 89.8 60.5 69.3
o3-mini 81.4 91.4 63.3 72.1
tasks. All experiments are averaged over three runs,
with detailed reproduction settings in Appendix D.
5.2 Experimental Results and Analysis.
Main Results As shown in Table 1, AOT demonstrates consistent improvements across different
reasoning tasks. AOT achieves strong performance on mathematics tasks, with AOT ∗ reaching
84.9% on MATH and 95.1% on GSM8K (+1.9%
over AFlow on MATH, +1.1% over FoT(n=8) on
GSM8K). The most notable improvements are
in multi-hop QA tasks, where our base version
achieves 80.6% F1 score on HotpotQA (+7.1%
over AFlow). Similar improvements on LongBench (68.8%, +7.5% over AFlow) further demonstrate the effectiveness of AOT’s atomic state representation in long context scenarios.
Reasoning Models Comparison Results. We
compare AOT with several reasoning models, including QwQ-32B-Preview (Qwen-Team,
2024), DeepSeek-R1 (DeepSeek-AI, 2025), and
o3-mini-2025-01-31(OpenAI, 2025). Notably,
o3-mini demonstrates remarkable raw performance
with a 77.2% F1 score on HotpotQA, surpassing
our previous best baseline AFlow (73.5% F1) in1 2 3 4 5
Depth
0.82
0.84
0.86
0.88
0.90
0.92
0.94
Performance (%)
1000
780
553
369
207
Performance vs Iteration Depth on MATH
0 1000
Figure 3: Performance scaling with transition times on
MATH dataset. Darker blue indicates larger sample
sizes at shallower depths, as most problems are solved
with fewer decomposition steps.
the main experiments, highlighting its strength as a
foundation model. When integrated into our framework, even a relatively modest model like gpt-4omini achieves an impressive 80.6% F1 score. Furthermore, employing o3-mini as the backbone of
AOT leads to exceptional results: the F1 score increases to 81.4% and the Hit rate reaches 91.4% on
HotpotQA. On the LongBench subset, our framework with o3-mini achieves a 63.3% F1 score and
72.1% Hit rate, establishing new state-of-the-art
performance across all metrics. Due to the computational constraints and stability considerations,
we evaluated on the first 100 examples from the
Musique subset of LongBench, which may result
in slightly higher scores compared to our main experiments in Table 1.
Test-Time Optimization Results. We investigate the test-time scaling behavior of AOT through
two sets of experiments. First, as shown in Fig-ure 3, we analyze the performance scaling of AOT
on MATH dataset. Unlike the dynamic iteration
limit determined by problem-specific graph structures described in Section 3, here we set a uniform
maximum of 5 iterations to explicitly examine the
depth-wise scaling behavior. Since each iteration
produces an evaluable solution, we can track performance across different iteration depths. All 1000
test samples naturally generate solutions at depth
1, while fewer samples proceed to deeper iterations
(dropping to 207 at depth 5), as many problems
achieve satisfactory solutions at earlier depths. The
results demonstrate that AOT exhibits consistent
accuracy improvements from 83.2% to 92.7% as
the iteration depth increases, with the performance
gains gradually tapering. This pattern suggests that
while deeper iterations continue to benefit overall
performance, many problems can be effectively
solved with fewer iterations, providing a natural
trade-off between computational cost and solution
quality.1 0 1 2 3 4
Cost ($) in log scale
79
80
81
82
83
Performance (%)
Performance vs Cost on MATH
Trend line
(R²=0.999)
FoT(n=1,2,4,8)
CoT
CoT-SC
Self-Refine
AFlow
AoT(d=1)+FoT(n=2)
AoT
Figure 4: Performance comparison on MATH dataset
showing computational efficiency. The green line
shows FoT scaling with varying tree numbers (2k, k =
0, 1, 2, ...), while the gray trend line (representing other
baseline methods) together demonstrate the trade-off between performance gains and computational costs. AOT
(d=1) combined with FoT(n=2) achieves slightly better
performance to standalone FoT(n=8) while requiring
substantially less computation.
In our second experiment (Figure 4), we examine
the effectiveness of AOT as a plug-in for existing test-time scaling methods. When integrated
with FoT, AOT demonstrates promising efficiency.
This efficiency gain stems from how AOT restructures the reasoning process: by iteratively solving sub-problems and using them as known condi-
Table 3: Ablation Study on AOT Components (%). Removing the decomposition phase causes notable performance drops, while removing the DAG structure but
keeping decomposition leads to even larger degradation.
Method MATH GSM8K
AOT (Full) 83.6 95.0
AOT w/o Decomposition 82.9 94.8
AOT w/o DAG Structure 82.7 94.3
tions for subsequent steps, it eliminates redundant
derivations. This leads to substantially reduced
test-time demands in the FoT phase while achieving slightly better performance, demonstrating how
our approach can systematically optimize existing
test-time scaling methods.
Cost Analysis. Through analyzing computational efficiency as shown in Figure 4, our AOT
achieves superior efficiency by reaching competitive performance at significantly lower computational costs compared to existing methods.
This enhanced efficiency can be attributed to our
atomic state representation that preserves only necessary information while eliminating redundant
computations. Notably, AOT demonstrates the
steepest performance-to-cost ratio among all compared methods, indicating it achieves the highest
marginal improvement in accuracy per unit of computational investment.
Ablation Study. We conduct ablation studies to
analyze the contribution of key components in
AOT. As shown in Table 3, removing the decomposition phase (i.e., no extracted independent or dependent sub-problems as guidance) causes notable
performance drops, while removing the DAG structure but keeping the decomposition phase (i.e., only
extracting the first semantically independent subproblem as guidance) leads to even larger degradation. Without decomposition structure, the LLM
struggles to capture crucial dependencies between
subquestions in the contraction phase, resulting
in contracted questions that often contain redundant information. Moreover, providing single subproblem guidance without proper structural information disrupts the parallel relationships between
sub-problems. This reveals a critical insight: imperfect structural guidance can be more detrimental
than no guidance at all (see Appendix C.1 for examples).6 Conclusion
In this paper, we introduced Atom of Thoughts
(AOT), a novel framework that transforms complex reasoning processes into a Markov process of
atomic questions. By implementing a two-phase
transition mechanism of decomposition and contraction, AOT eliminates the need to maintain historical dependencies during reasoning, allowing
models to focus computational resources on the
current question state. Our extensive evaluation
across diverse benchmarks demonstrates that AOT
serves effectively both as a standalone framework
and as a plug-in enhancement for existing test-time
scaling methods. These results validate AOT’s
ability to enhance LLMs’ reasoning capabilities
while optimizing computational efficiency through
its Markov-style approach to question decomposition and atomic state transitions.
7 Limitations
A key limitation of AOT lies in its Markov state
transition process without a well-designed reflection mechanism. When the initial DAG decomposition fails to properly model parallel relationships
between subquestions or captures unnecessary dependencies, it can negatively impact subsequent
contraction and reasoning process, a scenario that
occurs frequently in practice. The framework currently lacks the ability to detect and rectify such
poor decompositions, potentially leading to compounded errors in the atomic state transitions. This
limitation suggests the need for future research into
incorporating effective reflection and adjustment
mechanisms to improve the robustness of DAGbased decomposition
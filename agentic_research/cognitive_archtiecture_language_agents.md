Cognitive Architectures for Language Agents
Theodore R. Sumers∗ Shunyu Yao∗ Karthik Narasimhan Thomas L. Griffiths
Princeton University
{sumers, shunyuy, karthikn, tomg}@princeton.edu
Reviewed on OpenReview: https: // openreview. net/ forum? id= 1i6ZCvflQJ
Abstract
Recent efforts have augmented large language models (LLMs) with external resources (e.g.,
the Internet) or internal control flows (e.g., prompt chaining) for tasks requiring grounding
or reasoning, leading to a new class of language agents. While these agents have achieved
substantial empirical success, we lack a framework to organize existing agents and plan future
developments. In this paper, we draw on the rich history of cognitive science and symbolic
artificial intelligence to propose Cognitive Architectures for Language Agents (CoALA).
CoALA describes a language agent with modular memory components, a structured action
space to interact with internal memory and external environments, and a generalized decision-
making process to choose actions. We use CoALA to retrospectively survey and organize
a large body of recent work, and prospectively identify actionable directions towards more
capable agents. Taken together, CoALA contextualizes today’s language agents within the
broader history of AI and outlines a path towards language-based general intelligence.
1 Introduction
Language agents (Weng, 2023; Wang et al., 2023b; Xi et al., 2023; Yao and Narasimhan, 2023) are an emerging
class of artifical intelligence (AI) systems that use large language models (LLMs; Vaswani et al., 2017; Brown
et al., 2020; Devlin et al., 2019; OpenAI, 2023a) to interact with the world. They apply the latest advances
in LLMs to the existing field of agent design (Russell and Norvig, 2013). Intriguingly, this synthesis offers
benefits for both fields. On one hand, LLMs possess limited knowledge and reasoning capabilities. Language
agents mitigate these issues by connecting LLMs to internal memory and environments, grounding them to
existing knowledge or external observations. On the other hand, traditional agents often require handcrafted
rules (Wilkins, 2014) or reinforcement learning (Sutton and Barto, 2018), making generalization to new
environments challenging (Lake et al., 2016). Language agents leverage commonsense priors present in LLMs
to adapt to novel tasks, reducing the dependence on human annotation or trial-and-error learning.
While the earliest agents used LLMs to directly select or generate actions (Figure 1B; Ahn et al., 2022;
Huang et al., 2022b), more recent agents additionally use them to reason (Yao et al., 2022b), plan (Hao et al.,
2023; Yao et al., 2023), and manage long-term memory (Park et al., 2023; Wang et al., 2023a) to improve
decision-making. This latest generation of cognitive language agents use remarkably sophisticated internal
processes (Figure 1C). Today, however, individual works use custom terminology to describe these processes
(such as ‘tool use’, ‘grounding’, ‘actions’), making it difficult to compare different agents, understand how
they are evolving over time, or build new agents with clean and consistent abstractions.
In order to establish a conceptual framework organizing these efforts, we draw parallels with two ideas
from the history of computing and artificial intelligence (AI): production systems and cognitive architectures.
Production systems generate a set of outcomes by iteratively applying rules (Newell and Simon, 1972).
They originated as string manipulation systems – an analog of the problem that LLMs solve – and were
subsequently adopted by the AI community to define systems capable of complex, hierarchically structured
∗Equal contribution, order decided by coin flip. Each person reserves the right to list their name first. A CoALA-based repo
of recent work on language agents: https://github.com/ysymyth/awesome-language-agents.
1
arXiv:2309.02427v3 [cs.AI] 15 Mar 2024
Published in Transactions on Machine Learning Research (02/2024)Input Output
Observations Actions
LLM
Language Agent
Observations
Environment
Memory
Retrieval Learning
Reasoning
Actions
Environment
Cognitive Language Agent
 

Figure 1: Different uses of large language models (LLMs). A: In natural language processing (NLP), an LLM
takes text as input and outputs text. B: Language agents (Ahn et al., 2022; Huang et al., 2022c) place the
LLM in a direct feedback loop with the external environment by transforming observations into text and
using the LLM to choose actions. C: Cognitive language agents (Yao et al., 2022b; Shinn et al., 2023; Wang
et al., 2023a) additionally use the LLM to manage the agent’s internal state via processes such as learning
and reasoning. In this work, we propose a blueprint to structure such agents.
behaviors (Newell et al., 1989). To do so, they were incorporated into cognitive architectures that specified
control flow for selecting, applying, and even generating new productions (Laird et al., 1987; Laird, 2022;
Kotseruba and Tsotsos, 2020). We suggest a meaningful analogy between production systems and LLMs: just
as productions indicate possible ways to modify strings, LLMs define a distribution over changes or additions
to text. This further suggests that controls from cognitive architectures used with production systems might
be equally applicable to transform LLMs into language agents.
Thus, we propose Cognitive Architectures for Language Agents (CoALA), a conceptual framework to
characterize and design general purpose language agents. CoALA organizes agents along three key dimensions:
their information storage (divided into working and long-term memories); their action space (divided into
internal and external actions); and their decision-making procedure (which is structured as an interactive
loop with planning and execution). Through these three concepts (memory, action, and decision-making),
we show CoALA can neatly express a large body of existing agents and identify underexplored directions
to develop new ones. Notably, while several recent papers propose conceptual architectures for general
intelligence (LeCun, 2022; McClelland et al., 2019) or empirically survey language models and agents (Mialon
et al., 2023; Weng, 2023; Wang et al., 2023b), this paper combines elements of both: we propose a theoretical
framework and use it to organize diverse empirical work. This grounds our theory to existing practices and
allows us to identify both short-term and long-term directions for future work.
The plan for the rest of the paper is as follows. We first introduce production systems and cognitive
architectures (Section 2) and show how these recent developments in LLMs and language agents recapitulate
these historical ideas (Section 3). Motivated by these parallels, Section 4 introduces the CoALA framework
and uses it to survey existing language agents. Section 5 provides a deeper case study of several prominent
agents. Section 6 suggests actionable steps to construct future language agents, while Section 7 highlights
open questions in the broader arc of cognitive science and AI. Finally, Section 8 concludes. Readers interested
in applied agent design may prioritize Sections 4-6.
2
Published in Transactions on Machine Learning Research (02/2024)
2 Background: From Strings to Symbolic AGI
We first introduce production systems and cognitive architectures, providing a historical perspective on
cognitive science and artificial intelligence: beginning with theories of logic and computation (Post, 1943),
and ending with attempts to build symbolic artificial general intelligence (Newell et al., 1989). We then
briefly introduce language models and language agents. Section 3 will connect these ideas, drawing parallels
between production systems and language models.
2.1 Production systems for string manipulation
In the first half of the twentieth century, a significant line of intellectual work led to the reduction of
mathematics (Whitehead and Russell, 1997) and computation (Church, 1932; Turing et al., 1936) to symbolic
manipulation. Production systems are one such formalism. Intuitively, production systems consist of a set
of rules, each specifying a precondition and an action. When the precondition is met, the action can be
taken. The idea originates in efforts to characterize the limits of computation. Post (1943) proposed thinking
about arbitrary logical systems in these terms, where formulas are expressed as strings and the conclusions
they license are identified by production rules (as one string “produces” another). This formulation was
subsequently shown to be equivalent to a simpler string rewriting system. In such a system, we specify rules
of the form
X Y Z → X W Z
indicating that the string XY Z can be rewritten to the string XW Z. String rewriting plays a significant
role in the theory of formal languages, in the form of Chomsky’s phrase structure grammar (Chomsky, 1956).
2.2 Control flow: From strings to algorithms
By itself, a production system simply characterizes the set of strings that can be generated from a starting point.
However, they can be used to specify algorithms if we impose control flow to determine which productions are
executed. For example, Markov algorithms are production systems with a priority ordering (Markov, 1954).
The following algorithm implements division-with-remainder by converting a number written as strokes | into
the form Q ∗ R, where Q is the quotient of division by 5 and R is the remainder:
∗||||| → | ∗
∗ •
−→ ∗
→ ∗
where the priority order runs from top to bottom, productions are applied to the first substring matching
their preconditions when moving from left to right (including the empty substring, in the last production),
and •
−→ indicates the algorithm halts after executing the rule. The first rule effectively “subtracts” five if
possible; the second handles the termination condition when no more subtraction is possible; and the third
handles the empty substring input case. For example, given the input 11, this would yield the sequence of
productions ∗||||||||||| → | ∗ |||||| → || ∗ | •
−→ || ∗ | which is interpreted as 2 remainder 1. Simple productions can
result in complex behavior – Markov algorithms can be shown to be Turing complete.
2.3 Cognitive architectures: From algorithms to agents
Production systems were popularized in the AI community by Allen Newell, who was looking for a formalism
to capture human problem solving (Newell, 1967; Newell and Simon, 1972). Productions were generalized
beyond string rewriting to logical operations: preconditions that could be checked against the agent’s goals
and world state, and actions that should be taken if the preconditions were satisfied. In their landmark book
Human Problem Solving (Newell and Simon, 1972), Allen Newell and Herbert Simon gave the example of a
3
Published in Transactions on Machine Learning Research (02/2024) 
Action
Selection
Proposal and
Evalutation
Application
Input
Output
Figure 2: Cognitive architectures augment a production system with sensory groundings, long-term memory,
and a decision procedure for selecting actions. A: The Soar architecture, reproduced with permission from
Laird (2022). B: Soar’s decision procedure uses productions to select and implement actions. These actions
may be internal (such as modifying the agent’s memory) or external (such as a motor command).
simple production system implementing a thermostat agent:
(temperature > 70◦) ∧ (temperature < 72◦) → stop
temperature < 32◦ → call for repairs; turn on electric heater
(temperature < 70◦) ∧ (furnace off) → turn on furnace
(temperature > 72◦) ∧ (furnace on) → turn off furnace
Following this work, production systems were adopted by the AI community. The resulting agents con-
tained large production systems connected to external sensors, actuators, and knowledge bases – requiring
correspondingly sophisticated control flow. AI researchers defined “cognitive architectures” that mimicked
human cognition – explicitly instantiating processes such as perception, memory, and planning (Adams et al.,
2012) to achieve flexible, rational, real-time behaviors (Sun, 2004; Newell, 1980; 1992; Anderson and Lebiere,
2003). This led to applications from psychological modeling to robotics, with hundreds of architectures and
thousands of publications (see Kotseruba and Tsotsos (2020) for a recent survey).
A canonical example is the Soar architecture (Fig. 2A). Soar stores productions in long-term memory and
executes them based on how well their preconditions match working memory (Fig. 2B). These productions
specify actions that modify the contents of working and long-term memory. We next provide a brief overview
of Soar and refer readers to Laird (2022; 2019) for deeper introductions.
Memory. Building on psychological theories, Soar uses several types of memory to track the agent’s
state (Atkinson and Shiffrin, 1968). Working memory (Baddeley and Hitch, 1974) reflects the agent’s current
circumstances: it stores the agent’s recent perceptual input, goals, and results from intermediate, internal
reasoning. Long term memory is divided into three distinct types. Procedural memory stores the production
system itself: the set of rules that can be applied to working memory to determine the agent’s behavior.
Semantic memory stores facts about the world (Lindes and Laird, 2016), while episodic memory stores
sequences of the agent’s past behaviors (Nuxoll and Laird, 2007).
Grounding. Soar can be instantiated in simulations (Tambe et al., 1995; Jones et al., 1999) or real-world
robotic systems (Laird et al., 2012). In embodied contexts, a variety of sensors stream perceptual input into
4
Published in Transactions on Machine Learning Research (02/2024)
working memory, where it is available for decision-making. Soar agents can also be equipped with actuators,
allowing for physical actions and interactive learning via language (Mohan et al., 2012; Mohan and Laird,
2014; Kirk and Laird, 2014).
Decision making. Soar implements a decision loop that evaluates productions and applies the one that
matches best (Fig. 2B). Productions are stored in long-term procedural memory. During each decision cycle,
their preconditions are checked against the agent’s working memory. In the proposal and evaluation phase,
a set of productions is used to generate and rank a candidate set of possible actions.∗ The best action is
then chosen.† Another set of productions is then used to implement the action – for example, modifying the
contents of working memory or issuing a motor command.
Learning. Soar supports multiple modes of learning. First, new information can be stored directly in
long-term memory: facts can be written to semantic memory, while experiences can be written to episodic
memory (Derbinsky et al., 2012). This information can later be retrieved back into working memory when
needed for decision-making. Second, behaviors can be modified. Reinforcement learning (Sutton and Barto,
2018) can be used to up-weight productions that have yielded good outcomes, allowing the agent to learn
from experience (Nason and Laird, 2005). Most remarkably, Soar is also capable of writing new productions
into its procedural memory (Laird et al., 1986) – effectively updating its source code.
Cognitive architectures were used broadly across psychology and computer science, with applications including
robotics (Laird et al., 2012), military simulations (Jones et al., 1999; Tambe et al., 1995), and intelligent
tutoring (Koedinger et al., 1997). Yet they have become less popular in the AI community over the last few
decades. This decrease in popularity reflects two of the challenges involved in such systems: they are limited
to domains that can be described by logical predicates and require many pre-specified rules to function.
Intriguingly, LLMs appear well-posed to meet these challenges. First, they operate over arbitrary text, making
them more flexible than logic-based systems. Second, rather than requiring the user to specify productions,
they learn a distribution over productions via pre-training on an internet corpus. Recognizing this, researchers
have begun to use LLMs within cognitive architectures, leveraging their implicit world knowledge (Wray
et al., 2021) to augment traditional symbolic approaches (Kirk et al., 2023; Romero et al., 2023). Here, we
instead import principles from cognitive architecture to guide the design of LLM-based agents.
2.4 Language models and agents
Language modeling is a decades-old endeavor in the NLP and AI communities, aiming to develop systems
that can generate text given some context (Jurafsky, 2000). Formally, language models learn a distribution
P (wi|w<i), where each w is an individual token (word). This model can then generate text by sampling from
the distribution, one token at a time. At its core, a language model is a probabilistic input-output system,
since there are inherently several ways to continue a text (e.g., “I went to the” → “market” | “beach” | ...).
While earlier attempts at modeling language (e.g., n-grams) faced challenges in generalization and scaling,
there has been a recent resurgence of the area due to the rise of Transformer-based (Vaswani et al., 2017)
LLMs with a large number (billions) of parameters (e.g., GPT-4; OpenAI, 2023a) and smart tokenization
schemes. Modern LLMs are trained on enormous amounts of data, which helps them accumulate knowledge
from a large number of input-output combinations and successfully generate human-like text (Andreas, 2022).
Unexpectedly, training these models on internet-scale text also made them useful for many tasks beyond
generating text, such as writing code (Li et al., 2022b; Rozière et al., 2023; Li et al., 2023c), modeling
proteins (Meier et al., 2021), and acting in interactive environments (Yao et al., 2022b; Nakano et al., 2021).
The latter has led to the rise of “language agents” – systems that use LLMs as a core computation unit to
reason, plan, and act – with applications in areas such as robotics (Ahn et al., 2022), manufacturing (Xia
et al., 2023), web manipulation (Yao et al., 2022a; Deng et al., 2023), puzzle solving (Yao et al., 2023; Hao
et al., 2023) and interactive code generation (Yang et al., 2023). The combination of language understanding
∗In more detail, Soar divides productions into two types: “operators,” which we refer to as actions, and “rules” which are
used to propose, evaluate, and execute operators.
†If no actions are valid, or multiple actions tie, then an impasse occurs. Soar creates a subgoal to resolve the impasse,
resulting in hierarchical task decomposition. We refer the reader to Laird (2022) for a more detailed discussion.
5
Published in Transactions on Machine Learning Research (02/2024)
and decision-making capabilities is an exciting and emerging direction that promises to bring these agents
closer to human-like intelligence.
3 Connections between Language Models and Production Systems
Based on their common origins in processing strings, there is a natural analogy between production systems
and language models. We develop this analogy, then show that prompting methods recapitulate the algorithms
and agents based on production systems. The correspondence between production systems and language
models motivates our use of cognitive architectures to build language agents, which we introduce in Section 4.
3.1 Language models as probabilistic production systems
In their original instantiation, production systems specified the set of strings that could be generated from a
starting point, breaking this process down into a series of string rewriting operations. Language models also
define a possible set of expansions or modifications of a string – the prompt provided to the model.‡
For example, we can formulate the problem of completing a piece of text as a production. If X is the prompt
and Y the continuation, then we can write this as the production X → X Y .§ We might want to allow
multiple possible continuations, in which case we have X → X Yi for some set of Yi. LLMs assign a probability
to each of these completions. Viewed from this perspective, the LLM defines a probability distribution
over which productions to select when presented with input X, yielding a distribution P (Yi|X) over possible
completions (Dohan et al., 2022). LLMs can thus be viewed as probabilistic production systems that sample
a possible completion each time they are called, e.g., X ∼∼▸ X Y .
This probabilistic form offers both advantages and disadvantages compared to traditional production systems.
The primary disadvantage of LLMs is their inherent opaqueness: while production systems are defined by
discrete and human-legible rules, LLMs consist of billions of uninterpretable parameters. This opaqueness –
coupled with inherent randomness from their probabilistic formulation – makes it challenging to analyze or
control their behaviors (Romero et al., 2023; Valmeekam et al., 2022). Nonetheless, their scale and pre-training
provide massive advantages over traditional production systems. LLMs pre-trained on large-scale internet
data learn a remarkably effective prior over string completions, allowing them to solve a wide range of tasks
out of the box (Huang et al., 2022b).
3.2 Prompt engineering as control flow
The weights of an LLM define a prioritization over output strings (completions), conditioned by the input string
(the prompt). The resulting distribution can be interpreted as a task-specific prioritization of productions –
in other words, a simple control flow. Tasks such as question answering can be formulated directly as an
input string (the question), yielding conditional distributions over completions (possible answers).
Early work on few-shot learning (Brown et al., 2020) and prompt engineering (Wei et al., 2022b; Kojima
et al., 2022; Xu et al., 2023c) found that the LLM could be further biased towards high-quality productions
by pre-processing the input string. These simple manipulations – typically concatenating additional text
to the input – can themselves be seen as productions, meaning that these methods define a sequence of
productions (Table 1). Later work extended these approaches to dynamic, context-sensitive prompts: for
example, selecting few-shot examples that are maximally relevant to the input (Liu et al., 2021) or populating
a template with external observations from video (Zeng et al., 2022) or databases (Lewis et al., 2020). For a
survey of such prompting techniques, see Liu et al. (2023d).
Subsequent work used the LLM itself as a pre-processing step, eliciting targeted reasoning to foreground a
particular aspect of the problem (Bai et al., 2022; Jin et al., 2022; Ganguli et al., 2023; Madaan et al., 2023;
Saunders et al., 2022; Kim et al., 2023; Kirk et al., 2023) or generate intermediate reasoning steps (Tafjord
‡In this work, we focus on autoregressive LLMs which are typically used for language agents. However, bidirectional LLMs
such as BERT (Devlin et al., 2019) can be seen in a similar light: they define a distribution over in-filling productions.
§Alternatively, we can treat the prompt as input and take the output of the LLM as the next state, represented by the
production X → Y – a more literal form of rewriting.
6
Published in Transactions on Machine Learning Research (02/2024)
Prompting Method Production Sequence
Zero-shot Q ∼∼∼∼▸
LLM
Q A
Few-shot Q −→ Q1 A1 Q2 A2 Q ∼∼∼∼▸
LLM
Q1 A1 Q2 A2 Q A
Retrieval Augmented Generation Q Wiki
−−−→ Q O ∼∼∼∼▸
LLM
Q O A
Socratic Models Q ∼∼∼∼▸
VLM
Q O ∼∼∼∼▸
LLM
Q O A
Self-Critique Q ∼∼∼∼▸
LLM
Q A ∼∼∼∼▸
LLM
Q A C ∼∼∼∼▸
LLM
Q A C A
Table 1: Conceptual diagram illustrating how prompting methods manipulate the input string before
generating completions. Q = question, A = answer, O = observation, C = critique, and ∼∼∼▸ denotes sampling
from a stochastic production. These pre-processing manipulations – which can employ other models such as
vision-language models (VLMs), or even the LLM itself – can be seen as productions. Prompting methods
thus define a sequence of productions. Question
CritiqueAnswer
Inner Monologue
VLM Act
ReAct
Refinement
Question
Selection Inference
Context
Answer
Answer
Environment Human
Reason Act
Environment
Self-Critique
Selection-Inference
Chain /
Agent
Input
LLM calls
Prompt
construction
LLM
String parsing

Execution
Figure 3: From language models to language agents. A: Basic structure of an LLM call. Prompt construction
selects a template and populates it with variables from working memory. After calling the LLM, the string
output is parsed into an action space and executed. An LLM call may result in one or more actions – for
example, returning an answer, calling a function, or issuing motor commands. B: Prompt chaining techniques
such as Self-Critique (Wang et al., 2022b) or Selection-Inference (Creswell et al., 2023) use a pre-defined
sequence of LLM calls to generate an output. C: Language agents such as Inner Monologue (Huang et al.,
2022c) and ReAct (Yao et al., 2022b) instead use an interactive feedback loop with the external environment.
Vision-language models (VLMs) can be used to translate perceptual data into text for the LLM to process.
et al., 2021; Creswell et al., 2023; Yao et al., 2023) before returning an answer. Chaining multiple calls to an
LLM (Wu et al., 2022a;b; Dohan et al., 2022) allows for increasingly complicated algorithms (Fig. 3).
3.3 Towards cognitive language agents
Language agents move beyond pre-defined prompt chains and instead place the LLM in a feedback loop with
the external environment (Fig. 1B). These approaches first transform multimodal input into text and pass it
to the LLM. The LLM’s output is then parsed and used to determine an external action (Fig. 3C). Early
agents interfaced the LLM directly with the external environment, using it to produce high-level instructions
based on the agent’s state (Ahn et al., 2022; Huang et al., 2022c; Dasgupta et al., 2022). Later work developed
more sophisticated language agents that use the LLM to perform intermediate reasoning before selecting
an action (Yao et al., 2022b). The most recent agents incorporate sophisticated learning strategies such as
reflecting on episodic memory to generate new semantic inferences (Shinn et al., 2023) or modifying their
7
Published in Transactions on Machine Learning Research (02/2024)Decision Procedure Observations
RetrievalParsePrompt

Proposal
Observation
Evaluation
Selection
Execution

Learning
Planning
Agent CodeLLM
Procedural Memory Semantic Memory Episodic Memory
Dialogue Physical Digital
Working Memory
Actions
Learning LearningRetrieval Retrieval
Reasoning
Figure 4: Cognitive architectures for language agents (CoALA). A: CoALA defines a set of interacting
modules and processes. The decision procedure executes the agent’s source code. This source code consists
of procedures to interact with the LLM (prompt templates and parsers), internal memories (retrieval and
learning), and the external environment (grounding). B: Temporally, the agent’s decision procedure executes
a decision cycle in a loop with the external environment. During each cycle, the agent uses retrieval and
reasoning to plan by proposing and evaluating candidate learning or grounding actions. The best action
is then selected and executed. An observation may be made, and the cycle begins again.
program code to generate procedural knowledge (Wang et al., 2023a), using their previous experience to
adapt their future behaviors.
These cognitive language agents employ nontrivial LLM-based reasoning and learning (Fig. 1C). Just as
cognitive architectures were used to structure production systems’ interactions with agents’ internal state and
external environments, we suggest that they can help design LLM-based cognitive agents. In the remainder
of the paper, we use this perspective to organize existing approaches and highlight promising extensions.
4 Cognitive Architectures for Language Agents (CoALA): A Conceptual Framework
We present Cognitive Architectures for Language Agents (CoALA) as a framework to organize existing
language agents and guide the development of new ones. CoALA positions the LLM as the core component
of a larger cognitive architecture (Figure 4). Under CoALA, a language agent stores information in memory
modules (Section 4.1), and acts in an action space structured into external and internal parts (Figure 5):
• External actions interact with external environments (e.g., control a robot, communicate with a
human, navigate a website) through grounding (Section 4.2).
• Internal actions interact with internal memories. Depending on which memory gets accessed and
whether the access is read or write, internal actions can be further decomposed into three kinds:
retrieval (read from long-term memory; Section 4.3), reasoning (update the short-term working
memory with LLM; Section 4.4), and learning (write to long-term memory; Section 4.5).
Language agents choose actions via decision-making, which follows a repeated cycle (Section 4.6, Figure 4B).
In each cycle, the agent can use reasoning and retrieval actions to plan. This planning subprocess selects a
grounding or learning action, which is executed to affect the outside world or the agent’s long-term memory.
CoALA’s decision cycle is analogous to a program’s “main” procedure (a method without return values, as
8
Published in Transactions on Machine Learning Research (02/2024)GroundingRetrieval LearningReasoning
Planning
ExternalInternal
Figure 5: Agents’ action spaces can be divided into internal memory accesses and external interactions
with the world. Reasoning and retrieval actions are used to support planning.
opposed to functions) that runs in loops continuously, accepting new perceptual input and calling various
action procedures in response.
CoALA (Figure 4) is inspired by the decades of research in cognitive architectures (Section 2.3), leveraging key
concepts such as memory, grounding, learning, and decision-making. Yet the incorporation of an LLM leads
to the addition of “reasoning” actions, which can flexibly produce new knowledge and heuristics for various
purposes – replacing hand-written rules in traditional cognitive architectures. It also makes text the de facto
internal representation, streamlining agents’ memory modules. Finally, recent advances in vision-language
models (VLMs; Alayrac et al., 2022) can simplify grounding by providing a straightforward translation of
perceptual data into text (Zeng et al., 2022).
The rest of this section details key concepts in CoALA: memory, actions (grounding, reasoning, retrieval,
and learning), and decision-making. For each concept, we use existing language agents (or relevant NLP/RL
methods) as examples – or note gaps in the literature for future directions.
4.1 Memory
Language models are stateless: they do not persist information across calls. In contrast, language agents
may store and maintain information internally for multi-step interaction with the world. Under the CoALA
framework, language agents explicitly organize information (mainly textural, but other modalities also allowed)
into multiple memory modules, each containing a different form of information. These include short-term
working memory and several long-term memories: episodic, semantic, and procedural.
Working memory. Working memory maintains active and readily available information as symbolic variables
for the current decision cycle (Section 4.6). This includes perceptual inputs, active knowledge (generated by
reasoning or retrieved from long-term memory), and other core information carried over from the previous
decision cycle (e.g., agent’s active goals). Previous methods encourage the LLM to generate intermediate
reasoning (Wei et al., 2022b; Nye et al., 2021), using the LLM’s own context as a form of working memory.
CoALA’s notion of working memory is more general: it is a data structure that persists across LLM calls.
On each LLM call, the LLM input is synthesized from a subset of working memory (e.g., a prompt template
and relevant variables). The LLM output is then parsed back into other variables (e.g., an action name
and arguments) which are stored back in working memory and used to execute the corresponding action
(Figure 3A). Besides the LLM, the working memory also interacts with long-term memories and grounding
interfaces. It thus serves as the central hub connecting different components of a language agent.
Episodic memory. Episodic memory stores experience from earlier decision cycles. This can consist of
training input-output pairs (Rubin et al., 2021), history event flows (Weston et al., 2014; Park et al., 2023),
game trajectories from previous episodes (Yao et al., 2020; Tuyls et al., 2022), or other representations of
the agent’s experiences. During the planning stage of a decision cycle, these episodes may be retrieved into
working memory to support reasoning. An agent can also write new experiences from working to episodic
memory as a form of learning (Section 4.5).
Semantic memory. Semantic memory stores an agent’s knowledge about the world and itself. Traditional
NLP or RL approaches that leverage retrieval for reasoning or decision-making initialize semantic memory
from an external database for knowledge support. For example, retrieval-augmented methods in NLP (Lewis
et al., 2020; Borgeaud et al., 2022; Chen et al., 2017) can be viewed as retrieving from a semantic memory of
9
Published in Transactions on Machine Learning Research (02/2024)
unstructured text (e.g., Wikipedia). In RL, “reading to learn” approaches (Branavan et al., 2012; Narasimhan
et al., 2018; Hanjie et al., 2021; Zhong et al., 2021) leverage game manuals and facts as a semantic memory
to affect the policy. While these examples essentially employ a fixed, read-only semantic memory, language
agents may also write new knowledge obtained from LLM reasoning into semantic memory as a form of
learning (Section 4.5) to incrementally build up world knowledge from experience.
Procedural memory. Language agents contain two forms of procedural memory: implicit knowledge stored
in the LLM weights, and explicit knowledge written in the agent’s code. The agent’s code can be further
divided into two types: procedures that implement actions (reasoning, retrieval, grounding, and learning
procedures), and procedures that implement decision-making itself (Section 4.6). During a decision cycle, the
LLM can be accessed via reasoning actions, and various code-based procedures can be retrieved and executed.
Unlike episodic or semantic memory that may be initially empty or even absent, procedural memory must be
initialized by the designer with proper code to bootstrap the agent. Finally, while learning new actions by
writing to procedural memory is possible (Section 4.5), it is significantly riskier than writing to episodic or
semantic memory, as it can easily introduce bugs or allow an agent to subvert its designers’ intentions.
4.2 Grounding actions
Grounding procedures execute external actions and process environmental feedback into working memory as
text. This effectively simplifies the agent’s interaction with the outside world as a “text game” with textual
observations and actions. We categorize three kinds of external environments:
Physical environments. Physical embodiment is the oldest instantiation envisioned for AI agents (Nilsson,
1984). It involves processing perceptual inputs (visual, audio, tactile) into textual observations (e.g., via
pre-trained captioning models), and affecting the physical environments via robotic planners that take
language-based commands. Recent advances in LLMs have led to numerous robotic projects (Ahn et al., 2022;
Liang et al., 2023a; Singh et al., 2023; Palo et al., 2023; Ren et al., 2023) that leverage LLMs as a “brain”
for robots to generate actions or plans in the physical world. For perceptual input, vision-language models
are typically used to convert images to text (Alayrac et al., 2022; Sumers et al., 2023) providing additional
context for the LLM (Driess et al., 2023; Huang et al., 2023; Brohan et al., 2022; 2023).
Dialogue with humans or other agents. Classic linguistic interactions allow the agent to accept
instructions (Winograd, 1972; Tellex et al., 2011; Chen and Mooney, 2011; Bisk et al., 2016) or learn from
people (Nguyen et al., 2021; Sumers et al., 2022; 2021; Wang et al., 2016). Agents capable of generating
language may ask for help (Ren et al., 2023; Nguyen et al., 2022b; 2019; Nguyen and Daumé III, 2019) or
clarification (Biyik and Palan, 2019; Sadigh et al., 2017; Padmakumar et al., 2022; Thomason et al., 2020;
Narayan-Chen et al., 2019) – or entertain or emotionally help people (Zhang et al., 2020; Zhou et al., 2018;
Pataranutaporn et al., 2021; Hasan et al., 2023; Ma et al., 2023). Recent work also investigates interaction
among multiple language agents for social simulation (Park et al., 2023; Jinxin et al., 2023; Gao et al., 2023),
debate (Chan et al., 2023; Liang et al., 2023b; Du et al., 2023), improved safety (Irving et al., 2018), or
collabrative task solving (Qian et al., 2023; Wu et al., 2023; Hong et al., 2023a; Dong et al., 2023).
Digital environments. This includes interacting with games (Hausknecht et al., 2020; Côté et al., 2019;
Shridhar et al., 2020; Wang et al., 2022a; Liu et al., 2023e), APIs (Schick et al., 2023; Yao et al., 2022b; Parisi
et al., 2022; Tang et al., 2023b), and websites (Shi et al., 2017; Nakano et al., 2021; Yao et al., 2022a; Zhou
et al., 2023b; Gur et al., 2023; Deng et al., 2023) as well as general code execution (Yang et al., 2023; Le
et al., 2022; Ni et al., 2023). Such digital grounding is cheaper and faster than physical or human interaction.
It is thus a convenient testbed for language agents and has been studied with increasing intensity in recent
years. In particular, for NLP tasks that require augmentation of external knowledge or computation, stateless
digital APIs (e.g., search, calculator, translator) are often packaged as “tools” (Parisi et al., 2022; Schick
et al., 2023; Xu et al., 2023a; Tang et al., 2023b; Qin et al., 2023), which can be viewed as special “single-use”
digital environments.
10

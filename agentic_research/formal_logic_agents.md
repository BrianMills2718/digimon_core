Write
Home
Following
Library
Stories

Recent
Volodymyr Pavlyshyn
Volodymyr Pavlyshyn
Sean Falconer
Sean Falconer
Jeong Yitae
Jeong Yitae
The Medium Blog
The Medium Blog
Lawrence Sanjay
Lawrence Sanjay
Don D.M. Tadaya • DASCIENT LLC
Don D.M. Tadaya • DASCIENT LLC
Carl Olinselot
Carl Olinselot
Andrew V Kennedy
Andrew V Kennedy
Victor Morgante
Victor Morgante
TDS Archive
TDS Archive
See all

Member-only story
Formalism for Game-Theoretic Approach to Formal Logic
Unifying Communication Theory, Formal Logic and Game Theory
Victor Morgante
Victor Morgante
17 min read
·
Jun 10, 2024

Victor Morgante

Also available as PDF: (13) (PDF) Formalism for Game-Theoretic Approach to Formal Logic. Unifying Communication Theory, Formal Logic and Game Theory (researchgate.net)
Abstract

This paper presents a game-theoretic approach to formal logic, where players cooperate to interpret theorems of a theory in a coherent and understandable manner. The objective is to achieve clear communication and a shared understanding of the theorems. We introduce a formalism for this non-adversarial game, including payoff functions, and explore conditions under which cooperation and consensus are likely to occur. Key theorems and propositions are presented, such as the Coherence Theorem, which states that there exists an interpretation allowing all cooperating players to achieve a positive payoff from the theorems of a theory. The Differential Interpretation Game (DIG) is introduced, where players can choose different interpretations that are provable under notation and syntax of a theory, drawing a parallel with the compactness theorem in logic. The stability and convergence of differential interpretations are discussed, highlighting the juxtaposition between local and global coherence in formal logic and game theory. This framework offers insights into the dynamics of interpretation and the role of interpreters in maintaining the integrity of a theory.
1 Introduction

Formal logic has long been a cornerstone of reasoning and philosophical inquiry. It provides a rigorous framework for analysing the structure of arguments, deriving valid conclusions, and exploring the principles that govern rational thought. However, the traditional approach to formal logic often focuses on the study of individual logical systems and their properties, without considering the broader context in which these systems are developed, interpreted, and communicated.

In this paper, we propose a novel meta-logical approach to formal logic that draws upon the principles of game theory.

By viewing the development and interpretation of logical theories as a cooperative game played by multiple agents, we aim to shed light on the complex dynamics that underlie the creation and sharing of mathematical knowledge. This approach represents a departure from the conventional perspective, which tends to treat formal logic as a static and solitary endeavor.

The game-theoretic framework we introduce allows us to explore the incentives, strategies, and interactions that shape the way logical theories are constructed and understood. We consider players as agents engaged in the process of creating and interpreting formal logic, each bringing their own unique perspectives and goals to the table. The objective of the game we investigate is to achieve a shared understanding of the theory under consideration, characterized by clear communication and a coherent interpretation of its theorems.

We also propose an extension of Ehrenfeucht-Fraısse games, from finite model theory, to cover judgment over any logical theory, regardless of its model-theoretic properties. By adapting these games to our framework, we establish a mechanism for testing the cohesion of interpretations proposed by players. This extension allows us to evaluate the robustness and consistency of the shared understanding reached through the cooperative game. Without such a test, we would have no means of assessing the validity and coherence of the interpretations developed by the players. The Ehrenfeucht-Fraisse games, in their expanded form, serve as a critical component of our meta-logical approach, ensuring that the collaborative effort produces a well-grounded and reliable understanding of the logical theory under consideration.

Central to our approach is the concept of coherence, both at the local and global levels. We investigate how players navigate the tension between developing locally consistent interpretations of a theory’s theorems and extending these interpretations to the entire theory in a globally coherent manner. Drawing upon the compactness theorem from logic, we explore the conditions under which local coherence can be leveraged to achieve global understanding. Our framework emphasizes the cooperative nature of the logical enterprise. We examine how players collaborate, negotiate, and refine their interpretations in the pursuit of a shared understanding. The process of arriving at a consensus interpretation is modelled as a cooperative game, where players work together to maximize their collective payoff by establishing clear and effective communication.

By situating formal logic within a game-theoretic context, we aim to provide a fresh perspective on the nature of logical reasoning and the mechanisms that drive the growth of mathematical knowledge. This meta-logical approach offers new insights into the role of collaboration, interpretation, and communication in the sphere of formal systems.

In the following sections, we will develop the formal framework for our game-theoretic approach, introduce key theorems and propositions, and explore the implications of this perspective for the study of logic. We discuss the novel concept of the Differential Interpretation Game, which allows players to propose and evaluate alternative interpretations of a theory, potentially leading to new discoveries and innovations.

Through this work, we hope to contribute to a deeper understanding of formal logic, highlighting the vital interplay between individual creativity and collective endeavour in the pursuit of mathematical truth and as that exists under any one game.
2 The Coherent Cooperative Game of Formal Logic (CCGFL)

In this section, we introduce a novel game-theoretic approach to formal logic, which we call the Coherent Cooperative Game of Formal Logic (CCGFL). This game models the process of developing and sharing interpretations of logical theories among multiple players, with the aim of achieving a shared understanding through cooperation and communication.

2.1 Game Description

The CCGFL is played by a group of players, each representing an agent engaged in the study of a particular logical theory. The game progresses through a series of moves, where each move consists of either:

1. Sharing a written theorem with one or more players for interpretation, or

2. Presenting a self-written and self-interpreted theorem under the theory being investigated.

The objective of the game is for all players to converge on a single, coherent interpretation of the logical theory under consideration. Players collaborate by exchanging ideas, proposing interpretations, and providing proofs to support their understanding. The game reaches a state of coherence when all players adopt the same interpretation and consistently apply it to the theorems being shared.

2.2 Ehrenfeucht-Fraısse Games and the CCGFL

The CCGFL can be seen as a stylized version of the classic Ehrenfeucht-Fraısse (EF) games, which are used in finite model theory to compare the expressive power of logical structures. However, there is a crucial difference between the two games.

In an EF game, players compete against each other, with one player aiming to prove the equivalence of two structures, while the other player attempts to disprove it. In contrast, the CCGFL is a cooperative game, where players work together to achieve a common goal — a shared and coherent interpretation of the logical theory.

In the CCGFL, there is no notion of losing, and players do not engage in deception or adversarial strategies. Instead, the focus is on collaboration, communication, and the collective pursuit of understanding. Proofs serve as a means to reach an agreement on an interpretation or to confirm its validity, rather than as tools for competition. Players do not lose if they diverge from a shared and global interpretation, they simply do not play a CCGFL.

2.3 Differential Interpretation Game

Later in this paper, we will introduce a variant of the CCGFL called the Differential Interpretation Game (DIG). In the DIG, players revert to the rules of a classic EF game, allowing for the emergence of multiple interpretations. This game models scenarios where players propose divergent interpretations of the logical theory, leading to a more complex and dynamic landscape of understanding.

The DIG serves as a counterpoint to the CCGFL, highlighting the potential for disagreement and the challenges of maintaining coherence in the face of competing interpretations. It also raises important questions about the conditions under which coherence can be restored and the mechanisms through which players can navigate the space of possible interpretations.

2.4 Coherence and the Impossibility of Certainty

A key insight that emerges from the CCGFL framework is that coherence and convergence on a shared interpretation can only be achieved through cooperative gameplay. It is only by engaging in the collaborative process of sharing, interpreting, and refining theories that players can hope to arrive at a common understanding.

However, the framework also highlights a fundamental limitation: no two players can ever be entirely certain that they have achieved perfect coherence. This is because there always exists the possibility that one or more players are secretly engaging in a Differential Interpretation Game, proposing alternative interpretations that diverge from the agreed-upon understanding.

This impossibility of certainty adds a layer of complexity to the game-theoretic analysis of formal logic. It suggests that the pursuit of coherence is an ongoing process, requiring continuous communication, verification, and refinement. It also highlights the fragility of the cooperative equilibrium, as the introduction of divergent interpretations can disrupt the shared understanding and necessitate further negotiation and resolution.
3 Game Mechanics and Definitions

In this section, we define the key components and mechanics of the CCGFL and establish the necessary terminology to facilitate a clear understanding of the game.

3.1 Preliminaries

Before defining the specifics of the game, we acknowledge that our framework relies on well-established concepts from formal logic. We assume familiarity with the notions of a logical theory, theorems, interpretation and the principles of formal logic and model theory, which also involve reducing sentences of knowledge expression to their smallest and rawest form using the symbols and syntax of the theory under consideration. Theorems, as statements that can be proven within the framework of a given theory, form the basic building blocks of our game.

3.2 Moves and Communications

In the CCGFL, a move consists of one or more players writing theorems of a theory and providing their interpretation. The interpretation of a theorem involves explaining its meaning, significance, and implications within the context of the theory.

A move can be made by a single player or collaboratively by multiple players working together to develop and interpret theorems.

A communication refers to the act of sharing fully written theorems with other players. It involves presenting the theorems and their associated interpretations to the other participants in the game. Communications can be seen as a component of a move, as they facilitate the exchange of ideas and interpretations among players.

3.3 Payoffs and Objectives

• Payoffs: In the CCGFL, a player receives a payoff when they successfully interpret theorems of a theory in a manner that is both consistent with the theory’s axioms, rules of inference (i.e., e.g., provable within the theory), established notation and conventions and coherent with the interpretations provided by themselves and all other players. That is, in this game, the payoff for a player is achieved when they can interpret theorems of a theory in a manner that is both interpretable and/or provable under the interpretation of the theory (all notions of incompleteness aside), and when these theorems meet the axiomatic and synthesis notation of the theory under study. The ultimate goal is to achieve effective and successful communication and shared understanding of the theorems among all players.

• Cooperative Nature: The CCGFL becomes a cooperative game when players work to interpret theorems using a consistent and agreed-upon interpretation. By aligning their interpretations and converging on the same interpretation, players ensure coherence and clarity in their understanding of the theory. The cooperative aspect of the game requires players to be aware of the specific theory they are working with and to strive towards the common objective of clear communication and comprehension of the theorems.

• Non-Adversarial Structure: Unlike adversarial games such as the Ehrenfeucht-Fraisse game, where players have opposing goals (e.g., the duplicator trying to prove the equivalence of structures, while the spoiler attempts to disprove it), the CCGFL is inherently non-adversarial. Players do not aim to confuse, confound or mislead each other but instead collaborate to develop a shared understanding of the theory. The focus is on cooperation, mutual support, and the collective pursuit of knowledge. It can be said that one or more players only play a CCGFL if their intent is that on each move all players win and achieve payoff.

3.4 Strategies and Outcomes

With the framework of the CCGFL in place, we can explore various aspects of the game, such as:

• The conditions that promote cooperation and facilitate the achievement of a shared interpretation among players.

• The strategies players may employ to ensure coherence and consistency in their interpretations, such as careful analysis of theorems, open communication, and iterative refinement of their understanding.

• The impact of the theory’s structure, axioms, and rules of inference on the game’s dynamics and the ease or difficulty of arriving at a unified interpretation.

By formalizing these aspects of the game, we can gain insights into the processes of collaborative theorem interpretation and the factors that influence the success of such endeavours.

With this framework, we can start to formalize the interactions and outcomes in this game. We can explore conditions under which cooperation is most likely to occur, place the strategies players might use to achieve coherence in interpretation under game theory, and how the structure of the theory itself influences the game.

In the following sections, we formalize the CCGFL providing a framework for extensions in the further study and implementation of formal logic and knowledge sharing.

We formulate a theorem stating the conditions by which a group of players interpreting theorems of a theory have converged to a common interpretation that maximizes their collective payoff (i.e., clear and coherent communication of theorems).

Symbols and Notation:

• Players: Let P = {p1, p2, . . . , pn} represent the set of players in the game, where each pi is an individual or entity involved in creating or interpreting formal logic.

• Theories: Let T = {t1, t2, . . . , tm} represent the set of theories under consideration in the game.

• Theorems: Let Th = {th1, th2, . . . , thk} represent the set of theorems derived from the theories in T.

• Interpretations: Let I = {i1, i2, . . . , il} represent the set of possible interpretations that players can apply to theorems in Th.

• Payoff Function: Let π : P × Th × I → R be the payoff function, where π(pi, thj , ik) represents the payoff to player pi when interpreting theorem thj using interpretation ik.

Theorems and Propositions:

• Coherence Theorem: For any theory t ∈ T and a set of players P′ ⊆ P, there exists an interpretation i* ∈ I such that for all p ∈ P′ and for all theorems th ∈ Th derived from t, π(p, th, i*) > 0. This theorem states that there is an interpretation that allows all players in P′ to achieve a positive payoff from the theorems of theory t.

Cooperation Proposition: If a set of players P′ ⊆ P use the same interpretation i* ∈ I for all theorems th ∈ Th derived from a theory t ∈ T, then the sum of their payoffs is maximized. That is,

is maximized for all th ∈ Th.

• Communication Theorem: For any theory t ∈ T and a set of players P′ ⊆ P, if there exists an interpretation i* ∈ I such that for all p ∈ P′ and for all theorems th ∈ Th derived from t, π(p, th, i*) > 0, then the players in P′ can successfully communicate and share theorems of theory t in an understandable way.

• Consensus Theorem: Let N be a finite number of moves or steps in the game. For any theory t ∈ T, if all players in P agree on an interpretation i* ∈ I within N moves, then the game is a coherent cooperative game with a maximal payoff, where the maximal payoff is achieved when all players work under the same interpretation i*.

Formally, if ∃i* ∈ I such that ∀p ∈ P, ∀th ∈ Th derived from t, and within N moves, π(p, th, i*) > 0 and ∀p, p′ ∈P, π(p, th, i*) = π(p′, th, i*), then the game is a coherent cooperative game with a maximal payoff.

This theorem states that if all players reach a consensus on the interpretation of theorems within a finite number of moves, then the game achieves its maximal payoff, characterized by coherent cooperation among the players.

• Differential Interpretation Game (DIG) Theorem: Let N be a finite number of moves in the game. For any theory t ∈ T, if a player p ∈ P chooses a different interpretation i′ ∈ I from the consensus interpretation i* after N moves, which is provable under the notation and syntax of theory t, then the player effectively engages in the Differential Interpretation Game (DIG).

Formally, if ∃i′ ∈ I and i′ ̸= i* such that for some p ∈ P and th1..n ⊆ Th derived from t, after N moves, p chooses i′ and π(p, th1..n, i′) > 0, then p is playing DIG.

• Stability Corollary: If a player consistently chooses the same differential interpretation i′ in successive games of DIG, then the interpretation i′ is considered stable.

• Convergence Corollary: If multiple players independently choose the same differential interpretation i′ in the DIG, it may indicate a convergence toward a new consensus interpretation.

• Compactness and Interpretation: The compactness theorem, if i′ limited to first-order logic, can be seen as an assurance that if a differential interpretation i′ can satisfy a finite subset of theorems derived from the theory t, then there exists a model (or an ”interpreter”) that can satisfy all theorems under the interpretation i′.

The Differential Interpretation Game (DIG) conceptually parallels the compactness theorem in the sense that both involve the idea of extending local consistency or satisfaction (in the case of DIG, the coherence and provability of a differential interpretation) to a broader context (the entire set of theorems in a theory). Just as the compactness theorem assures that a finitely satisfiable set of formulas is satisfiable in its entirety, the DIG suggests that a differential interpretation that is coherent and provable for a subset of theorems can be extended to the whole theory, given the right conditions and the existence of a suitable interpreter.

This analogy highlights the interplay between local and global coherence in formal logic and game theory, emphasizing the importance of consistent interpretation and the role of interpreters in maintaining the integrity of a theory. In the context of DIG, the compactness theorem can be interpreted assuring players in a game and as follows:

• Compactness and Interpretation: The compactness theorem states that if a set of formulas is finitely satisfiable, then it is satisfiable. In the context of DIG, this can be seen as an assurance that if a differential interpretation i′ can satisfy a finite subset of theorems derived from the theory t, then there exists a model (or an ”interpreter”) that can satisfy all theorems under the interpretation i′.

That is, in as much as a first-order theory may otherwise be interpreted under higher-order logic, given a limited set of theorems of an arbitrary theory and finitely satisfiable under first-order logic we have no way of knowing whether the global interpretation is under higher-order logic other than by the interpreter discovering and acknowledging the higer-order interpretation or by process of learning of that interpretation through engagement with other interpreters. We therefore acknowledge the existence of an interpreter and other interpreters.

• Existence of an Interpreter: The application of the compactness theorem relies on the existence of an interpreter that is distinct from theorems and a theory itself. This interpreter acts as an agent that validates the coherence and provability of the differential interpretation i′ within the framework of formal logic.

In DIG, the objective of the player p is to demonstrate that their new interpretation i′ is coherent and provable within the framework of formal logic, even if it differs from the consensus interpretation i* agreed upon by other players. This game allows for the exploration of diverse logical interpretations, potentially leading to new insights or advancements in the theory under investigation.
Local and Global Coherence in the Differential Interpretation Game

Local coherence from a player’s perspective:

• Refers to a player’s ability to choose an interpretation that is consistent and provable for a specific subset of theorems derived from a theory.

• In the Differential Interpretation Game (DIG), an individual player may choose a different interpretation that is coherent and provable for a subset of theorems they are focusing on.

• This local coherence allows the player to explore and validate their interpretation within a limited scope of the theory.

Global coherence from a player’s perspective:

• Refers to a player’s interpretation being consistent and provable for all theorems within the entire theory.

• When a player’s interpretation is globally coherent, it means that their understanding of the theory is consistent and provable across all derived theorems of the theory.

• Achieving global coherence is a more challenging task for an individual player, as it requires their interpretation to be valid for the entire theory.

The juxtaposition between local and global coherence from a player’s perspective highlights the idea that a player may start with a locally coherent interpretation (consistent and provable for a subset of theorems) and then work towards extending this interpretation to be globally coherent (consistent and provable for all theorems in the theory). This process of moving from local to global coherence suggests that if a player’s interpretation is finitely satisfiable (locally satisfiable), then there may exist a way to make it satisfiable for the entire theory (globally satisfiable).

In the Differential Interpretation Game, players have the opportunity to explore different interpretations and challenge the existing consensus. This allows for individual players to contribute their unique perspectives, a process of communication.

The leap from local to global coherence:

• In the Differential Interpretation Game (DIG), players start by exploring different interpretations that are coherent and provable for a subset of theorems (locally coherent).

• To make the leap from local to global coherence, players must demonstrate that their interpretation can be extended to satisfy all theorems within the theory.

• This process may involve iterative refinement of the interpretation, where players adjust and expand their understanding to encompass more theorems.

• The compactness theorem suggests that if a player’s interpretation is finitely satisfiable (locally satisfiable), there exists a model or an ”interpreter” that can satisfy all theorems under that interpretation.

• The existence of such an interpreter provides a mechanism for players to transition from local to global coherence, as it guarantees that a locally coherent interpretation can be extended to an/the entire theory and cements the role of a player in a game.

Mechanism for arriving at a shared interpretation: Communication and game play:

• In the game-theoretic approach to formal logic, players engage in a cooperative process to arrive at a shared interpretation of the theory.

• Players communicate their interpretations and provide justifications for their understanding of the theorems.

• Through discussion and collaboration, players compare their interpretations and identify areas of agreement and disagreement.

• The Coherence Theorem suggests that there may exist an interpretation that allows all cooperating players to achieve a positive payoff from the theorems of a theory.

• Players work towards finding this coherent interpretation that maximizes their collective payoff and enables clear communication and understanding of the theorems.

• The process of arriving at a shared interpretation involves negotiation, compromise, and the integration of different perspectives.

• Players may need to adapt their interpretations based on the insights and arguments presented by other players.

• The stability and convergence of differential interpretations (as mentioned in the Stability Corollary and Convergence Corollary) contribute to the development of a shared interpretation.

• If multiple players independently arrive at the same differential interpretation, it indicates a potential convergence towards a new consensus interpretation and provides the basis for engagement in a CCGFL.

The transition from local to global coherence and the mechanism for arriving at a shared interpretation are interconnected.

As players work towards extending their locally coherent interpretations to the entire theory, and if and when they engage in a collaborative process of communication, negotiation, and refinement as to the global interpretation is a CCGFL when each subsequent move results in a payoff under that shared interpretation. The pursuit of a coherent interpretation that maximizes collective payoff drives the process of arriving at a shared understanding.

The game-theoretic approach to formal logic highlights the importance of individual players’ contributions and the collaborative effort required to develop a comprehensive and shared interpretation of a theory. It emphasizes the interplay between local and global coherence, the role of interpreters, and the mechanisms of communication and negotiation in the pursuit of a unified understanding of formal logic.

3.5 Implications and Further Developments

The CCGFL framework offers a fresh perspective on the nature of formal logic and the processes through which logical theories are developed, interpreted, and shared. By modelling these processes as a cooperative game, we can gain insights into the dynamics of collaboration, the role of communication, and the challenges of achieving coherence in the face of multiple interpretations.

Through this work, we aim to contribute to a richer understanding of the social and interpersonal dimensions of logical reasoning, highlighting the importance of cooperation, dialogue, and the collective pursuit of knowledge in the sphere of formal logic.

This work was inspired by the introduction within “Models and Games” by Jouko Väänänen [1].
References

    J. Väänänen, Models and Games. Cambridge, UK: Cambridge University Press, 2011.

— -

More research in this area:

    The Genesis of Coherent Cooperative Games;
    Coherent Cooperative Games — Described;
    Coherent Cooperative Games and the Law;
    Formal Logic — And Coherent Cooperative Games;

….and…

    The Atoms of Knowledge;
    All of Logic is a Game;
    What is Formal Logic;
    Applied Use of Ehrenfeucht Fraisse Games;
    What is a Graph Database;

…and…

    The Atoms of Knowledge;
    The Richmond Architecture;

…and where it all started:

    Morphing Conceptual Models.

Game Theory
Information Theory
Communication Theory
Formal Logic
Coherent Games

Victor Morgante
Written by Victor Morgante
518 followers
·
247 following

@FactEngine_AI. Manager, Architect, Data Scientist, Researcher at www.factengine.ai and www.perceptible.ai
No responses yet
Brian Mills
Brian Mills

﻿
More from Victor Morgante
What is Fact-Based Modelling?
TDS Archive

In

TDS Archive

by

Victor Morgante
What is Fact-Based Modelling?
Fact-Based Modelling is a type of conceptual modelling where the key data structure, the fact type, operate over facts.
Jul 22, 2020
61
The AI Call Centre of the Future
AI Customer Service

In

AI Customer Service

by

Victor Morgante
The AI Call Centre of the Future
Voice Agents, Bot Frameworks, Conversational AI, Database Access
Jul 25, 2024
5
N-Ary Relationships in Graph Databases
TDS Archive

In

TDS Archive

by

Victor Morgante
N-Ary Relationships in Graph Databases
Why hypergraph databases have the edge
Mar 25, 2021
13
1
Why isn’t Object-Role Modeling more popular?
Victor Morgante

Victor Morgante
Why isn’t Object-Role Modeling more popular?
Should it be?
Sep 6, 2024
2
2
See all from Victor Morgante
Recommended from Medium
Semantic Spacetime 2: Why you still can’t find what you’re looking for…
Mark Burgess

Mark Burgess
Semantic Spacetime 2: Why you still can’t find what you’re looking for…
How to better know what you know “you already know”, you know?
Apr 8
56
2
AI Undresses Women And Girls “For Fun,” Makes 36 Million In Profit
History of Women

In

History of Women

by

Linda Caroll
AI Undresses Women And Girls “For Fun,” Makes 36 Million In Profit
Nudify websites make a killing but women lose their jobs if they have an OnlyFans account to make ends meet
Jul 16
6.2K
160
A lone figure seen from behind stands at the center of a sleek, all‑white suspension bridge framed by repeating vertical cables and graceful arches, gazing toward an open, light‑filled expanse.
Bootcamp

In

Bootcamp

by

Jagna Birecka
There is UX life beyond the corporate world — and it’s not bad at all
We often talk about design as a way to make life better for others, but how often do we stop to think what design does to our own lives?
5d ago
183
9
an image of a futuristic cyborg with the text “prompt engineering is dead” to the right of it
Jordan Gibbs

Jordan Gibbs
The Only ChatGPT Prompt that Matters.
Forget every prompt gimmick you’ve ever learned; this is all you need.
Jul 13
3.3K
85
GPT-5 Is Coming in July 2025 — And Everything Will Change
Predict

In

Predict

by

iswarya writes
GPT-5 Is Coming in July 2025 — And Everything Will Change
“It’s wild watching people use ChatGPT… knowing what’s coming.”  — OpenAI insider
Jul 7
8.9K
299
Why Japanese Developers Write Code Completely Differently (And Why It Works Better)
Sohail Saifi

Sohail Saifi
Why Japanese Developers Write Code Completely Differently (And Why It Works Better)
I’ve been studying Japanese software development practices for the past three years, and what I discovered completely changed how I think…
6d ago
6K
173
See more recommendations

Help

Status

About

Careers

Press

Blog

Privacy

Rules

Terms

Text to speech
All your favorite parts of Medium are now in one sidebar for easy access.


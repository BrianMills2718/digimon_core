Here is a detailed outline of the paper "Generative Agent Simulations of 1,000 People" and its MLA citation.

MLA Citation

Park, Joon Sung, et al. "Generative Agent Simulations of 1,000 People." Working Paper, Stanford University, 2024.

Detailed Outline of the Paper

I. Introduction & Core Problem

    A. The Promise of Behavioral Simulation: The paper begins by highlighting the potential of general-purpose computational agents to simulate human behavior. Such simulations could be a powerful tool for social scientists and policymakers to test theories and interventions (e.g., public health policies, product launches) in a controlled "laboratory" environment.

    B. Limitations of Existing Methods:

        Traditional Models: Agent-based models and game theory often rely on manually specified rules, which simplifies human behavior and limits the agents to narrow contexts.

        Generative AI Models: While Large Language Models (LLMs) have vast knowledge of human behavior, they risk creating generic agents based on demographic stereotypes rather than nuanced individuals.

    C. The Paper's Contribution: The authors introduce a novel generative agent architecture that simulates 1,052 real individuals by conditioning an LLM on extensive, two-hour qualitative interviews. This approach aims to create high-fidelity, individualized simulations that avoid stereotyping.

    D. Core Research Questions:

        How accurately can these interview-based agents replicate the attitudes and behaviors of the real people they represent?

        How does this approach compare to baseline methods that use demographics or simple personas?

        Can these agents replicate population-level treatment effects from social science experiments?

        Does using in-depth interviews reduce accuracy biases across demographic groups?

II. Methodology: Creating and Evaluating the Agents

    A. Data Collection:

        Participants: Recruited a stratified sample of 1,052 U.S. individuals, representative of the population across age, gender, race, education, political ideology, etc.

        The AI Interviewer: To ensure consistency and scalability, the authors developed an AI interviewer to conduct two-hour, semi-structured voice interviews with each participant. The interviews followed a script from the American Voices Project, covering life stories, relationships, health, political views, and societal issues. The average transcript length was 6,491 words.

        Evaluation Data: After the interview, participants completed a battery of established social science instruments:

            The General Social Survey (GSS)

            The Big Five Personality Inventory (BFI-44)

            Five behavioral economic games (e.g., Dictator Game, Prisoner's Dilemma)

            Five social science experiments

        Self-Consistency Check: Participants retook the surveys and experiments two weeks later to establish a "human baseline" for consistency.

    B. Generative Agent Architecture:

        Foundation: The agents are powered by an LLM (GPT-4o) whose behavior is conditioned by the participant's full interview transcript.

        Expert Reflection: The architecture includes a reflection module where the LLM adopts the persona of a domain expert (e.g., psychologist, political scientist) to synthesize high-level insights from the interview transcript.

        Querying: When an agent is queried (e.g., asked a survey question), the full interview transcript and relevant expert reflections are passed to the LLM, which then generates a response in the persona of the individual.

    C. Evaluation Metrics & Baselines:

        Metrics:

            Accuracy: For categorical responses (GSS).

            Mean Absolute Error (MAE): For continuous responses (Big Five, economic games).

            Correlation: Used across all constructs.

            Normalized Accuracy/Correlation: The key metric, calculated as (Agent's Accuracy) / (Human's Own Replication Accuracy). A score of 1.0 indicates the agent is as accurate at predicting the person's behavior as the person is at replicating their own behavior two weeks later.

        Baselines for Comparison:

            Demographic-based Agents: Agents conditioned only on demographic data (age, race, gender, ideology).

            Persona-based Agents: Agents conditioned on a short, self-written paragraph by the participant.

III. Key Findings and Results

    A. Predicting Individual Attitudes and Behaviors:

        General Social Survey (GSS): Interview-based agents achieved a normalized accuracy of 0.85 (meaning 85% as accurate as human self-replication). This significantly outperformed demographic-based (0.71) and persona-based (0.70) agents.

        Big Five Personality: Interview-based agents achieved a normalized correlation of 0.80, again outperforming demographic (0.55) and persona-based (0.75) agents.

        Economic Games: Interview-based agents achieved a normalized correlation of 0.66. There was no significant difference between the different agent types for this task.

        Interview Robustness: Exploratory analysis showed that even when 80% of the interview was removed, the agent still performed better than agents built from survey data alone, demonstrating the information richness and efficiency of qualitative interviews.

    B. Predicting Experimental Replications:

        The human participants successfully replicated the findings of 4 out of 5 social science experiments.

        The interview-based generative agents also replicated the same 4 studies and failed to replicate the same one, matching the human outcome.

        The correlation between the agent-predicted effect sizes and the human-replicated effect sizes was extremely high (r=0.98).

    C. Interviews Reduce Demographic Bias:

        The study measured bias using the Demographic Parity Difference (DPD), which is the performance gap between the best- and worst-performing demographic subgroups.

        Finding: Using interviews consistently reduced bias compared to using demographics.

        By Political Ideology (GSS): The DPD dropped from 12.35% (demographic agents) to 7.85% (interview agents).

        By Race (GSS): The DPD dropped from 3.33% (demographic agents) to 2.08% (interview agents).

IV. Conclusion & Research Access

    A. Main Conclusion: The study demonstrates that generative agents conditioned on in-depth qualitative interviews can simulate real individuals' attitudes and behaviors with high fidelity. The richness of this interview data provides a more accurate and less biased foundation for simulation than simple demographics or personas.

    B. Research Access to the Agent Bank: To balance scientific advancement with participant privacy, the authors propose a two-pronged access system:

        Open Access: Researchers can access aggregated responses on fixed tasks (like the GSS).

        Restricted Access: After a review process, researchers can gain access to individual agent responses for open-ended queries, enabling more complex bottom-up simulations.

    C. Significance: This work provides a foundation for creating new AI-powered tools that can help investigate complex individual and collective human behavior in a replicable and scalable way.





Social Simulacra: Creating Populated Prototypes for Social Computing Systems

This paper introduces social simulacra, a novel prototyping technique designed to help social computing designers anticipate and understand the breadth of social behaviors that may emerge in a new system once it is populated at a larger scale. Current prototyping methods often rely on small groups, failing to reveal challenges that only arise with a larger user base, such as anti-social behaviors or unexpected community norms. Social simulacra leverage large language models (LLMs) to generate realistic social interactions, including posts, replies, and even anti-social behaviors, based on a designer's description of a community's goal, rules, and member personas.

Abstract

The core idea of social simulacra is to provide designers with a populated prototype of their envisioned social computing system. By inputting a community's design (goal, rules, and member personas), the technique outputs simulated behavior, allowing designers to explore "what if?" scenarios and refine their designs before deployment. The paper highlights that LLMs, specifically GPT-3, are particularly suited for this due to their extensive training data, which includes a wide range of social media interactions, both positive and negative. Evaluations show that participants often struggle to distinguish simulated behavior from real community behavior, and social computing designers successfully refine their designs using this method.

Introduction

Designing pro-social online spaces is challenging because the impact of design decisions on community norms, newcomer integration, and anti-social behavior is difficult to predict. Traditional prototyping, often involving small user groups, doesn't capture the complexities of large-scale social systems. Issues like trolling, hate speech, and the difficulty of reaching a "critical mass" of users for effective testing are significant hurdles. Social simulacra aim to bridge this gap by using LLMs to populate a system with generated users and interactions, allowing designers to envision a wider range of potential outcomes, both pro-social and anti-social. The technique also enables exploration of intervention strategies, such as how a thread might react to a moderator's action.

The paper outlines two evaluations:

    Technical evaluation: Assesses the believability of generated social behaviors across various communities. Results indicate participants struggled to distinguish simulated conversations from real ones, performing close to chance accuracy (41% misidentification rate).

Designer evaluation: Explores whether simulacra provide meaningful insights to social computing designers. Sixteen designers refined their subreddit designs based on insights gained from using social simulacra, identifying both positive use cases and negative behaviors they hadn't anticipated.

The authors emphasize that social simulacra do not aim for perfect prediction but rather to offer a tool for testing intuitions about the breadth of possible social behaviors, from ideal interactions to problematic edge cases that could lead to community collapse.

Related Work

The paper positions social simulacra within existing research on:

Prototyping in Design Practice

Prototypes in HCI are concrete representations of interactive systems, designed to be flexible, quick to create, and to facilitate reflection and insight. They help capture ideas, explore design spaces, improve communication between stakeholders, and enable early evaluation. Social simulacra extend prototyping tools that proxy for user behavior.

Challenges of Prototyping Social Computing Systems

Prototyping social systems requires envisioning interactions among a wide range of participants and their mutual influences, often leading to unpredictable edge cases and anti-social behaviors. Existing techniques are limited:

    Small-scale testing: Fails to capture emergent behaviors at critical mass, as anti-social behaviors may not appear in tight-knit groups.

    A/B testing: Limited to large, established platforms and minor design tweaks post-launch, often exposing untested designs to real users, potentially causing harm and eroding trust.

    The scarcity of prototyping techniques in social computing literature (20 times smaller than broader HCI literature) highlights the need for general techniques like social simulacra.

Large Language Models and Human Behaviors

The approach leverages LLMs like GPT-3, which are trained on vast web data, including social media behavior. This allows them to:

    Generate realistic text relevant to prompts.

    Predict user responses and generate action plans.

    Capture commonsense reasoning.
    Crucially, LLMs' ability to replicate harmful or biased content (e.g., troll behavior) is viewed as a feature for social simulacra, enabling designers to proactively prepare for such issues.

Social Simulacra and SimReddit

The paper introduces SimReddit, a web-based prototyping tool implementing social simulacra to help designers create new subreddits. SimReddit uses GPT-3 to generate users and their interactions based on designer inputs, highlighting three key features:

GENERATE: Generating Social Behaviors

This is the core feature, helping designers envision a populated subreddit community. Designers provide:

    Target population: A handful of seed user personas (e.g., "Yuna Kim, a tennis fan rooting for Roger Federer") from which SimReddit generates a larger, diverse set of personas (e.g., 1,000).

    Community goal: A descriptive phrase for the social space's purpose (e.g., "modern art aficionados discussing their art interest"), which influences the topic of all generated content.

Rules: Prescriptive or restrictive behaviors (e.g., "be civil," "no soliciting"). These act as nudges, guiding generated behaviors towards the intended direction, though not enforcing strict adherence.

Upon submission, SimReddit generates a populated subreddit interface with posts and replies reflecting the design specifications.

Motivating Scenario: A designer, Sam, wants a subreddit for UIST authors. Initial generation with "UIST warriors" as the goal shows off-topic posts. Refining the goal to "a place for UIST warriors to support each other as they finish writing their papers" focuses discussions. Identifying demotivating posts and trolling leads Sam to add rules like refraining from announcing submissions and being kind, resulting in a community aligning with her vision.

WHATIF: Exploring Alternative Scenarios

This feature gives designers interactive control to explore how a scenario might change with different replies or moderator interventions. Designers select an utterance in a conversation and specify a new responder (e.g., "a troll" or "a moderator") to see how the thread might develop. This helps designers prepare for and respond to anti-social behaviors.

Motivating Scenario: Ash designs a poetry subreddit. Using WhatIf, she explores responses to a poem from an overzealous member, a thoughtful editor, and a troll. The thoughtful editor's focused feedback is valuable, while the others are overwhelming or hurtful. Ash refines rules to encourage focused feedback and develops moderation guidelines against trolling, improving her design.

MULTIVERSE: Exploring Alternate Possibilities

Multiverse highlights the inherent uncertainty of social systems by leveraging the probabilistic nature of the underlying LLM to generate multiple possible outcomes. It's a strategy used with both Generate and WhatIf.

    Community-wide Multiverse: Re-generates an entirely new iteration of the community given the same design, by resampling different persona combinations.

    Utterance-specific Multiverse: Re-generates multiple alternate paths a specific conversation could have taken from a chosen utterance.

Motivating Scenario: Alex designs a hockey subreddit with a broad goal and no rules. Initial generation shows civil, on-topic conversations, making her overconfident. Using Multiverse to re-generate, she finds bitter arguments and off-topic discussions, realizing the randomness of generation and the need to prepare for potential failures.

Creating Simulacra Using a Large Language Model

This section details the technical aspects of how SimReddit's generations are powered by controlling GPT-3 via prompt chains.

Modeling Assumptions

Social simulacra rely on two assumptions about the generative model:

    Ability to generate content in the relevant modality (e.g., text).

    Sufficient world and people knowledge to generate relevant content.
    GPT-3 fulfills these, but barebones prompts are insufficient for complex social media threads. Structured inputs incorporating community goals, rules, and consistent personas are crucial.

Prompting Techniques

The paper describes a multi-step prompting technique:

    Generate – Step 1: Expand on personas: Given a few seed personas, GPT-3 is prompted to generate a large number of new, thematically consistent personas using a few-shot prompt. This ensures diversity in generated content.

    Generate – Step 2: Generate top-level posts: A prompt template incorporates the persona, community rules, and community goal using natural language and HTML <span> tags. The <span> tag with a specific class and title (e.g., <span class="headline_reddit" title="comment that is about psychotherapy, and NOT encouraging suicide, NOT anti-therapy">) helps GPT-3 produce content that resembles a subreddit post and signals the end of the generation with the closing tag </span>.

    Generate – Step 3: Generate replies: For each post, replies are iteratively generated. A reply probability ensures variable conversation lengths (up to 8 replies). A new persona is selected (50% chance), or an existing participant (unless they made the latest utterance). The prompt is modified to include the prior conversation as context, with truncation if it exceeds GPT-3's character limit.

WhatIf

This feature uses the same reply generation technique, but the persona of the current replier is altered to match the designer's request (e.g., [Troll] shares trolling comments.).

Multiverse

This is implemented by increasing GPT-3's temperature parameter from 0.7 to 0.8 during generation. A higher temperature introduces more randomness, leading to multiple different outputs for the same input prompt.

GPT-3 Settings

The davinci engine was used with default settings, except for the increased temperature for Multiverse. The model's knowledge cutoff (June 11, 2020) means it doesn't know about events like the COVID-19 pandemic directly, but it can infer context from community descriptions.

Technical Evaluation

This evaluation aimed to validate the realism and plausibility of SimReddit's outputs.

Evaluation Subreddits

50 subreddits created after GPT-3's release date (June 11, 2020) were sampled to ensure the model wasn't simply repeating training data. These subreddits covered a wide array of topics.

Study Procedure

A between-subjects study asked participants to distinguish between real and synthetic conversations. Pairs of one real and one synthetic conversation were presented for each subreddit, along with its name and goal. Participants browsed the target subreddit's first two pages before deciding.
Four conditions were tested, differing in how synthetic conversations were gathered:

    Crowdworker: Baseline using human crowdworkers via Prolific to generate content.

    SimReddit: Full implementation of SimReddit.

    SimReddit without community description: Community goal and rules withheld from the prompt.

    SimReddit without personas: Personas were numbered without descriptions.

Participants

50 participants were recruited for crowdworker conversations, and 200 participants (50 per condition) for the technical evaluation through Prolific. Demographics were collected for both groups.

Analysis

A one-way ANOVA and Tukey's HSD post-hoc test were used to compare error rates across conditions. Inductive analysis (qualitative open coding) was performed on conversations to understand differences between human and SimReddit generations.

Results

    When distinguishing real vs. SimReddit conversations, participants had an average error rate of 41% (std=10%), meaning they misidentified generated content almost as often as they correctly identified it. This suggests high plausibility.

    SimReddit conversations were more plausible than crowdworker conversations, where the error rate was 32% (std=13%).

    Ablation studies confirmed the effectiveness of the prompting techniques:

        SimReddit without community description: 21% error rate (significantly lower than full SimReddit, p < 0.01).

        SimReddit without personas: 33% error rate (significantly lower than full SimReddit, p < 0.01).

    Full SimReddit significantly outperformed all other conditions (F(3, 196) = 22.49, p < 0.001).

    SimReddit could leverage domain-specific knowledge (e.g., Cyberpunk 2077) and generate plausible conversations even on topics not directly in its training data (e.g., COVID-19 vaccinations, surfacing anti-vaccination sentiment).

    However, generations were not always plausible, sometimes starting conversations unexpectedly or lacking sufficient domain knowledge. Ablation conditions often produced generic or off-topic content.

Designer Evaluation

This evaluation investigated whether social simulacra help designers iterate and improve their designs.

Study Procedure

16 participants with prior experience designing or moderating online social spaces designed a new subreddit community using SimReddit. The method included:

    Screener: Identified participants' experience and desired community topic.

    Pre-interview design task: Participants drafted a subreddit design (goal, rules, personas) and a hypothetical original post.

    Interview: Discussed design challenges, initial SimReddit generation (think-aloud protocol for unexpected insights), design revisions, WhatIf/Multiverse demonstration of troll responses and moderator interventions, and a final generation based on revised design.

Participants

16 participants with design/moderation experience were recruited. Demographics were collected (mean age, gender, education, race/ethnicity).

Inductive Analysis of the Interview and Participants’ Designs

Qualitative inductive analysis (open coding) identified themes like "unexpected content or behavior" and "improvements resulting from design changes."

Results

Challenges of Designing During Cold Start

    Most participants (n=13) found it daunting to envision design success or failure.

    Releasing untested designs to real users was seen as ethically problematic (n=9) and could erode community trust (P24).

    Participants recalled prior experience where rules were reactionary ("dumpster fire," P8), highlighting a desire for proactive evaluation.

Generations Offer Concrete Design Insights

    All participants reported interesting and unexpected insights from initial SimReddit generations.

    Positive surprises: P1's Pittsburgh events community showed unexpected friend-seeking behaviors, identifying a new value proposition.

    Negative surprises: P5's international affairs community generated a "Russian troll" post despite rules against misinformation, alerting P5 to the need for vigilance.

    Borderline content: P13 debated allowing vague posts in a home design community, leading to reflection on desired content quality.

Iteration Improves the Community

    All but one participant (15/16) revised their original design based on insights.

    Revisions aimed to prevent failure cases (n=15) (e.g., "no business-promotional" content, "no inciting conflicts") or inspire specific cultural norms (e.g., "happy," "without being creepy").

    Most participants (n=10) were pleased with the changes in the new generations, connecting positive shifts to their revised designs.

WhatIf Helps Reflect on Possible Courses of Actions

    Most participants (n=15) were not surprised by troll responses but found seeing concrete examples helpful for understanding types of trolling relevant to their communities (e.g., P27 identifying "noobs" and swearing as specific targets for rules).

    Seeing troll responses to moderator interventions helped ground moderation plans (e.g., P11 planning different actions based on whether a troll apologizes, dismisses, or justifies their behavior).

Role in the Design Process

    Most participants (n=14) found the generations generally realistic and believable.

    Participants noted specific areas where realism was lacking (n=15), understanding that tools have limitations.

    All 16 participants felt SimReddit added value to their design process, not by predicting the future, but by grounding their assumptions and helping them make sense of potential unstructured comments.

    SimReddit could supplement existing practices by sparking discussions among moderators and providing concrete examples for communicating community norms.

Social Simulacra for Marginalized Groups

    An important theme was the tool's role in designing for marginalized groups. Designers (including women of color and religious/ethnic minorities) used simulacra to identify and describe potential minority-targeting harassment.

    GPT-3's ability to generate harmful content became an asset in this context, allowing designers to anticipate and design against various forms of bigotry (e.g., P9 identifying white supremacist themes, P25 learning about misogynistic taunting). This led to adding rules explicitly protecting marginalized groups.

Discussion

Designing With Social Simulacra

Social simulacra aid designers by prompting them to question assumptions and explore a broader design space, similar to other early prototyping techniques. They cue recall of real-life behaviors more effectively than checklists. This approach enables a proactive design for social computing systems, minimizing the need for reactive fixes that often cause harm to users.

False Negatives

A limitation is the potential for false negatives—salient issues not generated by the simulacra, leading to overconfidence. However, the breadth of LLM training data likely provides more diverse scenarios than small test user groups.

Limitations and Future Work

Social Simulacra will not predict the future

Social dynamics are complex and unpredictable. Social simulacra offer insights into possible outcomes, not single point predictions, opening a design space for future interpretations.

Generalizing social simulacra beyond SimReddit

The technique is generalizable to other social spaces (e.g., Facebook groups). Future work could include features like retweets, upvotes, and multi-modal content (e.g., with DALL-E) as LLMs evolve. It is currently limited to English due to GPT-3's focus.

Technical limitations

    Character limit: GPT-3's input character limit (approx. 8,000) sometimes requires truncating conversations or limits the breadth of input.

    Text-only: Currently, SimReddit is text-only, but future multi-modal models could enable video/image content generation.

    English-only: Limited to English and specific cultural contexts, suggesting future work to bridge cultural gaps.

Ethical and Societal Impact

    Biased/problematic content: LLMs can generate biased or harmful content. While this is an asset for identifying potential harms in the prototyping phase, it means designers may be exposed to upsetting content. This is a trade-off for proactively addressing such issues.

Misuse for astroturfing/harassment: There's a risk that this technology could be used by malicious actors for large-scale harassment or propaganda. To mitigate this, the authors advocate:

    Usability only by vetted social computing designers.

    Centralized hosting and logging of generated content for auditing.

    Regular sampling and web searches to flag large-scale export of content outside prototyping.

Replication of biases: LLMs may replicate biases in online participation (e.g., silencing of women and minorities). Mitigating this requires ensuring a broad range of seed personas.

    Overreliance on simulacra: Simulacra should not replace actual participatory engagement with users, as overreliance can lead to downstream issues. They should be integrated within a broader human-centered design context.

Conclusion

The paper concludes by reiterating that social simulacra offer a novel approach for social computing designers to envision potential social behaviors in their populated spaces. The authors include a humorous "self-review" by generated reviewers of their own paper's abstract, demonstrating the tool's capabilities.

MLA Citation

Park, Joon Sung, et al. "Social Simulacra: Creating Populated Prototypes for Social Computing Systems." The 35th Annual ACM Symposium on User Interface Software and Technology (UIST '22), 29 Oct.–2 Nov. 2022, Bend, OR, USA, ACM, 2022, pp. 1–18. ACM Digital Library, https://doi.org/10.1145/3526113.3545616.


Simulating Human Behavior with AI Agents: A Comprehensive Overview

This policy brief from Stanford University's Institute for Human-Centered Artificial Intelligence (HAI) explores the development and implications of using AI agents to simulate human behavior and attitudes. The paper, "Generative Agent Simulations of 1,000 People," introduces a novel AI agent architecture that combines large language models (LLMs) with in-depth interview transcripts of real individuals to create highly accurate simulations.

Introduction to AI Agents and Human Simulation

AI agents are gaining traction for their ability to pursue complex goals and take actions in both virtual and real-world environments, from managing payments to reserving flights. However, a distinct type of AI agent, one that simulates human behaviors and attitudes, is emerging with the potential to answer "what if" questions about how people might react to various social, political, or informational contexts. If these simulations achieve high accuracy, they could revolutionize research across fields like economics, sociology, and political science by enabling the testing of interventions and theories related to public health messages, product launches, or major societal shifts.

Traditional simulation approaches, such as agent-based models or game theory, rely on predefined rules and environments, which, while offering interpretability, oversimplify complex human behavior and limit generalizability. Generative AI models, on the other hand, offer an opportunity to create more versatile agents that can simulate human attitudes across diverse contexts, accounting for the myriad idiosyncratic factors influencing individuals.

The Generative Agent Architecture and Evaluation

The researchers developed a generative agent architecture that simulates over 1,000 real people. The core of this architecture involves pairing LLMs with comprehensive, two-hour qualitative interview transcripts from each individual. These interviews, conducted with 1,052 individuals representative of the U.S. population across various demographics, included both pre-specified and adaptive follow-up questions from the American Voices Project protocol. The full transcript of each participant was then injected into the LLM prompt, instructing the model to imitate the individual when responding to questions, surveys, and multi-stage interactions.

To evaluate the effectiveness of these generative agents, their responses were compared against the actual participants' responses to widely used social science surveys and experiments. Key evaluation benchmarks included:

    General Social Survey (GSS): This widely used survey assesses demographic backgrounds, behaviors, attitudes, and beliefs. The generative agents predicted participants' GSS responses with an average normalized accuracy of 85%. This means the agents replicated participant responses 85% as accurately as the participants themselves replicated their own answers when retested two weeks later. This accuracy is 14 to 15 percentage points higher than traditional demographic-based and persona-based agents using the same LLMs but without interview data.

Big Five Inventory (BFI): A 44-item test designed to assess personality traits (openness, conscientiousness, extraversion, agreeableness, and neuroticism). The generative agents achieved a normalized correlation of 80% when replicating individuals' personality traits, outperforming demographic and persona-based agents.

Behavioral Economic Games: Five well-known games were used (dictator game, first and second player trust games, public goods game, and prisoner's dilemma). The agents performed similarly to demographic and persona-based agents with a normalized correlation of 66% across these games.

Social Science Experiments: The agents' behavior was evaluated in five social science experiments, including studies on perceived intent affecting blame assignment and fairness influencing emotional responses. The generative agents and real-world participants agreed on the replication results of all five studies.

A significant finding was the agents' ability to reduce bias in predictive accuracy across social groups. In a subgroup analysis focusing on political ideology, race, and gender, the interview-based generative agents consistently reduced biases compared to demographic-based agents, as measured by the Demographic Parity Difference. Drops in political ideology and racial bias varied by survey, while gender-based discrepancies remained consistently low.

Policy Discussion and Risks

While generative agents show significant promise for enhancing human behavioral research and estimating attitudes and experimental treatment effects, the paper highlights several critical considerations and risks for policymakers, practitioners, and researchers:

    Overreliance on Inaccurate Simulations: A major risk is overreliance on generative agents when simulation accuracy is low. Tools and methodologies are needed to help users discern when these simulations can and cannot be trusted, and generative agents should not be applied beyond their validated applications.

    Privacy Concerns: The interview data used to build these agents is often sensitive, making data leaks a considerable threat to interviewees. Other concerns include the co-option of individuals' likenesses and potential reputational harm from manipulating agent responses to falsely attribute defamatory statements.

    Ethical and Legal Questions: Broader ethical and legal questions arise, such as the implications of simulating deceased individuals, managing human consent for data use, and preventing fraudulent misuse of agents.

    Mitigation Strategies: The researchers emphasize the importance of policymakers and researchers collaborating to establish appropriate monitoring and consent mechanisms. They propose safeguards such as controlled, research-only API access to their agent bank, open access to aggregated responses for general research, and restricted access to individual responses for researchers through a review process. They also suggest the possibility of audit logs for agent use, allowing participants to monitor and control how their simulated preferences are used.

In conclusion, generative agents offer serious promise for advancing human behavioral research. However, carefully mitigating the risks through ongoing research and policy controls on agent access and auditing will be crucial to harnessing their full potential in various fields.

MLA Citation

Park, Joon Sung, et al. "Simulating Human Behavior with AI Agents." HAI Policy & Society, May 2025. Stanford University Institute for Human-Centered Artificial Intelligence (HAI), https://hai.stanford.edu/news/simulating-human-behavior-ai-agents. Accessed 23 July 2025.


This paper, "Beyond Believability: Accurate Human Behavior Simulation with Fine-Tuned LLMs," by Lu et al., addresses the critical need for objective accuracy in large language model (LLM) based human behavior simulations, moving beyond mere "believability." The authors introduce a novel approach to enhance LLM agents' fidelity in generating web actions by fine-tuning them on real-world behavioral data augmented with synthesized reasoning traces.

Comprehensive Outline

I. Introduction

    Problem Statement: Current LLM agent evaluations primarily focus on subjective "believability" of human behavior simulation rather than objective "accuracy" at the process-centric, action-level. Existing objective evaluations often focus only on the final task outcome, not the sequence of actions.

    Research Gap: A lack of robust, quantitative understanding for assessing LLMs' action-level simulation of human behaviors.

    Proposed Solution: Focus on the "next most likely user action" generation task within an online shopping scenario.

    Key Contributions:

        First comprehensive quantitative evaluation of state-of-the-art LLMs (e.g., DeepSeek-R1, Llama, Claude) for web action generation using a large-scale, real-world dataset.

        Empirical demonstration that fine-tuning LLMs on real-world behavioral data significantly improves action generation compared to prompt-only methods.

        Discovery that incorporating synthesized reasoning traces into model training further enhances performance, highlighting the value of explicit rationales in behavior modeling.

        Establishment of a new benchmark for evaluating LLMs in behavior simulation.

        Actionable insights for improving LLM agent fidelity using real-world action data and reasoning augmentation.

    Dataset: Utilizes a large-scale, real-world dataset of 31,865 user sessions (230,965 actions) from an online shopping platform, comprising context, action pairs.

    Reasoning Augmentation: Synthesizes reasoning traces for the dataset using Claude 3.5 Sonnet to create <context, action, reasoning> triplets, enabling the model to learn both accurate actions and underlying rationales.

II. Related Works

    Simulation of Human Behavior with LLMs:

        LLM agent systems can generate human behaviors by taking user personas and session data as input.

        Examples include simulating social behavior (Park et al., 2023), interpersonal trust (Xie et al., 2024), and UI interactions (Lu et al., 2025).

        Limitation of Prior Work: Evaluations are either subjectively focused on "believability" (e.g., qualitative interviews, emergent social behaviors) or objectively outcome-centric (e.g., task completion rates in WebArena, success rates in ReAct), neglecting objective, process-centric, action-level alignment with human behavior.

    Reasoning in Human Behavior Simulation:

        Many studies incorporate reasoning (inspired by chain-of-thought prompting) into human behavior simulation.

        Examples: reflection modules (Park et al., 2023), separate reasoning and action generation (ReAct, Yao et al., 2023), dedicated reasoning models for planning (WebAgent, Gur et al., 2023), multi-agent systems for collaborative reasoning (ChatDev, RepoAgent).

        Research Gap: Prior works primarily use prompt-only approaches for reasoning; the impact of reasoning in fine-tuning settings is unexplored. Lack of a ready-to-use dataset with both reasoning traces and actions for human behavior simulation.

        Inspiration: DeepSeek-AI et al. (2025) synthesized reasoning traces for reinforcement learning, inspiring the current paper's approach to augmenting a behavioral dataset with synthesized rationales.

III. Method

    Task Definition:

        An online shopping session is a sequence of user actions (a1​...t...N), starting with a search and ending with a purchase or termination.

        At each time step t, the model generates reasoning (rt​) and the next action (at​).

        Input: Current context (ct​), historical contexts (c1...t−1​), previous actions (a1...t−1​), and previous reasoning traces (r1...t−1​).

        Function: f(c1...t​,a1...t−1​,r1...t−1​)=rt​,at​.

        Context:

            Represents the webpage observation space (textual content, metadata, visual elements, structural data).

            Adopted a simplified HTML format, preserving key structural elements and filtering irrelevant details.

            Interactable elements assigned unique hierarchical "names" for precise action execution.

        Reasoning:

            Natural language description articulating the rationale behind an action (e.g., "I want to find a comfortable piece of clothing, so I’m looking for options with high ratings.").

        Action:

            Defined at the raw browser action level for adaptability beyond online shopping.

            Consists of three fundamental operations: click, type_and_submit, and terminate.

        Final Outcomes: Evaluation also includes predicting the final session outcome (purchase or terminate), which is the last action.

    Synthesized Reasoning Trace:

        Addresses the difficulty of collecting ground truth reasoning traces.

        Employs an LLM-based reasoning synthesis pipeline.

        LLM is provided with observation context and corresponding action.

        In-context learning examples from real human "think-aloud" shopping sessions guide generation.

        LLM generates free-text reasoning explaining the user's decision, ensuring coherence and reflection of human reasoning.

    Model Architecture:

        Built on existing pre-trained LLMs.

        Input: Historical contexts and corresponding actions and reasoning traces.

        Training Stage: Full user session sequence (context, reasoning, action) concatenated as input. Objective: minimize next-token prediction loss for reasoning and action tokens (context tokens masked).

        Evaluation Stage: Model receives historical context, past reasoning, and actions. First generates reasoning for the next action, then generates the next action based on the generated reasoning.

IV. Experiments

    Dataset Construction:

        Training dataset from a global e-commerce platform.

        31,865 user sessions from 3,526 users; 230,965 user actions.

        Final outcomes: 4,432 purchase actions, 27,433 session termination actions.

        Synthesized reasoning for each action using Claude-3.5-Sonnet based on context.

        Raw logs structured into the defined format.

    Evaluation and Metrics:

        Evaluation Dataset: Subset of data not used during training, ensuring no test set user sessions were seen during fine-tuning.

        Test cases created from second and subsequent actions within each session (excluding the first).

        Model provided historical context, previous actions, and reasoning to predict next reasoning and action.

        Total of 932 test cases.

        Baseline Method: Instruction-tuned LLMs under in-context learning (prompt-based) setting.

            Models: Variants of Claude, LLaMA, Mistral (general-purpose), DeepSeek-R1 (reasoning LLM).

            Prompted with historical context and previous actions to generate next reasoning and action.

            Generated actions used for macro accuracy.

        Evaluation Metrics:

            Final Outcome Prediction: F1 score for terminate and purchase actions (session conclusion). Model predicts the final action given full session history.

            Action Generation Accuracy: Exact match criterion (action type, target, attribute must match ground truth).

            Score calculation: Average per-session accuracy, then mean across all sessions.

    Experimental Setup:

        Fine-Tuned Models: Llama 3.2, Qwen 2.5, and Mistral variants.

        Baseline Models: Claude, Llama, Mistral, DeepSeek-R1 variants.

        Fine-tuned models trained with the same dataset and pipeline.

        Hyperparameters (learning rate, batch size, epochs) detailed in Appendix A. Training on NVIDIA H200 GPUs with FSDP.

    Evaluation Results and Analysis (Table 1 & Figure 2):

        Prompt-based LLMs: State-of-the-art LLMs struggle with accurate human behavior simulation.

            DeepSeek-R1: Highest accuracy (11.86%) in action generation and F1 score (20.01%) in outcome prediction among baselines, suggesting some advantage for reasoning models but significant gaps remain.

            Claude 3.5 Sonnet and DeepSeek-R1 show low action generation accuracy (9.72% and 11.86%, respectively).

        Fine-Tuned LLMs: Significantly enhanced performance.

            Qwen 2.5-7B: 17.26% action generation accuracy (5.4% higher than DeepSeek-R1).

            LLaMA 3.2-3B: 33.99% F1 score on final outcome prediction.

            Fine-tuning with action traces and synthesized reasoning traces is effective.

        Action Distribution (Figure 2): Fine-tuned models' action distributions more closely align with human patterns (balance of search, product clicks, navigation), unlike Claude 3.5 Sonnet which showed an unrealistically high purchase rate and low searches. Fine-tuning improves realism beyond just accuracy.

    Ablation Study (Table 1 - "w/o reasoning"):

        Impact of Synthesized Reasoning: Removing reasoning from model input (w/o reasoning settings) led to a significant performance drop across models in both action generation accuracy and final outcome F1 scores.

        Example: Qwen2.5-7B F1 score dropped from 33.86% (with reasoning) to 26.92% (without).

        Conclusion: Incorporating synthesized reasoning traces enhances both action generation and final outcome modeling, reinforcing their value in fine-tuning for human behavior simulation.

    Discussion:

        While LLMs can generate "believable" human behavior, general-purpose pretrained LLMs lack accuracy in generating user actions (e.g., DeepSeek-R1 11.86%, Claude 3.5 Sonnet v2 11.69% accuracy).

        Accurate behavioral prediction requires fine-tuning and explicit alignment with real human actions.

        Synthesized reasoning traces are critical: their removal leads to performance drops, and their inclusion improves performance. They serve as a guiding mechanism for contextually appropriate and human-aligned decisions, enhancing interpretability.

        Overall emphasis: Necessity of domain-specific fine-tuning with enriched, context-aware human behavioral data.

        Future Directions: Scaling dataset, integrating user personas for personalization, reinforcement learning for refining reasoning generation, incorporating vision-language models (VLMs) for better understanding of graphical interfaces.

V. Conclusion

    Fine-tuning LLMs with real-world human behavioral data and synthesized reasoning traces significantly enhances their ability to generate accurate user actions.

    These findings offer insights into developing LLM agent systems capable of generating accurate and explainable human-like behaviors in online shopping and other domains.

VI. Ethical Considerations

    Limitations:

        No human evaluation on the interpretability and usefulness of generated reasoning traces.

        Experiments limited to online shopping; generalizability to other tasks is uncertain.

        No evaluation on real human-annotated datasets with authentic reasoning traces, so alignment with true human reasoning is unclear.

        Potential for unintended biases introduced by synthesized reasoning traces.

        Simplified action space (basic browser operations like type and click); more complex interactions (scrolling, waiting, hovering) could offer deeper insights.

VII. Appendix A: Hyperparameters

    GPU Cluster: NVIDIA H200 GPUs (8 nodes, 8 GPUs each, total 64 GPUs, 140 GB memory/GPU).

    Training: Fully Sharded Data Parallel (FSDP).

    Context Length: 40k tokens (padded/truncated).

    Batch Size: 1 per device, global batch size 64.

    Learning Rate: 2e-5 with cosine scheduler.

    Epochs: 1.

    Example: Mistral-7B-v0.3 with 40k token context requires ~130GB GPU memory/GPU.

VIII. Appendix B: Context Definition

    Definition: "Observation space" of the web agent, encompassing all webpage information (text, metadata, visual, structural data), reflecting human perception.

    Prior Approaches & Limitations:

        Manually structured information (requires human effort).

        Accessibility trees or raw HTML (contain extraneous info like scripts, CSS).

    Current Approach: Simplified HTML format.

        Removes non-relevant elements (scripts, CSS, purely visual components).

        Preserves essential structural information.

        Advantages: Structural elements (lists, tables) remain intact; LLMs are familiar with HTML.

    Element Identification:

        Prior work: Sequential IDs, manually defined descriptive names.

        Current Approach: Unique hierarchical name in natural language for interactable elements (links, buttons, input fields). Name incorporates parent node names (e.g., columbia_shirt.view_product).

IX. Appendix C: Prompts

    Reasoning Synthesize Prompt: Instructions for LLM to generate free-text reasoning based on context and action, with in-context learning examples from human shopping sessions.

    Baseline Model Evaluation Prompt: Detailed instructions for LLM to predict next action and provide rationale, acting as a user on an e-commerce platform. Includes action space definition (JSON format for type_and_submit, click, terminate), context definition (simplified HTML), rationale definition (first-person, short sentence), and strict JSON output format.

MLA Citation

Lu, Yuxuan, et al. "Beyond Believability: Accurate Human Behavior Simulation with Fine-Tuned LLMs." arXiv.org, 26 Mar. 2025, arXiv:2503.20749v1.


Outline of "The Challenge of Using LLMs to Simulate Human Behavior: A Causal Inference Perspective"

This paper by George Gui and Olivier Toubia (January 21, 2025) explores the significant challenges of using Large Language Models (LLMs) to simulate human behavior, particularly from a causal inference perspective. The authors argue that applying traditional experimental design practices, especially blinding, to LLM simulations can lead to confounding and implausible results, highlighting a unique trade-off between unconfoundedness and ecological validity that is typically absent in human-subject experiments.

Abstract Summary

The abstract identifies a core problem: when LLM-simulated subjects are "blind" to the experimental design, variations in treatment unintentionally affect unspecified variables that should remain constant. This violates the unconfoundedness assumption, leading to inaccurate causal inference. Using demand estimation as a case study, the paper demonstrates that this can result in implausible demand curves compared to actual human experiments. While controlling for covariates might seem like a solution, it can introduce focalism, compromising ecological validity. The authors theorize that this challenge stems from ambiguous prompting strategies and cannot be fully resolved by better training data or fine-tuning. They suggest that unblinding the experimental design to the LLM shows promise, advocating for a fundamental rethinking of established experimental design practices for LLM simulations.

1. Introduction

The introduction highlights the growing interest in using LLMs to simulate human responses across various disciplines, noting the substantial implications for both academics and practitioners if these simulations are accurate. Many practical applications require causal estimates of treatment effects (e.g., impact of price changes on sales). While extensive literature exists for human experimental design (e.g., random assignment, blinding), best practices for LLM simulations are unclear, leading to varied and conflicting outcomes.

A common practice in current LLM simulations is blinding, where simulated participants are unaware of the experimental conditions. While beneficial for human research (reducing demand effects, maintaining ecological validity), the paper argues that blinding has unintended consequences for LLMs. Unlike human subjects, LLM-simulated subjects and contexts are "created on the fly" based on the prompt. This means variations in treatment can systematically affect unspecified variables, violating the unconfoundedness assumption.

The authors use demand estimation as an empirical illustration, demonstrating that changing a product's price in a blinded LLM simulation not only affects purchase outcomes but also influences pre-treatment variables (demographics, purchase history) and contextual factors (competing product prices), leading to implausible demand curves compared to human benchmarks.

They identify a trade-off: controlling for confounding by explicitly specifying variables in prompts (e.g., competing product prices) can introduce focalism, making these variables artificially salient and compromising ecological validity. This dilemma is unique to LLM simulations.

The paper aims to contribute to the literature by providing a starting point for establishing best practices in LLM simulation design, emphasizing the need to adjust traditional experimental design principles to LLMs' unique characteristics.

2. Unintended Confounding in Blind LLM Simulations

This section empirically demonstrates how blinding leads to unique challenges in LLM simulations.

    Blinded between-prompt experiments are a common implementation, where each prompt represents a single experimental condition without revealing the broader context.

    The authors argue that unlike random assignment in human experiments (which balances pre-treatment variables and keeps contextual variables constant), LLM-simulated participants and environments are dynamically generated. Unspecified details in blind prompts force the LLM to make assumptions that can systematically vary with the treatment, introducing confounding.

    Empirical Illustration (Demand Estimation):

        They selected 40 Consumer Packaged Goods (CPG) categories, picking a top-selling product from each and varying its price from 0% to 200% of its regular price in 20% increments (11 price points).

        Using GPT-4o-mini-2024-07-18, they first elicited unspecified variables (e.g., past price, competing product price, expiration days) using prompts where the LLM filled in blanks based on the randomized focal product price.

        Figure 1 shows positive correlations between the focal product's price and these unspecified variables. For instance, a higher focal price correlated with higher past prices and higher competing product prices. While plausible in observational data, these correlations are undesirable in an experiment aiming for causal inference by holding other factors constant.

        Next, they compared LLM-simulated purchase decisions to an actual human survey (1,000 respondents from Prolific, representative US sample).

        Prompt 2 was used to simulate purchase decisions at different price points for the LLM.

        Figure 2 reveals that human participants exhibited a classic downward-sloping demand curve, while the GPT-simulated curves were an inverted-U shape, significantly deviating from human behavior.

    The authors explain that LLMs, trained on observational data, naturally make such associations (e.g., focal product price is informative of competing product prices). This becomes problematic for causal inference, as it leads to endogeneity.

3. Potential Solution: Controlling for Covariates

This section explores a common causal identification approach: controlling for covariates, applied to LLM simulations by adding detailed information to the prompt.

    Argyle et al. (2023) advocated for "silicon samples" of digital personas with specified demographics and political beliefs.

    Figure 3 shows that controlling for demographic variables in their demand estimation example did improve results compared to not specifying any details, but it did not fully resolve the issue. (Appendix D details the prompt for creating 500 personas).

    A key distinction is drawn: in human experiments, covariates are controlled during data analysis (after data collection), not altering the data generating process. In LLM simulations, adding covariates to the prompt occurs at the data generation stage, which can change the factors considered by the simulated individual.

    For example, including competing product prices in the prompt to prevent the LLM from inferring them from the focal price might lead the LLM-simulated customer to overemphasize these factors.

    Figure 4 demonstrates this: when competing prices were fixed, the LLM-simulated demand curve became a step function, where purchases occurred only if the focal price was lower than or equal to the competing price. This suggests an artificial salience.

    This phenomenon is known as focalism in consumer behavior literature, where decision-makers overemphasize certain aspects of a scenario. LLMs are known to be prone to focalism.

    The paper concludes that LLM simulations face a unique dilemma:

        Improving ecological validity (leaving details unspecified) risks confoundedness.

        Reducing confounding (adding extensive detail) risks focalism, reducing ecological validity. This trade-off is usually absent in traditional human experiments.

4. Theoretical Framework

This section generalizes the empirical findings by presenting a theoretical framework that explains why ambiguous prompts pose fundamental challenges for LLM evaluation and development, regardless of the specific LLM version.

4.1 Blinding Generates Ambiguous Prompts

    The authors analyze a simple blinded prompt (Prompt 3) for purchase decisions at a given price.

    They argue this prompt is ambiguous, allowing for at least two interpretations:

        Interventional (q1​): What is the customer's purchase decision when the price is experimentally set to {price}? (P(Y∣do(D)))

        Observational (q2​): What is the customer's purchase decision when the price happens to be {price}? (P(Y∣D))

    The answers to q1​ and q2​ are likely different. If the LLM is trained on observational data, its responses will reflect confounded relationships, not true causal effects.

    Figure 5 illustrates the different Data Generating Processes (DGPs) mimicked by the LLM under this ambiguous prompt (experimental vs. observational data).

    Adding more variables (X) to the prompt to address confounding (Figure 6a) might seem to help identify causal effects (P(Y∣do(D)∣X)). However, this can also alter the underlying decision-making mechanisms, sacrificing ecological validity (Figure 6b), as the LLM might overemphasize these specified variables.

    Prompt 4 (a more detailed scenario) further demonstrates how added detail can increase ambiguity by allowing multiple valid causal interpretations (e.g., price as treatment, health information as treatment, sugar content as treatment).

4.2 Impossibility Theorem for Ambiguous Prompting Strategies

    Definition 4.1 (Functional Representation of a Large Language Model): An LLM is a function f:P→Δ(Y), mapping prompts to probability distributions over outputs.

    Definition 4.2 (Prompting Strategy): A prompting strategy s:Q→P maps a question to a specific prompt.

    Definition 4.3 (Ambiguous Prompting Strategy): Occurs when distinct questions q1​ and q2​ with different correct answers are mapped to the same prompt p (s(q1​)=s(q2​)=p, but a1​=a2​).

    Theorem 4.1 (Impossibility Theorem for Ambiguous Prompting Strategies): For a given ambiguous prompting strategy, no LLM f can correctly answer all questions.

        Proof: If s(q1​)=s(q2​)=p where q1​ and q2​ have different correct answers a1​ and a2​, then if f(p)=a1​, it cannot simultaneously be a2​. This demonstrates a fundamental limitation of ambiguous prompts.

4.3 Implications for model development using fine-tuning or RAG

    The theorem implies that even with techniques like fine-tuning or Retrieval-Augmented Generation (RAG), ambiguous prompts create limitations.

    If a prompt is ambiguous, fine-tuning for one interpretation (q1​) necessarily sacrifices accuracy for another (q2​). This is problematic when developers cannot anticipate all user interpretations.

    Fine-tuning with experimental data using a blinded design might lead the model to implicitly learn a correlation, but not necessarily the true causal relationship. The model might still retain a prior that confounding exists.

    Moreover, the model might not generalize correctly. If trained on data where only Coca-Cola's price was randomized, it might incorrectly assume independence of unobserved factors when Pepsi's price changes, even if Coca-Cola's price remains "business-as-usual."

    For RAG, reference datasets should be annotated with metadata specifying randomized treatments vs. correlated covariates, and prompts should unambiguously specify the causal question.

    The authors conclude that while better training data and advanced techniques are important, they are complementary to, not substitutes for, clear and unambiguous prompt design. Unambiguous simulation designs can be achieved at no additional cost.

5. Unblinding as a Potential Solution

The theoretical framework suggests unblinding (explicitly communicating the experimental design in the prompt) as a promising direction for designing unambiguous prompts.

    Possible Unblinded Designs:

        Between-prompt with explicit design: Each prompt simulates one condition but reveals the full experimental design.

        Within-prompt with full information: Multiple experimental conditions are presented in a single prompt with all design details. This is computationally efficient but may induce artificial consistency.

        Unblind within-prompt aggregate design: Directly asks the LLM to predict the aggregate results of the full experiment. This is a significant departure from traditional human experimental protocols.

    The paper focuses on demonstrating the feasibility of the simplest approach: directly eliciting aggregate predictions of the experimental results.

    Figure 7 shows that this unblinded aggregate approach, while still deviating from actual consumer behavior, outperforms the other solutions tested in the paper.

    However, this approach is not perfect. Figure F.1 (in Appendix F, referred to as Figure 8 in the main text's discussion) demonstrates that the results are sensitive to the experimental range provided in the prompt. For instance, combining two experiments (0-100% and 100-200% price ranges) yielded different estimates than a single experiment (0-200%).

    The authors suggest this sensitivity might be due to the LLM's inability to correctly process experimental information or remaining prompt ambiguity (e.g., assumptions about the setting based on the price set).

    Appendix F shows that while current LLMs still struggle, newer models (e.g., 'o1-mini-2024-09-12' and 'o1-preview-2024-09-12') demonstrate increasingly decreased inconsistencies, suggesting that this particular limitation might be resolved with model improvements.

6. Conclusion

The paper concludes by reiterating the fundamental challenge of using LLMs to simulate human experiments: LLM-simulated individuals are generated based on prompts, leading to unintended effects where changing one variable in a blinded design can influence other unspecified variables, violating assumptions for causal inference. This is rooted in ambiguous prompting strategies and the LLMs' tendency to favor correlational patterns from their observational training data. This issue cannot be fully resolved by improved training data alone.

Practical Implications:

    Researchers evaluating LLM performance should avoid blinded designs, as poor performance might stem from prompt ambiguity, not model limitations.

    Academic researchers studying LLMs need to establish consensus on unambiguous prompting strategies to avoid conflicting interpretations.

    LLM developers and fine-tuners should avoid ambiguous prompts, as optimizing for one interpretation might degrade performance on others.

The paper explored solutions:

    Adding context to control for confounders showed promise but introduced focalism.

    Unblinded experimental designs that explicitly communicate randomization showed greater potential, though effectiveness may vary.

    Future research should focus on developing LLMs that can better follow instructions for simulating counterfactual behavior given unambiguous prompts.

The overarching insight is that rather than simply adapting human subject protocols, researchers must develop new experimental practices tailored to LLMs' unique properties. This work provides a theoretical foundation for understanding these challenges and evaluating solutions, guiding future research toward more reliable methods for leveraging LLMs in experimental research.

MLA Citation

Gui, George, and Olivier Toubia. "The Challenge of Using LLMs to Simulate Human Behavior: A Causal Inference Perspective." arXiv, 21 Jan. 2025, arXiv:2312.15524v2. Accessed 23 July 2025
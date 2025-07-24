# ADR-020: Agent-Based Modeling Integration

**Status**: Accepted  
**Date**: 2025-01-23  
**Context**: KGAS currently focuses on descriptive analysis of social phenomena but lacks capability to validate theories through simulation or explore counterfactual scenarios

## Context

KGAS is designed as a theory-aware computational social science platform with strong capabilities in:
- Cross-modal analysis (graph/table/vector)
- Theory operationalization through schemas
- Uncertainty quantification and provenance tracking
- Academic research workflows

However, the current architecture is purely **analytical/descriptive** - it can analyze existing social phenomena but cannot:
- **Validate theories** through controlled simulation
- **Test counterfactuals** ("what if" scenarios)
- **Generate synthetic data** for theory testing
- **Explore emergent behaviors** from theoretical assumptions

Recent advances in **Generative Agent-Based Modeling (GABM)** using Large Language Models (Concordia framework, Google DeepMind) enable sophisticated theory-driven agent simulations that could complement KGAS's analytical capabilities.

## Decision

**Integrate Agent-Based Modeling capabilities into KGAS as a new architectural layer for theory validation and synthetic experiment generation.**

## KGAS Theory Meta-Schema v10 to ABM Translation

The theory meta-schema v10 provides a comprehensive framework for translating KGAS theories into agent-based models. This section demonstrates how schema components map to agent configurations.

### Translation Framework Overview

```python
class TheoryToABMTranslator:
    """Translates KGAS theory meta-schema v10 to ABM agent configurations"""
    
    def __init__(self, theory_schema: Dict):
        self.schema = theory_schema
        self.agent_factory = KGASTheoryDrivenAgent
        self.environment_builder = TheoryEnvironmentBuilder()
    
    def translate_theory_to_agents(self) -> List[AgentConfiguration]:
        """Main translation method"""
        # Extract entities from ontology
        entities = self.schema['ontology']['entities']
        
        # Create agent configurations for each entity type
        agent_configs = []
        for entity in entities:
            config = self._create_agent_config_from_entity(entity)
            agent_configs.append(config)
        
        return agent_configs
    
    def _create_agent_config_from_entity(self, entity: Dict) -> AgentConfiguration:
        """Convert theory entity to agent configuration"""
        agent_config = AgentConfiguration(
            agent_type=entity['name'],
            behavioral_rules=self._extract_behavioral_rules(entity),
            decision_framework=self._extract_decision_framework(entity),
            measurement_approach=self._extract_measurement_approach(entity),
            interaction_patterns=self._extract_interaction_patterns(entity)
        )
        return agent_config
```

### Example 1: Stakeholder Theory Translation

Using the stakeholder theory v10 schema as an example:

```python
# From stakeholder_theory_v10.json
stakeholder_entity = {
    "name": "Stakeholder",
    "properties": [
        {"name": "legitimacy", "type": "float", "operationalization": {...}},
        {"name": "urgency", "type": "float", "operationalization": {...}},
        {"name": "power", "type": "float", "operationalization": {...}}
    ]
}

# Translates to:
class StakeholderAgent(KGASTheoryDrivenAgent):
    def __init__(self, agent_id: str, legitimacy: float, urgency: float, power: float):
        super().__init__(agent_id, "Stakeholder")
        
        # Agent state from theory properties
        self.legitimacy = legitimacy  # 0-1 scale from operationalization
        self.urgency = urgency       # 0-1 scale from operationalization  
        self.power = power           # 0-1 scale from operationalization
        
        # Calculated salience using Mitchell-Agle-Wood model
        self.salience = self._calculate_salience()
        
        # Behavioral rules from execution steps
        self.behavioral_rules = [
            self._assess_organizational_impact,
            self._determine_influence_strategy,
            self._adapt_engagement_approach
        ]
    
    def _calculate_salience(self) -> float:
        """Implement custom_script from schema"""
        # From schema: "salience = (legitimacy * urgency * power) ^ (1/3)"
        return (self.legitimacy * self.urgency * self.power) ** (1/3)
    
    def _assess_organizational_impact(self, context: SimulationContext) -> Dict:
        """Behavioral rule derived from HAS_STAKE_IN relationship"""
        organization = context.get_organization()
        
        # Calculate stake strength from relationship properties
        stake_strength = self._evaluate_stake_strength(organization)
        
        return {
            'action': 'assess_impact',
            'stake_strength': stake_strength,
            'concerns': self._identify_concerns(organization)
        }
    
    def _determine_influence_strategy(self, context: SimulationContext) -> Dict:
        """Strategy based on power operationalization"""
        if self.power > 0.8:
            strategy = "direct_pressure"
        elif self.power > 0.5:
            strategy = "coalition_building" 
        else:
            strategy = "public_appeal"
        
        return {'influence_strategy': strategy, 'power_level': self.power}
    
    def step(self, context: SimulationContext) -> List[Dict]:
        """Execute theory-driven behavior"""
        actions = []
        
        # Apply behavioral rules in sequence
        for rule in self.behavioral_rules:
            action = rule(context)
            actions.append(action)
            
        # Update salience based on context changes
        self._update_salience(context)
        
        return actions
```

### Example 2: Framing Theory Translation

Using the Carter framing theory schema:

```python
# From carter_framing_theory_schema.yml
framing_analysis = {
    "frames_in_communication": [
        {"frame": "Peace Frame", "considerations": ["mutual benefit", "shared humanity"]},
        {"frame": "Security Frame", "considerations": ["strategic balance", "deterrence"]},
        {"frame": "Values Frame", "considerations": ["human rights", "moral leadership"]}
    ],
    "psychological_mechanisms": {
        "accessibility": "Vietnam/Watergate memories activate credibility concerns",
        "applicability": "Universal human values connect with audience beliefs"
    }
}

# Translates to:
class FramingAgent(KGASTheoryDrivenAgent):
    def __init__(self, agent_id: str, frame_preference: str, political_knowledge: float):
        super().__init__(agent_id, "FramingAgent")
        
        # Agent cognitive state from theory
        self.frame_preference = frame_preference  # "peace", "security", "values", "realism"
        self.political_knowledge = political_knowledge  # Individual moderator
        self.active_considerations = []
        
        # Frame processing mechanisms from explanatory_analysis
        self.accessibility_memory = self._initialize_memory()
        self.applicability_filter = self._initialize_value_filter()
        
        # Behavioral rules from competitive_dynamics
        self.behavioral_rules = [
            self._process_frame_exposure,
            self._evaluate_frame_strength,
            self._update_attitude_formation,
            self._generate_response
        ]
    
    def _process_frame_exposure(self, context: SimulationContext) -> Dict:
        """Implement accessibility mechanism from theory"""
        exposed_frames = context.get_current_frames()
        
        for frame in exposed_frames:
            # Theory: "Frame Exposure → Consideration Activation → Attitude Formation"
            considerations = self._activate_considerations(frame)
            self.active_considerations.extend(considerations)
            
        return {
            'action': 'frame_processing',
            'activated_considerations': self.active_considerations
        }
    
    def _evaluate_frame_strength(self, context: SimulationContext) -> Dict:
        """Implement competitive_dynamics from causal_analysis"""
        competing_frames = context.get_competing_frames()
        
        # Theory: "Stronger frames dominate weaker ones"
        frame_strengths = {}
        for frame in competing_frames:
            strength = self._calculate_frame_appeal(frame)
            frame_strengths[frame.id] = strength
            
        dominant_frame = max(frame_strengths, key=frame_strengths.get)
        
        return {
            'action': 'frame_evaluation',
            'dominant_frame': dominant_frame,
            'frame_competition_result': frame_strengths
        }
    
    def _update_attitude_formation(self, context: SimulationContext) -> Dict:
        """Implement expectancy_value_model from explanatory_analysis"""
        # Theory: "Attitude = Σ(value_i × weight_i)"
        key_values = ["peace", "security", "credibility", "moral_leadership"]
        
        attitude_score = 0
        for value in key_values:
            value_weight = self._get_value_weight(value)
            value_importance = self._get_value_importance(value, context)
            attitude_score += value_weight * value_importance
            
        self.current_attitude = attitude_score
        
        return {
            'action': 'attitude_update',
            'attitude_score': attitude_score,
            'value_weights': {v: self._get_value_weight(v) for v in key_values}
        }
```

### Cross-Modal Agent Representation

Agents can represent themselves across different analytical modes as specified in the schema's cross_modal_mappings:

```python
class MultiModalAgent(KGASTheoryDrivenAgent):
    def get_graph_representation(self) -> Dict:
        """Agent as graph node with properties"""
        return {
            'node_id': self.agent_id,
            'node_type': self.agent_type,
            'properties': {
                'salience_score': getattr(self, 'salience', 0),
                'legitimacy': getattr(self, 'legitimacy', 0),
                'urgency': getattr(self, 'urgency', 0),
                'power': getattr(self, 'power', 0)
            },
            'edges': self._get_relationship_edges()
        }
    
    def get_table_representation(self) -> Dict:
        """Agent as table row with calculated metrics"""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'salience_score': getattr(self, 'salience', 0),
            'influence_rank': self._calculate_influence_rank(),
            'network_centrality': self._calculate_centrality(),
            'cluster_membership': self._get_cluster_id()
        }
    
    def get_vector_representation(self) -> np.ndarray:
        """Agent as embedding vector for similarity analysis"""
        behavioral_features = self._extract_behavioral_features()
        communication_features = self._extract_communication_features()
        return np.concatenate([behavioral_features, communication_features])
```

### Dynamic Adaptation Implementation

For theories with dynamic_adaptation specifications:

```python
class AdaptiveAgent(KGASTheoryDrivenAgent):
    def __init__(self, agent_id: str, theory_schema: Dict):
        super().__init__(agent_id, "AdaptiveAgent")
        
        # Initialize state variables from schema
        dynamic_config = theory_schema.get('dynamic_adaptation', {})
        self.state_variables = {}
        
        for var_name, var_config in dynamic_config.get('state_variables', {}).items():
            self.state_variables[var_name] = var_config['initial']
        
        # Store adaptation rules and triggers
        self.adaptation_triggers = dynamic_config.get('adaptation_triggers', [])
        self.adaptation_rules = dynamic_config.get('adaptation_rules', [])
    
    def step(self, context: SimulationContext) -> List[Dict]:
        """Execute with dynamic adaptation"""
        # Normal behavior execution
        actions = super().step(context)
        
        # Check adaptation triggers
        for trigger in self.adaptation_triggers:
            if self._evaluate_condition(trigger['condition'], context):
                self._execute_adaptation(trigger['action'])
        
        return actions
    
    def _evaluate_condition(self, condition: str, context: SimulationContext) -> bool:
        """Evaluate adaptation trigger condition"""
        # Parse condition like "minority_visibility < 0.3"
        # Use safe evaluation with current state and context
        evaluation_context = {
            **self.state_variables,
            'context': context
        }
        
        return eval(condition, {"__builtins__": {}}, evaluation_context)
    
    def _execute_adaptation(self, action: str):
        """Execute adaptation action like 'increase_spiral_strength'"""
        # Apply adaptation rules
        for rule in self.adaptation_rules:
            if action in rule:
                # Execute rule like "spiral_strength *= 1.2 when minority_visibility decreases"
                self._apply_adaptation_rule(rule)
```

### Validation Integration

Agent behavior validation using theory test cases from the schema:

```python
class TheoryValidationFramework:
    def __init__(self, theory_schema: Dict, agent_population: List[KGASTheoryDrivenAgent]):
        self.schema = theory_schema
        self.agents = agent_population
        self.validation_config = theory_schema.get('validation', {})
    
    def run_theory_tests(self) -> Dict[str, bool]:
        """Execute theory_tests from validation section"""
        results = {}
        
        for test in self.validation_config.get('theory_tests', []):
            test_result = self._execute_theory_test(test)
            results[test['test_name']] = test_result
        
        return results
    
    def _execute_theory_test(self, test: Dict) -> bool:
        """Execute individual theory test"""
        # Set up scenario from input_scenario
        scenario = self._create_test_scenario(test['input_scenario'])
        
        # Run simulation with test scenario
        simulation_result = self._run_test_simulation(scenario)
        
        # Validate against expected_theory_application and validation_criteria
        return self._validate_result(simulation_result, test)
    
    def check_boundary_cases(self) -> List[Dict]:
        """Handle boundary_cases from validation section"""
        boundary_results = []
        
        for case in self.validation_config.get('boundary_cases', []):
            case_result = self._handle_boundary_case(case)
            boundary_results.append(case_result)
        
        return boundary_results
```

This translation framework demonstrates how KGAS theory meta-schema v10 components directly map to agent-based model configurations, enabling automated theory-to-simulation translation while maintaining theoretical fidelity and validation capabilities.

## Architecture Design

### Research-Informed Design Principles

Based on recent advances in generative agent research (Park et al. 2024, Lu et al. 2025, Gui & Toubia 2025), KGAS ABM incorporates:

1. **Rich Individual Parameterization**: Following Stanford's approach, agents use deep individual profiles beyond demographics
2. **Objective Accuracy Focus**: Emphasis on measurable accuracy metrics rather than subjective believability
3. **Unblinded Experimental Design**: Explicit experimental design communication to avoid confounding
4. **Expert Reflection Architecture**: Domain expert synthesis of agent characteristics from theory schemas
5. **Reasoning-Enhanced Agents**: Synthesized reasoning traces to improve decision accuracy
6. **Real-World Behavioral Validation**: Validation against actual behavioral datasets (COVID dataset)

### 1. ABM Service Layer

Add ABM capabilities as a new service in the Core Services Layer:

```python
class ABMService:
    """Agent-Based Modeling service for theory validation and simulation"""
    
    def __init__(self, theory_repository, knowledge_graphs, uncertainty_engine):
        self.theory_repository = theory_repository
        self.knowledge_graphs = knowledge_graphs
        self.uncertainty_engine = uncertainty_engine
        self.simulation_engine = GABMSimulationEngine()
        self.validation_engine = TheoryValidationEngine()
    
    def create_theory_simulation(self, theory_id: str) -> SimulationConfiguration:
        """Convert KGAS theory schema to GABM simulation parameters"""
        
    def run_simulation_experiment(self, config: SimulationConfiguration) -> SimulationResults:
        """Execute controlled ABM experiment with uncertainty tracking"""
        
    def validate_theory_predictions(self, theory_id: str, real_data: DataFrame) -> ValidationReport:
        """Compare simulation results to empirical data"""
```

### 2. Rich Individual Agent Architecture

Incorporating insights from Stanford's interview-based agents and reasoning-enhanced approaches:

```python
class KGASTheoryDrivenAgent(GenerativeAgent):
    """GABM agent with rich individual parameterization and expert reflection"""
    
    def __init__(self, theory_schema: TheoryMetaSchema, agent_profile: RichAgentProfile):
        # Core agent identity from multiple sources (Stanford approach)
        self.agent_id = agent_profile.agent_id
        self.theory_id = theory_schema.theory_id
        
        # Rich individual parameterization beyond demographics
        self.individual_profile = self._create_rich_profile(agent_profile)
        self.expert_reflection = self._synthesize_expert_insights(theory_schema, agent_profile)
        
        # Theory-derived components
        self.identity_component = self._create_identity_from_theory(theory_schema, agent_profile)
        self.behavioral_rules = self._extract_behavioral_predictions(theory_schema)
        self.social_context = self._apply_scope_conditions(theory_schema)
        
        # Reasoning-enhanced decision making (Lu et al. approach)
        self.reasoning_engine = ReasoningEngine(theory_schema)
        self.uncertainty_awareness = UncertaintyAwareness(uncertainty_engine)
        
        # Validation against real behavioral patterns
        self.behavioral_validator = BehavioralPatternValidator(covid_dataset)
    
    def _create_rich_profile(self, agent_profile: RichAgentProfile) -> RichIndividualProfile:
        """Create rich individual profile beyond demographics (Stanford approach)"""
        return RichIndividualProfile(
            # Demographic basics
            demographics=agent_profile.demographics,
            
            # Psychological characteristics (from COVID dataset psychometric scales)
            psychological_traits={
                'narcissism': agent_profile.narcissism_score,
                'need_for_chaos': agent_profile.need_for_chaos_score,
                'conspiracy_mentality': agent_profile.conspiracy_mentality_score,
                'denialism': agent_profile.denialism_score,
                'misinformation_susceptibility': agent_profile.misinformation_susceptibility
            },
            
            # Behavioral patterns (from COVID dataset engagement data)
            behavioral_history=agent_profile.twitter_engagement_patterns,
            
            # Social network position
            social_characteristics={
                'follower_count': agent_profile.follower_count,
                'following_count': agent_profile.following_count,
                'network_centrality': agent_profile.calculated_centrality,
                'engagement_frequency': agent_profile.engagement_frequency
            },
            
            # Theory-specific characteristics
            theory_relevance=agent_profile.theory_alignment_scores
        )
    
    def _synthesize_expert_insights(self, theory: TheoryMetaSchema, 
                                   profile: RichAgentProfile) -> ExpertReflection:
        """Expert reflection module (Stanford approach)"""
        expert_persona = f"You are a {theory.domain} expert analyzing this individual's profile"
        
        # Synthesize high-level insights from the rich profile
        expert_synthesis = self.llm_call(
            system_prompt=expert_persona,
            user_prompt=f"""
            Analyze this individual's profile and synthesize key psychological and behavioral insights:
            
            Demographics: {profile.demographics}
            Psychological Traits: {profile.psychological_traits}
            Behavioral History: {profile.behavioral_summary}
            Social Position: {profile.social_characteristics}
            Theory Alignment: {profile.theory_alignment_scores}
            
            Provide expert insights on:
            1. Core personality characteristics
            2. Likely behavioral tendencies
            3. Social influence patterns
            4. Decision-making style
            5. Vulnerability to misinformation
            """,
            temperature=0.3
        )
        
        return ExpertReflection(
            expert_domain=theory.domain,
            synthesis=expert_synthesis,
            confidence_assessment=self._assess_profile_completeness(profile),
            behavioral_predictions=self._extract_behavioral_predictions(expert_synthesis)
        )
    
    def _create_identity_from_theory(self, theory: TheoryMetaSchema) -> AgentIdentity:
        """Convert theory key concepts to agent identity"""
        return AgentIdentity(
            core_concepts=theory.key_concepts,
            domain_knowledge=theory.domain_specific_elements,
            theoretical_assumptions=theory.theoretical_predictions
        )
    
    async def decide_action(self, context: SimulationContext) -> AgentAction:
        """Reasoning-enhanced decision making (Lu et al. approach)"""
        
        # Step 1: Generate explicit reasoning trace
        reasoning_trace = await self.reasoning_engine.generate_reasoning(
            context=context,
            agent_profile=self.individual_profile,
            expert_reflection=self.expert_reflection,
            behavioral_rules=self.behavioral_rules
        )
        
        # Step 2: Assess confidence in decision context
        confidence = await self.uncertainty_awareness.assess_decision_confidence(
            context, self.behavioral_rules, self.memory, reasoning_trace
        )
        
        # Step 3: Make decision based on reasoning and confidence
        if confidence < self.decision_threshold:
            action = await self._seek_information_action(context, reasoning_trace)
        else:
            action = await self._apply_behavioral_rule(context, confidence, reasoning_trace)
        
        # Step 4: Validate against real behavioral patterns
        behavioral_plausibility = await self.behavioral_validator.validate_action(
            action, self.individual_profile, context
        )
        
        # Step 5: Track decision provenance
        decision_record = DecisionRecord(
            agent_id=self.agent_id,
            context=context,
            reasoning_trace=reasoning_trace,
            confidence_assessment=confidence,
            action_taken=action,
            behavioral_plausibility=behavioral_plausibility,
            theory_influence=self._trace_theory_influence(action),
            expert_reflection_influence=self._trace_expert_influence(action),
            timestamp=datetime.now()
        )
        
        self.decision_history.append(decision_record)
        return action

class ReasoningEngine:
    """Generate explicit reasoning traces for agent decisions (Lu et al. approach)"""
    
    def __init__(self, theory_schema: TheoryMetaSchema):
        self.theory_schema = theory_schema
        self.reasoning_synthesizer = ReasoningSynthesizer()
    
    async def generate_reasoning(self, 
                               context: SimulationContext,
                               agent_profile: RichIndividualProfile,
                               expert_reflection: ExpertReflection,
                               behavioral_rules: List[BehavioralRule]) -> ReasoningTrace:
        """Generate explicit reasoning for decision context"""
        
        reasoning_prompt = f"""
        You are {agent_profile.demographics['name']}, with the following characteristics:
        
        Psychological Profile: {agent_profile.psychological_traits}
        Behavioral History: {agent_profile.behavioral_history}
        Expert Assessment: {expert_reflection.synthesis}
        
        Current Situation: {context.description}
        Available Actions: {context.available_actions}
        
        Theory-Based Behavioral Rules:
        {[rule.description for rule in behavioral_rules]}
        
        Explain your reasoning for what you would do in this situation. Consider:
        1. How your personality traits influence your thinking
        2. What your past behavior suggests you might do
        3. How the expert assessment applies to this situation
        4. Which theoretical behavioral rules are most relevant
        5. What uncertainties or concerns you have
        
        Provide your reasoning in first-person, as if thinking through the decision.
        """
        
        reasoning_text = await self.llm_call(
            system_prompt="You are reasoning through a decision as this specific individual.",
            user_prompt=reasoning_prompt,
            temperature=0.7
        )
        
        return ReasoningTrace(
            raw_reasoning=reasoning_text,
            key_factors=self._extract_key_factors(reasoning_text),
            theory_applications=self._identify_theory_applications(reasoning_text, behavioral_rules),
            uncertainty_sources=self._identify_uncertainty_sources(reasoning_text),
            confidence_indicators=self._assess_reasoning_confidence(reasoning_text)
        )
```

### 3. Cross-Modal Agent Environments

Use KGAS's tri-modal architecture to create rich simulation environments:

```python
class CrossModalGameMaster(GameMaster):
    """Game Master that uses KGAS cross-modal data as environment"""
    
    def __init__(self, knowledge_graph, demographic_data, semantic_embeddings):
        self.social_network = knowledge_graph  # Constrains agent interactions
        self.agent_characteristics = demographic_data  # Agent initial states
        self.conceptual_space = semantic_embeddings  # Semantic similarity
        self.provenance_tracker = ProvenanceTracker()
    
    def determine_agent_interactions(self, agent_actions: List[AgentAction]) -> List[Interaction]:
        """Use knowledge graph to determine possible interactions"""
        possible_interactions = []
        
        for action in agent_actions:
            # Query knowledge graph for interaction possibilities
            interaction_candidates = self.social_network.query_interaction_possibilities(
                agent=action.agent,
                action_type=action.action_type,
                context=action.context
            )
            
            # Filter by demographic compatibility
            compatible_interactions = self.filter_by_demographics(
                interaction_candidates, 
                self.agent_characteristics
            )
            
            # Score by semantic similarity
            scored_interactions = self.score_by_semantic_similarity(
                compatible_interactions,
                self.conceptual_space
            )
            
            possible_interactions.extend(scored_interactions)
        
        return self.resolve_interaction_conflicts(possible_interactions)

### 4. Unblinded Experimental Design (Gui & Toubia Insights)

Addressing critical confounding issues in LLM-based simulations:

```python
class UnblindedExperimentalDesign:
    """Unblinded experimental design to avoid confounding (Gui & Toubia approach)"""
    
    def __init__(self, theory_repository: TheoryRepository):
        self.theory_repository = theory_repository
        self.causal_inference_validator = CausalInferenceValidator()
    
    def create_unblinded_simulation_prompt(self, 
                                         experimental_design: ExperimentalDesign,
                                         agent_profile: RichAgentProfile) -> UnblindedPrompt:
        """Create unambiguous experimental prompt avoiding confounding"""
        
        # Explicitly communicate the experimental design to avoid ambiguity
        experimental_context = f"""
        EXPERIMENTAL DESIGN CONTEXT:
        - This is a controlled experiment testing: {experimental_design.hypothesis}
        - Treatment variable: {experimental_design.treatment_variable}
        - Treatment conditions: {experimental_design.treatment_conditions}
        - Control variables held constant: {experimental_design.control_variables}
        - Randomization scheme: {experimental_design.randomization_method}
        
        IMPORTANT: You are experiencing the {experimental_design.current_condition} condition.
        This condition was randomly assigned for experimental purposes.
        All other factors should be considered at their typical/baseline levels unless specified.
        """
        
        # Agent-specific context
        agent_context = f"""
        YOUR INDIVIDUAL CHARACTERISTICS:
        Demographics: {agent_profile.demographics}
        Psychological Traits: {agent_profile.psychological_traits}
        Behavioral History: {agent_profile.behavioral_history}
        Social Position: {agent_profile.social_characteristics}
        """
        
        # Clear causal question
        causal_question = f"""
        DECISION TASK:
        Given your individual characteristics and the experimental condition you're experiencing,
        how would you respond to: {experimental_design.decision_scenario}
        
        Focus on how the treatment condition ({experimental_design.treatment_variable}: 
        {experimental_design.current_condition}) affects your decision, holding all other 
        factors at their typical levels.
        """
        
        return UnblindedPrompt(
            experimental_context=experimental_context,
            agent_context=agent_context,
            causal_question=causal_question,
            control_variables=experimental_design.control_variables,
            is_unambiguous=True
        )
    
    def validate_experimental_design(self, design: ExperimentalDesign) -> ValidationResult:
        """Validate experimental design for causal inference"""
        
        validation_checks = {
            'treatment_clarity': self._check_treatment_clarity(design),
            'control_specification': self._check_control_specification(design),
            'randomization_validity': self._check_randomization_validity(design),
            'confounding_prevention': self._check_confounding_prevention(design),
            'prompt_ambiguity': self._check_prompt_ambiguity(design)
        }
        
        overall_validity = all(check.is_valid for check in validation_checks.values())
        
        return ValidationResult(
            is_valid=overall_validity,
            validation_checks=validation_checks,
            recommendations=self._generate_design_recommendations(validation_checks)
        )

class CausalInferenceValidator:
    """Validate simulation results for causal inference (Gui & Toubia approach)"""
    
    def __init__(self):
        self.confounding_detector = ConfoundingDetector()
        self.ecological_validator = EcologicalValidityValidator()
    
    def validate_simulation_results(self, 
                                  simulation_results: SimulationResults,
                                  experimental_design: ExperimentalDesign) -> CausalValidationReport:
        """Comprehensive validation of causal inference from simulation"""
        
        # Check for confounding patterns
        confounding_analysis = self.confounding_detector.detect_confounding(
            simulation_results, experimental_design
        )
        
        # Validate ecological validity
        ecological_validity = self.ecological_validator.assess_ecological_validity(
            simulation_results, experimental_design
        )
        
        # Compare to real-world benchmarks (COVID dataset)
        benchmark_comparison = self._compare_to_benchmarks(
            simulation_results, experimental_design
        )
        
        # Generate causal inference assessment
        causal_inference_quality = self._assess_causal_inference_quality(
            confounding_analysis, ecological_validity, benchmark_comparison
        )
        
        return CausalValidationReport(
            confounding_analysis=confounding_analysis,
            ecological_validity=ecological_validity,
            benchmark_comparison=benchmark_comparison,
            causal_inference_quality=causal_inference_quality,
            recommendations=self._generate_causal_recommendations(
                confounding_analysis, ecological_validity
            )
        )
    
    def _compare_to_benchmarks(self, 
                              results: SimulationResults,
                              design: ExperimentalDesign) -> BenchmarkComparison:
        """Compare simulation results to real behavioral data"""
        
        # Find similar real-world studies from COVID dataset
        similar_studies = self._find_similar_studies(design)
        
        if not similar_studies:
            return BenchmarkComparison(
                comparison_available=False,
                reason="No similar real-world studies found"
            )
        
        # Compare effect sizes and patterns
        effect_size_comparison = self._compare_effect_sizes(results, similar_studies)
        pattern_comparison = self._compare_behavioral_patterns(results, similar_studies)
        
        return BenchmarkComparison(
            comparison_available=True,
            similar_studies=similar_studies,
            effect_size_similarity=effect_size_comparison,
            pattern_similarity=pattern_comparison,
            overall_similarity=np.mean([effect_size_comparison, pattern_comparison])
        )

class WhatIfScenarioExplorer:
    """Explore counterfactual scenarios (Social Simulacra approach)"""
    
    def __init__(self, abm_service: ABMService):
        self.abm_service = abm_service
        self.scenario_generator = ScenarioGenerator()
    
    async def explore_whatif_scenario(self, 
                                    base_simulation: SimulationResults,
                                    intervention: Intervention) -> WhatIfResults:
        """Explore 'what if' scenario with specified intervention"""
        
        # Create modified simulation configuration
        modified_config = self._apply_intervention(
            base_simulation.configuration, intervention
        )
        
        # Run counterfactual simulation
        counterfactual_results = await self.abm_service.run_simulation_experiment(
            modified_config
        )
        
        # Compare outcomes
        outcome_comparison = self._compare_outcomes(
            base_simulation, counterfactual_results
        )
        
        # Assess intervention effectiveness
        intervention_effectiveness = self._assess_intervention_effectiveness(
            outcome_comparison, intervention
        )
        
        return WhatIfResults(
            base_scenario=base_simulation,
            counterfactual_scenario=counterfactual_results,
            intervention_applied=intervention,
            outcome_comparison=outcome_comparison,
            intervention_effectiveness=intervention_effectiveness,
            causal_interpretation=self._generate_causal_interpretation(
                outcome_comparison, intervention
            )
        )
    
    async def explore_multiverse_scenarios(self, 
                                         base_config: SimulationConfiguration,
                                         num_variations: int = 10) -> MultiverseResults:
        """Generate multiple scenario variations (Social Simulacra multiverse)"""
        
        multiverse_results = []
        
        for i in range(num_variations):
            # Add randomness to simulation parameters
            varied_config = self._add_random_variation(base_config, variation_seed=i)
            
            # Run simulation with variation
            variant_results = await self.abm_service.run_simulation_experiment(varied_config)
            multiverse_results.append(variant_results)
        
        # Analyze variance across scenarios
        variance_analysis = self._analyze_multiverse_variance(multiverse_results)
        
        # Identify robust vs. fragile patterns
        robustness_analysis = self._analyze_pattern_robustness(multiverse_results)
        
        return MultiverseResults(
            base_configuration=base_config,
            scenario_variations=multiverse_results,
            variance_analysis=variance_analysis,
            robustness_analysis=robustness_analysis,
            design_implications=self._generate_design_implications(
                variance_analysis, robustness_analysis
            )
        )
```

### 4. Uncertainty-Aware Simulation

Integrate KGAS uncertainty framework into ABM:

```python
class UncertaintyAwareSimulation:
    """ABM simulation with KGAS uncertainty quantification"""
    
    def __init__(self, uncertainty_engine: UncertaintyEngine):
        self.uncertainty_engine = uncertainty_engine
        self.simulation_uncertainty = SimulationUncertainty()
    
    def run_simulation_with_uncertainty(self, config: SimulationConfiguration) -> UncertainSimulationResults:
        """Run simulation with uncertainty propagation"""
        
        # Track uncertainty in initial conditions
        initial_uncertainty = self.uncertainty_engine.assess_initial_conditions(config)
        
        # Run multiple simulation variants
        simulation_variants = self.generate_simulation_variants(config, initial_uncertainty)
        results = []
        
        for variant in simulation_variants:
            result = self.run_single_simulation(variant)
            result.uncertainty_metadata = self.track_simulation_uncertainty(variant, result)
            results.append(result)
        
        # Aggregate results with uncertainty
        aggregated_results = self.uncertainty_engine.aggregate_simulation_results(results)
        
        return UncertainSimulationResults(
            mean_results=aggregated_results.mean,
            confidence_intervals=aggregated_results.confidence_intervals,
            uncertainty_distribution=aggregated_results.uncertainty,
            provenance=self.generate_simulation_provenance(config, results)
        )
```

### 5. Validation Against Real Data

Use COVID conspiracy theory dataset for validation:

```python
class SimulationValidationEngine:
    """Validate ABM results against empirical data"""
    
    def __init__(self, covid_dataset: CovidConspiracyDataset):
        self.validation_data = covid_dataset
        self.psychological_profiles = covid_dataset.psychological_scales
        self.behavioral_data = covid_dataset.twitter_engagements
    
    def validate_conspiracy_theory_simulation(self, simulation_results: SimulationResults) -> ValidationReport:
        """Compare ABM results to COVID conspiracy behavior"""
        
        validation_metrics = []
        
        # Level 1: Behavioral Pattern Validation
        behavioral_similarity = self.compare_behavioral_patterns(
            simulation_results.agent_behaviors,
            self.behavioral_data.engagement_patterns
        )
        validation_metrics.append(("behavioral_similarity", behavioral_similarity))
        
        # Level 2: Psychological Construct Validation
        psychological_accuracy = self.validate_psychological_constructs(
            simulation_results.agent_psychological_states,
            self.psychological_profiles
        )
        validation_metrics.append(("psychological_accuracy", psychological_accuracy))
        
        # Level 3: Network Effect Validation
        network_effects = self.validate_network_propagation(
            simulation_results.information_spread,
            self.behavioral_data.retweet_cascades
        )
        validation_metrics.append(("network_effects", network_effects))
        
        return ValidationReport(
            overall_validity=self.calculate_overall_validity(validation_metrics),
            detailed_metrics=validation_metrics,
            recommendations=self.generate_improvement_recommendations(validation_metrics)
        )
    
    def compare_behavioral_patterns(self, simulated_behaviors: List[AgentBehavior], 
                                  real_behaviors: List[TwitterEngagement]) -> float:
        """Compare simulated agent behaviors to real Twitter engagement patterns"""
        
        # Extract behavioral features from both datasets
        simulated_features = self.extract_behavioral_features(simulated_behaviors)
        real_features = self.extract_behavioral_features(real_behaviors)
        
        # Calculate similarity using multiple metrics
        correlation_similarity = self.calculate_correlation(simulated_features, real_features)
        distribution_similarity = self.calculate_distribution_similarity(simulated_features, real_features)
        temporal_similarity = self.calculate_temporal_similarity(simulated_features, real_features)
        
        return (correlation_similarity + distribution_similarity + temporal_similarity) / 3
```

## Integration with Existing Architecture

### 1. Updated Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│    (Natural Language → Agent → Workflow → Results)           │
│                    + ABM Simulation Controls                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Cross-Modal Analysis Layer                    │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐   │
│  │Graph Analysis│ │Table Analysis│ │Vector Analysis      │   │
│  └─────────────┘ └──────────────┘ └─────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              ABM Simulation Layer                       │ │
│  │    Theory Validation + Synthetic Experiments            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Core Services Layer                        │
│  ┌────────────────────┐ ┌────────────────┐ ┌─────────────┐ │
│  │PipelineOrchestrator│ │IdentityService │ │PiiService   │ │
│  ├────────────────────┤ ├────────────────┤ ├─────────────┤ │
│  │AnalyticsService    │ │TheoryRepository│ │QualityService│ │
│  ├────────────────────┤ ├────────────────┤ ├─────────────┤ │
│  │ProvenanceService   │ │WorkflowEngine  │ │SecurityMgr  │ │
│  ├────────────────────┤ ├────────────────┤ ├─────────────┤ │
│  │    ABMService      │ │ValidationEngine│ │UncertaintyMgr│ │
│  └────────────────────┘ └────────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2. Data Architecture Extension

Extend bi-store architecture to support simulation data:

```sql
-- SQLite: Simulation metadata and results
CREATE TABLE simulations (
    simulation_id TEXT PRIMARY KEY,
    theory_id TEXT,
    configuration JSON,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT,
    uncertainty_metadata JSON
);

CREATE TABLE simulation_results (
    result_id TEXT PRIMARY KEY,
    simulation_id TEXT,
    agent_id TEXT,
    timestep INTEGER,
    action_type TEXT,
    action_data JSON,
    uncertainty_score REAL,
    provenance_chain TEXT
);

CREATE TABLE validation_reports (
    report_id TEXT PRIMARY KEY,
    simulation_id TEXT,
    validation_dataset TEXT,
    behavioral_similarity REAL,
    psychological_accuracy REAL,
    network_effects REAL,
    overall_validity REAL,
    recommendations JSON
);
```

```cypher
-- Neo4j: Agent relationships and simulation networks
CREATE (:SimulationAgent {
    agent_id: string,
    simulation_id: string,
    agent_type: string,
    psychological_profile: map,
    behavioral_rules: list,
    uncertainty_threshold: float
})

CREATE (:SimulationInteraction {
    interaction_id: string,
    simulation_id: string,
    timestep: integer,
    interaction_type: string,
    participants: list,
    outcome: map,
    uncertainty_metadata: map
})

// Relationship between agents and their interactions
CREATE (:SimulationAgent)-[:PARTICIPATED_IN]->(:SimulationInteraction)
```

### 3. Tool Ecosystem Extension

Add ABM tools to the 121+ tool ecosystem:

```python
# New ABM-specific tools
class T122_TheoryToAgentTranslator(KGASTool):
    """Convert theory schemas to agent configurations"""
    
class T123_SimulationDesigner(KGASTool):
    """Design controlled experiments for theory testing"""
    
class T124_AgentPopulationGenerator(KGASTool):
    """Generate diverse agent populations from demographic data"""
    
class T125_SimulationValidator(KGASTool):
    """Validate simulation results against empirical data"""
    
class T126_CounterfactualExplorer(KGASTool):
    """Explore 'what if' scenarios through simulation"""
    
class T127_SyntheticDataGenerator(KGASTool):
    """Generate synthetic datasets for theory testing"""
    
class T128_EmergentBehaviorDetector(KGASTool):
    """Detect emergent patterns in simulation results"""
```

## Rationale

### Why ABM Integration Is Strategic

1. **Complements Analytical Capabilities**: KGAS analyzes existing data; ABM validates theories through simulation
2. **Leverages Existing Architecture**: Theory schemas, uncertainty framework, and cross-modal analysis enhance ABM
3. **Academic Research Value**: Theory validation through simulation is cutting-edge computational social science
4. **Real Dataset Validation**: COVID conspiracy dataset provides ground truth for validation
5. **Publication Opportunities**: GABM validation of social science theories is highly publishable

### Why Now

1. **GABM Technology Maturity**: Concordia framework proves LLM-based ABM is feasible
2. **KGAS Foundation Ready**: Theory operationalization and uncertainty framework provide perfect foundation
3. **Validation Dataset Available**: COVID conspiracy dataset enables immediate validation capability
4. **Research Gap**: No existing platforms combine theory-driven ABM with cross-modal analysis

### Technical Advantages

1. **Theory-Driven Parameterization**: Unlike generic ABM, agents are parameterized by academic theories
2. **Uncertainty-Aware Simulation**: Incorporates KGAS's sophisticated uncertainty framework
3. **Cross-Modal Environments**: Uses graph/table/vector data to create rich simulation environments
4. **Empirical Validation**: Built-in validation against real behavioral data

## Consequences

### Positive Consequences

1. **Complete Research Platform**: KGAS becomes analysis + validation platform
2. **Theory Testing Capability**: Researchers can test theories through controlled experiments
3. **Synthetic Data Generation**: Generate realistic social science data for training/testing
4. **Academic Impact**: Positions KGAS at forefront of computational social science
5. **Validation Evidence**: Built-in validation against real psychological/behavioral data

### Challenges

1. **Complexity Increase**: ABM adds significant architectural complexity
2. **Resource Requirements**: Simulations are computationally intensive
3. **Validation Complexity**: Ensuring simulation realism requires sophisticated validation
4. **Development Time**: ABM integration requires substantial development effort

### Risk Mitigation

1. **Phased Implementation**: Start with simple theory-agent translation, add complexity gradually
2. **Validation-First Approach**: Use COVID dataset validation to ensure realism from start
3. **Resource Management**: Implement intelligent resource allocation for simulations
4. **Academic Partnerships**: Collaborate with ABM researchers for domain expertise

## Implementation Phases

### Phase 1: Foundation (Months 1-3)
- Basic theory-to-agent translation
- Simple simulation engine integration
- COVID dataset validation framework

### Phase 2: Cross-Modal Integration (Months 4-6)
- Cross-modal environment generation
- Uncertainty-aware simulation
- Empirical validation automation

### Phase 3: Advanced Capabilities (Months 7-12)
- Counterfactual exploration tools
- Synthetic data generation
- Emergent behavior detection
- Academic publication support

## Alternatives Considered

### Alternative 1: External ABM Integration
**Approach**: Integrate with existing ABM platforms (NetLogo, MASON)
**Rejected Because**: 
- Traditional ABM lacks LLM-based agent sophistication
- Integration complexity without GABM benefits
- No theory-driven parameterization capability

### Alternative 2: Pure Analytical Focus
**Approach**: Keep KGAS purely analytical, no simulation
**Rejected Because**:
- Misses opportunity to validate theories through simulation
- Limits research impact and publication opportunities
- Doesn't leverage full potential of theory operationalization

### Alternative 3: Separate ABM Platform
**Approach**: Build separate ABM platform, integrate via API
**Rejected Because**:
- Loses integration benefits with uncertainty framework
- Duplicates architecture and increases maintenance
- Fragments user experience across platforms

## KGAS Theory Meta-Schema v10 to ABM Translation

Based on analysis of your theory meta-schema v10 structure and examples (Stakeholder Theory v10.json, Carter Framing Analysis YAML), here's how KGAS theories directly map to ABM agents:

### Theory Schema → Agent Behavioral Rules Mapping

**From Stakeholder Theory Schema:**
```python
# Mitchell-Agle-Wood Salience Algorithm → Agent Behavioral Rule
salience_rule = BehavioralRule(
    rule_id="stakeholder_priority_response",
    behavioral_tendency="priority_response = (legitimacy * urgency * power) ** (1/3)",
    custom_script=theory_schema['execution']['analysis_steps'][4]['custom_script'],
    test_cases=theory_schema['validation']['theory_tests'],
    operationalization=theory_schema['validation']['operationalization_notes']
)
```

**From Carter Framing Theory Analysis:**
```python
# Frame Competition Mechanism → Agent Decision Process
frame_competition_rule = BehavioralRule(
    rule_id="frame_competition_response",
    behavioral_tendency="""
    frame_strength = cultural_resonance * logical_coherence * source_credibility
    response_probability = sigmoid(dominant_frame_strength - competing_frame_strength)
    """,
    psychological_mechanisms=['accessibility', 'availability', 'applicability'],
    causal_analysis=carter_schema['causal_analysis']['competitive_dynamics']
)
```

### Theory Operationalization → Agent Measurement Sensitivity

**From Stakeholder Theory Legitimacy Property:**
```python
# Operationalization boundaries → Agent assessment patterns
legitimacy_assessment = MeasurementApproach(
    boundary_rules=theory_schema['ontology']['entities'][0]['properties'][0]['operationalization']['boundary_rules'],
    # {"condition": "legal_right == true", "legitimacy": 0.8}
    # {"condition": "moral_claim == true", "legitimacy": 0.6}
    validation_examples=theory_schema['validation']['theory_tests'],
    fuzzy_boundaries=True
)
```

### Theory Execution Steps → Agent Decision Framework

**From Stakeholder Theory Analysis Steps:**
```python
# LLM extraction prompts → Agent reasoning processes
stakeholder_identification = ReasoningProcess(
    reasoning_prompt=theory_schema['execution']['analysis_steps'][0]['llm_prompts']['extraction_prompt'],
    validation_prompt=theory_schema['execution']['analysis_steps'][0]['llm_prompts']['validation_prompt'],
    confidence_thresholds=theory_schema['execution']['analysis_steps'][0]['uncertainty_handling']['confidence_thresholds']
)
```

### Cross-Modal Mappings → Agent Environment Integration

**From Theory Cross-Modal Specifications:**
```python
# Cross-modal mappings → Agent environment understanding
agent_environment_mapping = {
    'graph_mode': theory_schema['execution']['cross_modal_mappings']['graph_representation'],
    'table_mode': theory_schema['execution']['cross_modal_mappings']['table_representation'], 
    'vector_mode': theory_schema['execution']['cross_modal_mappings']['vector_representation']
}
```

### Key Insights from Schema Analysis

1. **Rich Operationalization**: Your v10 schemas contain detailed operationalization with boundary rules, validation examples, and confidence thresholds - perfect for agent parameterization
2. **Executable Algorithms**: Custom scripts (like Mitchell-Agle-Wood salience) can be directly implemented as agent behavioral algorithms
3. **LLM Prompts Ready**: Extraction and validation prompts can be repurposed as agent reasoning templates
4. **Validation Framework**: Theory tests provide ready-made validation scenarios for agent behavior
5. **Cross-Modal Support**: Agents can naturally work across graph/table/vector modes using your mappings

### Theory-Agent Translation Pipeline

```python
class KGASTheoryToAgentPipeline:
    """Complete pipeline for translating v10 schemas to ABM agents"""
    
    def translate_theory_schema(self, theory_schema_path: str, 
                              covid_dataset: CovidDataset) -> List[KGASTheoryDrivenAgent]:
        
        # Step 1: Parse theory schema
        theory_schema = self.load_theory_schema(theory_schema_path)
        
        # Step 2: Create agent population from COVID dataset
        agent_profiles = self.create_agent_profiles_from_covid_data(
            covid_dataset, theory_schema
        )
        
        # Step 3: Translate schema to agent behavioral components
        behavioral_rules = self.extract_behavioral_rules(theory_schema)
        decision_framework = self.create_decision_framework(theory_schema['execution'])
        measurement_approaches = self.extract_measurement_approaches(theory_schema['ontology'])
        
        # Step 4: Create theory-driven agents
        agents = []
        for profile in agent_profiles:
            agent = KGASTheoryDrivenAgent(
                theory_schema=theory_schema,
                agent_profile=profile,
                behavioral_rules=behavioral_rules,
                decision_framework=decision_framework,
                measurement_approaches=measurement_approaches
            )
            agents.append(agent)
        
        return agents
```

This translation framework demonstrates that your sophisticated theory meta-schema v10 already contains all the components needed for creating behaviorally accurate ABM agents - operationalization details, measurement approaches, validation frameworks, executable algorithms, and even specific LLM prompts.

## Success Metrics

### Technical Metrics
1. **Simulation Performance**: Able to run 1000+ agent simulations within reasonable time
2. **Validation Accuracy**: >0.75 correlation with COVID dataset behavioral patterns
3. **Theory Coverage**: Support for major social science theories (>10 theory domains)
4. **Uncertainty Propagation**: Accurate uncertainty tracking through simulation pipelines

### Research Impact Metrics
1. **Academic Publications**: Enable 5+ publications in computational social science venues
2. **User Adoption**: 100+ researchers using ABM capabilities within 18 months
3. **Theory Validation**: Successful validation of 20+ existing social science theories
4. **Synthetic Data Quality**: Generated data indistinguishable from real data in blind tests

### Platform Integration Metrics
1. **Cross-Modal Utilization**: ABM uses all three data modes (graph/table/vector)
2. **Tool Ecosystem**: ABM tools integrate seamlessly with existing 121+ tools
3. **Workflow Integration**: ABM accessible through all three agent interface layers
4. **Provenance Tracking**: Complete audit trails for all simulation operations

## Conclusion

Integrating Agent-Based Modeling capabilities into KGAS represents a strategic evolution from a descriptive analysis platform to a complete theory validation and synthetic experimentation platform. The combination of KGAS's theory operationalization, uncertainty framework, and cross-modal analysis with GABM's generative simulation capabilities creates a unique and powerful platform for computational social science research.

The availability of the COVID conspiracy theory dataset for validation provides immediate capability to demonstrate ABM effectiveness, while the sophisticated theoretical foundation of KGAS ensures that simulations are grounded in rigorous academic theory rather than ad-hoc assumptions.

This integration positions KGAS as a next-generation research platform that can both analyze existing social phenomena and validate theoretical understanding through controlled simulation experiments.
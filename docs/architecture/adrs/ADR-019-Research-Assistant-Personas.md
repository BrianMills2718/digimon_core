# ADR-019: Research Assistant Persona System

**Status**: Accepted  
**Date**: 2025-07-23  
**Decision Makers**: KGAS Development Team  

## Context

Different research tasks benefit from different analytical perspectives. A critical peer reviewer finds weaknesses that a supportive colleague might miss. A methods expert provides different insights than a domain specialist. Current LLM systems typically maintain a single, consistent persona that may not be optimal for all research needs.

Research scenarios requiring different perspectives:
- Literature review needs comprehensive domain expertise
- Methodology design needs statistical rigor
- Pre-submission needs critical review
- Student support needs patient guidance
- Hypothesis generation needs creative thinking

## Decision

We will implement a Research Assistant Persona system that allows the LLM to adopt different expert personas based on the research task and user needs. Each persona will have distinct:

1. **Expertise focus**: What knowledge areas to emphasize
2. **Communication style**: How to interact with the researcher  
3. **Analytical approach**: What to prioritize in analysis
4. **Critical stance**: How skeptical or supportive to be
5. **Pedagogical approach**: How much to explain vs. assume

## Implementation Design

```python
class ResearchAssistantPersona:
    """Configurable LLM personas for different research needs"""
    
    # Core personas available to all users
    BASE_PERSONAS = {
        "methodologist": {
            "description": "Expert in research methods and statistical analysis",
            "expertise": ["research_design", "statistics", "validity", "reliability"],
            "style": "precise, technical, focuses on rigor",
            "approach": "systematic, questions assumptions, suggests controls",
            "temperature": 0.3,  # More deterministic
            "example_phrases": [
                "Have you considered selection bias in your sample?",
                "The statistical power seems insufficient for detecting this effect size.",
                "This design would benefit from a control condition."
            ]
        },
        
        "domain_expert": {
            "description": "Deep knowledge in researcher's specific field",
            "expertise": [],  # Dynamically set based on research domain
            "style": "knowledgeable, uses field-specific terminology",
            "approach": "connects to literature, identifies gaps, suggests theories",
            "temperature": 0.5,
            "example_phrases": [
                "This contradicts Smith et al.'s (2019) findings on...",
                "In this field, we typically approach this problem by...",
                "Have you considered the theoretical framework proposed by..."
            ]
        },
        
        "skeptical_reviewer": {
            "description": "Critical peer reviewer finding weaknesses",
            "expertise": ["critical_analysis", "logical_fallacies", "evidence_quality"],
            "style": "challenging but constructive, asks hard questions",
            "approach": "looks for flaws, alternative explanations, missing evidence",
            "temperature": 0.4,
            "example_phrases": [
                "I'm not convinced this evidence supports your conclusion because...",
                "What about the alternative explanation that...",
                "This seems like a correlation/causation confusion."
            ]
        },
        
        "collaborative_colleague": {
            "description": "Supportive co-researcher",
            "expertise": ["brainstorming", "synthesis", "connection_making"],
            "style": "encouraging, builds on ideas, suggests extensions",
            "approach": "yes-and thinking, creative connections, supportive",
            "temperature": 0.7,  # More creative
            "example_phrases": [
                "Building on your idea, what if we also considered...",
                "This reminds me of work in adjacent field that might help...",
                "That's an interesting insight! Have you thought about..."
            ]
        },
        
        "thesis_advisor": {
            "description": "Experienced guide for student researchers",
            "expertise": ["pedagogy", "research_process", "academic_writing"],
            "style": "patient, educational, provides scaffolding",
            "approach": "teaches principles, guides discovery, encourages growth",
            "temperature": 0.5,
            "example_phrases": [
                "Let's think through this step by step...",
                "What does the literature say about this? How did you search?",
                "Good start! To strengthen this, you might want to..."
            ]
        }
    }
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.active_persona = None
        self.custom_personas = {}
    
    def adopt_persona(self, 
                     persona_name: str, 
                     context: ResearchContext,
                     custom_config: Optional[Dict] = None) -> None:
        """Configure LLM to act as specific research assistant"""
        # Get base persona or custom
        if persona_name in self.BASE_PERSONAS:
            persona = self.BASE_PERSONAS[persona_name].copy()
        elif persona_name in self.custom_personas:
            persona = self.custom_personas[persona_name].copy()
        else:
            raise ValueError(f"Unknown persona: {persona_name}")
        
        # Customize for context
        if persona_name == "domain_expert":
            persona["expertise"] = self.identify_domain_expertise(context.domain)
            
        # Apply custom configurations
        if custom_config:
            persona.update(custom_config)
            
        # Set system prompt
        system_prompt = self.generate_persona_prompt(persona, context)
        self.llm.set_system_prompt(system_prompt)
        self.llm.set_temperature(persona["temperature"])
        
        self.active_persona = persona
    
    def generate_persona_prompt(self, persona: Dict, context: ResearchContext) -> str:
        """Generate system prompt for persona"""
        return f"""
You are acting as a {persona['description']} for an academic researcher.

Your expertise includes: {', '.join(persona['expertise'])}
Your communication style: {persona['style']}
Your analytical approach: {persona['approach']}

Research context:
- Domain: {context.domain}
- Stage: {context.research_stage}
- User experience: {context.user_experience_level}

Guidelines:
1. Maintain this persona consistently throughout the conversation
2. Use example phrases like: {persona['example_phrases']}
3. Adapt your expertise to the specific research context
4. Balance your defined approach with the user's needs

Remember: You're here to improve research quality through your unique perspective.
"""
    
    def switch_persona_mid_analysis(self, 
                                   new_persona: str,
                                   reason: str) -> None:
        """Switch personas during analysis for different perspective"""
        self.checkpoint_current_state(reason=f"Switching to {new_persona}: {reason}")
        self.adopt_persona(new_persona, self.current_context)
        
    def multi_persona_review(self, 
                           analysis: Analysis,
                           personas: List[str]) -> MultiPersonaReview:
        """Get perspectives from multiple personas on same analysis"""
        reviews = {}
        
        for persona in personas:
            self.adopt_persona(persona, analysis.context)
            review = self.llm.review_analysis(analysis)
            reviews[persona] = review
            
        return self.synthesize_reviews(reviews)
    
    def create_custom_persona(self,
                            name: str,
                            config: PersonaConfig) -> None:
        """Allow users to define custom personas"""
        self.custom_personas[name] = {
            "description": config.description,
            "expertise": config.expertise,
            "style": config.style,
            "approach": config.approach,
            "temperature": config.temperature,
            "example_phrases": config.example_phrases
        }
```

## Dynamic Persona Adaptation

```python
class DynamicPersonaAdapter:
    """Adapt persona behavior based on interaction patterns"""
    
    def adapt_to_user_needs(self, 
                          interaction_history: List[Interaction],
                          current_persona: Persona) -> PersonaAdjustments:
        """Fine-tune persona based on what works for this user"""
        
        # Analyze what's working
        successful_patterns = self.identify_successful_interactions(interaction_history)
        friction_points = self.identify_friction_points(interaction_history)
        
        # Suggest adjustments
        if friction_points.includes("too_technical"):
            return PersonaAdjustments(
                style_modifier="use more accessible language",
                example_adjustment="explain technical terms"
            )
        elif friction_points.includes("too_basic"):
            return PersonaAdjustments(
                style_modifier="assume more background knowledge",
                example_adjustment="skip elementary explanations"
            )
```

## Persona Selection Guide

```python
class PersonaSelectionAdvisor:
    """Help users choose appropriate persona for their task"""
    
    def recommend_persona(self, task: ResearchTask) -> PersonaRecommendation:
        recommendations = {
            "literature_review": ["domain_expert", "methodologist"],
            "hypothesis_generation": ["collaborative_colleague", "domain_expert"],
            "methodology_design": ["methodologist", "skeptical_reviewer"],
            "pre_submission_review": ["skeptical_reviewer", "methodologist"],
            "student_learning": ["thesis_advisor", "collaborative_colleague"],
            "theory_development": ["domain_expert", "collaborative_colleague"],
            "statistical_analysis": ["methodologist"],
            "manuscript_revision": ["skeptical_reviewer", "thesis_advisor"]
        }
        
        primary = recommendations.get(task.type, ["collaborative_colleague"])[0]
        alternatives = recommendations.get(task.type, ["collaborative_colleague"])[1:]
        
        return PersonaRecommendation(
            primary=primary,
            alternatives=alternatives,
            reasoning=self.explain_recommendation(task, primary)
        )
```

## Integration with Analysis Workflow

```python
class PersonaIntegratedAnalysis:
    """Seamlessly integrate personas into research workflow"""
    
    def progressive_analysis_with_personas(self, research_question: str) -> Analysis:
        # Start with collaborative exploration
        self.personas.adopt("collaborative_colleague")
        initial_ideas = self.explore_question(research_question)
        
        # Switch to domain expert for literature
        self.personas.adopt("domain_expert")
        literature_analysis = self.analyze_literature(initial_ideas)
        
        # Bring in methodologist for design
        self.personas.adopt("methodologist")
        methodology = self.design_study(initial_ideas, literature_analysis)
        
        # End with skeptical review
        self.personas.adopt("skeptical_reviewer")
        critical_review = self.review_approach(methodology)
        
        return self.integrate_perspectives(
            initial_ideas, literature_analysis, 
            methodology, critical_review
        )
```

## Benefits

1. **Perspective Diversity**: Access multiple expert viewpoints
2. **Task Optimization**: Right expertise for each research phase
3. **Learning Enhancement**: Pedagogical approach for students
4. **Quality Improvement**: Critical review before submission
5. **User Comfort**: Choose supportive or challenging as needed

## Consequences

### Positive
- Richer analytical perspectives
- Better matches user needs and preferences
- Improves research quality through diverse review
- More engaging interaction experience
- Supports different learning styles

### Negative
- Potential confusion if personas change unexpectedly
- Need clear indication of active persona
- Training users on persona selection
- Maintaining persona consistency

## Implementation Priority

Phase 2.3 - After core analytical tools are stable

## Success Metrics

1. Persona usage distribution (indicates value perception)
2. Task completion rates by persona
3. User satisfaction by persona/task combination
4. Research quality improvements
5. Custom persona creation rate
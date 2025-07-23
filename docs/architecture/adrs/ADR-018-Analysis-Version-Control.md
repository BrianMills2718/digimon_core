# ADR-018: Analysis Version Control System

**Status**: Accepted  
**Date**: 2025-07-23  
**Decision Makers**: KGAS Development Team  

## Context

Academic research is inherently iterative. Researchers refine hypotheses, explore alternative analytical approaches, and evolve their understanding over time. Current systems typically overwrite previous analyses or require manual copying, losing the research evolution history.

Key challenges in academic research that version control addresses:
- Need to explore alternative analytical approaches without losing work
- Requirement to document how understanding evolved for papers
- Desire to checkpoint analyses before major changes
- Need to share specific versions with collaborators or reviewers
- Ability to return to earlier analytical states

## Decision

We will implement a Git-like version control system for all KGAS analyses that allows:

1. **Checkpointing**: Save analysis state with descriptive messages
2. **Branching**: Explore alternative approaches in parallel
3. **History**: Track evolution of understanding over time
4. **Comparison**: See what changed between versions
5. **Collaboration**: Share specific versions with others

## Implementation Design

```python
class AnalysisVersionControl:
    """Git-like version control for research analyses"""
    
    def __init__(self, storage_backend: StorageBackend):
        self.storage = storage_backend
        self.version_graph = VersionGraph()
    
    def checkpoint_analysis(self, 
                          analysis: Analysis, 
                          message: str,
                          auto_checkpoint: bool = False) -> Version:
        """Save analysis state with message"""
        version = Version(
            id=generate_version_id(),
            analysis_snapshot=self.serialize_analysis(analysis),
            message=message,
            timestamp=datetime.utcnow(),
            parent_version=analysis.current_version,
            author=analysis.current_user,
            auto_generated=auto_checkpoint
        )
        
        self.storage.save_version(version)
        self.version_graph.add_version(version)
        
        return version
    
    def branch_analysis(self, 
                       analysis: Analysis, 
                       branch_name: str,
                       branch_point: Optional[Version] = None) -> Analysis:
        """Create alternate analysis branch"""
        if branch_point is None:
            branch_point = analysis.current_version
            
        new_branch = AnalysisBranch(
            name=branch_name,
            base_version=branch_point,
            created_at=datetime.utcnow(),
            description=f"Branched from {analysis.current_branch} at {branch_point.id}"
        )
        
        # Create new analysis on branch
        branched_analysis = self.create_analysis_copy(analysis)
        branched_analysis.current_branch = new_branch
        branched_analysis.current_version = branch_point
        
        return branched_analysis
    
    def merge_analyses(self,
                      source_branch: AnalysisBranch,
                      target_branch: AnalysisBranch,
                      merge_strategy: MergeStrategy) -> MergeResult:
        """Merge insights from one branch into another"""
        # LLM assists in intelligent merging of analytical insights
        conflicts = self.detect_conflicts(source_branch, target_branch)
        
        if conflicts:
            resolution = self.llm_assisted_conflict_resolution(conflicts)
            
        return self.apply_merge(source_branch, target_branch, resolution)
    
    def diff_versions(self,
                     version1: Version,
                     version2: Version) -> AnalysisDiff:
        """Show what changed between versions"""
        return AnalysisDiff(
            theories_added=self.get_added_theories(version1, version2),
            theories_removed=self.get_removed_theories(version1, version2),
            theories_modified=self.get_modified_theories(version1, version2),
            evidence_changes=self.get_evidence_changes(version1, version2),
            confidence_changes=self.get_confidence_changes(version1, version2),
            methodology_changes=self.get_methodology_changes(version1, version2)
        )
```

## Version Control Features

### Automatic Checkpointing
```python
# Auto-checkpoint on significant changes
auto_checkpoint_triggers = [
    "major_hypothesis_change",
    "confidence_shift_over_20_percent",
    "new_evidence_contradicts_conclusion",
    "methodology_switch",
    "before_llm_model_change"
]
```

### Branch Strategies
```python
common_branch_patterns = {
    "alternative_theory": "Explore different theoretical framework",
    "methodology_comparison": "Try different analytical approach",
    "sensitivity_analysis": "Test with different parameters",
    "reviewer_response": "Address specific reviewer concerns",
    "collaborative_exploration": "Shared branch with collaborator"
}
```

### Version Metadata
```python
@dataclass
class VersionMetadata:
    # Core version info
    id: str
    timestamp: datetime
    message: str
    author: str
    
    # Research context
    research_stage: str  # "exploratory", "hypothesis_testing", "final"
    confidence_level: float
    major_findings: List[str]
    
    # Relationships
    parent_version: Optional[str]
    child_versions: List[str]
    branch_name: str
    tags: List[str]  # "submitted_to_journal", "shared_with_advisor"
```

## Integration with IC Features

Version control enhances IC analytical techniques:

1. **ACH Evolution**: Track how competing hypotheses evolved
2. **Calibration History**: See how confidence accuracy improved
3. **Information Value**: Compare which information actually changed conclusions
4. **Stopping Rules**: Document why collection stopped at each version

## Benefits

1. **Research Transparency**: Full history of analytical evolution
2. **Exploration Safety**: Try new approaches without losing work
3. **Collaboration**: Share specific versions with others
4. **Learning**: See how understanding developed over time
5. **Reproducibility**: Return to any previous analytical state

## Consequences

### Positive
- Encourages exploration and experimentation
- Documents research journey for papers
- Enables "what if" analysis safely
- Supports collaborative workflows
- Preserves institutional knowledge

### Negative
- Storage requirements for version history
- Complexity in UI for version management
- Learning curve for version control concepts
- Potential for "version sprawl"

## Alternatives Considered

1. **Simple Checkpointing Only**: Rejected - doesn't support exploration
2. **Full Git Integration**: Rejected - too complex for researchers
3. **Manual Save As**: Rejected - loses relationships between versions

## Implementation Priority

Phase 2.2 - After core IC features are implemented

## Success Metrics

1. Average branches per analysis (target: 2-3)
2. Checkpoint frequency (target: 5-10 per analysis)
3. Version recovery usage (indicates trust in system)
4. Collaboration via shared versions
5. Research paper citations of version IDs
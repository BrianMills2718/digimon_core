# Theory Repository Abstraction

*Status: Living Document*

## 1. Overview

To support future integration of a dedicated version control system for theories (e.g., Git, TerminusDB, Dolt) without requiring a major refactor, all interactions with theory storage **MUST** go through the `TheoryRepository` interface.

This abstraction decouples the core application logic from the underlying storage mechanism of the theories.

## 2. The `TheoryRepository` Interface

The interface is defined by the following abstract base class (`ABC`). Any concrete implementation of a theory store must inherit from this class and implement all its methods.

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class TheoryRepository(ABC):
    """
    An abstract interface for storing, versioning, and retrieving 
    theoretical models.
    """

    @abstractmethod
    def get_theory_version(self, theory_id: str, version_hash: str) -> Dict[str, Any]:
        """
        Retrieves a specific, immutable version of a theory.
        
        Args:
            theory_id: The stable identifier for the theory family.
            version_hash: The unique hash identifying the specific version.
            
        Returns:
            The theory content as a dictionary.
            
        Raises:
            TheoryNotFoundException: If the theory or version does not exist.
        """
        pass

    @abstractmethod
    def list_theory_versions(self, theory_id: str) -> List[Dict[str, str]]:
        """
        Lists all available versions for a given theory family.
        
        Args:
            theory_id: The stable identifier for the theory family.
            
        Returns:
            A list of dictionaries, each containing 'version_hash' and 'commit_message'.
        """
        pass

    @abstractmethod
    def create_branch(self, theory_id: str, parent_version_hash: str, branch_name: str) -> str:
        """
        Creates a new, editable branch from a specific parent version.
        
        Args:
            theory_id: The stable identifier for the theory family.
            parent_version_hash: The hash of the version to branch from.
            branch_name: The name for the new branch.
            
        Returns:
            A unique identifier for the new branch.
        """
        pass

    @abstractmethod
    def commit_changes(self, branch_id: str, commit_message: str, theory_content: Dict[str, Any]) -> str:
        """
        Commits changes from a branch, creating a new immutable version.
        
        Args:
            branch_id: The identifier of the branch to commit.
            commit_message: A message describing the changes.
            theory_content: The new content of the theory.
            
        Returns:
            The new 'version_hash' for the committed version.
        """
        pass
```

## 3. Filesystem-Based Stub Implementation

For the initial MVP, a simple filesystem-based implementation will be provided. This implementation will satisfy the interface but will not offer true branching or versioning capabilities. It will serve as a placeholder to allow development of other services to proceed.

**Behavior:**
- `get_theory_version`: Reads a JSON file from a directory structure like `/theories/{theory_id}/{version_hash}.json`.
- `list_theory_versions`: Lists files in the `{theory_id}` directory.
- `create_branch` and `commit_changes`: These will be placeholder methods that may simply copy files and will not provide transactional guarantees or true `git`-like functionality.

This stub ensures that all dependent services correctly use the abstraction, making a future upgrade to a real versioning system a matter of swapping out the repository implementation. 
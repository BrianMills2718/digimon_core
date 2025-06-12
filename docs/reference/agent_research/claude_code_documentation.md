# Claude Code overview

> Learn about Claude Code, an agentic coding tool made by Anthropic.

Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster through natural language commands. By integrating directly with your development environment, Claude Code streamlines your workflow without requiring additional servers or complex setup.

```bash
npm install -g @anthropic-ai/claude-code
```

Claude Code's key capabilities include:

* Editing files and fixing bugs across your codebase
* Answering questions about your code's architecture and logic
* Executing and fixing tests, linting, and other commands
* Searching through git history, resolving merge conflicts, and creating commits and PRs
* Browsing documentation and resources from the internet using web search
* Works with [Amazon Bedrock and Google Vertex AI](/en/docs/claude-code/bedrock-vertex-proxies) for enterprise deployments

## Why Claude Code?

Claude Code operates directly in your terminal, understanding your project context and taking real actions. No need to manually add files to context - Claude will explore your codebase as needed.

### Enterprise integration

Claude Code seamlessly integrates with enterprise AI platforms. You can connect to [Amazon Bedrock or Google Vertex AI](/en/docs/claude-code/bedrock-vertex-proxies) for secure, compliant deployments that meet your organization's requirements.

### Security and privacy by design

Your code's security is paramount. Claude Code's architecture ensures:

* **Direct API connection**: Your queries go straight to Anthropic's API without intermediate servers
* **Works where you work**: Operates directly in your terminal
* **Understands context**: Maintains awareness of your entire project structure
* **Takes action**: Performs real operations like editing files and creating commits

## Getting started

To get started with Claude Code, follow our [installation guide](/en/docs/claude-code/getting-started) which covers system requirements, installation steps, and authentication process.

## Quick tour

Here's what you can accomplish with Claude Code:

### From questions to solutions in seconds

```bash
# Ask questions about your codebase
claude
> how does our authentication system work?

# Create a commit with one command
claude commit

# Fix issues across multiple files
claude "fix the type errors in the auth module"
```

### Understand unfamiliar code

```
> what does the payment processing system do?
> find where user permissions are checked
> explain how the caching layer works
```

### Automate Git operations

```
> commit my changes
> create a pr
> which commit added tests for markdown back in December?
> rebase on main and resolve any merge conflicts
```

## Next steps

<CardGroup>
  <Card title="Getting started" icon="rocket" href="/en/docs/claude-code/getting-started">
    Install Claude Code and get up and running
  </Card>

  <Card title="Core features" icon="star" href="/en/docs/claude-code/common-tasks">
    Explore what Claude Code can do for you
  </Card>

  <Card title="Commands" icon="terminal" href="/en/docs/claude-code/cli-usage">
    Learn about CLI commands and controls
  </Card>

  <Card title="Configuration" icon="gear" href="/en/docs/claude-code/settings">
    Customize Claude Code for your workflow
  </Card>
</CardGroup>

## Additional resources

<CardGroup>
  <Card title="Claude Code tutorials" icon="graduation-cap" href="/en/docs/claude-code/tutorials">
    Step-by-step guides for common tasks
  </Card>

  <Card title="Troubleshooting" icon="wrench" href="/en/docs/claude-code/troubleshooting">
    Solutions for common issues with Claude Code
  </Card>

  <Card title="Bedrock & Vertex integrations" icon="cloud" href="/en/docs/claude-code/bedrock-vertex-proxies">
    Configure Claude Code with Amazon Bedrock or Google Vertex AI
  </Card>

  <Card title="Reference implementation" icon="code" href="https://github.com/anthropics/claude-code/tree/main/.devcontainer">
    Clone our development container reference implementation.
  </Card>
</CardGroup>

## License and data usage

Claude Code is provided under Anthropic's [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms).

### How we use your data

We aim to be fully transparent about how we use your data. We may use feedback to improve our products and services, but we will not train generative models using your feedback from Claude Code. Given their potentially sensitive nature, we store user feedback transcripts for only 30 days.

#### Feedback transcripts

If you choose to send us feedback about Claude Code, such as transcripts of your usage, Anthropic may use that feedback to debug related issues and improve Claude Code's functionality (e.g., to reduce the risk of similar bugs occurring in the future). We will not train generative models using this feedback.

### Privacy safeguards

We have implemented several safeguards to protect your data, including limited retention periods for sensitive information, restricted access to user session data, and clear policies against using feedback for model training.

For full details, please review our [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms) and [Privacy Policy](https://www.anthropic.com/legal/privacy).

### License

© Anthropic PBC. All rights reserved. Use is subject to Anthropic's [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms).

Claude Code: Best practices for agentic coding
Published Apr 18, 2025
Claude Code is a command line tool for agentic coding. This post covers tips and tricks that have proven effective for using Claude Code across various codebases, languages, and environments. 
We recently released Claude Code, a command line tool for agentic coding. Developed as a research project, Claude Code gives Anthropic engineers and researchers a more native way to integrate Claude into their coding workflows.
Claude Code is intentionally low-level and unopinionated, providing close to raw model access without forcing specific workflows. This design philosophy creates a flexible, customizable, scriptable, and safe power tool. While powerful, this flexibility presents a learning curve for engineers new to agentic coding tools—at least until they develop their own best practices.
This post outlines general patterns that have proven effective, both for Anthropic's internal teams and for external engineers using Claude Code across various codebases, languages, and environments. Nothing in this list is set in stone nor universally applicable; consider these suggestions as starting points. We encourage you to experiment and find what works best for you!
Looking for more detailed information? Our comprehensive documentation at claude.ai/code covers all the features mentioned in this post and provides additional examples, implementation details, and advanced techniques.
1. Customize your setup
Claude Code is an agentic coding assistant that automatically pulls context into prompts. This context gathering consumes time and tokens, but you can optimize it through environment tuning.
a. Create CLAUDE.md files
CLAUDE.md is a special file that Claude automatically pulls into context when starting a conversation. This makes it an ideal place for documenting:
	• Common bash commands
	• Core files and utility functions
	• Code style guidelines
	• Testing instructions
	• Repository etiquette (e.g., branch naming, merge vs. rebase, etc.)
	• Developer environment setup (e.g., pyenv use, which compilers work)
	• Any unexpected behaviors or warnings particular to the project
	• Other information you want Claude to remember
There’s no required format for CLAUDE.md files. We recommend keeping them concise and human-readable. For example:
# Bash commands
- npm run build: Build the project
- npm run typecheck: Run the typechecker
# Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')
# Workflow
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
You can place CLAUDE.md files in several locations:
	• The root of your repo, or wherever you run claude from (the most common usage). Name it CLAUDE.md and check it into git so that you can share it across sessions and with your team (recommended), or name it CLAUDE.local.md and .gitignore it
	• Any parent of the directory where you run claude. This is most useful for monorepos, where you might run claude from root/foo, and have CLAUDE.md files in both root/CLAUDE.md and root/foo/CLAUDE.md. Both of these will be pulled into context automatically
	• Any child of the directory where you run claude. This is the inverse of the above, and in this case, Claude will pull in CLAUDE.md files on demand when you work with files in child directories
	• Your home folder (~/.claude/CLAUDE.md), which applies it to all your claude sessions
When you run the /init command, Claude will automatically generate a CLAUDE.md for you.
b. Tune your CLAUDE.md files
Your CLAUDE.md files become part of Claude’s prompts, so they should be refined like any frequently used prompt. A common mistake is adding extensive content without iterating on its effectiveness. Take time to experiment and determine what produces the best instruction following from the model.
You can add content to your CLAUDE.md manually or press the # key to give Claude an instruction that it will automatically incorporate into the relevant CLAUDE.md. Many engineers use # frequently to document commands, files, and style guidelines while coding, then include CLAUDE.md changes in commits so team members benefit as well.
At Anthropic, we occasionally run CLAUDE.md files through the prompt improver and often tune instructions (e.g. adding emphasis with "IMPORTANT" or "YOU MUST") to improve adherence.

c. Curate Claude's list of allowed tools
By default, Claude Code requests permission for any action that might modify your system: file writes, many bash commands, MCP tools, etc. We designed Claude Code with this deliberately conservative approach to prioritize safety. You can customize the allowlist to permit additional tools that you know are safe, or to allow potentially unsafe tools that are easy to undo (e.g., file editing, git commit).
There are four ways to manage allowed tools:
	• Select "Always allow" when prompted during a session.
	• Use the /permissions command after starting Claude Code to add or remove tools from the allowlist. For example, you can add Edit to always allow file edits, Bash(git commit:*) to allow git commits, or mcp__puppeteer__puppeteer_navigate to allow navigating with the Puppeteer MCP server.
	• Manually edit your .claude/settings.json or ~/.claude.json (we recommend checking the former into source control to share with your team).
	• Use the --allowedTools CLI flag for session-specific permissions.
d. If using GitHub, install the gh CLI
Claude knows how to use the gh CLI to interact with GitHub for creating issues, opening pull requests, reading comments, and more. Without gh installed, Claude can still use the GitHub API or MCP server (if you have it installed).
2. Give Claude more tools
Claude has access to your shell environment, where you can build up sets of convenience scripts and functions for it just like you would for yourself. It can also leverage more complex tools through MCP and REST APIs.
a. Use Claude with bash tools
Claude Code inherits your bash environment, giving it access to all your tools. While Claude knows common utilities like unix tools and gh, it won't know about your custom bash tools without instructions:
	1. Tell Claude the tool name with usage examples
	2. Tell Claude to run --help to see tool documentation
	3. Document frequently used tools in CLAUDE.md
b. Use Claude with MCP
Claude Code functions as both an MCP server and client. As a client, it can connect to any number of MCP servers to access their tools in three ways:
	• In project config (available when running Claude Code in that directory)
	• In global config (available in all projects)
	• In a checked-in .mcp.json file (available to anyone working in your codebase). For example, you can add Puppeteer and Sentry servers to your .mcp.json, so that every engineer working on your repo can use these out of the box.
When working with MCP, it can also be helpful to launch Claude with the --mcp-debug flag to help identify configuration issues.
c. Use custom slash commands
For repeated workflows—debugging loops, log analysis, etc.—store prompt templates in Markdown files within the .claude/commands folder. These become available through the slash commands menu when you type /. You can check these commands into git to make them available for the rest of your team.
Custom slash commands can include the special keyword $ARGUMENTS to pass parameters from command invocation.
For example, here’s a slash command that you could use to automatically pull and fix a Github issue:
Please analyze and fix the GitHub issue: $ARGUMENTS.
Follow these steps:
1. Use `gh issue view` to get the issue details
2. Understand the problem described in the issue
3. Search the codebase for relevant files
4. Implement the necessary changes to fix the issue
5. Write and run tests to verify the fix
6. Ensure code passes linting and type checking
7. Create a descriptive commit message
8. Push and create a PR
Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks.
Putting the above content into .claude/commands/fix-github-issue.md makes it available as the /project:fix-github-issue command in Claude Code. You could then for example use /project:fix-github-issue 1234 to have Claude fix issue #1234. Similarly, you can add your own personal commands to the ~/.claude/commands folder for commands you want available in all of your sessions.
3. Try common workflows
Claude Code doesn’t impose a specific workflow, giving you the flexibility to use it how you want. Within the space this flexibility affords, several successful patterns for effectively using Claude Code have emerged across our community of users:
a. Explore, plan, code, commit
This versatile workflow suits many problems:
	1. Ask Claude to read relevant files, images, or URLs, providing either general pointers ("read the file that handles logging") or specific filenames ("read logging.py"), but explicitly tell it not to write any code just yet.
		1. This is the part of the workflow where you should consider strong use of subagents, especially for complex problems. Telling Claude to use subagents to verify details or investigate particular questions it might have, especially early on in a conversation or task, tends to preserve context availability without much downside in terms of lost efficiency.
	2. Ask Claude to make a plan for how to approach a specific problem. We recommend using the word "think" to trigger extended thinking mode, which gives Claude additional computation time to evaluate alternatives more thoroughly. These specific phrases are mapped directly to increasing levels of thinking budget in the system: "think" < "think hard" < "think harder" < "ultrathink." Each level allocates progressively more thinking budget for Claude to use.
		1. If the results of this step seem reasonable, you can have Claude create a document or a GitHub issue with its plan so that you can reset to this spot if the implementation (step 3) isn’t what you want.
	3. Ask Claude to implement its solution in code. This is also a good place to ask it to explicitly verify the reasonableness of its solution as it implements pieces of the solution.
	4. Ask Claude to commit the result and create a pull request. If relevant, this is also a good time to have Claude update any READMEs or changelogs with an explanation of what it just did.
Steps #1-#2 are crucial—without them, Claude tends to jump straight to coding a solution. While sometimes that's what you want, asking Claude to research and plan first significantly improves performance for problems requiring deeper thinking upfront.
b. Write tests, commit; code, iterate, commit
This is an Anthropic-favorite workflow for changes that are easily verifiable with unit, integration, or end-to-end tests. Test-driven development (TDD) becomes even more powerful with agentic coding:
	1. Ask Claude to write tests based on expected input/output pairs. Be explicit about the fact that you’re doing test-driven development so that it avoids creating mock implementations, even for functionality that doesn’t exist yet in the codebase.
	2. Tell Claude to run the tests and confirm they fail. Explicitly telling it not to write any implementation code at this stage is often helpful.
	3. Ask Claude to commit the tests when you’re satisfied with them.
	4. Ask Claude to write code that passes the tests, instructing it not to modify the tests. Tell Claude to keep going until all tests pass. It will usually take a few iterations for Claude to write code, run the tests, adjust the code, and run the tests again.
		1. At this stage, it can help to ask it to verify with independent subagents that the implementation isn’t overfitting to the tests
	5. Ask Claude to commit the code once you’re satisfied with the changes.
Claude performs best when it has a clear target to iterate against—a visual mock, a test case, or another kind of output. By providing expected outputs like tests, Claude can make changes, evaluate results, and incrementally improve until it succeeds.
c. Write code, screenshot result, iterate
Similar to the testing workflow, you can provide Claude with visual targets:
	1. Give Claude a way to take browser screenshots (e.g., with the Puppeteer MCP server, an iOS simulator MCP server, or manually copy / paste screenshots into Claude).
	2. Give Claude a visual mock by copying / pasting or drag-dropping an image, or giving Claude the image file path.
	3. Ask Claude to implement the design in code, take screenshots of the result, and iterate until its result matches the mock.
	4. Ask Claude to commit when you're satisfied.
Like humans, Claude's outputs tend to improve significantly with iteration. While the first version might be good, after 2-3 iterations it will typically look much better. Give Claude the tools to see its outputs for best results.

d. Safe YOLO mode
Instead of supervising Claude, you can use claude --dangerously-skip-permissions to bypass all permission checks and let Claude work uninterrupted until completion. This works well for workflows like fixing lint errors or generating boilerplate code.
Letting Claude run arbitrary commands is risky and can result in data loss, system corruption, or even data exfiltration (e.g., via prompt injection attacks). To minimize these risks, use --dangerously-skip-permissions in a container without internet access. You can follow this reference implementation using Docker Dev Containers.
e. Codebase Q&A
When onboarding to a new codebase, use Claude Code for learning and exploration. You can ask Claude the same sorts of questions you would ask another engineer on the project when pair programming. Claude can agentically search the codebase to answer general questions like:
	• How does logging work?
	• How do I make a new API endpoint?
	• What does async move { ... } do on line 134 of foo.rs?
	• What edge cases does CustomerOnboardingFlowImpl handle?
	• Why are we calling foo() instead of bar() on line 333?
	• What’s the equivalent of line 334 of baz.py in Java?
At Anthropic, using Claude Code in this way has become our core onboarding workflow, significantly improving ramp-up time and reducing load on other engineers. No special prompting is required! Simply ask questions, and Claude will explore the code to find answers.

f. Use Claude to interact with git
Claude can effectively handle many git operations. Many Anthropic engineers use Claude for 90%+ of our git interactions:
	• Searching git history to answer questions like "What changes made it into v1.2.3?", "Who owns this particular feature?", or "Why was this API designed this way?" It helps to explicitly prompt Claude to look through git history to answer queries like these.
	• Writing commit messages. Claude will look at your changes and recent history automatically to compose a message taking all the relevant context into account
	• Handling complex git operations like reverting files, resolving rebase conflicts, and comparing and grafting patches
g. Use Claude to interact with GitHub
Claude Code can manage many GitHub interactions:
	• Creating pull requests: Claude understands the shorthand "pr" and will generate appropriate commit messages based on the diff and surrounding context.
	• Implementing one-shot resolutions for simple code review comments: just tell it to fix comments on your PR (optionally, give it more specific instructions) and push back to the PR branch when it's done.
	• Fixing failing builds or linter warnings
	• Categorizing and triaging open issues by asking Claude to loop over open GitHub issues
This eliminates the need to remember gh command line syntax while automating routine tasks.
h. Use Claude to work with Jupyter notebooks
Researchers and data scientists at Anthropic use Claude Code to read and write Jupyter notebooks. Claude can interpret outputs, including images, providing a fast way to explore and interact with data. There are no required prompts or workflows, but a workflow we recommend is to have Claude Code and a .ipynb file open side-by-side in VS Code.
You can also ask Claude to clean up or make aesthetic improvements to your Jupyter notebook before you show it to colleagues. Specifically telling it to make the notebook or its data visualizations “aesthetically pleasing” tends to help remind it that it’s optimizing for a human viewing experience.
4. Optimize your workflow
The suggestions below apply across all workflows:
a. Be specific in your instructions
Claude Code’s success rate improves significantly with more specific instructions, especially on first attempts. Giving clear directions upfront reduces the need for course corrections later.
For example:
Poor	Good
add tests for foo.py	write a new test case for foo.py, covering the edge case where the user is logged out. avoid mocks
why does ExecutionFactory have such a weird api?	look through ExecutionFactory's git history and summarize how its api came to be
add a calendar widget	look at how existing widgets are implemented on the home page to understand the patterns and specifically how code and interfaces are separated out. HotDogWidget.php is a good example to start with. then, follow the pattern to implement a new calendar widget that lets the user select a month and paginate forwards/backwards to pick a year. Build from scratch without libraries other than the ones already used in the rest of the codebase.
Claude can infer intent, but it can't read minds. Specificity leads to better alignment with expectations.

b. Give Claude images
Claude excels with images and diagrams through several methods:
	• Paste screenshots (pro tip: hit cmd+ctrl+shift+4 in macOS to screenshot to clipboard and ctrl+v to paste. Note that this is not cmd+v like you would usually use to paste on mac and does not work remotely.)
	• Drag and drop images directly into the prompt input
	• Provide file paths for images
This is particularly useful when working with design mocks as reference points for UI development, and visual charts for analysis and debugging. If you are not adding visuals to context, it can still be helpful to be clear with Claude about how important it is for the result to be visually appealing.
c. Mention files you want Claude to look at or work on
Use tab-completion to quickly reference files or folders anywhere in your repository, helping Claude find or update the right resources.

d. Give Claude URLs
Paste specific URLs alongside your prompts for Claude to fetch and read. To avoid permission prompts for the same domains (e.g., docs.foo.com), use /permissions to add domains to your allowlist.
e. Course correct early and often
While auto-accept mode (shift+tab to toggle) lets Claude work autonomously, you'll typically get better results by being an active collaborator and guiding Claude's approach. You can get the best results by thoroughly explaining the task to Claude at the beginning, but you can also course correct Claude at any time.
These four tools help with course correction:
	• Ask Claude to make a plan before coding. Explicitly tell it not to code until you’ve confirmed its plan looks good.
	• Press Escape to interrupt Claude during any phase (thinking, tool calls, file edits), preserving context so you can redirect or expand instructions.
	• Double-tap Escape to jump back in history, edit a previous prompt, and explore a different direction. You can edit the prompt and repeat until you get the result you're looking for.
	• Ask Claude to undo changes, often in conjunction with option #2 to take a different approach.
Though Claude Code occasionally solves problems perfectly on the first attempt, using these correction tools generally produces better solutions faster.
f. Use /clear to keep context focused
During long sessions, Claude's context window can fill with irrelevant conversation, file contents, and commands. This can reduce performance and sometimes distract Claude. Use the /clear command frequently between tasks to reset the context window.
g. Use checklists and scratchpads for complex workflows
For large tasks with multiple steps or requiring exhaustive solutions—like code migrations, fixing numerous lint errors, or running complex build scripts—improve performance by having Claude use a Markdown file (or even a GitHub issue!) as a checklist and working scratchpad:
For example, to fix a large number of lint issues, you can do the following:
	1. Tell Claude to run the lint command and write all resulting errors (with filenames and line numbers) to a Markdown checklist
	2. Instruct Claude to address each issue one by one, fixing and verifying before checking it off and moving to the next
h. Pass data into Claude
Several methods exist for providing data to Claude:
	• Copy and paste directly into your prompt (most common approach)
	• Pipe into Claude Code (e.g., cat foo.txt | claude), particularly useful for logs, CSVs, and large data
	• Tell Claude to pull data via bash commands, MCP tools, or custom slash commands
	• Ask Claude to read files or fetch URLs (works for images too)
Most sessions involve a combination of these approaches. For example, you can pipe in a log file, then tell Claude to use a tool to pull in additional context to debug the logs.
5. Use headless mode to automate your infra
Claude Code includes headless mode for non-interactive contexts like CI, pre-commit hooks, build scripts, and automation. Use the -p flag with a prompt to enable headless mode, and --output-format stream-json for streaming JSON output.
Note that headless mode does not persist between sessions. You have to trigger it each session.
a. Use Claude for issue triage
Headless mode can power automations triggered by GitHub events, such as when a new issue is created in your repository. For example, the public Claude Code repository uses Claude to inspect new issues as they come in and assign appropriate labels.
b. Use Claude as a linter
Claude Code can provide subjective code reviews beyond what traditional linting tools detect, identifying issues like typos, stale comments, misleading function or variable names, and more.
6. Uplevel with multi-Claude workflows
Beyond standalone usage, some of the most powerful applications involve running multiple Claude instances in parallel:
a. Have one Claude write code; use another Claude to verify
A simple but effective approach is to have one Claude write code while another reviews or tests it. Similar to working with multiple engineers, sometimes having separate context is beneficial:
	1. Use Claude to write code
	2. Run /clear or start a second Claude in another terminal
	3. Have the second Claude review the first Claude's work
	4. Start another Claude (or /clear again) to read both the code and review feedback
	5. Have this Claude edit the code based on the feedback
You can do something similar with tests: have one Claude write tests, then have another Claude write code to make the tests pass. You can even have your Claude instances communicate with each other by giving them separate working scratchpads and telling them which one to write to and which one to read from.
This separation often yields better results than having a single Claude handle everything.
b. Have multiple checkouts of your repo
Rather than waiting for Claude to complete each step, something many engineers at Anthropic do is:
	1. Create 3-4 git checkouts in separate folders
	2. Open each folder in separate terminal tabs
	3. Start Claude in each folder with different tasks
	4. Cycle through to check progress and approve/deny permission requests
c. Use git worktrees
This approach shines for multiple independent tasks, offering a lighter-weight alternative to multiple checkouts. Git worktrees allow you to check out multiple branches from the same repository into separate directories. Each worktree has its own working directory with isolated files, while sharing the same Git history and reflog.
Using git worktrees enables you to run multiple Claude sessions simultaneously on different parts of your project, each focused on its own independent task. For instance, you might have one Claude refactoring your authentication system while another builds a completely unrelated data visualization component. Since the tasks don't overlap, each Claude can work at full speed without waiting for the other's changes or dealing with merge conflicts:
	1. Create worktrees: git worktree add ../project-feature-a feature-a
	2. Launch Claude in each worktree: cd ../project-feature-a && claude
	3. Create additional worktrees as needed (repeat steps 1-2 in new terminal tabs)
Some tips:
	• Use consistent naming conventions
	• Maintain one terminal tab per worktree
	• If you’re using iTerm2 on Mac, set up notifications for when Claude needs attention
	• Use separate IDE windows for different worktrees
	• Clean up when finished: git worktree remove ../project-feature-a
d. Use headless mode with a custom harness
claude -p (headless mode) integrates Claude Code programmatically into larger workflows while leveraging its built-in tools and system prompt. There are two primary patterns for using headless mode:
1. Fanning out handles large migrations or analyses (e.g., analyzing sentiment in hundreds of logs or analyzing thousands of CSVs):
	1. Have Claude write a script to generate a task list. For example, generate a list of 2k files that need to be migrated from framework A to framework B.
	2. Loop through tasks, calling Claude programmatically for each and giving it a task and a set of tools it can use. For example: claude -p “migrate foo.py from React to Vue. When you are done, you MUST return the string OK if you succeeded, or FAIL if the task failed.” --allowedTools Edit Bash(git commit:*)
	3. Run the script several times and refine your prompt to get the desired outcome.
2. Pipelining integrates Claude into existing data/processing pipelines:
	1. Call claude -p “<your prompt>” --json | your_command, where your_command is the next step of your processing pipeline
	2. That’s it! JSON output (optional) can help provide structure for easier automated processing.
For both of these use cases, it can be helpful to use the --verbose flag for debugging the Claude invocation. We generally recommend turning verbose mode off in production for cleaner output.
What are your tips and best practices for working with Claude Code? Tag @AnthropicAI so we can see what you're building!

From <https://www.anthropic.com/engineering/claude-code-best-practices> 



# Getting started with Claude Code

> Learn how to install, authenticate, and start using Claude Code.

## Check system requirements

* **Operating Systems**: macOS 10.15+, Ubuntu 20.04+/Debian 10+, or Windows via WSL
* **Hardware**: 4GB RAM minimum
* **Software**:
  * Node.js 18+
  * [git](https://git-scm.com/downloads) 2.23+ (optional)
  * [GitHub](https://cli.github.com/) or [GitLab](https://gitlab.com/gitlab-org/cli) CLI for PR workflows (optional)
  * [ripgrep](https://github.com/BurntSushi/ripgrep?tab=readme-ov-file#installation) (rg) for enhanced file search (optional)
* **Network**: Internet connection required for authentication and AI processing
* **Location**: Available only in [supported countries](https://www.anthropic.com/supported-countries)

<Note>
  **Troubleshooting WSL installation**

  Currently, Claude Code does not run directly in Windows, and instead requires WSL. If you encounter issues in WSL:

  1. **OS/platform detection issues**: If you receive an error during installation, WSL may be using Windows `npm`. Try:

     * Run `npm config set os linux` before installation
     * Install with `npm install -g @anthropic-ai/claude-code --force --no-os-check` (Do NOT use `sudo`)

  2. **Node not found errors**: If you see `exec: node: not found` when running `claude`, your WSL environment may be using a Windows installation of Node.js. You can confirm this with `which npm` and `which node`, which should point to Linux paths starting with `/usr/` rather than `/mnt/c/`. To fix this, try installing Node via your Linux distribution's package manager or via [`nvm`](https://github.com/nvm-sh/nvm).
</Note>

## Install and authenticate

<Steps>
  <Step title="Install Claude Code">
    Install [NodeJS 18+](https://nodejs.org/en/download), then run:

    ```sh
    npm install -g @anthropic-ai/claude-code
    ```

    <Warning>
      Do NOT use `sudo npm install -g` as this can lead to permission issues and
      security risks. If you encounter permission errors, see [configure Claude
      Code](/en/docs/claude-code/troubleshooting#linux-permission-issues) for recommended solutions.
    </Warning>
  </Step>

  <Step title="Navigate to your project">
    ```bash
    cd your-project-directory 
    ```
  </Step>

  <Step title="Start Claude Code">
    ```bash
    claude
    ```
  </Step>

  <Step title="Complete authentication">
    Claude Code offers multiple authentication options:

    1. **Anthropic Console**: The default option. Connect through the Anthropic Console and
       complete the OAuth process. Requires active billing at [console.anthropic.com](https://console.anthropic.com).
    2. **Claude App (with Pro or Max plan)**: Subscribe to Claude's [Pro or Max plan](https://www.anthropic.com/pricing) for a unified subscription that includes both Claude Code and the web interface. Get more value at the same price point while managing your account in one place. Log in with your Claude.ai account. During launch, choose the option that matches your subscription type.
    3. **Enterprise platforms**: Configure Claude Code to use
       [Amazon Bedrock or Google Vertex AI](/en/docs/claude-code/bedrock-vertex-proxies)
       for enterprise deployments with your existing cloud infrastructure.
  </Step>
</Steps>

## Initialize your project

For first-time users, we recommend:

<Steps>
  <Step title="Start Claude Code">
    ```bash
    claude
    ```
  </Step>

  <Step title="Run a simple command">
    ```bash
    summarize this project
    ```
  </Step>

  <Step title="Generate a CLAUDE.md project guide">
    ```bash
    /init 
    ```
  </Step>

  <Step title="Commit the generated CLAUDE.md file">
    Ask Claude to commit the generated CLAUDE.md file to your repository.
  </Step>
</Steps>



# Core tasks and workflows

> Explore Claude Code's powerful features for editing, searching, testing, and automating your development workflow.

Claude Code operates directly in your terminal, understanding your project
context and taking real actions. No need to manually add files to context -
Claude will explore your codebase as needed.

## Understand unfamiliar code

```
> what does the payment processing system do?
> find where user permissions are checked
> explain how the caching layer works
```

## Automate Git operations

```
> commit my changes
> create a pr
> which commit added tests for markdown back in December?
> rebase on main and resolve any merge conflicts
```

## Edit code intelligently

```
> add input validation to the signup form
> refactor the logger to use the new API
> fix the race condition in the worker queue
```

## Test and debug your code

```
> run tests for the auth module and fix failures
> find and fix security vulnerabilities
> explain why this test is failing
```

## Encourage deeper thinking

For complex problems, explicitly ask Claude to think more deeply:

```
> think about how we should architect the new payment service
> think hard about the edge cases in our authentication flow
```

Claude Code will show when the model is using extended thinking. You can
proactively prompt Claude to "think" or "think deeply" for more
planning-intensive tasks. We suggest that you first tell Claude about your task
and let it gather context from your project. Then, ask it to "think" to create a
plan.

<Tip>
  Claude will think more based on the words you use. For example, "think hard" will trigger more extended thinking than saying "think" alone.

  For more tips, see
  [Extended thinking tips](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips).
</Tip>

## Automate CI and infra workflows

Claude Code comes with a non-interactive mode for headless execution. This is
especially useful for running Claude Code in non-interactive contexts like
scripts, pipelines, and Github Actions.

Use `--print` (`-p`) to run Claude in non-interactive mode. In this mode, you
can set the `ANTHROPIC_API_KEY` environment variable to provide a custom API
key.

Non-interactive mode is especially useful when you pre-configure the set of
commands Claude is allowed to use:

```sh
export ANTHROPIC_API_KEY=sk_...
claude -p "update the README with the latest changes" --allowedTools "Bash(git diff:*)" "Bash(git log:*)" Write --disallowedTools ...
```



# CLI usage and controls

> Learn how to use Claude Code from the command line, including CLI commands, flags, and slash commands.

## Getting started

Claude Code provides two main ways to interact:

* **Interactive mode**: Run `claude` to start a REPL session
* **One-shot mode**: Use `claude -p "query"` for quick commands

```bash
# Start interactive mode
claude

# Start with an initial query
claude "explain this project"

# Run a single command and exit
claude -p "what does this function do?"

# Process piped content
cat logs.txt | claude -p "analyze these errors"
```

## CLI commands

| Command                            | Description                              | Example                                                                                          |
| :--------------------------------- | :--------------------------------------- | :----------------------------------------------------------------------------------------------- |
| `claude`                           | Start interactive REPL                   | `claude`                                                                                         |
| `claude "query"`                   | Start REPL with initial prompt           | `claude "explain this project"`                                                                  |
| `claude -p "query"`                | Run one-off query, then exit             | `claude -p "explain this function"`                                                              |
| `cat file \| claude -p "query"`    | Process piped content                    | `cat logs.txt \| claude -p "explain"`                                                            |
| `claude -c`                        | Continue most recent conversation        | `claude -c`                                                                                      |
| `claude -c -p "query"`             | Continue in print mode                   | `claude -c -p "Check for type errors"`                                                           |
| `claude -r "<session-id>" "query"` | Resume session by ID                     | `claude -r "abc123" "Finish this PR"`                                                            |
| `claude update`                    | Update to latest version                 | `claude update`                                                                                  |
| `claude mcp`                       | Configure Model Context Protocol servers | [See MCP section in tutorials](/en/docs/claude-code/tutorials#set-up-model-context-protocol-mcp) |

## CLI flags

Customize Claude Code's behavior with these command-line flags:

| Flag                             | Description                                                                                                                                              | Example                                                    |
| :------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------- |
| `--allowedTools`                 | A list of tools that should be allowed without prompting the user for permission, in addition to [settings.json files](/en/docs/claude-code/settings)    | `"Bash(git log:*)" "Bash(git diff:*)" "Write"`             |
| `--disallowedTools`              | A list of tools that should be disallowed without prompting the user for permission, in addition to [settings.json files](/en/docs/claude-code/settings) | `"Bash(git log:*)" "Bash(git diff:*)" "Write"`             |
| `--print`, `-p`                  | Print response without interactive mode (see [SDK documentation](/en/docs/claude-code/sdk) for programmatic usage details)                               | `claude -p "query"`                                        |
| `--output-format`                | Specify output format for print mode (options: `text`, `json`, `stream-json`)                                                                            | `claude -p "query" --output-format json`                   |
| `--verbose`                      | Enable verbose logging, shows full turn-by-turn output (helpful for debugging in both print and interactive modes)                                       | `claude --verbose`                                         |
| `--max-turns`                    | Limit the number of agentic turns in non-interactive mode                                                                                                | `claude -p --max-turns 3 "query"`                          |
| `--model`                        | Sets the model for the current session with an alias for the latest model (`sonnet` or `opus`) or a model's full name                                    | `claude --model claude-sonnet-4-20250514`                  |
| `--permission-prompt-tool`       | Specify an MCP tool to handle permission prompts in non-interactive mode                                                                                 | `claude -p --permission-prompt-tool mcp_auth_tool "query"` |
| `--resume`                       | Resume a specific session by ID, or by choosing in interactive mode                                                                                      | `claude --resume abc123 "query"`                           |
| `--continue`                     | Load the most recent conversation in the current directory                                                                                               | `claude --continue`                                        |
| `--dangerously-skip-permissions` | Skip permission prompts (use with caution)                                                                                                               | `claude --dangerously-skip-permissions`                    |

<Tip>
  The `--output-format json` flag is particularly useful for scripting and
  automation, allowing you to parse Claude's responses programmatically.
</Tip>

For detailed information about print mode (`-p`) including output formats,
streaming, verbose logging, and programmatic usage, see the
[SDK documentation](/en/docs/claude-code/sdk).

## Slash commands

Control Claude's behavior during an interactive session:

| Command                   | Purpose                                                               |
| :------------------------ | :-------------------------------------------------------------------- |
| `/bug`                    | Report bugs (sends conversation to Anthropic)                         |
| `/clear`                  | Clear conversation history                                            |
| `/compact [instructions]` | Compact conversation with optional focus instructions                 |
| `/config`                 | View/modify configuration                                             |
| `/cost`                   | Show token usage statistics                                           |
| `/doctor`                 | Checks the health of your Claude Code installation                    |
| `/help`                   | Get usage help                                                        |
| `/init`                   | Initialize project with CLAUDE.md guide                               |
| `/login`                  | Switch Anthropic accounts                                             |
| `/logout`                 | Sign out from your Anthropic account                                  |
| `/memory`                 | Edit CLAUDE.md memory files                                           |
| `/model`                  | Select or change the AI model                                         |
| `/permissions`            | View or update [permissions](settings#permissions)                    |
| `/pr_comments`            | View pull request comments                                            |
| `/review`                 | Request code review                                                   |
| `/status`                 | View account and system statuses                                      |
| `/terminal-setup`         | Install Shift+Enter key binding for newlines (iTerm2 and VSCode only) |
| `/vim`                    | Enter vim mode for alternating insert and command modes               |

## Special shortcuts

### Quick memory with `#`

Add memories instantly by starting your input with `#`:

```
# Always use descriptive variable names
```

You'll be prompted to select which memory file to store this in.

### Line breaks in terminal

Enter multiline commands using:

* **Quick escape**: Type `\` followed by Enter
* **Keyboard shortcut**: Option+Enter (or Shift+Enter if configured)

To set up Option+Enter in your terminal:

**For Mac Terminal.app:**

1. Open Settings → Profiles → Keyboard
2. Check "Use Option as Meta Key"

**For iTerm2 and VSCode terminal:**

1. Open Settings → Profiles → Keys
2. Under General, set Left/Right Option key to "Esc+"

**Tip for iTerm2 and VSCode users**: Run `/terminal-setup` within Claude Code to
automatically configure Shift+Enter as a more intuitive alternative.

See [terminal setup in settings](/en/docs/claude-code/settings#line-breaks) for
configuration details.

## Vim Mode

Claude Code supports a subset of Vim keybindings that can be enabled with `/vim`
or configured via `/config`.

The supported subset includes:

* Mode switching: `Esc` (to NORMAL), `i`/`I`, `a`/`A`, `o`/`O` (to INSERT)
* Navigation: `h`/`j`/`k`/`l`, `w`/`e`/`b`, `0`/`$`/`^`, `gg`/`G`
* Editing: `x`, `dw`/`de`/`db`/`dd`/`D`, `cw`/`ce`/`cb`/`cc`/`C`, `.` (repeat)


# IDE integrations

> Integrate Claude Code with your favorite development environments

Claude Code seamlessly integrates with popular Integrated Development
Environments (IDEs) to enhance your coding workflow. This integration allows you
to leverage Claude's capabilities directly within your preferred development
environment.

## Supported IDEs

Claude Code currently supports two major IDE families:

* **Visual Studio Code** (including popular forks like Cursor and Windsurf)
* **JetBrains IDEs** (including PyCharm, WebStorm, IntelliJ, and GoLand)

## Features

* **Quick launch**: Use `Cmd+Esc` (Mac) or `Ctrl+Esc` (Windows/Linux) to open
  Claude Code directly from your editor, or click the Claude Code button in the
  UI
* **Diff viewing**: Code changes can be displayed directly in the IDE diff
  viewer instead of the terminal. You can configure this in `/config`
* **Selection context**: The current selection/tab in the IDE is automatically
  shared with Claude Code
* **File reference shortcuts**: Use `Cmd+Option+K` (Mac) or `Alt+Ctrl+K`
  (Linux/Windows) to insert file references (e.g., @File#L1-99)
* **Diagnostic sharing**: Diagnostic errors (lint, syntax, etc.) from the IDE
  are automatically shared with Claude as you work

## Installation

### VS Code

1. Open VSCode
2. Open the integrated terminal
3. Run `claude` - the extension will auto-install

Going forward you can also use the `/ide` command in any external terminal to
connect to the IDE.

<Note>
  These installation instructions also apply to VS Code forks like Cursor and
  Windsurf.
</Note>

### JetBrains IDEs

Install the
[Claude Code plugin](https://docs.anthropic.com/s/claude-code-jetbrains) from
the marketplace and restart your IDE.

<Note>
  The plugin may also be auto-installed when you run `claude` in the integrated
  terminal. The IDE must be restarted completely to take effect.
</Note>

<Warning>
  **Remote Development Limitations**: When using JetBrains Remote Development,
  you must install the plugin in the remote host via `Settings > Plugin (Host)`.
</Warning>

## Configuration

Both integrations work with Claude Code's configuration system. To enable
IDE-specific features:

1. Connect Claude Code to your IDE by running `claude` in the built-in terminal
2. Run the `/config` command
3. Set the diff tool to `auto` for automatic IDE detection
4. Claude Code will automatically use the appropriate viewer based on your IDE

If you're using an external terminal (not the IDE's built-in terminal), you can
still connect to your IDE by using the `/ide` command after launching Claude
Code. This allows you to benefit from IDE integration features even when running
Claude from a separate terminal application. This works for both VS Code and
JetBrains IDEs.

<Note>
  When using an external terminal, to ensure Claude has default access to the
  same files as your IDE, start Claude from the same directory as your IDE
  project root.
</Note>

## Troubleshooting

### VS Code extension not installing

* Ensure you're running Claude Code from VS Code's integrated terminal
* Ensure that the CLI corresponding to your IDE is installed:
  * For VS Code: `code` command should be available
  * For Cursor: `cursor` command should be available
  * For Windsurf: `windsurf` command should be available
  * If not installed, use `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
    and search for "Shell Command: Install 'code' command in PATH" (or the
    equivalent for your IDE)
* Check that VS Code has permission to install extensions

### JetBrains plugin not working

* Ensure you're running Claude Code from the project root directory
* Check that the JetBrains plugin is enabled in the IDE settings
* Completely restart the IDE. You may need to do this multiple times
* For JetBrains Remote Development, ensure that the Claude Code plugin is
  installed in the remote host and not locally on the client

For additional help, refer to our
[troubleshooting guide](/en/docs/claude-code/troubleshooting) or reach out to
support.



# Manage Claude's memory

> Learn how to manage Claude Code's memory across sessions with different memory locations and best practices.

Claude Code can remember your preferences across sessions, like style guidelines and common commands in your workflow.

## Determine memory type

Claude Code offers three memory locations, each serving a different purpose:

| Memory Type                | Location              | Purpose                                  | Use Case Examples                                                |
| -------------------------- | --------------------- | ---------------------------------------- | ---------------------------------------------------------------- |
| **Project memory**         | `./CLAUDE.md`         | Team-shared instructions for the project | Project architecture, coding standards, common workflows         |
| **User memory**            | `~/.claude/CLAUDE.md` | Personal preferences for all projects    | Code styling preferences, personal tooling shortcuts             |
| **Project memory (local)** | `./CLAUDE.local.md`   | Personal project-specific preferences    | *(Deprecated, see below)* Your sandbox URLs, preferred test data |

All memory files are automatically loaded into Claude Code's context when launched.

## CLAUDE.md imports

CLAUDE.md files can import additional files using `@path/to/import` syntax. The following example imports 3 files:

```
See @README for project overview and @package.json for available npm commands for this project.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

Both relative and absolute paths are allowed. In particular, importing files in user's home dir is a convenient way for your team members to provide individual instructions that are not checked into the repository. Previously CLAUDE.local.md served a similar purpose, but is now deprecated in favor of imports since they work better across multiple git worktrees.

```
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

To avoid potential collisions, imports are not evaluated inside markdown code spans and code blocks.

```
This code span will not be treated as an import: `@anthropic-ai/claude-code`
```

Imported files can recursively import additional files, with a max-depth of 5 hops. You can see what memory files are loaded by running `/memory` command.

## How Claude looks up memories

Claude Code reads memories recursively: starting in the cwd, Claude Code recurses up to */* and reads any CLAUDE.md or CLAUDE.local.md files it finds. This is especially convenient when working in large repositories where you run Claude Code in *foo/bar/*, and have memories in both *foo/CLAUDE.md* and *foo/bar/CLAUDE.md*.

Claude will also discover CLAUDE.md nested in subtrees under your current working directory. Instead of loading them at launch, they are only included when Claude reads files in those subtrees.

## Quickly add memories with the `#` shortcut

The fastest way to add a memory is to start your input with the `#` character:

```
# Always use descriptive variable names
```

You'll be prompted to select which memory file to store this in.

## Directly edit memories with `/memory`

Use the `/memory` slash command during a session to open any memory file in your system editor for more extensive additions or organization.

## Memory best practices

* **Be specific**: "Use 2-space indentation" is better than "Format code properly".
* **Use structure to organize**: Format each individual memory as a bullet point and group related memories under descriptive markdown headings.
* **Review periodically**: Update memories as your project evolves to ensure Claude is always using the most up to date information and context.



# Claude Code settings

> Learn how to configure Claude Code with global and project-level settings, themes, and environment variables.

Claude Code offers a variety of settings to configure its behavior to meet your
needs. You can configure Claude Code by running the `/config` command when using
the interactive REPL.

## Settings files

The new `settings.json` file format is our official mechanism for configuring Claude
Code through hierarchical settings:

* **User settings** are defined in `~/.claude/settings.json` and apply to all
  projects.
* **Project settings** are saved in your project directory under
  `.claude/settings.json` for shared settings, and `.claude/settings.local.json`
  for local project settings. Claude Code will configure git to ignore
  `.claude/settings.local.json` when it is created.
* For enterprise deployments of Claude Code, we also support **enterprise
  managed policy settings**. These take precedence over user and project
  settings. System administrators can deploy policies to
  `/Library/Application Support/ClaudeCode/policies.json` on macOS and
  `/etc/claude-code/policies.json` on Linux and Windows via WSL.

```JSON Example settings.json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test:*)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl:*)"
    ]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp"
  }
}
```

### Available settings

`settings.json` supports a number of options:

| Key                   | Description                                                                                                                                                                                                    | Example                               |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------ |
| `apiKeyHelper`        | Custom script, to be executed in `/bin/sh`, to generate an auth value. This value will generally be sent as `X-Api-Key`, `Authorization: Bearer`, and `Proxy-Authorization: Bearer` headers for model requests | `/bin/generate_temp_api_key.sh`       |
| `cleanupPeriodDays`   | How long to locally retain chat transcripts (default: 30 days)                                                                                                                                                 | `20`                                  |
| `env`                 | Environment variables that will be applied to every session                                                                                                                                                    | `{"FOO": "bar"}`                      |
| `includeCoAuthoredBy` | Whether to include the `co-authored-by Claude` byline in git commits and pull requests (default: `true`)                                                                                                       | `false`                               |
| `permissions`         | `allow` and `deny` keys are a list of [permission rules](#permissions)                                                                                                                                         | `{"allow": [ "Bash(npm run lint)" ]}` |

### Settings precedence

Settings are applied in order of precedence:

1. Enterprise policies
2. Command line arguments
3. Local project settings
4. Shared project settings
5. User settings

## Permissions

You can view & manage Claude Code's tool permissions with `/permissions`. This UI
lists all permission rules and the settings.json file they are sourced from.

* **Allow** rules will allow Claude Code to use the specified tool without
  further manual approval.
* **Deny** rules will prevent Claude Code from using the specified tool. Deny
  rules take precedence over allow rules.

Permission rules use the format: `Tool(optional-specifier)`

A rule that is just the tool name matched any use of that tool.
For example, adding `Bash` to the list of allow rules would allow Claude Code to use
the Bash tool without requiring user approval. See the list of
[tools available to Claude](security#tools-available-to-claude).

### Tool-specific permission rules

Some tools use the optional specifier for more fine-grained permission controls.
For example, an allow rule with `Bash(git diff:*)` would allow Bash commands
that start with `git diff`. The following tools support permission rules with specifiers:

#### Bash

* `Bash(npm run build)` Matches the exact Bash command `npm run build`
* `Bash(npm run test:*)` Matches Bash commands starting with `npm run test`.

<Tip>
  Claude Code is aware of shell operators (like `&&`) so a prefix match rule
  like `Bash(safe-cmd:*)` won't give it permission to run the command `safe-cmd
  && other-cmd`
</Tip>

#### Read & Edit

`Edit` rules apply to all built-in tools that edit files.
Claude will make a best-effort attempt to apply `Read` rules to
all built-in tools that read files like Grep, Glob, and LS.

Read & Edit rules both follow the
[gitignore](https://git-scm.com/docs/gitignore) specification. Patterns are
resolved relative to the directory containing `.claude/settings.json`. To
reference an absolute path, use `//`. For a path relative to your home
directory, use `~/`.

* `Edit(docs/**)` Matches edits to files in the `docs` directory of your project
* `Read(~/.zshrc)` Matches reads to your `~/.zshrc` file
* `Edit(//tmp/scratch.txt)` Matches edits to `/tmp/scratch.txt`

#### WebFetch

* `WebFetch(domain:example.com)` Matches fetch requests to example.com

#### MCP

* `mcp__puppeteer` Matches any tool provided by the `puppeteer` server (name configured in Claude Code)
* `mcp__puppeteer__puppeteer_navigate` Matches the `puppeteer_navigate` tool provided by the `puppeteer` server

## Auto-updater permission options

When Claude Code detects that it doesn't have sufficient permissions to write to
your global npm prefix directory (required for automatic updates), you'll see a
warning that points to this documentation page. For detailed solutions to
auto-updater issues, see the
[troubleshooting guide](/en/docs/claude-code/troubleshooting#auto-updater-issues).

### Recommended: Create a new user-writable npm prefix

```bash
# First, save a list of your existing global packages for later migration
npm list -g --depth=0 > ~/npm-global-packages.txt

# Create a directory for your global packages
mkdir -p ~/.npm-global

# Configure npm to use the new directory path
npm config set prefix ~/.npm-global

# Note: Replace ~/.bashrc with ~/.zshrc, ~/.profile, or other appropriate file for your shell
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc

# Apply the new PATH setting
source ~/.bashrc

# Now reinstall Claude Code in the new location
npm install -g @anthropic-ai/claude-code

# Optional: Reinstall your previous global packages in the new location
# Look at ~/npm-global-packages.txt and install packages you want to keep
# npm install -g package1 package2 package3...
```

**Why we recommend this option:**

* Avoids modifying system directory permissions
* Creates a clean, dedicated location for your global npm packages
* Follows security best practices

Since Claude Code is actively developing, we recommend setting up auto-updates
using the recommended option above.

### Disabling the auto-updater

If you prefer to disable the auto-updater instead of fixing permissions, you can
set the `DISABLE_AUTOUPDATER` [environment variable](#environment-variables) to `1`

## Optimize your terminal setup

Claude Code works best when your terminal is properly configured. Follow these
guidelines to optimize your experience.

**Supported shells**:

* Bash
* Zsh
* Fish

### Themes and appearance

Claude cannot control the theme of your terminal. That's handled by your
terminal application. You can match Claude Code's theme to your terminal during
onboarding or any time via the `/config` command

### Line breaks

You have several options for entering linebreaks into Claude Code:

* **Quick escape**: Type `\` followed by Enter to create a newline
* **Keyboard shortcut**: Press Option+Enter (Meta+Enter) with proper
  configuration

To set up Option+Enter in your terminal:

**For Mac Terminal.app:**

1. Open Settings → Profiles → Keyboard
2. Check "Use Option as Meta Key"

**For iTerm2 and VSCode terminal:**

1. Open Settings → Profiles → Keys
2. Under General, set Left/Right Option key to "Esc+"

**Tip for iTerm2 and VSCode users**: Run `/terminal-setup` within Claude Code to
automatically configure Shift+Enter as a more intuitive alternative.

### Notification setup

Never miss when Claude completes a task with proper notification configuration:

#### Terminal bell notifications

Enable sound alerts when tasks complete:

```sh
claude config set --global preferredNotifChannel terminal_bell
```

**For macOS users**: Don't forget to enable notification permissions in System
Settings → Notifications → \[Your Terminal App].

#### iTerm 2 system notifications

For iTerm 2 alerts when tasks complete:

1. Open iTerm 2 Preferences
2. Navigate to Profiles → Terminal
3. Enable "Silence bell" and Filter Alerts → "Send escape sequence-generated
   alerts"
4. Set your preferred notification delay

Note that these notifications are specific to iTerm 2 and not available in the
default macOS Terminal.

### Handling large inputs

When working with extensive code or long instructions:

* **Avoid direct pasting**: Claude Code may struggle with very long pasted
  content
* **Use file-based workflows**: Write content to a file and ask Claude to read
  it
* **Be aware of VS Code limitations**: The VS Code terminal is particularly
  prone to truncating long pastes

### Vim Mode

Claude Code supports a subset of Vim keybindings that can be enabled with `/vim`
or configured via `/config`.

The supported subset includes:

* Mode switching: `Esc` (to NORMAL), `i`/`I`, `a`/`A`, `o`/`O` (to INSERT)
* Navigation: `h`/`j`/`k`/`l`, `w`/`e`/`b`, `0`/`$`/`^`, `gg`/`G`
* Editing: `x`, `dw`/`de`/`db`/`dd`/`D`, `cw`/`ce`/`cb`/`cc`/`C`, `.` (repeat)

## Environment variables

Claude Code supports the following environment variables to control its
behavior:

<Note>
  All environment variables can also be configured in
  [`settings.json`](#available-settings). This is
  useful as a way to automatically set environment variables for each session,
  or to roll out a set of environment variables for your whole team or
  organization.
</Note>

| Variable                                   | Purpose                                                                                                                                |
| :----------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| `ANTHROPIC_API_KEY`                        | API key sent as `X-Api-Key` header, typically for the Claude SDK (for interactive usage, run `/login`)                                 |
| `ANTHROPIC_AUTH_TOKEN`                     | Custom value for the `Authorization` and `Proxy-Authorization` headers (the value you set here will be prefixed with `Bearer `)        |
| `ANTHROPIC_CUSTOM_HEADERS`                 | Custom headers you want to add to the request (in `Name: Value` format)                                                                |
| `ANTHROPIC_MODEL`                          | Name of custom model to use (see [Model Configuration](/en/docs/claude-code/bedrock-vertex-proxies#model-configuration))               |
| `ANTHROPIC_SMALL_FAST_MODEL`               | Name of [Haiku-class model for background tasks](/en/docs/claude-code/costs)                                                           |
| `BASH_DEFAULT_TIMEOUT_MS`                  | Default timeout for long-running bash commands                                                                                         |
| `BASH_MAX_TIMEOUT_MS`                      | Maximum timeout the model can set for long-running bash commands                                                                       |
| `BASH_MAX_OUTPUT_LENGTH`                   | Maximum number of characters in bash outputs before they are middle-truncated                                                          |
| `CLAUDE_CODE_API_KEY_HELPER_TTL_MS`        | Interval in milliseconds at which credentials should be refreshed (when using `apiKeyHelper`)                                          |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS`            | Set the maximum number of output tokens for most requests                                                                              |
| `CLAUDE_CODE_USE_BEDROCK`                  | Use Bedrock (see [Bedrock & Vertex](/en/docs/claude-code/bedrock-vertex-proxies))                                                      |
| `CLAUDE_CODE_USE_VERTEX`                   | Use Vertex (see [Bedrock & Vertex](/en/docs/claude-code/bedrock-vertex-proxies))                                                       |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH`            | Skip AWS authentication for Bedrock (e.g. when using an LLM gateway)                                                                   |
| `CLAUDE_CODE_SKIP_VERTEX_AUTH`             | Skip Google authentication for Vertex (e.g. when using an LLM gateway)                                                                 |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Equivalent of setting `DISABLE_AUTOUPDATER`, `DISABLE_BUG_COMMAND`, `DISABLE_ERROR_REPORTING`, and `DISABLE_TELEMETRY`                 |
| `DISABLE_AUTOUPDATER`                      | Set to `1` to disable the automatic updater                                                                                            |
| `DISABLE_BUG_COMMAND`                      | Set to `1` to disable the `/bug` command                                                                                               |
| `DISABLE_COST_WARNINGS`                    | Set to `1` to disable cost warning messages                                                                                            |
| `DISABLE_ERROR_REPORTING`                  | Set to `1` to opt out of Sentry error reporting                                                                                        |
| `DISABLE_NON_ESSENTIAL_MODEL_CALLS`        | Set to `1` to disable model calls for non-critical paths like flavor text                                                              |
| `DISABLE_TELEMETRY`                        | Set to `1` to opt out of Statsig telemetry (note that Statsig events do not include user data like code, file paths, or bash commands) |
| `HTTP_PROXY`                               | Specify HTTP proxy server for network connections                                                                                      |
| `HTTPS_PROXY`                              | Specify HTTPS proxy server for network connections                                                                                     |
| `MAX_THINKING_TOKENS`                      | Force a thinking for the model budget                                                                                                  |
| `MCP_TIMEOUT`                              | Timeout in milliseconds for MCP server startup                                                                                         |
| `MCP_TOOL_TIMEOUT`                         | Timeout in milliseconds for MCP tool execution                                                                                         |

## Configuration options

We are in the process of migration global configuration to `settings.json`.

`claude config` will be deprecated in place of [settings.json](#settings-files)

To manage your configurations, use the following commands:

* List settings: `claude config list`
* See a setting: `claude config get <key>`
* Change a setting: `claude config set <key> <value>`
* Push to a setting (for lists): `claude config add <key> <value>`
* Remove from a setting (for lists): `claude config remove <key> <value>`

By default `config` changes your project configuration. To manage your global
configuration, use the `--global` (or `-g`) flag.

### Global configuration

To set a global configuration, use `claude config set -g <key> <value>`:

| Key                     | Description                                                      | Example                                                                    |
| :---------------------- | :--------------------------------------------------------------- | :------------------------------------------------------------------------- |
| `autoUpdaterStatus`     | Enable or disable the auto-updater (default: `enabled`)          | `disabled`                                                                 |
| `preferredNotifChannel` | Where you want to receive notifications (default: `iterm2`)      | `iterm2`, `iterm2_with_bell`, `terminal_bell`, or `notifications_disabled` |
| `theme`                 | Color theme                                                      | `dark`, `light`, `light-daltonized`, or `dark-daltonized`                  |
| `verbose`               | Whether to show full bash and command outputs (default: `false`) | `true`                                                                     |



# Manage permissions and security

> Learn about Claude Code's permission system, tools access, and security safeguards.

Claude Code uses a tiered permission system to balance power and safety:

| Tool Type         | Example              | Approval Required | "Yes, don't ask again" Behavior               |
| :---------------- | :------------------- | :---------------- | :-------------------------------------------- |
| Read-only         | File reads, LS, Grep | No                | N/A                                           |
| Bash Commands     | Shell execution      | Yes               | Permanently per project directory and command |
| File Modification | Edit/write files     | Yes               | Until session end                             |

## Tools available to Claude

Claude Code has access to a set of powerful tools that help it understand and modify your codebase:

| Tool             | Description                                          | Permission Required |
| :--------------- | :--------------------------------------------------- | :------------------ |
| **Agent**        | Runs a sub-agent to handle complex, multi-step tasks | No                  |
| **Bash**         | Executes shell commands in your environment          | Yes                 |
| **Edit**         | Makes targeted edits to specific files               | Yes                 |
| **Glob**         | Finds files based on pattern matching                | No                  |
| **Grep**         | Searches for patterns in file contents               | No                  |
| **LS**           | Lists files and directories                          | No                  |
| **MultiEdit**    | Performs multiple edits on a single file atomically  | Yes                 |
| **NotebookEdit** | Modifies Jupyter notebook cells                      | Yes                 |
| **NotebookRead** | Reads and displays Jupyter notebook contents         | No                  |
| **Read**         | Reads the contents of files                          | No                  |
| **TodoRead**     | Reads the current session's task list                | No                  |
| **TodoWrite**    | Creates and manages structured task lists            | No                  |
| **WebFetch**     | Fetches content from a specified URL                 | Yes                 |
| **WebSearch**    | Performs web searches with domain filtering          | Yes                 |
| **Write**        | Creates or overwrites files                          | Yes                 |

Permission rules can be configured using `/allowed-tools` or in [permission settings](/en/docs/claude-code/settings#permissions).

## Protect against prompt injection

Prompt injection is a technique where an attacker attempts to override or manipulate an AI assistant's instructions by inserting malicious text. Claude Code includes several safeguards against these attacks:

* **Permission system**: Sensitive operations require explicit approval
* **Context-aware analysis**: Detects potentially harmful instructions by analyzing the full request
* **Input sanitization**: Prevents command injection by processing user inputs
* **Command blocklist**: Blocks risky commands that fetch arbitrary content from the web like `curl` and `wget`

**Best practices for working with untrusted content**:

1. Review suggested commands before approval
2. Avoid piping untrusted content directly to Claude
3. Verify proposed changes to critical files
4. Report suspicious behavior with `/bug`

<Warning>
  While these protections significantly reduce risk, no system is completely
  immune to all attacks. Always maintain good security practices when working
  with any AI tool.
</Warning>

## Configure network access

Claude Code requires access to:

* api.anthropic.com
* statsig.anthropic.com
* sentry.io

Allowlist these URLs when using Claude Code in containerized environments.

## Development container reference implementation

Claude Code provides a development container configuration for teams that need consistent, secure environments. This preconfigured [devcontainer setup](https://code.visualstudio.com/docs/devcontainers/containers) works seamlessly with VS Code's Remote - Containers extension and similar tools.

The container's enhanced security measures (isolation and firewall rules) allow you to run `claude --dangerously-skip-permissions` to bypass permission prompts for unattended operation. We've included a [reference implementation](https://github.com/anthropics/claude-code/tree/main/.devcontainer) that you can customize for your needs.

<Warning>
  While the devcontainer provides substantial protections, no system is
  completely immune to all attacks. Always maintain good security practices and
  monitor Claude's activities.
</Warning>

### Key features

* **Production-ready Node.js**: Built on Node.js 20 with essential development dependencies
* **Security by design**: Custom firewall restricting network access to only necessary services
* **Developer-friendly tools**: Includes git, ZSH with productivity enhancements, fzf, and more
* **Seamless VS Code integration**: Pre-configured extensions and optimized settings
* **Session persistence**: Preserves command history and configurations between container restarts
* **Works everywhere**: Compatible with macOS, Windows, and Linux development environments

### Getting started in 4 steps

1. Install VS Code and the Remote - Containers extension
2. Clone the [Claude Code reference implementation](https://github.com/anthropics/claude-code/tree/main/.devcontainer) repository
3. Open the repository in VS Code
4. When prompted, click "Reopen in Container" (or use Command Palette: Cmd+Shift+P → "Remote-Containers: Reopen in Container")

### Configuration breakdown

The devcontainer setup consists of three primary components:

* [**devcontainer.json**](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json): Controls container settings, extensions, and volume mounts
* [**Dockerfile**](https://github.com/anthropics/claude-code/blob/main/.devcontainer/Dockerfile): Defines the container image and installed tools
* [**init-firewall.sh**](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh): Establishes network security rules

### Security features

The container implements a multi-layered security approach with its firewall configuration:

* **Precise access control**: Restricts outbound connections to whitelisted domains only (npm registry, GitHub, Anthropic API, etc.)
* **Default-deny policy**: Blocks all other external network access
* **Startup verification**: Validates firewall rules when the container initializes
* **Isolation**: Creates a secure development environment separated from your main system

### Customization options

The devcontainer configuration is designed to be adaptable to your needs:

* Add or remove VS Code extensions based on your workflow
* Modify resource allocations for different hardware environments
* Adjust network access permissions
* Customize shell configurations and developer tooling


# Team setup

> Learn how to onboard your team to Claude Code, including user management, security, and best practices.

## User management

Setting up Claude Code requires access to Anthropic models. For teams, you can set up Claude Code access in one of three ways:

* Anthropic API via the Anthropic Console
* Amazon Bedrock
* Google Vertex AI

**To set up Claude Code access for your team via Anthropic API:**

1. Use your existing Anthropic Console account or create a new Anthropic Console account
2. You can add users through either method below:
   * Bulk invite users from within the Console (Console -> Settings -> Members -> Invite)
   * [Set up SSO](https://support.anthropic.com/en/articles/10280258-setting-up-single-sign-on-on-the-api-console)
3. When inviting users, they need one of the following roles:
   * "Claude Code" role means users can only create Claude Code API keys
   * "Developer" role means users can create any kind of API key
4. Each invited user needs to complete these steps:
   * Accept the Console invite
   * [Check system requirements](/en/docs/claude-code/getting-started#check-system-requirements)
   * [Install Claude Code](/en/docs/claude-code/getting-started#install-and-authenticate)
   * Login with Console account credentials

**To set up Claude Code access for your team via Bedrock or Vertex:**

1. Follow the [Bedrock docs](/en/docs/claude-code/bedrock-vertex-proxies#connect-to-amazon-bedrock) or [Vertex docs](/en/docs/claude-code/bedrock-vertex-proxies#connect-to-google-vertex-ai)
2. Distribute the environment variables and instructions for generating cloud credentials to your users. Read more about how to [manage configuration here](/en/docs/claude-code/settings).
3. Users can [install Claude Code](/en/docs/claude-code/getting-started#install-and-authenticate)

# How we approach security

Your code's security is paramount. Claude Code is built with security at its core. We've developed Claude Code, as we develop all of our applications and services, according to the requirements of Anthropic's comprehensive security program. You can read more about our program and request access to resources (such as our SOC 2 Type 2 report, ISO 27001 certificate, etc.) at [Anthropic Trust Center](https://trust.anthropic.com).

We've designed Claude Code to have strict read-only permissions by default, including reading files in the current working directory, and specific bash commands such as `date`, `pwd`, and `whoami`. As Claude Code requests to perform additional actions (such as to edit files, run tests, and execute bash commands), it will ask users for permission. When Claude Code requests permission, users can approve it just for that instance or allow it to run that command automatically going forward. We support fine-grained permissions so that you're able to specify exactly what the agent is allowed to do (e.g. run tests, run linter) and what it is not allowed to do (e.g. update cloud infrastructure). These permission settings can be checked into version control and distributed to all developers in your organization, as well as customized by individual developers.

For enterprise deployments of Claude Code, we also support enterprise managed policy settings. These take precedence over user and project settings, allowing system administrators to enforce security policies that users cannot override. [Learn how to configure enterprise managed policy settings](/en/docs/claude-code/settings).

We designed Claude Code to be transparent and secure. For example, we allow the model to suggest `git` commands before executing them, thus giving control to the user to grant or deny permission. This enables users and organizations to configure their own permissions directly rather than trying to monitor all possible workarounds.

Agentic systems are fundamentally different from AI chat experiences since agents are able to call tools that interact with the real world and act for longer periods of time. Agentic systems are non-deterministic and we have a number of built in protections to mitigate risks for users.

1. **Prompt injection** is when model inputs alter model behavior in an undesired way. To reduce the risk of this happening, we've added a few in-product mitigations:
   * Tools that make network requests require user approval by default
   * Web fetch uses a separate context window, to avoid injecting potentially malicious prompts into the main context window
   * The first time you run Claude Code in a new codebase, we will prompt you to verify that you trust the code
   * The first time you see new MCP servers (configured via `.mcp.json`), we will prompt you to verify that you trust the servers
   * When we detect a bash command with potential command injection (as a result of prompt injection), we will ask users to manually approve the command even if they have allowlisted it
   * If we cannot reliably match a bash command to an allowlisted permission, we fail closed and prompt users for manual approval
   * When the model generates complex bash commands, we generate natural language descriptions for users, so that they understand what the command does
2. **Prompt fatigue.** We support allowlisting frequently used safe commands per-user, per-codebase, or per-organization. We also let you switch into Accept Edits mode to accept many edits at a time, focusing permission prompts on tools that may have side effects (eg. bash)

Ultimately, Claude Code only has as many permissions as the user who is guiding it, and users are responsible for making sure the proposed code and commands are safe.

**MCP security**

Claude Code allows users to configure Model Context Protocol (MCP) servers. The list of allowed MCP servers is configured in your source code, as part of Claude Code settings engineers check into source control.

We encourage either writing your own MCP servers or using MCP servers from providers that you trust. You are able to configure Claude Code permissions for MCP servers. Anthropic does not manage or audit any MCP servers.

# Data flow and dependencies

![Claude Code data flow diagram](https://mintlify.s3.us-west-1.amazonaws.com/anthropic/images/claude-code-data-flow.png)

Claude Code is installed from [NPM](https://www.npmjs.com/package/@anthropic-ai/claude-code). Claude Code runs locally. In order to interact with the LLM, Claude Code sends data over the network. This data includes all user prompts and model outputs. The data is encrypted in transit via TLS and is not encrypted at rest. Claude Code is compatible with most popular VPNs and LLM proxies.

Claude Code is built on Anthropic's APIs. For details regarding our API's security controls, including our API logging procedures, please refer to compliance artifacts offered in the [Anthropic Trust Center](https://trust.anthropic.com).

Claude Code supports authentication via Claude.ai credentials, Anthropic API credentials, Bedrock Auth, and Vertex Auth. On MacOS, the API keys, OAuth tokens, and other credentials are stored on encrypted macOS Keychain. Alternately, the setting [apiKeyHelper](/en/docs/claude-code/settings#available-settings) can be set to a shell script which returns an API key. By default, this helper is called after 5 minutes or on HTTP 401 response; specifying environment variable `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` defines a custom refresh interval.

Claude Code connects from users' machines to the Statsig service to log operational metrics such as latency, reliability, and usage patterns. This logging does not include any code or file paths. Data is encrypted in transit using TLS and at rest using 256-bit AES encryption. Read more in the [Statsig security documentation](https://www.statsig.com/trust/security). To opt out of Statsig telemetry, set the `DISABLE_TELEMETRY` environment variable.

Claude Code connects from users' machines to Sentry for operational error logging. The data is encrypted in transit using TLS and at rest using 256-bit AES encryption. Read more in the [Sentry security documentation](https://sentry.io/security/). To opt out of error logging, set the `DISABLE_ERROR_REPORTING` environment variable.

When users run the `/bug` command, a copy of their full conversation history including code is sent to Anthropic. The data is encrypted in transit and at rest. Optionally, a Github issue is created in our public repository. To opt out of bug reporting, set the `DISABLE_BUG_COMMAND` environment variable.

By default, we disable all non-essential traffic (including error reporting, telemetry, and bug reporting functionality) when using Bedrock or Vertex. You can also opt out of all of these at once by setting the `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` environment variable. Here are the full default behaviors:

| Service                            | Anthropic API                                            | Vertex API                                            | Bedrock API                                            |
| ---------------------------------- | -------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------ |
| **Statsig (Metrics)**              | Default on.<br />`DISABLE_TELEMETRY=1` to disable.       | Default off.<br />`CLAUDE_CODE_USE_VERTEX` must be 1. | Default off.<br />`CLAUDE_CODE_USE_BEDROCK` must be 1. |
| **Sentry (Errors)**                | Default on.<br />`DISABLE_ERROR_REPORTING=1` to disable. | Default off.<br />`CLAUDE_CODE_USE_VERTEX` must be 1. | Default off.<br />`CLAUDE_CODE_USE_BEDROCK` must be 1. |
| **Anthropic API (`/bug` reports)** | Default on.<br />`DISABLE_BUG_COMMAND=1` to disable.     | Default off.<br />`CLAUDE_CODE_USE_VERTEX` must be 1. | Default off.<br />`CLAUDE_CODE_USE_BEDROCK` must be 1. |

All environment variables can be checked into `settings.json` ([read more](/en/docs/claude-code/settings)).

Claude Code stores conversation history locally, in plain text, so that users can resume prior conversations. Conversations are retained for 30 days, and they can delete them earlier by running `rm -r ~/.claude/projects/*/`. The retention period can be customized using the `cleanupPeriodDays` setting; like other settings, you can check this setting into your repository, set it globally so that it applies across all repositories, or manage it for all employees using your enterprise policy. Uninstalling `claude` does not delete history.

# Managing costs

When using Anthropic API, you can limit the total Claude Code workspace spend. To configure, [follow these instructions](https://support.anthropic.com/en/articles/9796807-creating-and-managing-workspaces). Admins can view cost and usage reporting by [following these instructions](https://support.anthropic.com/en/articles/9534590-cost-and-usage-reporting-in-console).

On Bedrock and Vertex, Claude Code does not send metrics from your cloud. In order to get cost metrics, several large enterprises reported using [LiteLLM](/en/docs/claude-code/bedrock-vertex-proxies#litellm), which is an open-source tool that helps companies [track spend by key](https://docs.litellm.ai/docs/proxy/virtual_keys#tracking-spend). This project is unaffiliated with Anthropic and we have not audited its security.

For team usage, Claude Code charges by API token consumption. On average, Claude Code costs \~\$50-60/developer per month with Sonnet 3.7 though there is large variance depending on how many instances users are running and whether they're using it in automation.

# Best practices for organizations

1. We strongly recommend investing in documentation so that Claude Code understands your codebase. Many organizations make a `CLAUDE.md` file (which we also refer to as memory) in the root of the repository that contains the system architecture, how to run tests and other common commands, and best practices for contributing to the codebase. This file is typically checked into source control so that all users can benefit from it. [Learn more](/en/docs/claude-code/memory).
2. If you have a custom development environment, we find that creating a "one click" way to install Claude Code is key to growing adoption across an organization.
3. Encourage new users to try Claude Code for codebase Q\&A, or on smaller bug fixes or feature requests. Ask Claude Code to make a plan. Check Claude's suggestions and give feedback if it's off-track. Over time, as users understand this new paradigm better, then they'll be more effective at letting Claude Code run more agentically.
4. Security teams can configure managed permissions for what Claude Code is and is not allowed to do, which cannot be overwritten by local configuration. [Learn more](/en/docs/claude-code/overview).
5. MCP is a great way to give Claude Code more information, such as connecting to ticket management systems or error logs. We recommend that one central team configures MCP servers and checks a `.mcp.json` configuration into the codebase so that all users benefit. [Learn more](/en/docs/claude-code/tutorials#set-up-model-context-protocol-mcp).

At Anthropic, we trust Claude Code to power development across every Anthropic codebase. We hope you enjoy using Claude Code as much as we do!

# FAQ

**Q: Does my existing commercial agreement apply?**

Whether you're using Anthropic's API directly (1P) or accessing it through AWS Bedrock or Google Vertex (3P), your existing commercial agreement will apply to Claude Code usage, unless we've mutually agreed otherwise.

**Q: Does Claude Code train on user content?**

By default, Anthropic does not train generative models using code or prompts that are sent to Claude Code.

If you explicitly opt in to methods to provide us with materials to train on, such as via the [Development Partner Program](https://support.anthropic.com/en/articles/11174108-about-the-development-partner-program), we may use those materials provided to train our models. An organization admin can expressly opt-in to the Development Partner Program for their organization. Note that this program is available only for Anthropic first-party API, and not for Bedrock or Vertex users.

More details can be found in our [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms) and [Privacy Policy](https://www.anthropic.com/legal/privacy).

**Q: Can I use a zero data retention key?**

Yes, you can use an API key from a zero data retention organization. When doing so, Claude Code will not retain your chat transcripts on our servers. Users' local Claude Code clients may store sessions locally for up to 30 days so that users can resume them. This behavior is configurable.

**Q: Where can I learn more about trust and safety at Anthropic?**

You can find more information in the [Anthropic Trust Center](https://trust.anthropic.com) and [Transparency Hub](https://www.anthropic.com/transparency).

**Q: How can I report security vulnerabilities?**

Anthropic manages our security program through HackerOne. [Use this form to report vulnerabilities](https://hackerone.com/anthropic-vdp/reports/new?type=team\&report_type=vulnerability).

# Monitoring usage

> Monitor Claude Code usage with OpenTelemetry metrics

<Note>
  OpenTelemetry support is currently in beta and details are subject to change.
</Note>

# OpenTelemetry in Claude Code

Claude Code supports OpenTelemetry (OTel) metrics and events for monitoring and observability. This document explains how to enable and configure OTel for Claude Code.

All metrics are time series data exported via OpenTelemetry's standard metrics protocol, and events are exported via OpenTelemetry's logs/events protocol. It is the user's responsibility to ensure their metrics and logs backends are properly configured and that the aggregation granularity meets their monitoring requirements.

## Quick Start

Configure OpenTelemetry using environment variables:

```bash
# 1. Enable telemetry
export CLAUDE_CODE_ENABLE_TELEMETRY=1

# 2. Choose exporters (both are optional - configure only what you need)
export OTEL_METRICS_EXPORTER=otlp       # Options: otlp, prometheus, console
export OTEL_LOGS_EXPORTER=otlp          # Options: otlp, console

# 3. Configure OTLP endpoint (for OTLP exporter)
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# 4. Set authentication (if required)
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"

# 5. For debugging: reduce export intervals
export OTEL_METRIC_EXPORT_INTERVAL=10000  # 10 seconds (default: 60000ms)
export OTEL_LOGS_EXPORT_INTERVAL=5000     # 5 seconds (default: 5000ms)

# 6. Run Claude Code
claude
```

<Note>
  The default export intervals are 60 seconds for metrics and 5 seconds for logs. During setup, you may want to use shorter intervals for debugging purposes. Remember to reset these for production use.
</Note>

For full configuration options, see the [OpenTelemetry specification](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md#configuration-options).

## Administrator Configuration

Administrators can configure OpenTelemetry settings for all users through the managed settings file. This allows for centralized control of telemetry settings across an organization. See the [settings precedence](/en/docs/claude-code/settings#settings-precedence) for more information about how settings are applied.

The managed settings file is located at:

* macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`
* Linux: `/etc/claude-code/managed-settings.json`

Example managed settings configuration:

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector.company.com:4317",
    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer company-token"
  }
}
```

<Note>
  Managed settings can be distributed via MDM (Mobile Device Management) or other device management solutions. Environment variables defined in the managed settings file have high precedence and cannot be overridden by users.
</Note>

## Configuration Details

### Common Configuration Variables

| Environment Variable                            | Description                                               | Example Values                       |
| ----------------------------------------------- | --------------------------------------------------------- | ------------------------------------ |
| `CLAUDE_CODE_ENABLE_TELEMETRY`                  | Enables telemetry collection (required)                   | `1`                                  |
| `OTEL_METRICS_EXPORTER`                         | Metrics exporter type(s) (comma-separated)                | `console`, `otlp`, `prometheus`      |
| `OTEL_LOGS_EXPORTER`                            | Logs/events exporter type(s) (comma-separated)            | `console`, `otlp`                    |
| `OTEL_EXPORTER_OTLP_PROTOCOL`                   | Protocol for OTLP exporter (all signals)                  | `grpc`, `http/json`, `http/protobuf` |
| `OTEL_EXPORTER_OTLP_ENDPOINT`                   | OTLP collector endpoint (all signals)                     | `http://localhost:4317`              |
| `OTEL_EXPORTER_OTLP_METRICS_PROTOCOL`           | Protocol for metrics (overrides general)                  | `grpc`, `http/json`, `http/protobuf` |
| `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`           | OTLP metrics endpoint (overrides general)                 | `http://localhost:4318/v1/metrics`   |
| `OTEL_EXPORTER_OTLP_LOGS_PROTOCOL`              | Protocol for logs (overrides general)                     | `grpc`, `http/json`, `http/protobuf` |
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`              | OTLP logs endpoint (overrides general)                    | `http://localhost:4318/v1/logs`      |
| `OTEL_EXPORTER_OTLP_HEADERS`                    | Authentication headers for OTLP                           | `Authorization=Bearer token`         |
| `OTEL_EXPORTER_OTLP_METRICS_CLIENT_KEY`         | Client key for mTLS authentication                        | Path to client key file              |
| `OTEL_EXPORTER_OTLP_METRICS_CLIENT_CERTIFICATE` | Client certificate for mTLS authentication                | Path to client cert file             |
| `OTEL_METRIC_EXPORT_INTERVAL`                   | Export interval in milliseconds (default: 60000)          | `5000`, `60000`                      |
| `OTEL_LOGS_EXPORT_INTERVAL`                     | Logs export interval in milliseconds (default: 5000)      | `1000`, `10000`                      |
| `OTEL_LOG_USER_PROMPTS`                         | Enable logging of user prompt content (default: disabled) | `1` to enable                        |

### Metrics Cardinality Control

The following environment variables control which attributes are included in metrics to manage cardinality:

| Environment Variable                | Description                                     | Default Value | Example to Disable |
| ----------------------------------- | ----------------------------------------------- | ------------- | ------------------ |
| `OTEL_METRICS_INCLUDE_SESSION_ID`   | Include session.id attribute in metrics         | `true`        | `false`            |
| `OTEL_METRICS_INCLUDE_VERSION`      | Include app.version attribute in metrics        | `false`       | `true`             |
| `OTEL_METRICS_INCLUDE_ACCOUNT_UUID` | Include user.account\_uuid attribute in metrics | `true`        | `false`            |

These variables help control the cardinality of metrics, which affects storage requirements and query performance in your metrics backend. Lower cardinality generally means better performance and lower storage costs but less granular data for analysis.

### Example Configurations

```bash
# Console debugging (1-second intervals)
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console
export OTEL_METRIC_EXPORT_INTERVAL=1000

# OTLP/gRPC
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Prometheus
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=prometheus

# Multiple exporters
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=console,otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=http/json

# Different endpoints/backends for metrics and logs
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_METRICS_PROTOCOL=http/protobuf
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=http://metrics.company.com:4318
export OTEL_EXPORTER_OTLP_LOGS_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://logs.company.com:4317

# Metrics only (no events/logs)
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Events/logs only (no metrics)
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

## Available Metrics and Events

### Metrics

Claude Code exports the following metrics:

| Metric Name                           | Description                                     | Unit   |
| ------------------------------------- | ----------------------------------------------- | ------ |
| `claude_code.session.count`           | Count of CLI sessions started                   | count  |
| `claude_code.lines_of_code.count`     | Count of lines of code modified                 | count  |
| `claude_code.pull_request.count`      | Number of pull requests created                 | count  |
| `claude_code.commit.count`            | Number of git commits created                   | count  |
| `claude_code.cost.usage`              | Cost of the Claude Code session                 | USD    |
| `claude_code.token.usage`             | Number of tokens used                           | tokens |
| `claude_code.code_edit_tool.decision` | Count of code editing tool permission decisions | count  |

### Metric Details

All metrics share these standard attributes:

* `session.id`: Unique session identifier (controlled by `OTEL_METRICS_INCLUDE_SESSION_ID`)
* `app.version`: Current Claude Code version (controlled by `OTEL_METRICS_INCLUDE_VERSION`)
* `organization.id`: Organization UUID (when authenticated)
* `user.account_uuid`: Account UUID (when authenticated, controlled by `OTEL_METRICS_INCLUDE_ACCOUNT_UUID`)

#### 1. Session Counter

Emitted at the start of each session.

#### 2. Lines of Code Counter

Emitted when code is added or removed.

* Additional attribute: `type` (`"added"` or `"removed"`)

#### 3. Pull Request Counter

Emitted when creating pull requests via Claude Code.

#### 4. Commit Counter

Emitted when creating git commits via Claude Code.

#### 5. Cost Counter

Emitted after each API request.

* Additional attribute: `model`

#### 6. Token Counter

Emitted after each API request.

* Additional attributes: `type` (`"input"`, `"output"`, `"cacheRead"`, `"cacheCreation"`) and `model`

#### 7. Code Edit Tool Decision Counter

Emitted when user accepts or rejects Edit, MultiEdit, Write, or NotebookEdit tool usage.

* Additional attributes: `tool` (tool name: `"Edit"`, `"MultiEdit"`, `"Write"`, `"NotebookEdit"`) and `decision` (`"accept"`, `"reject"`)

### Events

Claude Code exports the following events via OpenTelemetry logs/events (when `OTEL_LOGS_EXPORTER` is configured):

#### 1. User Prompt Event

* **Event Name**: `claude_code.user_prompt`
* **Description**: Logged when a user submits a prompt
* **Attributes**:
  * All standard attributes (user.id, session.id, etc.)
  * `event.name`: `"user_prompt"`
  * `event.timestamp`: ISO 8601 timestamp
  * `prompt_length`: Length of the prompt
  * `prompt`: Prompt content (redacted by default, enable with `OTEL_LOG_USER_PROMPTS=1`)

#### 2. Tool Result Event

* **Event Name**: `claude_code.tool_result`
* **Description**: Logged when a tool completes execution
* **Attributes**:
  * All standard attributes
  * `event.name`: `"tool_result"`
  * `event.timestamp`: ISO 8601 timestamp
  * `name`: Name of the tool
  * `success`: `"true"` or `"false"`
  * `duration_ms`: Execution time in milliseconds
  * `error`: Error message (if failed)

#### 3. API Request Event

* **Event Name**: `claude_code.api_request`
* **Description**: Logged for each API request to Claude
* **Attributes**:
  * All standard attributes
  * `event.name`: `"api_request"`
  * `event.timestamp`: ISO 8601 timestamp
  * `model`: Model used (e.g., "claude-3-5-sonnet-20241022")
  * `cost_usd`: Estimated cost in USD
  * `duration_ms`: Request duration in milliseconds
  * `input_tokens`: Number of input tokens
  * `output_tokens`: Number of output tokens
  * `cache_read_tokens`: Number of tokens read from cache
  * `cache_creation_tokens`: Number of tokens used for cache creation

#### 4. API Error Event

* **Event Name**: `claude_code.api_error`
* **Description**: Logged when an API request to Claude fails
* **Attributes**:
  * All standard attributes
  * `event.name`: `"api_error"`
  * `event.timestamp`: ISO 8601 timestamp
  * `model`: Model used (e.g., "claude-3-5-sonnet-20241022")
  * `error`: Error message
  * `status_code`: HTTP status code (if applicable)
  * `duration_ms`: Request duration in milliseconds
  * `attempt`: Attempt number (for retried requests)

#### 5. Tool Decision Event

* **Event Name**: `claude_code.tool_decision`
* **Description**: Logged when a tool permission decision is made (accept/reject)
* **Attributes**:
  * All standard attributes
  * `event.name`: `"tool_decision"`
  * `event.timestamp`: ISO 8601 timestamp
  * `tool_name`: Name of the tool (e.g., "Read", "Edit", "MultiEdit", "Write", "NotebookEdit", etc.)
  * `decision`: Either `"accept"` or `"reject"`
  * `source`: Decision source - `"config"`, `"user_permanent"`, `"user_temporary"`, `"user_abort"`, or `"user_reject"`

## Interpreting Metrics and Events Data

The metrics exported by Claude Code provide valuable insights into usage patterns and productivity. Here are some common visualizations and analyses you can create:

### Usage Monitoring

| Metric                                                        | Analysis Opportunity                                      |
| ------------------------------------------------------------- | --------------------------------------------------------- |
| `claude_code.token.usage`                                     | Break down by `type` (input/output), user, team, or model |
| `claude_code.session.count`                                   | Track adoption and engagement over time                   |
| `claude_code.lines_of_code.count`                             | Measure productivity by tracking code additions/removals  |
| `claude_code.commit.count` & `claude_code.pull_request.count` | Understand impact on development workflows                |

### Cost Monitoring

The `claude_code.cost.usage` metric helps with:

* Tracking usage trends across teams or individuals
* Identifying high-usage sessions for optimization

<Note>
  Cost metrics are approximations. For official billing data, refer to your API provider (Anthropic Console, AWS Bedrock, or Google Cloud Vertex).
</Note>

### Alerting and Segmentation

Common alerts to consider:

* Cost spikes
* Unusual token consumption
* High session volume from specific users

All metrics can be segmented by `user.account_uuid`, `organization.id`, `session.id`, `model`, and `app.version`.

### Event Analysis

The event data provides detailed insights into Claude Code interactions:

1. **Tool Usage Patterns**: Analyze tool result events to identify:
   * Most frequently used tools
   * Tool success rates
   * Average tool execution times
   * Error patterns by tool type

2. **Performance Monitoring**: Track API request durations and tool execution times to identify performance bottlenecks.

## Backend Considerations

Your choice of metrics and logs backends will determine the types of analyses you can perform:

### For Metrics:

* **Time series databases (e.g., Prometheus)**: Rate calculations, aggregated metrics
* **Columnar stores (e.g., ClickHouse)**: Complex queries, unique user analysis
* **Full-featured observability platforms (e.g., Honeycomb, Datadog)**: Advanced querying, visualization, alerting

### For Events/Logs:

* **Log aggregation systems (e.g., Elasticsearch, Loki)**: Full-text search, log analysis
* **Columnar stores (e.g., ClickHouse)**: Structured event analysis
* **Full-featured observability platforms (e.g., Honeycomb, Datadog)**: Correlation between metrics and events

For organizations requiring Daily/Weekly/Monthly Active User (DAU/WAU/MAU) metrics, consider backends that support efficient unique value queries.

## Service Information

All metrics are exported with:

* Service Name: `claude-code`
* Service Version: Current Claude Code version
* Meter Name: `com.anthropic.claude_code`

## Security/Privacy Considerations

* Telemetry is opt-in and requires explicit configuration
* Sensitive information like API keys or file contents are never included in metrics or events
* User prompt content is redacted by default - only prompt length is recorded. To enable user prompt logging, set `OTEL_LOG_USER_PROMPTS=1`


# Manage costs effectively

> Learn how to track and optimize token usage and costs when using Claude Code.

Claude Code consumes tokens for each interaction. The average cost is \$6 per developer per day, with daily costs remaining below \$12 for 90% of users.

## Track your costs

* Use `/cost` to see current session usage
* **Anthropic Console users**:
  * Check [historical usage](https://support.anthropic.com/en/articles/9534590-cost-and-usage-reporting-in-console) in the Anthropic Console (requires Admin or Billing role)
  * Set [workspace spend limits](https://support.anthropic.com/en/articles/9796807-creating-and-managing-workspaces) for the Claude Code workspace (requires Admin role)
* **Pro and Max plan users**: Usage is included in your subscription

## Reduce token usage

* **Compact conversations:**

  * Claude uses auto-compact by default when context exceeds 95% capacity
  * Toggle auto-compact: Run `/config` and navigate to "Auto-compact enabled"
  * Use `/compact` manually when context gets large
  * Add custom instructions: `/compact Focus on code samples and API usage`
  * Customize compaction by adding to CLAUDE.md:

    ```markdown
    # Summary instructions

    When you are using compact, please focus on test output and code changes
    ```

* **Write specific queries:** Avoid vague requests that trigger unnecessary scanning

* **Break down complex tasks:** Split large tasks into focused interactions

* **Clear history between tasks:** Use `/clear` to reset context

Costs can vary significantly based on:

* Size of codebase being analyzed
* Complexity of queries
* Number of files being searched or modified
* Length of conversation history
* Frequency of compacting conversations
* Background processes (haiku generation, conversation summarization)

## Background token usage

Claude Code uses tokens for some background functionality even when idle:

* **Haiku generation**: Small creative messages that appear while you type (approximately 1 cent per day)
* **Conversation summarization**: Background jobs that summarize previous conversations for the `claude --resume` feature
* **Command processing**: Some commands like `/cost` may generate requests to check status

These background processes consume a small amount of tokens (typically under \$0.04 per session) even without active interaction.

<Note>
  For team deployments, we recommend starting with a small pilot group to
  establish usage patterns before wider rollout.
</Note>


# GitHub Actions

> Integrate Claude Code with your GitHub workflows for automated code review, PR management, and issue triage.

Claude Code GitHub Actions brings AI-powered automation to your GitHub workflow. With a simple `@claude` mention in any PR or issue, Claude can analyze your code, create pull requests, implement features, and fix bugs - all while following your project's standards.

<Info>
  Claude Code GitHub Actions is currently in beta. Features and functionality may evolve as we refine the experience.
</Info>

<Note>
  Claude Code GitHub Actions is built on top of the [Claude Code SDK](/en/docs/claude-code/sdk), which enables programmatic integration of Claude Code into your applications. You can use the SDK to build custom automation workflows beyond GitHub Actions.
</Note>

## Why use Claude Code GitHub Actions?

* **Instant PR creation**: Describe what you need, and Claude creates a complete PR with all necessary changes
* **Automated code implementation**: Turn issues into working code with a single command
* **Follows your standards**: Claude respects your `CLAUDE.md` guidelines and existing code patterns
* **Simple setup**: Get started in minutes with our installer and API key
* **Secure by default**: Your code stays on Github's runners

## What can Claude do?

Claude Code provides powerful GitHub Actions that transform how you work with code:

### Claude Code Action

This GitHub Action allows you to run Claude Code within your GitHub Actions workflows. You can use this to build any custom workflow on top of Claude Code.

[View repository →](https://github.com/anthropics/claude-code-action)

### Claude Code Action (Base)

The foundation for building custom GitHub workflows with Claude. This extensible framework gives you full access to Claude's capabilities for creating tailored automation.

[View repository →](https://github.com/anthropics/claude-code-base-action)

## Quick start

The easiest way to set up this action is through Claude Code in the terminal. Just open claude and run `/install-github-app`.

This command will guide you through setting up the GitHub app and required secrets.

<Note>
  * You must be a repository admin to install the GitHub app and add secrets
  * This quickstart method is only available for direct Anthropic API users. If you're using AWS Bedrock or Google Vertex AI, please see the [Using with AWS Bedrock & Google Vertex AI](#using-with-aws-bedrock-%26-google-vertex-ai) section.
</Note>

### If the setup script fails

If the `/install-github-app` command fails or you prefer manual setup, please follow these manual setup instructions:

1. **Install the Claude GitHub app** to your repository: [https://github.com/apps/claude](https://github.com/apps/claude)
2. **Add ANTHROPIC\_API\_KEY** to your repository secrets ([Learn how to use secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions))
3. **Copy the workflow file** from [examples/claude.yml](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml) into your repository's `.github/workflows/`

<Steps>
  <Step title="Test the action">
    After completing either the quickstart or manual setup, test the action by tagging `@claude` in an issue or PR comment!
  </Step>
</Steps>

## Example use cases

Claude Code GitHub Actions can help you with a variety of tasks. For complete working examples, see the [examples directory](https://github.com/anthropics/claude-code-action/tree/main/examples).

### Turn issues into PRs

```yaml
# In an issue comment:
@claude implement this feature based on the issue description
```

Claude will analyze the issue, write the code, and create a PR for review.

### Get implementation help

```yaml
# In a PR comment:
@claude how should I implement user authentication for this endpoint?
```

Claude will analyze your code and provide specific implementation guidance.

### Fix bugs quickly

```yaml
# In an issue:
@claude fix the TypeError in the user dashboard component
```

Claude will locate the bug, implement a fix, and create a PR.

## Best practices

### CLAUDE.md configuration

Create a `CLAUDE.md` file in your repository root to define code style guidelines, review criteria, project-specific rules, and preferred patterns. This file guides Claude's understanding of your project standards.

### Security considerations

**⚠️ IMPORTANT: Never commit API keys directly to your repository!**

Always use GitHub Secrets for API keys:

* Add your API key as a repository secret named `ANTHROPIC_API_KEY`
* Reference it in workflows: `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`
* Limit action permissions to only what's necessary
* Review Claude's suggestions before merging

Always use GitHub Secrets (e.g., `${{ secrets.ANTHROPIC_API_KEY }}`) rather than hardcoding API keys directly in your workflow files.

### Optimizing performance

Use issue templates to provide context, keep your `CLAUDE.md` concise and focused, and configure appropriate timeouts for your workflows.

### CI costs

When using Claude Code GitHub Actions, be aware of the associated costs:

**GitHub Actions costs:**

* Claude Code runs on GitHub-hosted runners, which consume your GitHub Actions minutes
* See [GitHub's billing documentation](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions) for detailed pricing and minute limits

**API costs:**

* Each Claude interaction consumes API tokens based on the length of prompts and responses
* Token usage varies by task complexity and codebase size
* See [Claude's pricing page](https://www.anthropic.com/api) for current token rates

**Cost optimization tips:**

* Use specific `@claude` commands to reduce unnecessary API calls
* Configure appropriate `max_turns` limits to prevent excessive iterations
* Set reasonable `timeout_minutes` to avoid runaway workflows
* Consider using GitHub's concurrency controls to limit parallel runs

## Configuration examples

For ready-to-use workflow configurations for different use cases, including:

* Basic workflow setup for issue and PR comments
* Automated code reviews on pull requests
* Custom implementations for specific needs

Visit the [examples directory](https://github.com/anthropics/claude-code-action/tree/main/examples) in the Claude Code Action repository.

<Tip>
  The examples repository includes complete, tested workflows that you can copy directly into your `.github/workflows/` directory.
</Tip>

## Using with AWS Bedrock & Google Vertex AI

For enterprise environments, you can use Claude Code GitHub Actions with your own cloud infrastructure. This approach gives you control over data residency and billing while maintaining the same functionality.

### Prerequisites

Before setting up Claude Code GitHub Actions with cloud providers, you need:

#### For Google Cloud Vertex AI:

1. A Google Cloud Project with Vertex AI enabled
2. Workload Identity Federation configured for GitHub Actions
3. A service account with the required permissions
4. A GitHub App (recommended) or use the default GITHUB\_TOKEN

#### For AWS Bedrock:

1. An AWS account with Amazon Bedrock enabled
2. GitHub OIDC Identity Provider configured in AWS
3. An IAM role with Bedrock permissions
4. A GitHub App (recommended) or use the default GITHUB\_TOKEN

<Steps>
  <Step title="Create a custom GitHub App (Recommended for 3P Providers)">
    For best control and security when using 3P providers like Vertex AI or Bedrock, we recommend creating your own GitHub App:

    1. Go to [https://github.com/settings/apps/new](https://github.com/settings/apps/new)
    2. Fill in the basic information:
       * **GitHub App name**: Choose a unique name (e.g., "YourOrg Claude Assistant")
       * **Homepage URL**: Your organization's website or the repository URL
    3. Configure the app settings:
       * **Webhooks**: Uncheck "Active" (not needed for this integration)
    4. Set the required permissions:
       * **Repository permissions**:
         * Contents: Read & Write
         * Issues: Read & Write
         * Pull requests: Read & Write
    5. Click "Create GitHub App"
    6. After creation, click "Generate a private key" and save the downloaded `.pem` file
    7. Note your App ID from the app settings page
    8. Install the app to your repository:
       * From your app's settings page, click "Install App" in the left sidebar
       * Select your account or organization
       * Choose "Only select repositories" and select the specific repository
       * Click "Install"
    9. Add the private key as a secret to your repository:
       * Go to your repository's Settings → Secrets and variables → Actions
       * Create a new secret named `APP_PRIVATE_KEY` with the contents of the `.pem` file
    10. Add the App ID as a secret:

    * Create a new secret named `APP_ID` with your GitHub App's ID

    <Note>
      This app will be used with the [actions/create-github-app-token](https://github.com/actions/create-github-app-token) action to generate authentication tokens in your workflows.
    </Note>

    **Alternative for Anthropic API or if you don't want to setup your own Github app**: Use the official Anthropic app:

    1. Install from: [https://github.com/apps/claude](https://github.com/apps/claude)
    2. No additional configuration needed for authentication
  </Step>

  <Step title="Configure cloud provider authentication">
    Choose your cloud provider and set up secure authentication:

    <AccordionGroup>
      <Accordion title="AWS Bedrock">
        **Configure AWS to allow GitHub Actions to authenticate securely without storing credentials.**

        > **Security Note**: Use repository-specific configurations and grant only the minimum required permissions.

        **Required Setup**:

        1. **Enable Amazon Bedrock**:
           * Request access to Claude models in Amazon Bedrock
           * For cross-region models, request access in all required regions

        2. **Set up GitHub OIDC Identity Provider**:
           * Provider URL: `https://token.actions.githubusercontent.com`
           * Audience: `sts.amazonaws.com`

        3. **Create IAM Role for GitHub Actions**:
           * Trusted entity type: Web identity
           * Identity provider: `token.actions.githubusercontent.com`
           * Permissions: `AmazonBedrockFullAccess` policy
           * Configure trust policy for your specific repository

        **Required Values**:

        After setup, you'll need:

        * **AWS\_ROLE\_TO\_ASSUME**: The ARN of the IAM role you created

        <Tip>
          OIDC is more secure than using static AWS access keys because credentials are temporary and automatically rotated.
        </Tip>

        See [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html) for detailed OIDC setup instructions.
      </Accordion>

      <Accordion title="Google Vertex AI">
        **Configure Google Cloud to allow GitHub Actions to authenticate securely without storing credentials.**

        > **Security Note**: Use repository-specific configurations and grant only the minimum required permissions.

        **Required Setup**:

        1. **Enable APIs** in your Google Cloud project:
           * IAM Credentials API
           * Security Token Service (STS) API
           * Vertex AI API

        2. **Create Workload Identity Federation resources**:
           * Create a Workload Identity Pool
           * Add a GitHub OIDC provider with:
             * Issuer: `https://token.actions.githubusercontent.com`
             * Attribute mappings for repository and owner
             * **Security recommendation**: Use repository-specific attribute conditions

        3. **Create a Service Account**:
           * Grant only `Vertex AI User` role
           * **Security recommendation**: Create a dedicated service account per repository

        4. **Configure IAM bindings**:
           * Allow the Workload Identity Pool to impersonate the service account
           * **Security recommendation**: Use repository-specific principal sets

        **Required Values**:

        After setup, you'll need:

        * **GCP\_WORKLOAD\_IDENTITY\_PROVIDER**: The full provider resource name
        * **GCP\_SERVICE\_ACCOUNT**: The service account email address

        <Tip>
          Workload Identity Federation eliminates the need for downloadable service account keys, improving security.
        </Tip>

        For detailed setup instructions, consult the [Google Cloud Workload Identity Federation documentation](https://cloud.google.com/iam/docs/workload-identity-federation).
      </Accordion>
    </AccordionGroup>
  </Step>

  <Step title="Add Required Secrets">
    Add the following secrets to your repository (Settings → Secrets and variables → Actions):

    #### For Anthropic API (Direct):

    1. **For API Authentication**:
       * `ANTHROPIC_API_KEY`: Your Anthropic API key from [console.anthropic.com](https://console.anthropic.com)

    2. **For GitHub App (if using your own app)**:
       * `APP_ID`: Your GitHub App's ID
       * `APP_PRIVATE_KEY`: The private key (.pem) content

    #### For Google Cloud Vertex AI

    1. **For GCP Authentication**:
       * `GCP_WORKLOAD_IDENTITY_PROVIDER`
       * `GCP_SERVICE_ACCOUNT`

    2. **For GitHub App (if using your own app)**:
       * `APP_ID`: Your GitHub App's ID
       * `APP_PRIVATE_KEY`: The private key (.pem) content

    #### For AWS Bedrock

    1. **For AWS Authentication**:
       * `AWS_ROLE_TO_ASSUME`

    2. **For GitHub App (if using your own app)**:
       * `APP_ID`: Your GitHub App's ID
       * `APP_PRIVATE_KEY`: The private key (.pem) content
  </Step>

  <Step title="Create workflow files">
    Create GitHub Actions workflow files that integrate with your cloud provider. The examples below show complete configurations for both AWS Bedrock and Google Vertex AI:

    <AccordionGroup>
      <Accordion title="AWS Bedrock workflow">
        **Prerequisites:**

        * AWS Bedrock access enabled with Claude model permissions
        * GitHub configured as an OIDC identity provider in AWS
        * IAM role with Bedrock permissions that trusts GitHub Actions

        **Required GitHub secrets:**

        | Secret Name          | Description                                       |
        | -------------------- | ------------------------------------------------- |
        | `AWS_ROLE_TO_ASSUME` | ARN of the IAM role for Bedrock access            |
        | `APP_ID`             | Your GitHub App ID (from app settings)            |
        | `APP_PRIVATE_KEY`    | The private key you generated for your GitHub App |

        ```yaml
        name: Claude PR Action 

        permissions:
          contents: write
          pull-requests: write
          issues: write
          id-token: write 

        on:
          issue_comment:
            types: [created]
          pull_request_review_comment:
            types: [created]
          issues:
            types: [opened, assigned]

        jobs:
          claude-pr:
            if: |
              (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
            runs-on: ubuntu-latest
            env:
              AWS_REGION: us-west-2
            steps:
              - name: Checkout repository
                uses: actions/checkout@v4

              - name: Generate GitHub App token
                id: app-token
                uses: actions/create-github-app-token@v2
                with:
                  app-id: ${{ secrets.APP_ID }}
                  private-key: ${{ secrets.APP_PRIVATE_KEY }}

              - name: Configure AWS Credentials (OIDC)
                uses: aws-actions/configure-aws-credentials@v4
                with:
                  role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
                  aws-region: us-west-2

              - uses: ./.github/actions/claude-pr-action
                with:
                  trigger_phrase: "@claude"
                  timeout_minutes: "60"
                  github_token: ${{ steps.app-token.outputs.token }}
                  use_bedrock: "true"
                  model: "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        ```

        <Tip>
          The model ID format for Bedrock includes the region prefix (e.g., `us.anthropic.claude...`) and version suffix.
        </Tip>
      </Accordion>

      <Accordion title="Google Vertex AI workflow">
        **Prerequisites:**

        * Vertex AI API enabled in your GCP project
        * Workload Identity Federation configured for GitHub
        * Service account with Vertex AI permissions

        **Required GitHub secrets:**

        | Secret Name                      | Description                                       |
        | -------------------------------- | ------------------------------------------------- |
        | `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload identity provider resource name          |
        | `GCP_SERVICE_ACCOUNT`            | Service account email with Vertex AI access       |
        | `APP_ID`                         | Your GitHub App ID (from app settings)            |
        | `APP_PRIVATE_KEY`                | The private key you generated for your GitHub App |

        ```yaml
        name: Claude PR Action

        permissions:
          contents: write
          pull-requests: write
          issues: write
          id-token: write  

        on:
          issue_comment:
            types: [created]
          pull_request_review_comment:
            types: [created]
          issues:
            types: [opened, assigned]

        jobs:
          claude-pr:
            if: |
              (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
              (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
            runs-on: ubuntu-latest
            steps:
              - name: Checkout repository
                uses: actions/checkout@v4

              - name: Generate GitHub App token
                id: app-token
                uses: actions/create-github-app-token@v2
                with:
                  app-id: ${{ secrets.APP_ID }}
                  private-key: ${{ secrets.APP_PRIVATE_KEY }}

              - name: Authenticate to Google Cloud
                id: auth
                uses: google-github-actions/auth@v2
                with:
                  workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
                  service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}
              
              - uses: ./.github/actions/claude-pr-action
                with:
                  trigger_phrase: "@claude"
                  timeout_minutes: "60"
                  github_token: ${{ steps.app-token.outputs.token }}
                  use_vertex: "true"
                  model: "claude-3-7-sonnet@20250219"
                env:
                  ANTHROPIC_VERTEX_PROJECT_ID: ${{ steps.auth.outputs.project_id }}
                  CLOUD_ML_REGION: us-east5
                  VERTEX_REGION_CLAUDE_3_7_SONNET: us-east5
        ```

        <Tip>
          The project ID is automatically retrieved from the Google Cloud authentication step, so you don't need to hardcode it.
        </Tip>
      </Accordion>
    </AccordionGroup>
  </Step>
</Steps>

## Troubleshooting

### Claude not responding to @claude commands

Verify the GitHub App is installed correctly, check that workflows are enabled, ensure API key is set in repository secrets, and confirm the comment contains `@claude` (not `/claude`).

### CI not running on Claude's commits

Ensure you're using the GitHub App or custom app (not Actions user), check workflow triggers include the necessary events, and verify app permissions include CI triggers.

### Authentication errors

Confirm API key is valid and has sufficient permissions. For Bedrock/Vertex, check credentials configuration and ensure secrets are named correctly in workflows.

## Advanced configuration

### Action parameters

The Claude Code Action supports these key parameters:

| Parameter           | Description                    | Required |
| ------------------- | ------------------------------ | -------- |
| `prompt`            | The prompt to send to Claude   | Yes\*    |
| `prompt_file`       | Path to file containing prompt | Yes\*    |
| `anthropic_api_key` | Anthropic API key              | Yes\*\*  |
| `max_turns`         | Maximum conversation turns     | No       |
| `timeout_minutes`   | Execution timeout              | No       |

\*Either `prompt` or `prompt_file` required\
\*\*Required for direct Anthropic API, not for Bedrock/Vertex

### Alternative integration methods

While the `/install-github-app` command is the recommended approach, you can also:

* **Custom GitHub App**: For organizations needing branded usernames or custom authentication flows. Create your own GitHub App with required permissions (contents, issues, pull requests) and use the actions/create-github-app-token action to generate tokens in your workflows.
* **Manual GitHub Actions**: Direct workflow configuration for maximum flexibility
* **MCP Configuration**: Dynamic loading of Model Context Protocol servers

See the [Claude Code Action repository](https://github.com/anthropics/claude-code-action) for detailed documentation.

### Customizing Claude's behavior

You can configure Claude's behavior in two ways:

1. **CLAUDE.md**: Define coding standards, review criteria, and project-specific rules in a `CLAUDE.md` file at the root of your repository. Claude will follow these guidelines when creating PRs and responding to requests. Check out our [Memory documentation](/en/docs/claude-code/memory) for more details.
2. **Custom prompts**: Use the `prompt` parameter in the workflow file to provide workflow-specific instructions. This allows you to customize Claude's behavior for different workflows or tasks.

Claude will follow these guidelines when creating PRs and responding to requests.



# SDK

> Programmatically integrate Claude Code into your applications using the SDK.

The Claude Code SDK allows developers to programmatically integrate Claude Code into their applications. It enables running Claude Code as a subprocess, providing a way to build AI-powered coding assistants and tools that leverage Claude's capabilities.

The SDK currently support command line usage. TypeScript and Python SDKs are coming soon.

## Authentication

To use the Claude Code SDK, we recommend creating a dedicated API key:

1. Create an Anthropic API key in the [Anthropic Console](https://console.anthropic.com/)
2. Then, set the `ANTHROPIC_API_KEY` environment variable. We recommend storing this key securely (eg. using a Github [secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions))

## Basic SDK usage

The Claude Code SDK allows you to use Claude Code in non-interactive mode from your applications. Here's a basic example:

```bash
# Run a single prompt and exit (print mode)
$ claude -p "Write a function to calculate Fibonacci numbers"

# Using a pipe to provide stdin
$ echo "Explain this code" | claude -p

# Output in JSON format with metadata
$ claude -p "Generate a hello world function" --output-format json

# Stream JSON output as it arrives
$ claude -p "Build a React component" --output-format stream-json
```

## Advanced usage

### Multi-turn conversations

For multi-turn conversations, you can resume conversations or continue from the most recent session:

```bash
# Continue the most recent conversation
$ claude --continue

# Continue and provide a new prompt
$ claude --continue "Now refactor this for better performance"

# Resume a specific conversation by session ID
$ claude --resume 550e8400-e29b-41d4-a716-446655440000

# Resume in print mode (non-interactive)
$ claude -p --resume 550e8400-e29b-41d4-a716-446655440000 "Update the tests"

# Continue in print mode (non-interactive)
$ claude -p --continue "Add error handling"
```

### Custom system prompts

You can provide custom system prompts to guide Claude's behavior:

```bash
# Override system prompt (only works with --print)
$ claude -p "Build a REST API" --system-prompt "You are a senior backend engineer. Focus on security, performance, and maintainability."

# System prompt with specific requirements
$ claude -p "Create a database schema" --system-prompt "You are a database architect. Use PostgreSQL best practices and include proper indexing."
```

You can also append instructions to the default system prompt:

```bash
# Append system prompt (only works with --print)
$ claude -p "Build a REST API" --append-system-prompt "After writing code, be sure to code review yourself."
```

### MCP Configuration

The Model Context Protocol (MCP) allows you to extend Claude Code with additional tools and resources from external servers. Using the `--mcp-config` flag, you can load MCP servers that provide specialized capabilities like database access, API integrations, or custom tooling.

Create a JSON configuration file with your MCP servers:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/files"
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-github-token"
      }
    }
  }
}
```

Then use it with Claude Code:

```bash
# Load MCP servers from configuration
$ claude -p "List all files in the project" --mcp-config mcp-servers.json

# Important: MCP tools must be explicitly allowed using --allowedTools
# MCP tools follow the format: mcp__$serverName__$toolName
$ claude -p "Search for TODO comments" \
  --mcp-config mcp-servers.json \
  --allowedTools "mcp__filesystem__read_file,mcp__filesystem__list_directory"

# Use an MCP tool for handling permission prompts in non-interactive mode
$ claude -p "Deploy the application" \
  --mcp-config mcp-servers.json \
  --allowedTools "mcp__permissions__approve" \
  --permission-prompt-tool mcp__permissions__approve
```

Note: When using MCP tools, you must explicitly allow them using the `--allowedTools` flag. MCP tool names follow the pattern `mcp__<serverName>__<toolName>` where:

* `serverName` is the key from your MCP configuration file
* `toolName` is the specific tool provided by that server

This security measure ensures that MCP tools are only used when explicitly permitted.

### Custom permission prompt tool

Optionally, use `--permission-prompt-tool` to pass in an MCP tool that we will use to check whether or not the user grants the model permissions to invoke a given tool. When the model invokes a tool the following happens:

1. We first check permission settings: all [settings.json files](/en/docs/claude-code/settings), as well as `--allowedTools` and `--disallowedTools` passed into the SDK; if one of these allows or denies the tool call, we proceed with the tool call
2. Otherwise, we invoke the MCP tool you provided in `--permission-prompt-tool`

The `--permission-prompt-tool` MCP tool is passed the tool name and input, and must return a JSON-stringified payload with the result. The payload must be one of:

```ts
// tool call is allowed
{
  "behavior": "allow",
  "updatedInput": {...}, // updated input, or just return back the original input
}

// tool call is denied
{
  "behavior": "deny",
  "message": "..." // human-readable string explaining why the permission was denied
}
```

For example, a TypeScript MCP permission prompt tool implementation might look like this:

```ts
const server = new McpServer({
  name: "Test permission prompt MCP Server",
  version: "0.0.1",
});

server.tool(
  "approval_prompt",
  'Simulate a permission check - approve if the input contains "allow", otherwise deny',
  {
    tool_name: z.string().describe("The tool requesting permission"),
    input: z.object({}).passthrough().describe("The input for the tool"),
  },
  async ({ tool_name, input }) => {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            JSON.stringify(input).includes("allow")
              ? {
                  behavior: "allow",
                  updatedInput: input,
                }
              : {
                  behavior: "deny",
                  message: "Permission denied by test approval_prompt tool",
                }
          ),
        },
      ],
    };
  }
);
```

To use this tool, add your MCP server (eg. with `--mcp-config`), then invoke the SDK like so:

```sh
claude -p "..." \
  --permission-prompt-tool mcp__test-server__approval_prompt \
  --mcp-config my-config.json
```

Usage notes:

* Use `updatedInput` to tell the model that the permission prompt mutated its input; otherwise, set `updatedInput` to the original input, as in the example above. For example, if the tool shows a file edit diff to the user and lets them edit the diff manually, the permission prompt tool should return that updated edit.
* The payload must be JSON-stringified

## Available CLI options

The SDK leverages all the CLI options available in Claude Code. Here are the key ones for SDK usage:

| Flag                       | Description                                                      | Example                                                     |
| :------------------------- | :--------------------------------------------------------------- | :---------------------------------------------------------- |
| `--print`, `-p`            | Run in non-interactive mode                                      | `claude -p "query"`                                         |
| `--output-format`          | Specify output format (`text`, `json`, `stream-json`)            | `claude -p --output-format json`                            |
| `--resume`, `-r`           | Resume a conversation by session ID                              | `claude --resume abc123`                                    |
| `--continue`, `-c`         | Continue the most recent conversation                            | `claude --continue`                                         |
| `--verbose`                | Enable verbose logging                                           | `claude --verbose`                                          |
| `--max-turns`              | Limit agentic turns in non-interactive mode                      | `claude --max-turns 3`                                      |
| `--system-prompt`          | Override system prompt (only with `--print`)                     | `claude --system-prompt "Custom instruction"`               |
| `--append-system-prompt`   | Append to system prompt (only with `--print`)                    | `claude --append-system-prompt "Custom instruction"`        |
| `--allowedTools`           | Comma/space-separated list of allowed tools (includes MCP tools) | `claude --allowedTools "Bash(npm install),mcp__filesystem"` |
| `--disallowedTools`        | Comma/space-separated list of denied tools                       | `claude --disallowedTools "Bash(git commit),mcp__github"`   |
| `--mcp-config`             | Load MCP servers from a JSON file                                | `claude --mcp-config servers.json`                          |
| `--permission-prompt-tool` | MCP tool for handling permission prompts (only with `--print`)   | `claude --permission-prompt-tool mcp__auth__prompt`         |

For a complete list of CLI options and features, see the [CLI usage](/en/docs/claude-code/cli-usage) documentation.

## Output formats

The SDK supports multiple output formats:

### Text output (default)

Returns just the response text:

```bash
$ claude -p "Explain file src/components/Header.tsx"
# Output: This is a React component showing...
```

### JSON output

Returns structured data including metadata:

```bash
$ claude -p "How does the data layer work?" --output-format json
```

Response format:

```json
{
  "type": "result",
  "subtype": "success",
  "cost_usd": 0.003,
  "is_error": false,
  "duration_ms": 1234,
  "duration_api_ms": 800,
  "num_turns": 6,
  "result": "The response text here...",
  "session_id": "abc123"
}
```

### Streaming JSON output

Streams each message as it is received:

```bash
$ claude -p "Build an application" --output-format stream-json
```

Each conversation begins with an initial `init` system message, followed by a list of user and assistant messages, followed by a final `result` system message with stats. Each message is emitted as a separate JSON object.

## Message schema

Messages returned from the JSON API are strictly typed according to the following schema:

```ts
type SDKMessage =
  // An assistant message
  | {
      type: "assistant";
      message: Message; // from Anthropic SDK
      session_id: string;
    }

  // A user message
  | {
      type: "user";
      message: MessageParam; // from Anthropic SDK
      session_id: string;
    }

  // Emitted as the last message
  | {
      type: "result";
      subtype: "success";
      cost_usd: float;
      duration_ms: float;
      duration_api_ms: float;
      is_error: boolean;
      num_turns: int;
      result: string;
      session_id: string;
    }

  // Emitted as the last message, when we've reached the maximum number of turns
  | {
      type: "result";
      subtype: "error_max_turns";
      cost_usd: float;
      duration_ms: float;
      duration_api_ms: float;
      is_error: boolean;
      num_turns: int;
      session_id: string;
    }

  // Emitted as the first message at the start of a conversation
  | {
      type: "system";
      subtype: "init";
      session_id: string;
      tools: string[];
      mcp_servers: {
        name: string;
        status: string;
      }[];
    };
```

We will soon publish these types in a JSONSchema-compatible format. We use semantic versioning for the main Claude Code package to communicate breaking changes to this format.

`Message` and `MessageParam` types are available in Anthropic SDKs. For example, see the Anthropic [TypeScript](https://github.com/anthropics/anthropic-sdk-typescript) and [Python](https://github.com/anthropics/anthropic-sdk-python/) SDKs.

## Examples

### Simple script integration

```bash
#!/bin/bash

# Simple function to run Claude and check exit code
run_claude() {
    local prompt="$1"
    local output_format="${2:-text}"

    if claude -p "$prompt" --output-format "$output_format"; then
        echo "Success!"
    else
        echo "Error: Claude failed with exit code $?" >&2
        return 1
    fi
}

# Usage examples
run_claude "Write a Python function to read CSV files"
run_claude "Optimize this database query" "json"
```

### Processing files with Claude

```bash
# Process a file through Claude
$ cat mycode.py | claude -p "Review this code for bugs"

# Process multiple files
$ for file in *.js; do
    echo "Processing $file..."
    claude -p "Add JSDoc comments to this file:" < "$file" > "${file}.documented"
done

# Use Claude in a pipeline
$ grep -l "TODO" *.py | while read file; do
    claude -p "Fix all TODO items in this file" < "$file"
done
```

### Session management

```bash
# Start a session and capture the session ID
$ claude -p "Initialize a new project" --output-format json | jq -r '.session_id' > session.txt

# Continue with the same session
$ claude -p --resume "$(cat session.txt)" "Add unit tests"
```

## Best practices

1. **Use JSON output format** for programmatic parsing of responses:

   ```bash
   # Parse JSON response with jq
   result=$(claude -p "Generate code" --output-format json)
   code=$(echo "$result" | jq -r '.result')
   cost=$(echo "$result" | jq -r '.cost_usd')
   ```

2. **Handle errors gracefully** - check exit codes and stderr:

   ```bash
   if ! claude -p "$prompt" 2>error.log; then
       echo "Error occurred:" >&2
       cat error.log >&2
       exit 1
   fi
   ```

3. **Use session management** for maintaining context in multi-turn conversations

4. **Consider timeouts** for long-running operations:

   ```bash
   timeout 300 claude -p "$complex_prompt" || echo "Timed out after 5 minutes"
   ```

5. **Respect rate limits** when making multiple requests by adding delays between calls

## Real-world applications

The Claude Code SDK enables powerful integrations with your development workflow. One notable example is the [Claude Code GitHub Actions](/en/docs/claude-code/github-actions), which uses the SDK to provide automated code review, PR creation, and issue triage capabilities directly in your GitHub workflow.

## Related resources

* [CLI usage and controls](/en/docs/claude-code/cli-usage) - Complete CLI documentation
* [GitHub Actions integration](/en/docs/claude-code/github-actions) - Automate your GitHub workflow with Claude
* [Tutorials](/en/docs/claude-code/tutorials) - Step-by-step guides for common use cases



# Tutorials

> Practical examples and patterns for effectively using Claude Code in your development workflow.

This guide provides step-by-step tutorials for common workflows with Claude Code. Each tutorial includes clear instructions, example commands, and best practices to help you get the most from Claude Code.

## Table of contents

* [Resume previous conversations](#resume-previous-conversations)
* [Understand new codebases](#understand-new-codebases)
* [Fix bugs efficiently](#fix-bugs-efficiently)
* [Refactor code](#refactor-code)
* [Work with tests](#work-with-tests)
* [Create pull requests](#create-pull-requests)
* [Handle documentation](#handle-documentation)
* [Work with images](#work-with-images)
* [Use extended thinking](#use-extended-thinking)
* [Set up project memory](#set-up-project-memory)
* [Set up Model Context Protocol (MCP)](#set-up-model-context-protocol-mcp)
* [Use Claude as a unix-style utility](#use-claude-as-a-unix-style-utility)
* [Create custom slash commands](#create-custom-slash-commands)
* [Run parallel Claude Code sessions with Git worktrees](#run-parallel-claude-code-sessions-with-git-worktrees)

## Resume previous conversations

### Continue your work seamlessly

**When to use:** You've been working on a task with Claude Code and need to continue where you left off in a later session.

Claude Code provides two options for resuming previous conversations:

* `--continue` to automatically continue the most recent conversation
* `--resume` to display a conversation picker

<Steps>
  <Step title="Continue the most recent conversation">
    ```bash
    claude --continue
    ```

    This immediately resumes your most recent conversation without any prompts.
  </Step>

  <Step title="Continue in non-interactive mode">
    ```bash
    claude --continue --print "Continue with my task"
    ```

    Use `--print` with `--continue` to resume the most recent conversation in non-interactive mode, perfect for scripts or automation.
  </Step>

  <Step title="Show conversation picker">
    ```bash
    claude --resume
    ```

    This displays an interactive conversation selector showing:

    * Conversation start time
    * Initial prompt or conversation summary
    * Message count

    Use arrow keys to navigate and press Enter to select a conversation.
  </Step>
</Steps>

**How it works:**

1. **Conversation Storage**: All conversations are automatically saved locally with their full message history
2. **Message Deserialization**: When resuming, the entire message history is restored to maintain context
3. **Tool State**: Tool usage and results from the previous conversation are preserved
4. **Context Restoration**: The conversation resumes with all previous context intact

**Tips:**

* Conversation history is stored locally on your machine
* Use `--continue` for quick access to your most recent conversation
* Use `--resume` when you need to select a specific past conversation
* When resuming, you'll see the entire conversation history before continuing
* The resumed conversation starts with the same model and configuration as the original

**Examples:**

```bash
# Continue most recent conversation
claude --continue

# Continue most recent conversation with a specific prompt
claude --continue --print "Show me our progress"

# Show conversation picker
claude --resume

# Continue most recent conversation in non-interactive mode
claude --continue --print "Run the tests again"
```

## Understand new codebases

### Get a quick codebase overview

**When to use:** You've just joined a new project and need to understand its structure quickly.

<Steps>
  <Step title="Navigate to the project root directory">
    ```bash
    cd /path/to/project 
    ```
  </Step>

  <Step title="Start Claude Code">
    ```bash
    claude 
    ```
  </Step>

  <Step title="Ask for a high-level overview">
    ```
    > give me an overview of this codebase 
    ```
  </Step>

  <Step title="Dive deeper into specific components">
    ```
    > explain the main architecture patterns used here 
    ```

    ```
    > what are the key data models?
    ```

    ```
    > how is authentication handled?
    ```
  </Step>
</Steps>

**Tips:**

* Start with broad questions, then narrow down to specific areas
* Ask about coding conventions and patterns used in the project
* Request a glossary of project-specific terms

### Find relevant code

**When to use:** You need to locate code related to a specific feature or functionality.

<Steps>
  <Step title="Ask Claude to find relevant files">
    ```
    > find the files that handle user authentication 
    ```
  </Step>

  <Step title="Get context on how components interact">
    ```
    > how do these authentication files work together? 
    ```
  </Step>

  <Step title="Understand the execution flow">
    ```
    > trace the login process from front-end to database 
    ```
  </Step>
</Steps>

**Tips:**

* Be specific about what you're looking for
* Use domain language from the project

***

## Fix bugs efficiently

### Diagnose error messages

**When to use:** You've encountered an error message and need to find and fix its source.

<Steps>
  <Step title="Share the error with Claude">
    ```
    > I'm seeing an error when I run npm test 
    ```
  </Step>

  <Step title="Ask for fix recommendations">
    ```
    > suggest a few ways to fix the @ts-ignore in user.ts 
    ```
  </Step>

  <Step title="Apply the fix">
    ```
    > update user.ts to add the null check you suggested 
    ```
  </Step>
</Steps>

**Tips:**

* Tell Claude the command to reproduce the issue and get a stack trace
* Mention any steps to reproduce the error
* Let Claude know if the error is intermittent or consistent

***

## Refactor code

### Modernize legacy code

**When to use:** You need to update old code to use modern patterns and practices.

<Steps>
  <Step title="Identify legacy code for refactoring">
    ```
    > find deprecated API usage in our codebase 
    ```
  </Step>

  <Step title="Get refactoring recommendations">
    ```
    > suggest how to refactor utils.js to use modern JavaScript features 
    ```
  </Step>

  <Step title="Apply the changes safely">
    ```
    > refactor utils.js to use ES2024 features while maintaining the same behavior 
    ```
  </Step>

  <Step title="Verify the refactoring">
    ```
    > run tests for the refactored code 
    ```
  </Step>
</Steps>

**Tips:**

* Ask Claude to explain the benefits of the modern approach
* Request that changes maintain backward compatibility when needed
* Do refactoring in small, testable increments

***

## Work with tests

### Add test coverage

**When to use:** You need to add tests for uncovered code.

<Steps>
  <Step title="Identify untested code">
    ```
    > find functions in NotificationsService.swift that are not covered by tests 
    ```
  </Step>

  <Step title="Generate test scaffolding">
    ```
    > add tests for the notification service 
    ```
  </Step>

  <Step title="Add meaningful test cases">
    ```
    > add test cases for edge conditions in the notification service 
    ```
  </Step>

  <Step title="Run and verify tests">
    ```
    > run the new tests and fix any failures 
    ```
  </Step>
</Steps>

**Tips:**

* Ask for tests that cover edge cases and error conditions
* Request both unit and integration tests when appropriate
* Have Claude explain the testing strategy

***

## Create pull requests

### Generate comprehensive PRs

**When to use:** You need to create a well-documented pull request for your changes.

<Steps>
  <Step title="Summarize your changes">
    ```
    > summarize the changes I've made to the authentication module 
    ```
  </Step>

  <Step title="Generate a PR with Claude">
    ```
    > create a pr 
    ```
  </Step>

  <Step title="Review and refine">
    ```
    > enhance the PR description with more context about the security improvements 
    ```
  </Step>

  <Step title="Add testing details">
    ```
    > add information about how these changes were tested 
    ```
  </Step>
</Steps>

**Tips:**

* Ask Claude directly to make a PR for you
* Review Claude's generated PR before submitting
* Ask Claude to highlight potential risks or considerations

## Handle documentation

### Generate code documentation

**When to use:** You need to add or update documentation for your code.

<Steps>
  <Step title="Identify undocumented code">
    ```
    > find functions without proper JSDoc comments in the auth module 
    ```
  </Step>

  <Step title="Generate documentation">
    ```
    > add JSDoc comments to the undocumented functions in auth.js 
    ```
  </Step>

  <Step title="Review and enhance">
    ```
    > improve the generated documentation with more context and examples 
    ```
  </Step>

  <Step title="Verify documentation">
    ```
    > check if the documentation follows our project standards 
    ```
  </Step>
</Steps>

**Tips:**

* Specify the documentation style you want (JSDoc, docstrings, etc.)
* Ask for examples in the documentation
* Request documentation for public APIs, interfaces, and complex logic

## Work with images

### Analyze images and screenshots

**When to use:** You need to work with images in your codebase or get Claude's help analyzing image content.

<Steps>
  <Step title="Add an image to the conversation">
    You can use any of these methods:

    1. Drag and drop an image into the Claude Code window
    2. Copy an image and paste it into the CLI with cmd+v (on Mac)
    3. Provide an image path claude "Analyze this image: /path/to/your/image.png"
  </Step>

  <Step title="Ask Claude to analyze the image">
    ```
    > What does this image show? 
    > Describe the UI elements in this screenshot 
    > Are there any problematic elements in this diagram? 
    ```
  </Step>

  <Step title="Use images for context">
    ```
    > Here's a screenshot of the error. What's causing it? 
    > This is our current database schema. How should we modify it for the new feature? 
    ```
  </Step>

  <Step title="Get code suggestions from visual content">
    ```
    > Generate CSS to match this design mockup 
    > What HTML structure would recreate this component? 
    ```
  </Step>
</Steps>

**Tips:**

* Use images when text descriptions would be unclear or cumbersome
* Include screenshots of errors, UI designs, or diagrams for better context
* You can work with multiple images in a conversation
* Image analysis works with diagrams, screenshots, mockups, and more

***

## Use extended thinking

### Leverage Claude's extended thinking for complex tasks

**When to use:** When working on complex architectural decisions, challenging bugs, or planning multi-step implementations that require deep reasoning.

<Steps>
  <Step title="Provide context and ask Claude to think">
    ```
    > I need to implement a new authentication system using OAuth2 for our API. Think deeply about the best approach for implementing this in our codebase. 
    ```

    Claude will gather relevant information from your codebase and
    use extended thinking, which will be visible in the interface.
  </Step>

  <Step title="Refine the thinking with follow-up prompts">
    ```
    > think about potential security vulnerabilities in this approach 
    > think harder about edge cases we should handle 
    ```
  </Step>
</Steps>

**Tips to get the most value out of extended thinking:**

Extended thinking is most valuable for complex tasks such as:

* Planning complex architectural changes
* Debugging intricate issues
* Creating implementation plans for new features
* Understanding complex codebases
* Evaluating tradeoffs between different approaches

The way you prompt for thinking results in varying levels of thinking depth:

* "think" triggers basic extended thinking
* intensifying phrases such as "think more", "think a lot", "think harder", or "think longer" triggers deeper thinking

For more extended thinking prompting tips, see [Extended thinking tips](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips).

<Note>
  Claude will display its thinking process as italic gray text above the
  response.
</Note>

***

## Set up project memory

### Create an effective CLAUDE.md file

**When to use:** You want to set up a CLAUDE.md file to store important project information, conventions, and frequently used commands.

<Steps>
  <Step title="Bootstrap a CLAUDE.md for your codebase">
    ```
    > /init 
    ```
  </Step>
</Steps>

**Tips:**

* Include frequently used commands (build, test, lint) to avoid repeated searches
* Document code style preferences and naming conventions
* Add important architectural patterns specific to your project
* CLAUDE.md memories can be used for both instructions shared with your team and for your individual preferences.

***

## Set up Model Context Protocol (MCP)

Model Context Protocol (MCP) is an open protocol that enables LLMs to access external tools and data sources. For more details, see the [MCP documentation](https://modelcontextprotocol.io/introduction).

<Warning>
  Use third party MCP servers at your own risk. Make sure you trust the MCP
  servers, and be especially careful when using MCP servers that talk to the
  internet, as these can expose you to prompt injection risk.
</Warning>

### Configure MCP servers

**When to use:** You want to enhance Claude's capabilities by connecting it to specialized tools and external servers using the Model Context Protocol.

<Steps>
  <Step title="Add an MCP Stdio Server">
    ```bash
    # Basic syntax
    claude mcp add <name> <command> [args...]

    # Example: Adding a local server
    claude mcp add my-server -e API_KEY=123 -- /path/to/server arg1 arg2
    ```
  </Step>

  <Step title="Add an MCP SSE Server">
    ```bash
    # Basic syntax
    claude mcp add --transport sse <name> <url>

    # Example: Adding an SSE server
    claude mcp add --transport sse sse-server https://example.com/sse-endpoint
    ```
  </Step>

  <Step title="Manage your MCP servers">
    ```bash
    # List all configured servers
    claude mcp list

    # Get details for a specific server
    claude mcp get my-server

    # Remove a server
    claude mcp remove my-server
    ```
  </Step>
</Steps>

**Tips:**

* Use the `-s` or `--scope` flag to specify where the configuration is stored:
  * `local` (default): Available only to you in the current project (was called `project` in older versions)
  * `project`: Shared with everyone in the project via `.mcp.json` file
  * `user`: Available to you across all projects (was called `global` in older versions)
* Set environment variables with `-e` or `--env` flags (e.g., `-e KEY=value`)
* Configure MCP server startup timeout using the MCP\_TIMEOUT environment variable (e.g., `MCP_TIMEOUT=10000 claude` sets a 10-second timeout)
* Check MCP server status any time using the `/mcp` command within Claude Code
* MCP follows a client-server architecture where Claude Code (the client) can connect to multiple specialized servers

### Understanding MCP server scopes

**When to use:** You want to understand how different MCP scopes work and how to share servers with your team.

<Steps>
  <Step title="Local-scoped MCP servers">
    The default scope (`local`) stores MCP server configurations in your project-specific user settings. These servers are only available to you while working in the current project.

    ```bash
    # Add a local-scoped server (default)
    claude mcp add my-private-server /path/to/server

    # Explicitly specify local scope
    claude mcp add my-private-server -s local /path/to/server
    ```
  </Step>

  <Step title="Project-scoped MCP servers (.mcp.json)">
    Project-scoped servers are stored in a `.mcp.json` file at the root of your project. This file should be checked into version control to share servers with your team.

    ```bash
    # Add a project-scoped server
    claude mcp add shared-server -s project /path/to/server
    ```

    This creates or updates a `.mcp.json` file with the following structure:

    ```json
    {
      "mcpServers": {
        "shared-server": {
          "command": "/path/to/server",
          "args": [],
          "env": {}
        }
      }
    }
    ```
  </Step>

  <Step title="User-scoped MCP servers">
    User-scoped servers are available to you across all projects on your machine, and are private to you.

    ```bash
    # Add a user server
    claude mcp add my-user-server -s user /path/to/server
    ```
  </Step>
</Steps>

**Tips:**

* Local-scoped servers take precedence over project-scoped and user-scoped servers with the same name
* Project-scoped servers (in `.mcp.json`) take precedence over user-scoped servers with the same name
* Before using project-scoped servers from `.mcp.json`, Claude Code will prompt you to approve them for security
* The `.mcp.json` file is intended to be checked into version control to share MCP servers with your team
* Project-scoped servers make it easy to ensure everyone on your team has access to the same MCP tools
* If you need to reset your choices for which project-scoped servers are enabled or disabled, use the `claude mcp reset-project-choices` command

### Connect to a Postgres MCP server

**When to use:** You want to give Claude read-only access to a PostgreSQL database for querying and schema inspection.

<Steps>
  <Step title="Add the Postgres MCP server">
    ```bash
    claude mcp add postgres-server /path/to/postgres-mcp-server --connection-string "postgresql://user:pass@localhost:5432/mydb"
    ```
  </Step>

  <Step title="Query your database with Claude">
    ```
    # In your Claude session, you can ask about your database

    > describe the schema of our users table
    > what are the most recent orders in the system?
    > show me the relationship between customers and invoices
    ```
  </Step>
</Steps>

**Tips:**

* The Postgres MCP server provides read-only access for safety
* Claude can help you explore database structure and run analytical queries
* You can use this to quickly understand database schemas in unfamiliar projects
* Make sure your connection string uses appropriate credentials with minimum required permissions

### Add MCP servers from JSON configuration

**When to use:** You have a JSON configuration for a single MCP server that you want to add to Claude Code.

<Steps>
  <Step title="Add an MCP server from JSON">
    ```bash
    # Basic syntax
    claude mcp add-json <name> '<json>'

    # Example: Adding a stdio server with JSON configuration
    claude mcp add-json weather-api '{"type":"stdio","command":"/path/to/weather-cli","args":["--api-key","abc123"],"env":{"CACHE_DIR":"/tmp"}}'
    ```
  </Step>

  <Step title="Verify the server was added">
    ```bash
    claude mcp get weather-api
    ```
  </Step>
</Steps>

**Tips:**

* Make sure the JSON is properly escaped in your shell
* The JSON must conform to the MCP server configuration schema
* You can use `-s global` to add the server to your global configuration instead of the project-specific one

### Import MCP servers from Claude Desktop

**When to use:** You have already configured MCP servers in Claude Desktop and want to use the same servers in Claude Code without manually reconfiguring them.

<Steps>
  <Step title="Import servers from Claude Desktop">
    ```bash
    # Basic syntax 
    claude mcp add-from-claude-desktop 
    ```
  </Step>

  <Step title="Select which servers to import">
    After running the command, you'll see an interactive dialog that allows you to select which servers you want to import.
  </Step>

  <Step title="Verify the servers were imported">
    ```bash
    claude mcp list 
    ```
  </Step>
</Steps>

**Tips:**

* This feature only works on macOS and Windows Subsystem for Linux (WSL)
* It reads the Claude Desktop configuration file from its standard location on those platforms
* Use the `-s global` flag to add servers to your global configuration
* Imported servers will have the same names as in Claude Desktop
* If servers with the same names already exist, they will get a numerical suffix (e.g., `server_1`)

### Use Claude Code as an MCP server

**When to use:** You want to use Claude Code itself as an MCP server that other applications can connect to, providing them with Claude's tools and capabilities.

<Steps>
  <Step title="Start Claude as an MCP server">
    ```bash
    # Basic syntax
    claude mcp serve
    ```
  </Step>

  <Step title="Connect from another application">
    You can connect to Claude Code MCP server from any MCP client, such as Claude Desktop. If you're using Claude Desktop, you can add the Claude Code MCP server using this configuration:

    ```json
    {
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
    ```
  </Step>
</Steps>

**Tips:**

* The server provides access to Claude's tools like View, Edit, LS, etc.
* In Claude Desktop, try asking Claude to read files in a directory, make edits, and more.
* Note that this MCP server is simply exposing Claude Code's tools to your MCP client, so your own client is responsible for implementing user confirmation for individual tool calls.

***

## Use Claude as a unix-style utility

### Add Claude to your verification process

**When to use:** You want to use Claude Code as a linter or code reviewer.

**Steps:**

<Steps>
  <Step title="Add Claude to your build script">
    ```json
    // package.json
    {
        ...
        "scripts": {
            ...
            "lint:claude": "claude -p 'you are a linter. please look at the changes vs. main and report any issues related to typos. report the filename and line number on one line, and a description of the issue on the second line. do not return any other text.'"
        }
    }
    ```
  </Step>
</Steps>

### Pipe in, pipe out

**When to use:** You want to pipe data into Claude, and get back data in a structured format.

<Steps>
  <Step title="Pipe data through Claude">
    ```bash
    cat build-error.txt | claude -p 'concisely explain the root cause of this build error' > output.txt
    ```
  </Step>
</Steps>

### Control output format

**When to use:** You need Claude's output in a specific format, especially when integrating Claude Code into scripts or other tools.

<Steps>
  <Step title="Use text format (default)">
    ```bash
    cat data.txt | claude -p 'summarize this data' --output-format text > summary.txt
    ```

    This outputs just Claude's plain text response (default behavior).
  </Step>

  <Step title="Use JSON format">
    ```bash
    cat code.py | claude -p 'analyze this code for bugs' --output-format json > analysis.json
    ```

    This outputs a JSON array of messages with metadata including cost and duration.
  </Step>

  <Step title="Use streaming JSON format">
    ```bash
    cat log.txt | claude -p 'parse this log file for errors' --output-format stream-json
    ```

    This outputs a series of JSON objects in real-time as Claude processes the request. Each message is a valid JSON object, but the entire output is not valid JSON if concatenated.
  </Step>
</Steps>

**Tips:**

* Use `--output-format text` for simple integrations where you just need Claude's response
* Use `--output-format json` when you need the full conversation log
* Use `--output-format stream-json` for real-time output of each conversation turn

***

## Create custom slash commands

Claude Code supports custom slash commands that you can create to quickly execute specific prompts or tasks.

### Create project-specific commands

**When to use:** You want to create reusable slash commands for your project that all team members can use.

<Steps>
  <Step title="Create a commands directory in your project">
    ```bash
    mkdir -p .claude/commands
    ```
  </Step>

  <Step title="Create a Markdown file for each command">
    ```bash
    echo "Analyze the performance of this code and suggest three specific optimizations:" > .claude/commands/optimize.md 
    ```
  </Step>

  <Step title="Use your custom command in Claude Code">
    ```bash
    claude > /project:optimize 
    ```
  </Step>
</Steps>

**Tips:**

* Command names are derived from the filename (e.g., `optimize.md` becomes `/project:optimize`)
* You can organize commands in subdirectories (e.g., `.claude/commands/frontend/component.md` becomes `/project:frontend:component`)
* Project commands are available to everyone who clones the repository
* The Markdown file content becomes the prompt sent to Claude when the command is invoked

### Add command arguments with \$ARGUMENTS

**When to use:** You want to create flexible slash commands that can accept additional input from users.

<Steps>
  <Step title="Create a command file with the $ARGUMENTS placeholder">
    ```bash
    echo "Find and fix issue #$ARGUMENTS. Follow these steps: 1.
    Understand the issue described in the ticket 2. Locate the relevant code in
    our codebase 3. Implement a solution that addresses the root cause 4. Add
    appropriate tests 5. Prepare a concise PR description" >
    .claude/commands/fix-issue.md 
    ```
  </Step>

  <Step title="Use the command with an issue number">
    ```bash
    claude > /project:fix-issue 123 
    ```

    This will replace \$ARGUMENTS with "123" in the prompt.
  </Step>
</Steps>

**Tips:**

* The \$ARGUMENTS placeholder is replaced with any text that follows the command
* You can position \$ARGUMENTS anywhere in your command template
* Other useful applications: generating test cases for specific functions, creating documentation for components, reviewing code in particular files, or translating content to specified languages

### Create personal slash commands

**When to use:** You want to create personal slash commands that work across all your projects.

<Steps>
  <Step title="Create a commands directory in your home folder">
    ```bash
    mkdir -p ~/.claude/commands 
    ```
  </Step>

  <Step title="Create a Markdown file for each command">
    ```bash
    echo "Review this code for security vulnerabilities, focusing on:" >
    ~/.claude/commands/security-review.md 
    ```
  </Step>

  <Step title="Use your personal custom command">
    ```bash
    claude > /user:security-review 
    ```
  </Step>
</Steps>

**Tips:**

* Personal commands are prefixed with `/user:` instead of `/project:`
* Personal commands are only available to you and not shared with your team
* Personal commands work across all your projects
* You can use these for consistent workflows across different codebases

***

## Run parallel Claude Code sessions with Git worktrees

### Use worktrees for isolated coding environments

**When to use:** You need to work on multiple tasks simultaneously with complete code isolation between Claude Code instances.

<Steps>
  <Step title="Understand Git worktrees">
    Git worktrees allow you to check out multiple branches from the same
    repository into separate directories. Each worktree has its own working
    directory with isolated files, while sharing the same Git history. Learn
    more in the [official Git worktree
    documentation](https://git-scm.com/docs/git-worktree).
  </Step>

  <Step title="Create a new worktree">
    ```bash
    # Create a new worktree with a new branch 
    git worktree add ../project-feature-a -b feature-a

    # Or create a worktree with an existing branch
    git worktree add ../project-bugfix bugfix-123
    ```

    This creates a new directory with a separate working copy of your repository.
  </Step>

  <Step title="Run Claude Code in each worktree">
    ```bash
    # Navigate to your worktree 
    cd ../project-feature-a

    # Run Claude Code in this isolated environment
    claude
    ```
  </Step>

  <Step>
    In another terminal:

    ```bash
    cd ../project-bugfix
    claude
    ```
  </Step>

  <Step title="Manage your worktrees">
    ```bash
    # List all worktrees
    git worktree list

    # Remove a worktree when done
    git worktree remove ../project-feature-a
    ```
  </Step>
</Steps>

**Tips:**

* Each worktree has its own independent file state, making it perfect for parallel Claude Code sessions
* Changes made in one worktree won't affect others, preventing Claude instances from interfering with each other
* All worktrees share the same Git history and remote connections
* For long-running tasks, you can have Claude working in one worktree while you continue development in another
* Use descriptive directory names to easily identify which task each worktree is for
* Remember to initialize your development environment in each new worktree according to your project's setup. Depending on your stack, this might include:
  * JavaScript projects: Running dependency installation (`npm install`, `yarn`)
  * Python projects: Setting up virtual environments or installing with package managers
  * Other languages: Following your project's standard setup process

***

## Next steps

<Card title="Claude Code reference implementation" icon="code" href="https://github.com/anthropics/claude-code/tree/main/.devcontainer">
  Clone our development container reference implementation.
</Card>



# Troubleshooting

> Solutions for common issues with Claude Code installation and usage.

## Common installation issues

### Linux permission issues

When installing Claude Code with npm, you may encounter permission errors if your npm global prefix is not user writable (eg. `/usr`, or `/usr/local`).

#### Recommended solution: Create a user-writable npm prefix

The safest approach is to configure npm to use a directory within your home folder:

```bash
# First, save a list of your existing global packages for later migration
npm list -g --depth=0 > ~/npm-global-packages.txt

# Create a directory for your global packages
mkdir -p ~/.npm-global

# Configure npm to use the new directory path
npm config set prefix ~/.npm-global

# Note: Replace ~/.bashrc with ~/.zshrc, ~/.profile, or other appropriate file for your shell
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc

# Apply the new PATH setting
source ~/.bashrc

# Now reinstall Claude Code in the new location
npm install -g @anthropic-ai/claude-code

# Optional: Reinstall your previous global packages in the new location
# Look at ~/npm-global-packages.txt and install packages you want to keep
```

This solution is recommended because it:

* Avoids modifying system directory permissions
* Creates a clean, dedicated location for your global npm packages
* Follows security best practices

#### System Recovery: If you have run commands that change ownership and permissions of system files or similar

If you've already run a command that changed system directory permissions (such as `sudo chown -R $USER:$(id -gn) /usr && sudo chmod -R u+w /usr`) and your system is now broken (for example, if you see `sudo: /usr/bin/sudo must be owned by uid 0 and have the setuid bit set`), you'll need to perform recovery steps.

##### Ubuntu/Debian Recovery Method:

1. While rebooting, hold **SHIFT** to access the GRUB menu

2. Select "Advanced options for Ubuntu/Debian"

3. Choose the recovery mode option

4. Select "Drop to root shell prompt"

5. Remount the filesystem as writable:
   ```bash
   mount -o remount,rw /
   ```

6. Fix permissions:

   ```bash
   # Restore root ownership
   chown -R root:root /usr
   chmod -R 755 /usr

   # Ensure /usr/local is owned by your user for npm packages
   chown -R YOUR_USERNAME:YOUR_USERNAME /usr/local

   # Set setuid bit for critical binaries
   chmod u+s /usr/bin/sudo
   chmod 4755 /usr/bin/sudo
   chmod u+s /usr/bin/su
   chmod u+s /usr/bin/passwd
   chmod u+s /usr/bin/newgrp
   chmod u+s /usr/bin/gpasswd
   chmod u+s /usr/bin/chsh
   chmod u+s /usr/bin/chfn

   # Fix sudo configuration
   chown root:root /usr/libexec/sudo/sudoers.so
   chmod 4755 /usr/libexec/sudo/sudoers.so
   chown root:root /etc/sudo.conf
   chmod 644 /etc/sudo.conf
   ```

7. Reinstall affected packages (optional but recommended):

   ```bash
   # Save list of installed packages
   dpkg --get-selections > /tmp/installed_packages.txt

   # Reinstall them
   awk '{print $1}' /tmp/installed_packages.txt | xargs -r apt-get install --reinstall -y
   ```

8. Reboot:
   ```bash
   reboot
   ```

##### Alternative Live USB Recovery Method:

If the recovery mode doesn't work, you can use a live USB:

1. Boot from a live USB (Ubuntu, Debian, or any Linux distribution)

2. Find your system partition:
   ```bash
   lsblk
   ```

3. Mount your system partition:
   ```bash
   sudo mount /dev/sdXY /mnt  # replace sdXY with your actual system partition
   ```

4. If you have a separate boot partition, mount it too:
   ```bash
   sudo mount /dev/sdXZ /mnt/boot  # if needed
   ```

5. Chroot into your system:

   ```bash
   # For Ubuntu/Debian:
   sudo chroot /mnt

   # For Arch-based systems:
   sudo arch-chroot /mnt
   ```

6. Follow steps 6-8 from the Ubuntu/Debian recovery method above

After restoring your system, follow the recommended solution above to set up a user-writable npm prefix.

## Auto-updater issues

If Claude Code can't update automatically, it may be due to permission issues with your npm global prefix directory. Follow the [recommended solution](#recommended-solution-create-a-user-writable-npm-prefix) above to fix this.

If you prefer to disable the auto-updater instead, you can use:
If you prefer to disable the auto-updater instead , you can
set the `DISABLE_AUTOUPDATER` [environment variable](settings#environment-variables) to `1`

## Permissions and authentication

### Repeated permission prompts

If you find yourself repeatedly approving the same commands, you can allow specific tools
to run without approval using the `/permissions` command. See [Permissions docs](settings#permissions).

### Authentication issues

If you're experiencing authentication problems:

1. Run `/logout` to sign out completely
2. Close Claude Code
3. Restart with `claude` and complete the authentication process again

If problems persist, try:

```bash
rm -rf ~/.config/claude-code/auth.json
claude
```

This removes your stored authentication information and forces a clean login.

## Performance and stability

### High CPU or memory usage

Claude Code is designed to work with most development environments, but may consume significant resources when processing large codebases. If you're experiencing performance issues:

1. Use `/compact` regularly to reduce context size
2. Close and restart Claude Code between major tasks
3. Consider adding large build directories to your `.gitignore` file

### Command hangs or freezes

If Claude Code seems unresponsive:

1. Press Ctrl+C to attempt to cancel the current operation
2. If unresponsive, you may need to close the terminal and restart

### ESC key not working in JetBrains (IntelliJ, PyCharm, etc.) terminals

If you're using Claude Code in JetBrains terminals and the ESC key doesn't interrupt the agent as expected, this is likely due to a keybinding clash with JetBrains' default shortcuts.

To fix this issue:

1. Go to Settings → Tools → Terminal
2. Click the "Configure terminal keybindings" hyperlink next to "Override IDE Shortcuts"
3. Within the terminal keybindings, scroll down to "Switch focus to Editor" and delete that shortcut

This will allow the ESC key to properly function for canceling Claude Code operations instead of being captured by PyCharm's "Switch focus to Editor" action.

## Getting more help

If you're experiencing issues not covered here:

1. Use the `/bug` command within Claude Code to report problems directly to Anthropic
2. Check the [GitHub repository](https://github.com/anthropics/claude-code) for known issues
3. Run `/doctor` to check the health of your Claude Code installation





# Overview

Claude Code can integrate with various third-party services and infrastructure to meet enterprise requirements. This page provides an overview of available integration options and helps you choose the right configuration for your organization.

## Provider comparison

<table>
  <thead>
    <tr>
      <th>Feature</th>
      <th>Anthropic</th>
      <th>Amazon Bedrock</th>
      <th>Google Vertex AI</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td>Regions</td>
      <td>Supported [countries](https://www.anthropic.com/supported-countries)</td>
      <td>Multiple AWS [regions](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)</td>
      <td>Multiple GCP [regions](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations)</td>
    </tr>

    <tr>
      <td>Prompt caching</td>
      <td>Enabled by default</td>
      <td>Contact AWS for enablement</td>
      <td>Contact Google for enablement</td>
    </tr>

    <tr>
      <td>Authentication</td>
      <td>API key</td>
      <td>AWS credentials (IAM)</td>
      <td>GCP credentials (OAuth/Service Account)</td>
    </tr>

    <tr>
      <td>Cost tracking</td>
      <td>Dashboard</td>
      <td>AWS Cost Explorer</td>
      <td>GCP Billing</td>
    </tr>

    <tr>
      <td>Enterprise features</td>
      <td>Teams, usage monitoring</td>
      <td>IAM policies, CloudTrail</td>
      <td>IAM roles, Cloud Audit Logs</td>
    </tr>
  </tbody>
</table>

## Integration options

### Cloud providers

<CardGroup cols={2}>
  <Card title="Amazon Bedrock" icon="aws" href="/en/docs/claude-code/amazon-bedrock">
    Use Claude models through AWS infrastructure with IAM-based authentication and AWS-native monitoring
  </Card>

  <Card title="Google Vertex AI" icon="google" href="/en/docs/claude-code/google-vertex-ai">
    Access Claude models via Google Cloud Platform with enterprise-grade security and compliance
  </Card>
</CardGroup>

### Corporate infrastructure

<CardGroup cols={2}>
  <Card title="Corporate Proxy" icon="shield" href="/en/docs/claude-code/corporate-proxy">
    Configure Claude Code to work with your organization's proxy servers and SSL/TLS requirements
  </Card>

  <Card title="LLM Gateway" icon="server" href="/en/docs/claude-code/llm-gateway">
    Deploy centralized model access with usage tracking, budgeting, and audit logging
  </Card>
</CardGroup>

## Mixing and matching settings

Claude Code supports flexible configuration options that allow you to combine different providers and infrastructure:

<Note>
  Understand the difference between:

  * **Corporate proxy**: An HTTP/HTTPS proxy for routing traffic (set via `HTTPS_PROXY` or `HTTP_PROXY`)
  * **LLM Gateway**: A service that handles authentication and provides provider-compatible endpoints (set via `ANTHROPIC_BASE_URL`, `ANTHROPIC_BEDROCK_BASE_URL`, or `ANTHROPIC_VERTEX_BASE_URL`)

  Both configurations can be used in tandem.
</Note>

### Using Bedrock with corporate proxy

Route Bedrock traffic through a corporate HTTP/HTTPS proxy:

```bash
# Enable Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1

# Configure corporate proxy
export HTTPS_PROXY='https://proxy.example.com:8080'
```

### Using Bedrock with LLM Gateway

Use a gateway service that provides Bedrock-compatible endpoints:

```bash
# Enable Bedrock
export CLAUDE_CODE_USE_BEDROCK=1

# Configure LLM gateway
export ANTHROPIC_BEDROCK_BASE_URL='https://your-llm-gateway.com/bedrock'
export CLAUDE_CODE_SKIP_BEDROCK_AUTH=1  # If gateway handles AWS auth
```

### Using Vertex AI with corporate proxy

Route Vertex AI traffic through a corporate HTTP/HTTPS proxy:

```bash
# Enable Vertex
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
export ANTHROPIC_VERTEX_PROJECT_ID=your-project-id

# Configure corporate proxy
export HTTPS_PROXY='https://proxy.example.com:8080'
```

### Using Vertex AI with LLM Gateway

Combine Google Vertex AI models with an LLM gateway for centralized management:

```bash
# Enable Vertex
export CLAUDE_CODE_USE_VERTEX=1

# Configure LLM gateway
export ANTHROPIC_VERTEX_BASE_URL='https://your-llm-gateway.com/vertex'
export CLAUDE_CODE_SKIP_VERTEX_AUTH=1  # If gateway handles GCP auth
```

### Authentication configuration

Claude Code uses the `ANTHROPIC_AUTH_TOKEN` for both `Authorization` and `Proxy-Authorization` headers when needed. The `SKIP_AUTH` flags (`CLAUDE_CODE_SKIP_BEDROCK_AUTH`, `CLAUDE_CODE_SKIP_VERTEX_AUTH`) are used in LLM gateway scenarios where the gateway handles provider authentication.

## Choosing the right integration

Consider these factors when selecting your integration approach:

### Direct provider access

Best for organizations that:

* Want the simplest setup
* Have existing AWS or GCP infrastructure
* Need provider-native monitoring and compliance

### Corporate proxy

Best for organizations that:

* Have existing corporate proxy requirements
* Need traffic monitoring and compliance
* Must route all traffic through specific network paths

### LLM Gateway

Best for organizations that:

* Need usage tracking across teams
* Want to dynamically switch between models
* Require custom rate limiting or budgets
* Need centralized authentication management

## Debugging

When debugging your third-party integration configuration:

* Use the `claude /status` [slash command](/en/docs/claude-code/cli-usage#slash-command). This command provides observability into any applied authentication, proxy, and URL settings.
* Set environment variable `export ANTHROPIC_LOG=debug` to log requests.

## Next steps

* [Set up Amazon Bedrock](/en/docs/claude-code/amazon-bedrock) for AWS-native integration
* [Configure Google Vertex AI](/en/docs/claude-code/google-vertex-ai) for GCP deployment
* [Implement Corporate Proxy](/en/docs/claude-code/corporate-proxy) for network requirements
* [Deploy LLM Gateway](/en/docs/claude-code/llm-gateway) for enterprise management
* [Settings](/en/docs/claude-code/settings) for configuration options and environment variables





# Amazon Bedrock integration

This page provides instructions on configuring Claude Code through Amazon Bedrock, including setup, IAM configuration, cost tracking, and troubleshooting.

## Prerequisites

Before configuring Claude Code with Bedrock, ensure you have:

* An AWS account with Bedrock access enabled
* Access to desired Claude models (e.g., Claude Sonnet 4) in Bedrock
* AWS CLI installed and configured (optional - only needed if you don't have another mechanism for getting credentials)
* Appropriate IAM permissions

## Setup

### 1. Enable model access

First, ensure you have access to the required Claude models in your AWS account:

1. Navigate to the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock/)
2. Go to **Model access** in the left navigation
3. Request access to desired Claude models (e.g., Claude Sonnet 4)
4. Wait for approval (usually instant for most regions)

### 2. Configure AWS credentials

Claude Code uses the default AWS SDK credential chain. Set up your credentials using one of these methods:

<Note>
  Claude Code does not currently support dynamic credential management (such as automatically calling `aws sts assume-role`). You will need to run `aws configure`, `aws sso login`, or set the `AWS_` environment variables yourself.
</Note>

**Option A: AWS CLI configuration**

```bash
aws configure
```

**Option B: Environment variables (access key)**

```bash
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_SESSION_TOKEN=your-session-token
```

**Option C: Environment variables (SSO profile)**

```bash
aws sso login --profile=<your-profile-name>

export AWS_PROFILE=your-profile-name
```

### 3. Configure Claude Code

Set the following environment variables to enable Bedrock:

```bash
# Enable Bedrock integration
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1  # or your preferred region
```

<Note>
  `AWS_REGION` is a required environment variable. Claude Code does not read from the `.aws` config file for this setting.
</Note>

```bash
# Optional: Disable prompt caching if not enabled in your account
export DISABLE_PROMPT_CACHING=1
```

<Note>
  Contact AWS support to enable prompt caching for reduced costs and higher rate limits. Once enabled, remove the `DISABLE_PROMPT_CACHING` setting.
</Note>

### 4. Model configuration

Claude Code uses these default models for Bedrock:

| Model type       | Default value                                  |
| :--------------- | :--------------------------------------------- |
| Primary model    | `us.anthropic.claude-3-7-sonnet-20250219-v1:0` |
| Small/fast model | `us.anthropic.claude-3-5-haiku-20241022-v1:0`  |

To customize models, use one of these methods:

```bash
# Using inference profile ID
export ANTHROPIC_MODEL='us.anthropic.claude-opus-4-20250514-v1:0'
export ANTHROPIC_SMALL_FAST_MODEL='us.anthropic.claude-3-5-haiku-20241022-v1:0'

# Using application inference profile ARN
export ANTHROPIC_MODEL='arn:aws:bedrock:us-east-2:your-account-id:application-inference-profile/your-model-id'
```

## IAM configuration

Create an IAM policy with the required permissions for Claude Code.

For details, see [Bedrock IAM documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html).

<Note>
  We recommend creating a dedicated AWS account for Claude Code to simplify cost tracking and access control.
</Note>

## Troubleshooting

If you encounter region issues:

* Check model availability: `aws bedrock list-inference-profiles --region your-region`
* Switch to a supported region: `export AWS_REGION=us-east-1`
* Consider using inference profiles for cross-region access

If you receive an error "on-demand throughput isn’t supported":

* Specify the model as an [inference profile](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) ID

## Additional resources

* [Bedrock documentation](https://docs.aws.amazon.com/bedrock/)
* [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
* [Bedrock inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html)



# Google Vertex AI integration

This page provides instructions on configuring Claude Code through Google Vertex AI, including setup, IAM configuration, cost tracking, and troubleshooting.

## Prerequisites

Before configuring Claude Code with Vertex AI, ensure you have:

* A Google Cloud Platform (GCP) account with billing enabled
* A GCP project with Vertex AI API enabled
* Access to desired Claude models (e.g., Claude Sonnet 4)
* Google Cloud SDK (`gcloud`) installed and configured
* Quota allocated in desired GCP region

<Warning>
  Vertex AI may not support the Claude Code default models on non-`us-east5` regions. Ensure you are using `us-east5` and have quota allocated, or switch to supported models.
</Warning>

## Setup

### 1. Enable Vertex AI API

Enable the Vertex AI API in your GCP project:

```bash
# Set your project ID
gcloud config set project YOUR-PROJECT-ID

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

### 2. Request model access

Request access to Claude models in Vertex AI:

1. Navigate to the [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
2. Search for "Claude" models
3. Request access to desired Claude models (e.g., Claude Sonnet 4)
4. Wait for approval (may take 24-48 hours)

### 3. Configure GCP credentials

Claude Code uses standard Google Cloud authentication.

For more information, see [Google Cloud authentication documentation](https://cloud.google.com/docs/authentication).

### 4. Configure Claude Code

Set the following environment variables:

```bash
# Enable Vertex AI integration
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
export ANTHROPIC_VERTEX_PROJECT_ID=YOUR-PROJECT-ID

# Optional: Disable prompt caching if not enabled
export DISABLE_PROMPT_CACHING=1
```

<Note>
  For heightened rate limits and prompt caching enablement, contact Google Cloud support. Once enabled, remove the `DISABLE_PROMPT_CACHING` setting.
</Note>

### 5. Model configuration

Claude Code uses these default models for Vertex AI:

| Model type       | Default value               |
| :--------------- | :-------------------------- |
| Primary model    | `claude-sonnet-4@20250514`  |
| Small/fast model | `claude-3-5-haiku@20241022` |

To customize models:

```bash
export ANTHROPIC_MODEL='claude-opus-4@20250514'
export ANTHROPIC_SMALL_FAST_MODEL='claude-3-5-haiku@20241022'
```

## IAM configuration

Grant the required IAM roles for Claude Code.

For details, see [Vertex IAM documentation](https://cloud.google.com/vertex-ai/docs/general/access-control).

<Note>
  We recommend creating a dedicated GCP project for Claude Code to simplify cost tracking and access control.
</Note>

## Troubleshooting

If you encounter quota issues:

* Check current quotas or request quota increase through [Cloud Console](https://cloud.google.com/docs/quotas/view-manage)

If you encounter "model not found" 404 errors:

* Verify you have access to the specified region
* Confirm model is Enabled in [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)

If you encounter 429 errors:

* Ensure the primary model and small/fast model are supported in your selected region

## Additional resources

* [Vertex AI documentation](https://cloud.google.com/vertex-ai/docs)
* [Vertex AI pricing](https://cloud.google.com/vertex-ai/pricing)
* [Vertex AI quotas and limits](https://cloud.google.com/vertex-ai/docs/quotas)



# Corporate proxy configuration

This page covers how to configure Claude Code to work with corporate proxy servers, including environment variable configuration, authentication, and SSL/TLS certificate handling.

## Overview

Claude Code supports standard HTTP/HTTPS proxy configurations through environment variables. This allows you to route all Claude Code traffic through your organization's proxy servers for security, compliance, and monitoring purposes.

## Basic proxy configuration

### Environment variables

Claude Code respects standard proxy environment variables:

```bash
# HTTPS proxy (recommended)
export HTTPS_PROXY=https://proxy.example.com:8080

# HTTP proxy (if HTTPS not available)
export HTTP_PROXY=http://proxy.example.com:8080
```

<Note>
  Claude Code currently does not support the `NO_PROXY` environment variable. All traffic will be routed through the configured proxy.
</Note>

<Note>
  Claude Code does not support SOCKS proxies.
</Note>

## Authentication

### Basic authentication

If your proxy requires basic authentication, include credentials in the proxy URL:

```bash
export HTTPS_PROXY=http://username:password@proxy.example.com:8080
```

<Warning>
  Avoid hardcoding passwords in scripts. Use environment variables or secure credential storage instead.
</Warning>

<Tip>
  For proxies requiring advanced authentication (NTLM, Kerberos, etc.), consider using an LLM Gateway service that supports your authentication method.
</Tip>

### SSL certificate issues

If your proxy uses custom SSL certificates, you may encounter certificate errors.

Ensure that you set the correct certificate bundle path:

```bash
export SSL_CERT_FILE=/path/to/certificate-bundle.crt
export NODE_EXTRA_CA_CERTS=/path/to/certificate-bundle.crt
```

## Additional resources

* [Claude Code settings](/en/docs/claude-code/settings)
* [Environment variables reference](/en/docs/claude-code/settings#environment-variables)
* [Troubleshooting guide](/en/docs/claude-code/troubleshooting)


# LLM gateway configuration

This page covers how to configure Claude Code with LLM gateway solutions, including LiteLLM setup, authentication methods, and enterprise features like usage tracking and budget management.

## Overview

LLM gateways provide a centralized proxy layer between Claude Code and model providers, offering:

* **Centralized authentication** - Single point for API key management
* **Usage tracking** - Monitor usage across teams and projects
* **Cost controls** - Implement budgets and rate limits
* **Audit logging** - Track all model interactions for compliance
* **Model routing** - Switch between providers without code changes

## LiteLLM configuration

<Note>
  LiteLLM is a third-party proxy service. Anthropic doesn't endorse, maintain, or audit LiteLLM's security or functionality. This guide is provided for informational purposes and may become outdated. Use at your own discretion.
</Note>

### Prerequisites

* Claude Code updated to the latest version
* LiteLLM Proxy Server deployed and accessible
* Access to Claude models through your chosen provider

### Basic LiteLLM setup

**Configure Claude Code**:

#### Authentication methods

##### Static API key

Simplest method using a fixed API key:

```bash
# Set in environment
export ANTHROPIC_AUTH_TOKEN=sk-litellm-static-key

# Or in Claude Code settings
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-litellm-static-key"
  }
}
```

This value will be sent as the `Authorization` and `Proxy-Authorization` headers, although `Authorization` may be overwritten (see Vertex "Client-specified credentials" below).

##### Dynamic API key with helper

For rotating keys or per-user authentication:

1. Create an API key helper script:

```bash
#!/bin/bash
# ~/bin/get-litellm-key.sh

# Example: Fetch key from vault
vault kv get -field=api_key secret/litellm/claude-code

# Example: Generate JWT token
jwt encode \
  --secret="${JWT_SECRET}" \
  --exp="+1h" \
  '{"user":"'${USER}'","team":"engineering"}'
```

2. Configure Claude Code settings to use the helper:

```json
{
  "apiKeyHelper": "~/bin/get-litellm-key.sh"
}
```

3. Set token refresh interval:

```bash
# Refresh every hour (3600000 ms)
export CLAUDE_CODE_API_KEY_HELPER_TTL_MS=3600000
```

This value will be sent as `Authorization`, `Proxy-Authorization`, and `X-Api-Key` headers, although `Authorization` may be overwritten (see [Google Vertex AI through LiteLLM](#google-vertex-ai-through-litellm)). The `apiKeyHelper` has lower precedence than `ANTHROPIC_AUTH_TOKEN` or `ANTHROPIC_API_KEY`.

#### Provider-specific configurations

##### Anthropic API through LiteLLM

Using [pass-through endpoint](https://docs.litellm.ai/docs/pass_through/anthropic_completion):

```bash
export ANTHROPIC_BASE_URL=https://litellm-server:4000/anthropic
```

##### Amazon Bedrock through LiteLLM

Using [pass-through endpoint](https://docs.litellm.ai/docs/pass_through/bedrock):

```bash
export ANTHROPIC_BEDROCK_BASE_URL=https://litellm-server:4000/bedrock
export CLAUDE_CODE_SKIP_BEDROCK_AUTH=1
export CLAUDE_CODE_USE_BEDROCK=1
```

##### Google Vertex AI through LiteLLM

Using [pass-through endpoint](https://docs.litellm.ai/docs/pass_through/vertex_ai):

**Recommended: Proxy-specified credentials**

```bash
export ANTHROPIC_VERTEX_BASE_URL=https://litellm-server:4000/vertex_ai/v1
export ANTHROPIC_VERTEX_PROJECT_ID=your-gcp-project-id
export CLAUDE_CODE_SKIP_VERTEX_AUTH=1
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
```

**Alternative: Client-specified credentials**

If you prefer to use local GCP credentials:

1. Authenticate with GCP locally:

```bash
gcloud auth application-default login
```

2. Set Claude Code environment:

```bash
export ANTHROPIC_VERTEX_BASE_URL=https://litellm-server:4000/vertex_ai/v1
export ANTHROPIC_VERTEX_PROJECT_ID=your-gcp-project-id
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
```

3. Update LiteLLM header configuration:

Ensure your LiteLLM config has `general_settings.litellm_key_header_name` set to `Proxy-Authorization`, since the pass-through GCP token will be located on the `Authorization` header.

#### Unified endpoint

Using LiteLLM's [Anthropic format endpoint](https://docs.litellm.ai/docs/anthropic_unified):

```bash
export ANTHROPIC_BASE_URL=https://litellm-server:4000
```

### Model selection

By default, the models will use those specified in [Model configuration](/en/docs/claude-code/bedrock-vertex-proxies#model-configuration).

If you have configured custom model names in LiteLLM, set the aforementioned environment variables to those custom names.

For more detailed information, refer to the [LiteLLM documentation](https://docs.litellm.ai/).

## Additional resources

* [LiteLLM documentation](https://docs.litellm.ai/)
* [Claude Code settings](/en/docs/claude-code/settings)
* [Corporate proxy setup](/en/docs/claude-code/corporate-proxy)
* [Third-party integrations overview](/en/docs/claude-code/third-party-integrations)

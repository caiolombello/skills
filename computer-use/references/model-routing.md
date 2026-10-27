# Model and runtime routing

Use this only when choosing a computer-use worker or reconciling provider guidance. Discover the live provider/model/options and the actual child's tool surface; model names below are a dated starting preference, not a permanent ranking or permission to switch.

## Initial preference

This personal library's starting preference is OpenAI for visual interaction. As reviewed on 2026-10-27, official documentation positions `gpt-6.1-terra` for visual reasoning and precise computer use. Start with Terra at medium effort for a clear, bounded interaction; Sol at medium for mixed coding/UI work; consider Astra for difficult investigation or uncertain multi-step work. Increase effort when evidence justifies the extra cost. Preserve explicit user model/provider choices and supported runtime settings.

Check the current catalog before selecting these models. If the requested model/provider is unavailable, say so without silently substituting. Do not assume an API model alias is a valid Codex/Cursor/other harness slug. No controlled comparison in this library establishes that OpenAI wins every GUI task.

Keep the work in the main loop when it already has suitable tools/model/context. Delegate when a different supported model or an isolated surface adds a concrete benefit. A child needs the target, authorized actions and exclusions, starting evidence, tool/session access, control ownership, finish condition, and required readback. A screenshot handed to a child can support analysis; it does not transfer control. Never place secrets in the brief.

Judge routing with comparable isolated tasks: same tool surface, start state, completion checks, and permissions. Record completion, unintended effects, retries, human intervention, latency/cost when available, and remaining uncertainty. Do not infer model quality from a missing tool or login. A synthetic routing exercise is not a live computer-use benchmark.

## Provider guidance is not an installed integration

- **T3:** use [delegation](../../t3-workflows/references/delegation.md) and [surfaces/context](../../t3-workflows/references/surfaces-and-context.md). Cross-provider delegation must use the host's supported orchestration. It cannot grant missing desktop tools or transfer tab ownership implicitly.
- **Hermes:** its `computer_use` actions wrap cua-driver. Element indices, `effect`, `delivery_mode`, auxiliary vision, and focus guarantees are wrapper/driver contracts, not portable tools. Read the installed tool schema before using them. Do not install Hermes/cua-driver merely because the source skill mentions installation. Reject its suggestion to split blocked commands to evade a guard.
- **OpenAI/Anthropic APIs:** model calls and action execution are distinct. An integration must supply an allowed driver/environment, preserve its state, execute actions, return observations, verify effects, and clean up. SDK code and client toolsets in documentation are not callable tools in this session. Do not build or install an API integration unless requested.

## Sources reviewed

- [OpenAI model selection](https://developers.openai.com/api/docs/guides/latest-model) and [computer use](https://developers.openai.com/api/docs/guides/tools-computer-use).
- [Anthropic computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool).
- [Hermes computer-use v2.1.0](https://github.com/NousResearch/hermes-agent/blob/69f73ec5f11f5a945cc864f29c4e2ad2307eaec3/skills/autonomous-ai-agents/computer-use/SKILL.md), MIT, Francesco Bonacci and Hermes Agent. Adapted principles only; no driver or upstream executable copied.

Refresh current official guidance when implementing an integration or making a new version-sensitive claim. Live runtime instructions and actual permissions govern actions.

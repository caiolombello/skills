# Delegation in T3 Code

Read current orchestration instructions first. Use [dispatching-parallel-agents](../../dispatching-parallel-agents/SKILL.md) for independence, briefs, and integration; this reference owns only host-specific choices.

## Choose the mechanism

- Use the native subagent tool when the child uses the current provider, a model it offers, needs no settings beyond yours, and finishes in this turn. Follow the host's synchronous/background rules.
- Use `delegate_task` for another provider's model, user-requested settings, a separate checkout (`isolation: "worktree"`), background work, or a request naming that tool. Do not create the child's checkout in the shell or its prompt.
- Use Workflow only when asked. A missing provider/model is not permission to switch to a native agent, Workflow, or CLI fallback.
- `t3_thread_launch` and `create_threads` create top-level threads. Use them only when a new thread is requested; "delegate" or "parallel" does not mean one. For an authorized top-level worktree thread, bind it with the supported `workspaceStrategy`; a shell checkout does not bind a thread.

Call `orchestrator_capabilities` once per thread before the first `delegate_task`; repeat only after an error or a user-named provider change. Select an available provider, model, and options from that catalog. Put settings in `target.options`, using actual option ids/values. Preserve explicit choices; report unavailability rather than guessing a similar slug. A recommendation does not change the active model.

Omit runtime overrides unless the user requests a supervised child or the host requires them. A narrower runtime mode is not equivalent to read-only behavior; include the read-only scope in the brief. Never ask for a mode above the caller's authority.

## Brief and collect

Children started through `delegate_task` receive the task, not the parent's full history. Provide the actual objective, relevant sources/versions, scope and file ownership, permitted actions, verification, stop condition, and output contract. Use source pointers and essential excerpts; do not pass secrets or rely on uncommitted edits appearing in a prepared worktree. Unless explicitly tasked to coordinate, a child should do the work itself without recursively spawning agents.

Use `mode: "wait"` only when this turn needs the result and the live contract supports it. A timed-out wait does not cancel the child. A returned question/approval remains pending; it is not granted by the parent. For async work, honor returned `next`; when completion will wake this thread, end the turn. Do not poll a running delegate with `task_status`, sleep, a watcher, a scheduler, or a private monitoring loop.

Retain `taskId` for cancellation/result handling. Cancel a task tree with `task_cancel` if replaced, no longer needed, or the user reduces/stops delegation; do not interrupt its child thread instead. A new delegated review or re-check is a new `delegate_task`, with findings and objections in the brief, not a follow-up sent through `t3_thread_send`. Fix small review findings in the main loop.

Check the returned provider/model/options and outcome. A launched child is not a completed task. Reconcile its claims against artifacts before integrating. Return links using the host's thread-link rules. Never take over the coordinator's PR watcher from a child; follow the current host handoff contract for PR/head/checks/reviews.

## Computer-use worker

Read [model routing](../../computer-use/references/model-routing.md) when relevant. OpenAI is an initial preference, subject to live availability and the user's explicit choices. If the current agent already has the suitable tools and model, keep the task there.

Before handing control to a child, establish its tool/surface access, relevant account, allowed actions, starting observation, owner, and finish/readback condition. Only one writer may control a tab/desktop. Shared filesystem access does not prove shared browser login or tab ownership; screenshots alone do not transfer control. If the child lacks required tools, return that gap without claiming a GUI result or widening permissions.

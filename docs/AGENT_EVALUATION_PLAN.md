# Future AI agent desktop evaluation

This is a proposal, not an implemented or validated agent benchmark. No AI model training, API calls, agent ranking or scientific result was produced.

DeskTrace could expose a limited action interface within a disposable Windows VM. A human-curated task would define an allowed executable/window, safe initial state, data-only UIA actions, explicit forbidden side effects, timeout budget and independently checked end-state assertions. The evaluator would retain the original action script, environment versions and complete failed runs.

Prefer deterministic state/reset and semantic assertions over screenshots alone. Separate agent planning failure, locator/provider failure, application failure and ambiguous oracle outcomes. A UI assertion passing is not proof of task completion; use independently owned application state or exported artifacts where feasible. Avoid giving an agent direct file/network/terminal access merely because the desktop adapter is scoped.

Before evaluation claims: demonstrate reset reliability, test oracle false positives/negatives, establish task provenance/licenses, preregister repetition/timeout rules, measure annotator disagreement, and perform a threat-model review of app/provider impersonation and data leakage. Include simple scripted baselines and known-failing controls. Report missing cases and unknown outcomes rather than converting them into failures/successes silently.

Potential engineering next steps are fixture-based task manifests, a capability-restricted adapter service inside the VM, result-schema adapters and deterministic reset verification. They require a new authorized scope. Current DeskTrace supplies a small replay/evidence foundation only; existing UIA, recorder and desktop-agent evaluation work must be compared before any novelty claim.

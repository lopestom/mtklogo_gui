## Contributing
mtklogo_2026 welcomes focused bug fixes, documentation improvements, tests, and possible workflows. For large source code or files changes, explain the intended scope and link the relevant issue or any discussion.

## Choosing a contribution
For capability organization and provider better understanding of your device tested, always include/write: `Brand` - `Model` - `Chipset/Board_Platform` - `CPU` - `Resolution` | Ex: Tecno - Pova - MT6768 - 64bits Octa-core - 720x1640 pixels

- Explain the concrete problem, keep related corrections together, and report verification and unavailable coverage. Contributions should justify their review and maintenance cost. Keep cosmetic polish with useful fixes; confusing or incorrect user instructions warrant standalone corrections. Collect other cosmetic-only suggestions in an issue rather than separate PRs.

- For analysis workflows: compare equivalent real tasks before claiming an improvement. Any PR about it should have a real conscistence prove about that.

- When adding or changing or moddifying any file or binary preserve the minimal idea and layout of application.

## Reporting issues
Use the issue form that fits the report and keep it concise. For bugs, include the actual result, the shortest reproduction you ran, the tested version and environment, and the smallest useful output, artifact, screenshot, or source reference. Ground expected behavior in documentation, source, or a known-good version when available. State observed impact and frequency; keep untested scope and suspected causes explicit.

Clearly label source-only findings and proposed checks; do not claim runtime reproduction or results you did not observe. A root-cause analysis or fix is not required to report a problem. Documentation reports should identify the relevant passage or missing guidance and explain the correction or confusion.

## Pull request ownership and readiness
AI-assisted contributions are welcome. Every PR must have a human owner who takes responsibility for the complete change, including code, tests, documentation, and claims produced with AI assistance. The PR author is the owner unless another human is named in the PR and explicitly accepts ownership.
These requirements also apply to maintainer-authored PRs.

Before requesting maintainer review, the human owner must:
- Review the final diff and relevant existing code. Be able to explain the problem, the chosen approach, how it fits mtklogo_2026, and meaningful edge cases.
- Provide evidence that the change works. Summarize what was checked, the observed results, and meaningful gaps in the PR body. Use focused tests, representative CLI/MCP output, CI artifacts, screenshots, or other checks  appropriate to the change. For fixes, show the original failure and why the  regression coverage catches it when practical. Documentation-only changes  can use source, link, or rendered-document checks. Label source-derived  conclusions and proposed checks accurately; never report an unrun check as  passing.
- Complete the **Author readiness** declaration in the PR template, explicitly  stating that the PR is ready for initial review.

Keep the PR description concise and current. Explain the problem, observable outcome, approach, and useful evidence; link long logs or put them in optional details. Address actionable automated review findings and explain disagreements.
Human ownership and review remain required when CI or an automated reviewer reports success. Readiness requests maintainer review; it does not grant scope approval or permission to merge.

Draft PRs may request early feedback with open questions and incomplete checks.
Leave the readiness declaration unchecked until the human owner has completed it. The declaration records initial readiness; later pushes do not invalidate it or require another human sign-off. Keep the PR description and affected validation current as work changes. AI agents must leave human declarations to the human owner and must not attest to a human review on their behalf.

Maintainers may return a PR to the author or close it when the problem is unsupported, validation is missing, or the owner cannot explain the change.
Contributors are responsible for completing this work before requesting review.

## Contribution scope
mtklogo_2026 focuses on simetrical&harmonious process structure, runtime behavior and evidence conscintence global-purpose  in order to establish a simple idea with a purely visual objective and without security attacks on the device.

Supported contributions include format inspection, ordinary archive and standard compression extraction, disassembly, decompilation, cross-references, vulnerability analysis, and evidence reporting. Security fixes and isolated tests remain in scope.

Runtime investigation needs explicit boundaries. Launching or attaching to a process, injecting process, running scripts, and changing memory or registers require review of target selection, execution and mutation authority, provenance, resource limits, cancellation, and cleanup. 

## Cautions
mtklogo_2026 does not integrate or officially distribute:

- Purpose-built workflows to defeat commercial packing or code-virtualization  protections and automatically recover protected code;
- Anti-instrumentation evasion, or DRM, license, anti-cheat, or   access-control bypass workflows;
- Exploit or attack-payload automation, credential theft, covert persistence,  unauthorized access, or bulk attack workflows.

This is a decision for maintenance boundary, not a judgment about a contributor's intentions or a declaration that all excluded research is unlawful. Contributors must have the rights and authorization needed for their work. A local-only design or an "authorized use only" disclaimer does not establish containment or settle legal and scope questions.

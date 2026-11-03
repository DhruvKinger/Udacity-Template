# Governed Personal Productivity Agent — Project Feedback Report

This report contains only the five named project criteria (the five phases). Detailed submission requirements are addressed within their corresponding criterion. The four optional extensions are not graded criteria.

---

## Identify an AI opportunity and apply the decision framework

### Pass feedback
- The Phase 1 Opportunity Assessment includes a Workflow Analysis table with at least six rows. Each row names a workflow step, identifies its inputs or sources by Artifact A, B, C, or D name, and describes a concrete friction point.
- Sections A1–A4 each contain at least one Vireo-specific entry.
- Section A6 evaluates at least three candidate tasks, assigning each one of the five approaches: prompt, existing agent, new agent, automation, or do-not-use AI. At least one task is assigned do-not-use AI with a governance reason.
- Section A5 identifies at least three no-delegate items with specific reasons. It names the sensitive or individual-linked source identified by the learner and explains its classification-based governance treatment.
- Section A7 provides a plain-language, two-to-three-sentence opportunity statement explaining the agent's function, value, and what remains human. It does not claim that the agent decides, confirms, or sends anything.
- All five governance checkpoint items are checked, including the sensitive-item check referencing the specific source identified.
- The reflection references at least two specific artifacts and distinguishes an always-human item from an item fixable through instructions.

**Further reading:** [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) · [Microsoft Responsible AI](https://www.microsoft.com/ai/principles-and-approach) · [NIST Privacy Framework](https://www.nist.gov/privacy-framework)

### Fail feedback
- The workflow analysis is missing, has fewer than six sufficiently specific rows, or fails to identify source artifacts and concrete friction points.
- One or more of Sections A1–A4 lack Vireo-specific content, or Section A6 does not assess at least three candidate tasks using the five specified approaches.
- The decision framework lacks a do-not-use AI decision with a governance reason, or Section A5 identifies fewer than three specific no-delegate items.
- The sensitive or individual-linked source is not named and classified, or the governance checkpoint and reflection lack the required evidence.
- The opportunity statement is missing, outside the two-to-three-sentence requirement, uses unexplained technical terms, or assigns decision, confirmation, or sending authority to the agent.
- Complete the missing assessment sections and make the boundary between agent assistance and human responsibility explicit.

**Further reading:** [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) · [Microsoft Responsible AI](https://www.microsoft.com/ai/principles-and-approach)

---

## Design the AI-enabled workflow

### Pass feedback
- Phase 2 includes a current-state versus future-state table in Section 1.1, with both sides completed in every row. The agent-change description explicitly states that drafting is assisted but judgment stays with the human.
- Section 1.6 names the Vireo meeting-notes file as an approved source and explicitly excludes, by name, the sensitive source identified in Phase 1, with a governance reason.
- Section 1.7 includes at least four checkable success criteria, including one addressing governance compliance by requiring no sensitive content in the output.
- Section 1.8 includes at least three genuine learner-identified information gaps beyond the sample row. Each is scored for specificity, likely consequence, who could resolve it, and how the design works around it.
- The Part 3 governance checkpoint is completed for each named knowledge source. A source marked Unsure is documented as a gap and is not proceeded with.
- The reflection identifies at least one specific harm that could not be taken back and one annoyance that could be caught in review.

**Further reading:** [Microsoft 365 Copilot privacy, security, and data handling](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy) · [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

### Fail feedback
- The current-state/future-state table is incomplete, or it does not state that drafting is assisted while human judgment remains.
- The knowledge-source section does not name the approved Vireo meeting-notes file or explicitly exclude the sensitive Phase 1 source by name and governance reason.
- The success criteria contain fewer than four checkable items or omit the sensitive-content governance criterion.
- The information-gaps table has fewer than three genuine learner-identified gaps or omits one or more of the four required assessments for each gap.
- A source marked Unsure is treated as approved instead of being documented as a gap.
- The reflection does not distinguish an irreversible harm from an issue that could be caught in review. Complete the missing evidence and document source approval and human oversight clearly.

**Further reading:** [Microsoft 365 Copilot privacy, security, and data handling](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy) · [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

---

## Configure a governed personal productivity agent

### Pass feedback
- Phase 3 includes all five configuration components: name, purpose, standing instructions, approved knowledge sources, and output formats. They are consistent with the Phase 2 Workflow Design.
- Standing instructions include all seven guardrail types: no HR/sensitive content in wide outputs; flag gaps rather than invent; surface conflicts; flag identity ambiguity; preserve risk framing honestly; produce drafts rather than send-ready decisions; and use approved sources only.
- Prompt starters cover all five use cases: meeting preparation, prior discussion summary, action-item tracking, follow-up communication drafting, and status-report generation. They are provided as five individual starters or three bundled starters with explicit use-case mapping.
- The five-component checklist is ticked. Each knowledge source is documented as passed or excluded based on governance checks, with a note referencing the Data Classification Reference. The sensitive source identified by the learner is explicitly listed as excluded by name.
- Screenshot evidence follows the applicable access path. With live Copilot Agent Builder access, four annotated screenshots show: (a) agent overview with name and purpose; (b) instructions with all seven guardrails; (c) connected knowledge sources with the excluded Artifact C2 HR email visibly absent; and (d) prompt starters/output formats. Each has a one-line caption. For design-only submissions, written descriptions specify what all four captures visibly show, including annotations.
- The governance checkpoint covers data-classification confirmation per source, GovernAI alignment through the GovernAI portal, Acceptable Use confirmation against the published J&J Acceptable Use Guidelines for Microsoft 365 Copilot, and escalation routing. Anything that cannot be verified in-tenant is documented as an open item with the procedure to follow.

**Further reading:** [Microsoft 365 Copilot documentation](https://learn.microsoft.com/en-us/copilot/microsoft-365/) · [Microsoft Responsible AI](https://www.microsoft.com/ai/principles-and-approach) · [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

### Fail feedback
- One or more of the five configuration components is missing, or the configuration is inconsistent with Phase 2.
- The standing instructions omit one or more of the seven guardrail types, or prompt starters do not cover all five use cases with the required mapping.
- The configuration checklist is incomplete, sources are not documented as passed or excluded, or the sensitive source is not explicitly excluded by name.
- Screenshot evidence is missing or does not meet the applicable live-access/design-only requirements. In the live path, the excluded Artifact C2 HR email must be visibly absent from the knowledge-source screen.
- The governance checkpoint omits a required confirmation or escalation routing. Any item that cannot be verified in-tenant must be recorded as an open item with the procedure to follow.
- Complete the configuration, guardrails, evidence, and governance documentation so the agent's approved scope and limitations can be verified.

**Further reading:** [Microsoft 365 Copilot documentation](https://learn.microsoft.com/en-us/copilot/microsoft-365/) · [Microsoft Responsible AI](https://www.microsoft.com/ai/principles-and-approach)

---

## Test, identify failures, and refine agent instructions

### Pass feedback
- Phase 4 contains six completed test rows: four core tests and two learner-designed tests. Every row records test inputs, task, expected behavior written before running, summarized actual output, pass/fail result, and issue found.
- Test 4 documents the governance red-team test: a wider-stakeholder status update with the sensitive source pasted into the prompt as context. It records the pre-written expected behavior and actual outcome. A first-time pass or a fail is acceptable if documented.
- Every test references the Phase 2 success criterion it validates by Section 1.7 number, or names a newly discovered criterion with a one-line rationale.
- If a test failed, the refinement log records the exact instruction text added (v1.0 to v1.1), the passing retest, and what changed in the output. If every test passed at v1.0, the log identifies the guardrail that prevented the leak and an edge case still requiring human review.
- The four-dimension checklist—accuracy, completeness, tone/clarity, and governance alignment—is fully ticked against the post-v1.1 agent. Governance alignment includes confirmation against the published J&J Acceptable Use Guidelines for Microsoft 365 Copilot.
- The reflection distinguishes a failure fixed by a guardrail or a test passed because of a specific guardrail from an issue that always requires human judgment.
- Screenshot evidence follows the applicable access path. With live access, three annotated screenshots with one-line captions show: (a) Test 4 result at v1.0, with leaked sensitive content visible or the full response confirming its absence; (b) the instruction configuration at test time, including before-and-after if v1.1 was made; and (c) the governance outcome, either the v1.1 retest or the v1.0 first-pass output. For design-only submissions, written descriptions specify what all three captures visibly show.

**Further reading:** [Microsoft Copilot Studio analytics and evaluation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview) · [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) · [Microsoft Responsible AI](https://www.microsoft.com/ai/principles-and-approach)

### Fail feedback
- The test table does not contain six fully completed rows or omits test inputs, task, pre-written expected behavior, actual output, pass/fail result, or issue found.
- Test 4 does not document the specified sensitive-content red-team scenario and its expected and actual behavior.
- Tests do not map to Phase 2 success criteria, and newly discovered criteria are not justified.
- The refinement log does not record the exact v1.0-to-v1.1 instruction change and passing retest after a failure, or, if all tests passed at v1.0, it does not identify the effective guardrail and a remaining human-review edge case.
- The four-dimension checklist is incomplete or lacks explicit confirmation against the published J&J Acceptable Use Guidelines for Microsoft 365 Copilot.
- The reflection does not distinguish an instruction-addressable issue from an issue requiring human judgment.
- Required screenshot evidence or design-only descriptions are incomplete. Provide the Test 4 outcome, applicable instruction configuration, and governance outcome.

**Further reading:** [Microsoft Copilot Studio analytics and evaluation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview) · [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

---

## Articulate business value and build a human-validation plan

### Pass feedback
- Phase 5 includes the workflow-at-a-glance table in Section 2.1, with before-and-after information for every row. Elapsed-effort/cycle figures are identified as estimates with a visible assumptions note.
- Section 2.2 names all five agent use cases as specific tasks performed: meeting preparation, prior discussion summary, action-item tracking, follow-up communication drafting, and status-report generation. It explicitly states that the AI did not decide, resolve contradictions, or send.
- Section 2.3 lists at least five specific human-judgment items from the Vireo canon, including Option B decision status, Lena K. / L. Kensington identity, the moved reforecast deadline, the sensitive-source exclusion identified in Phase 1, and the ambiguous stakeholder ask. Each has a reason for remaining human.
- Section 2.6 presents productivity as an estimate, not measured data. It includes a per-step effort breakdown and an assumptions box stating that the estimate is not a time-and-motion study, cadence is assumed bi-weekly, and review time is based on the canon cycle.
- The Human Validation Plan names at least five specific review gates, each with a named role and trigger. It includes action-item-owner confirmation, sensitive-content exclusion, final send approval, stakeholder-audience confirmation, and factual-accuracy verification for external-facing content.
- The reflection names at least three J&J functions beyond the meeting-owner scenario and gives a one-sentence rationale for each.

**Further reading:** [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) · [Microsoft Responsible AI](https://www.microsoft.com/ai/principles-and-approach) · [Microsoft 365 Copilot privacy, security, and data handling](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy)

### Fail feedback
- The workflow-at-a-glance table is incomplete, or elapsed-effort/cycle figures are presented as measured facts rather than estimates with visible assumptions.
- The AI-contribution section omits one or more of the five use cases or does not clearly state that the AI did not decide, resolve contradictions, or send.
- The human-judgment section omits required Vireo canon items or does not explain why each remains a human responsibility.
- The productivity estimate lacks a per-step breakdown or the required assumptions: not a time-and-motion study, bi-weekly cadence, and review time based on the canon cycle.
- The Human Validation Plan has fewer than five specific gates, lacks named roles or triggers, or omits a required gate type.
- The reflection names fewer than three J&J functions beyond the meeting-owner scenario or does not explain each function's relevance.
- Revise the business-value summary and validation plan so estimated benefits, human decision rights, and review responsibilities are explicit.

**Further reading:** [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) · [Microsoft Responsible AI](https://www.microsoft.com/ai/principles-and-approach)

---

# Overall Project Feedback

## Pass
- The project completes all five phases, from opportunity assessment and workflow design through governed agent configuration, testing/refinement, and business-value assessment.
- It establishes a clear boundary between AI-assisted drafting and human responsibility for judgment, approvals, sensitive information, and external communication.
- Approved knowledge sources, exclusions, guardrails, governance checkpoints, and human-validation gates are documented and supported by the required evidence.
- Test results and reflections show how the agent was evaluated, how issues were addressed, and which risks continue to require human oversight.
- Business-value estimates are presented with assumptions, balancing productivity benefits against review and governance requirements.

## Fail
- One or more phases are incomplete, or required tables, reflections, checklists, test evidence, or configuration details are missing.
- Approved knowledge sources, sensitive-source exclusions, or the seven guardrail types are not sufficiently documented.
- Testing does not adequately demonstrate the expected behavior for the sensitive-content red-team scenario, or refinement and retesting evidence is incomplete.
- Human responsibilities, review gates, or the distinction between estimated and measured productivity benefits are unclear.
- Complete the missing phase requirements, provide the required evidence, and make governance controls and human decision rights explicit throughout the workflow.

## Ungradable — Required Files Missing
- Required Phase 1–5 deliverables, supporting Vireo artifacts, agent configuration evidence, or completed test results may be missing or inaccessible.
- Without the workflow analysis, design tables, configuration details, test outputs, screenshots or design-only evidence, and business-value summary, the five phases cannot be assessed reliably.
- Submit the missing deliverables and supporting evidence, including source references and governance documentation, before grading.

---

**Note:** The four items under “To make your project stand out” are optional extensions. They are not included as graded criteria in this report.

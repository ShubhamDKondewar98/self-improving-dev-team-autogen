### Coder schema (LOCKED)
{
  "code": "string",
  "change_summary": "string | null",   # null on attempt 1, populated on retries
  "addressed_feedback": "string | null" # null on attempt 1, populated on retries
}
Purpose: NOT used for routing (selector_func always sends Coder output to
Test-writer unconditionally, no branching needed). Exists purely for the
attempt_logger/PDF report's explainability — lets a human reading the report
see what changed between attempts without diffing raw code blobs.
Same schema shape every turn (simplifies logging code); fields are null on
attempt 1 since there's nothing to summarize yet, populated from attempt 2+.

### Test-writer/executor schema (LOCKED — confirmed, restating for completeness)
{
  "execution_status": "COMPLETED" | "INFRA_ERROR",
  "results": { "passed": int, "failed": int } | null,
  "error_detail": "string | null"
}
Purpose: used FOR ROUTING — selector_func branches: INFRA_ERROR → back to
Test-writer (retry), COMPLETED → forward to Critic.

### Critic schema (LOCKED — confirmed, restating for completeness)
{
  "verdict": "PASS" | "FAIL",
  "failure_category": "CODE_BUG" | "TEST_BUG" | "AMBIGUOUS_REQUIREMENT" | null,
  "reasoning": "string",
  "retry_recommended": true | false
}
Purpose: used FOR ROUTING — PASS → terminate/HITL, CODE_BUG → Coder,
TEST_BUG → Test-writer, AMBIGUOUS_REQUIREMENT → terminate early to HITL
(labeled "possible planning gap" in report, not counted as retry exhaustion).

### Design principle established this session:
Structure a message ONLY if selector_func needs to branch on it (routing
dependency) OR if the reporting layer needs it for explainability. Do not
add structure "for consistency" or on the unfounded assumption that forced
schema fields improve LLM output quality on subsequent turns — those are
not real justifications for added schema complexity.


### Selector state management (LOCKED — resolved after closure vs. class discussion)
Class-based approach chosen over nested closure for selector_func.
Reasoning: retry counters (code_retry_count, test_retry_count) are not
only needed inside routing logic — run_manager.py needs to read them for
termination checks, attempt_logger.py needs them for the JSON log, and
pdf_report.py needs them for the human-facing report. Multiple consumers
need external read access to this state. A closure traps state privately
by design (demonstrated: no way to read a closure's captured variable
from outside without a workaround). A class exposes state naturally via
self.attributes, which every consumer above needs. Choosing a class here
isn't "more structured for its own sake" — it's driven by the number of
places outside the selector that legitimately need to read this state.



### Correction: Code-executor merged into Test-writer (was 5 conceptual roles, now 4)
Originally planned as a separate speaking agent (code_executor_agent.py)
reflecting the analyzer_gpt reference pattern. Reconsidered: running a test
in Docker is a mechanical, deterministic action requiring no independent
judgment — same category of task previously rejected for a "Coordinator"
agent. Test-writer now handles both writing AND triggering execution
(likely via tool-calling to Docker execution logic), emitting one
COMPLETED/INFRA_ERROR message per cycle. Reduces selector_func branching
by one hop with no loss of the separation that actually matters
(Coder vs. Test-writer independence).


### Termination architecture (LOCKED)
Confirmed via AutoGen docs: TerminationCondition is a separate mechanism
from selector_func — implemented as a callable class (__call__ receives
messages, returns StopMessage | None), checked automatically by the
framework, entirely independent of routing.

Five real stopping conditions identified (expanded from originally-locked
"dual condition"):
1. Critic verdict == PASS
2. Critic failure_category == AMBIGUOUS_REQUIREMENT
3. code_retry_count >= max_code_retries
4. test_retry_count >= max_test_retries
5. token usage >= cap

Design: (1)+(2) handled by one custom CriticVerdictTermination class,
parsing the Critic's JSON directly from messages.
(3)+(4) handled by a custom RetryCapTermination class that receives a
REFERENCE to the same Selector instance used by selector_func (not
independently re-parsed from messages) — avoids duplicating retry-counting
logic in two places; Selector remains the single source of truth for
counters, since it's the only component that actually increments them.
(5) likely


teams/
├── dev_team.py
├── selector_func.py           # SelectorFunc class — routing logic only
└── termination_conditions.py  # CriticVerdictTermination, RetryCapTermination —
                                 # stopping logic only, kept separate from routing
                                 # per the routing-vs-stopping distinction established
                                 # during selector_func design


### Termination classes (LOCKED, implemented in teams/termination_conditions.py)
- CriticVerdictTermination(critic_agent) — parses Critic's JSON from messages,
  stops on verdict==PASS or failure_category==AMBIGUOUS_REQUIREMENT.
- RetryCapTermination(selector_instance) — holds a reference to the same
  Selector instance used by selector_func; reads live code_retry_count/
  test_retry_count directly (Option B), no message parsing needed.
Combined in dev_team.py via OR (|):
  termination = CriticVerdictTermination(critic_agent) | RetryCapTermination(selector) | <token cap condition>


### Termination — full picture (LOCKED, finalized)
Three termination conditions combined via OR (|):
1. CriticVerdictTermination(critic_agent) — PASS or AMBIGUOUS_REQUIREMENT
2. RetryCapTermination(selector_instance) — code_retry_count/test_retry_count
   reaching their caps
3. TokenUsageTermination(max_total_token=60000) — built-in AutoGen class,
   no custom implementation needed

Retry caps: max_code_retries = 3, max_test_retries = 3 (locked).

Token cap: max_total_token = 60000 — derived estimate, not measured.
Reasoning: ~13–16 worst-case agent calls in one fully-exhausted run
(1 Planner + up to 4 Coder + up to 4–7 Test-writer + up to 4 Critic),
roughly 1,000–2,000 tokens/call → ~15–30k tokens worst case, with cap set
at ~2x that estimate for headroom since a too-tight cap failing a healthy
run is worse than a bit of wasted spend on a run that would've failed
anyway. FLAGGED FOR REVISIT: after first 2-3 real end-to-end test runs,
check actual token usage in logs and tighten/loosen this number based on
real data rather than the current estimate.


### File ownership principle (established during termination_conditions.py review)
Class *definitions* (reusable logic) live in their own dedicated files
(selector_func.py, termination_conditions.py). Configured *instances*
(specific numbers, specific agent references, the actual wiring for THIS
run) live in dev_team.py, which owns final assembly responsibility.
token_termination = TokenUsageTermination(max_total_token=60000) belongs
in dev_team.py, not termination_conditions.py, for this reason.


### Known defensive-parsing requirement (for attempt_logger.py, when built)
Confirmed via test: json.loads('{"x": "null"}')["x"] returns the STRING
"null", not Python None — these behave differently in `is None` checks.
LLM output for Coder's change_summary/addressed_feedback (null on attempt 1)
is not guaranteed to emit real JSON null vs. the string "null".
attempt_logger.py must normalize this when parsing Coder messages:
if parsed.get("change_summary") == "null": parsed["change_summary"] = None
(same treatment for addressed_feedback). Do not rely on `is None` checks
against raw parsed LLM JSON without this normalization step. 

### Correction: retry_recommended dropped from Critic schema
Originally locked with 4 fields (verdict, failure_category, reasoning,
retry_recommended). Reopened during critic_agent.py implementation:
select() never reads retry_recommended (only checks verdict/failure_category
for routing), and no defined criteria existed for when the Critic should
set it — an undefined field an LLM is told to fill in produces inconsistent,
essentially random output. Cut per the established structure principle
(routing OR reporting need only). DEFERRED, not deleted as an idea: could
return as a soft "human attention" signal in the PDF report layer, IF a
clear definition is written for it at that point. Current Critic schema:
verdict, failure_category, reasoning — 3 fields, not 4. 

### Test execution signal (LOCKED, verified via real Docker/pytest probes)
- Outer exit_code (from execute_code_blocks): does NOT distinguish
  COMPLETED vs INFRA_ERROR — confirmed 0 in all three tested scenarios
  (all-pass, mixed pass/fail, syntax error). NOT used for routing.
- Decision signal: parse_pytest_summary(pytest_stdout) —
  regex-extracts "(\d+) passed" and "(\d+) failed" from pytest's summary
  line. Returns {"passed": int, "failed": int} if either regex matches
  (a legitimate result was produced, including all-pass with 0 failed
  since pytest omits "N failed" text when there are none) → COMPLETED.
  Returns None if neither matches (syntax error / collection error /
  nothing ran) → INFRA_ERROR.
- Verified via 3 real Docker probes: all-passing ("3 passed in 0.16s"),
  mixed ("1 failed, 1 passed..."), syntax error ("1 error in 1.06s",
  no passed/failed text at all, pytest exit code 2).


  ### Correction: Coder must expose a fixed entry-point function name
Added constraint: Coder's solution must always define a function named
exactly `solution` (can internally call as many helper functions as
needed — task complexity absorbed inside `solution`, not exposed as
multiple public functions). Reasoning: Test-writer needs a reliable,
deterministic way to import the Coder's code without parsing/guessing
function names from arbitrary generated code — `from solution import
solution` becomes a static, unconditional import with zero failure mode,
instead of introducing a new fragile INFRA_ERROR source (import errors
from mismatched/unpredictable function names). Standard pattern, same
convention used by coding-assessment platforms (LeetCode, HackerRank)
for the same reliability reason.


### test_agent.py — VERIFIED end-to-end (not just designed)
run_tests_in_docker tested directly (bypassing the LLM) with two real
scenarios:
1. Mixed pass/fail solution+test pair -> correctly returned COMPLETED,
   {"passed": 1, "failed": 1}, error_detail: null
2. Syntax error in test file -> correctly returned INFRA_ERROR,
   results: null, error_detail containing full pytest traceback
Both confirm the parse_pytest_summary() decision rule works correctly
through the actual function, not just in isolated probes.
Fixed filenames (solution.py, test_solution.py) confirmed safe -- each
call gets a fresh Docker container via docker_util.py.


### dev_team.py — implemented and verified
build_dev_team() assembles: 4 agents (imported from agents/), one shared
SelectorFunc instance (0/0 counters, max caps from constants), 
CriticVerdictTermination + RetryCapTermination(same selector_instance) +
TokenUsageTermination combined via OR, wired into SelectorGroupChat with
selector_func=selector_instance.select (bound method, not the class or
an unbound method — see reasoning locked earlier).
Deliberately a FUNCTION, not a module-level variable, so run_manager.py
can call it fresh per run for isolated retry counters.
allow_repeated_speaker=True required — routing table has agents speaking
consecutively (e.g. Test-writer -> Test-writer on INFRA_ERROR retry).
VERIFIED: full import chain across every file built this session
succeeds, team constructs without error.
# V3 Iterative Revision Coach — Improvement Opportunities Report

**Report version:** 1.0  
**Report date:** 2026-11-10  
**Based on:** V3_OUTCOMES_REPORT.md (2026-11-10)  
**Scope:** Pedagogical quality and operational efficiency improvements

## Executive Summary

This report identifies opportunities to improve V3 based on the completed outcomes evaluation. The V3 implementation is technically complete with 128 passing tests and successful browser verification, but critical pedagogical validation gates remain open and efficiency improvements are available.

**Key findings:**
- **Model configuration:** Non-thinking mode outperformed thinking mode on coverage, RACES alignment, speed (3.83×), and token efficiency (1.88×) with zero repairs
- **Critical gap:** Educator review gate remains open—the highest-priority pedagogical validation requirement
- **Incomplete coverage:** 8 of 30 required scenarios unvalidated with real model output
- **Efficiency opportunity:** Configuration decision blocked on repeated evaluation evidence

**Primary recommendation:** Complete scenario gaps → run repeated model comparison → conduct three-educator review → address findings before any student contact.

---

## 1. Model Configuration Findings

### 1.1 Non-Thinking Mode Advantages

The paired evaluation revealed non-thinking mode advantages across multiple dimensions:

| Dimension | Non-thinking | Thinking | Winner |
| --- | --- | --- | --- |
| **RACES alignment** | Used explicit R/A/C/E/S terminology | Generic criteria | Non-thinking |
| **Whole-draft coverage** | 3 candidates in accurate-source scenario | 1 candidate | Non-thinking |
| **Model latency** | 64.2s total | 246.2s total | Non-thinking (3.83× faster) |
| **Token usage** | 36,340 total | 68,407 total | Non-thinking (1.88× fewer) |
| **Schema repairs** | 0 repairs | 2 repairs | Non-thinking |
| **Nuanced diagnosis** | Standard | Caught author-vs-student claim distinction | Thinking |

### 1.2 Thinking Mode Strengths

Thinking mode showed isolated diagnostic advantages:
- Recognized that the opening sentence reported **the author's** position rather than stating **the student's** claim in the source-missing scenario
- Provided more explicit vocabulary meanings and elaborative guidance in some per-goal feedback
- Averaged 190.8 words per goal observation vs. 169.2 for non-thinking

### 1.3 Configuration Recommendation

**Use non-thinking as the leading candidate** for the next evaluation phase because it demonstrated:
- Comparable or better pedagogical coverage in 5 of 6 scenarios
- Substantially lower operational cost and latency
- Zero schema-validation failures
- Better alignment with teacher-supplied terminology (RACES)

**Critical caveat:** This is based on a single paired run of 6 scenarios. Temperature-0 non-thinking still exhibits run-to-run variability, and thinking introduces additional variability. The recommendation is to prioritize non-thinking in repeated evaluation, not to change the runtime configuration immediately.

### 1.4 Required Next Steps

1. **Run 3-5 repetitions** of the 6 representative scenarios in both modes to establish:
   - Confidence intervals on candidate counts
   - Repair rate consistency
   - RACES alignment consistency
   - Author-claim diagnostic reliability

2. **Capture repair diagnostics:** Modify `scripts/evaluate_v3.py` to store invalid first responses (prompts and raw responses only, never raw reasoning) during authorized debug evaluation so repair causes can be diagnosed.

3. **Document configuration decision** in `CLAUDE.md` after accumulated evidence supports a clear choice, including quality, reliability, latency, and token trade-offs.

---

## 2. Critical Pedagogical Validation Gaps

### 2.1 Educator Review Gate (Highest Priority)

**Status:** Open  
**Blocking:** Any supervised student contact

PRD Section 14.3 requires three qualified educators with grades 5-7 experience to complete synthetic walk-throughs before any student contact. This gate remains the highest-priority pedagogical validation requirement.

**Required review protocol:**
- 3 educators with current or recent grades 5-7 classroom experience
- 2-3 scenarios each, representing argumentative, informational, and narrative writing
- Assessment dimensions:
  - Navigation independence and clarity
  - Tone appropriateness for grade level
  - Feedback density and proportionality
  - Hint quality: guidance without answers
  - Confusion points and interaction issues
- Pass gate: At least 2 of 3 educators rate "Ready for supervised student pilot"

**Why this matters:** All current quality assessments rest on developer judgment and automated schema validation. Educator review establishes whether:
- Hints guide revision without supplying completed target responses
- Feedback density is appropriate for different grade levels
- Tone feels supportive rather than condescending
- Navigation is clear without adult assistance
- Terminology matches classroom practice

**Recommendation:** Recruit educators and conduct review in Week 3-4 of the improvement cycle, after scenario completion and model configuration decision.

### 2.2 Incomplete Scenario Coverage

**Status:** 8 of 30 required scenarios unvalidated with real model output

The following PRD Section 14.2 scenarios remain incomplete:

| # | Scenario | Pedagogical risk if missing |
| ---: | --- | --- |
| 7 | Three goals revised, three observations | Selection overflow and observation matching |
| 8 | One goal across multiple rounds then stop | Goal persistence and voluntary stopping flow |
| 9 | Meaningful organizational regression | Accurate comparative assessment |
| 22 | Short grade-5 proportional argument | Age-appropriate feedback density |
| 23 | Long grade-7 informational essay (350+ words) | Proportionality for older/longer writing |
| 24 | Grade-6 with non-obscuring language errors | Idea prioritization over mechanics |
| 25 | Strong intro/conclusion, weak middle | Middle-paragraph targeting accuracy |
| 27 | Grade-7 register shifts | Appropriate cohesion/register guidance |
| 28 | Several repeated identical resubmissions | Dignity-preserving neutral responses |

**Immediate priorities:**
- **#24** (language errors with good ideas): Tests core multilingual-learner pedagogy—idea prioritization
- **#25** (weak middle paragraphs): Tests whether feedback targets the right sections
- **#22** (short grade-5): Tests proportionality for younger/briefer writing

**Recommendation:** Implement scenarios #22, #24, #25 in Week 1, run them in the repeated model comparison, then complete #23, #27, #8, #9, #28 in Week 2-4.

### 2.3 Semantic Scaffold Review

**Status:** Schema validation insufficient for semantic over-scaffolding

Current validation catches:
- Assigned-topic sentence frames (rejected even with blanks)
- Numeric evidence answers in vocabulary options
- Readiness/mastery/score language

Current validation **cannot** catch:
- Borderline hints that name the reason or evidence the student should produce
- Vocabulary options that telegraph the expected answer without being numeric
- Steps that are specific enough to paste as a coherent paragraph

**Example risk:** A hint might pass schema validation but effectively say "Explain that the survey shows interest in **garden vegetables** specifically, not all fresh food generally" when the entire revision task is to make that connection. The words in bold aren't blanks, but they do contain the target idea.

**Recommendation:** Add to educator review protocol:
- Present 5-10 generated hints across genres without student context
- Ask: "Could a student paste these steps and get a coherent on-topic response?"
- Ask: "Does this name the specific reason, evidence, or explanation the student should produce?"
- Document patterns of borderline cases to inform future schema refinement

Consider adding a `scaffold_contains_target_idea: bool` validation field guided by documented patterns from educator review.

---

## 3. Efficiency Improvements

### 3.1 Latency and Token Comparison

**Current evidence:**

| Metric | Non-thinking | Thinking | Ratio |
| --- | ---: | ---: | ---: |
| **Mean model latency** | 4.3s | 14.5s | 3.37× |
| **Total model latency** | 64.2s | 246.2s | 3.83× |
| **Total tokens** | 36,340 | 68,407 | 1.88× |
| **Total model calls** | 15 | 17 | 1.13× |
| **Schema repairs** | 0 | 2 | — |

**Operational impact:**
- Non-thinking review feels responsive (4-5s)
- Thinking review may feel slow (14-15s) even with honest stage updates
- Token cost nearly doubles for thinking mode
- Repairs add unpredictable latency spikes

**Unknown factors:**
- End-to-end latency including network, validation, storage not measured
- Whether honest stage messages ("Reviewing your draft...") make 15s acceptable
- Student revision time between rounds not measured for comparison
- Streamlit Cloud deployment overhead not evaluated

**Recommendation:** If non-thinking becomes the default after repeated evaluation:
1. Measure end-to-end latency in local and deployed contexts
2. Consider whether sub-5s model latency justifies further optimization
3. Monitor whether repairs correlate with specific prompt/schema patterns

### 3.2 Repair Diagnostics Missing

**Current limitation:** Two thinking-mode repairs occurred during the garden revision, but invalid first responses were not captured. This blocks understanding whether:
- Invalid references are a systematic prompt issue
- Schema violations suggest unclear coordinator→support contracts
- Repairs introduce substantial latency spikes beyond base thinking overhead

**Recommendation:** Modify `scripts/evaluate_v3.py` to:

```python
# In authorized debug mode only:
if server_debug and capture_repair_diagnostics:
    # Store: invalid_response, validation_errors, prompt_version, schema_version
    # Never store raw hidden reasoning
    evidence_data["repair_diagnostics"].append({
        "agent": "coordinator" or "support",
        "validation_errors": [...],
        "prompt_version": "v3.1.0",
        "occurred_at": timestamp,
    })
```

After 3-5 more paired runs, analyze whether repairs cluster around:
- Reference location failures (paragraph/occurrence)
- Source-limitation contract violations
- Selected-goal observation count mismatches
- Specific scenario types or draft characteristics

---

## 4. Recommended Action Sequence

### Phase 1: Scenario Completion and Model Decision (Weeks 1-2)

**Week 1:**
1. Implement scenarios #22 (short grade-5), #24 (language errors), #25 (weak middle) with complete fixture data
2. Run 3× repeated paired evaluation (both modes, all 6 current scenarios + 3 new scenarios)
3. Add repair diagnostics capture to evaluation runner
4. Analyze accumulated results: candidate counts, repair rates, RACES consistency, diagnostic reliability

**Week 2:**
5. Document model configuration decision in `CLAUDE.md` with evidence summary
6. Update `.env.example` and evaluation commands if configuration changes
7. Implement remaining scenarios #23, #27, #8, #9, #28
8. Run final scenario validation with selected configuration

**Deliverables:**
- 3 new scenario fixtures with complete metadata
- 3× paired evaluation results with repair diagnostics
- Configuration decision document
- 5 additional scenario fixtures
- Updated `CLAUDE.md` and evaluation commands

### Phase 2: Educator Review (Weeks 3-4)

**Week 3:**
9. Recruit 3 qualified educators (grades 5-7 experience)
10. Prepare review protocol with scenarios, assessment rubric, and recording consent
11. Schedule and conduct first 2 educator walk-throughs
12. Document initial findings and patterns

**Week 4:**
13. Conduct third educator walk-through
14. Analyze findings across reviewers: navigation, tone, density, hints, confusion points
15. Implement identified concerns (if ≥2 educators surface the same issue)
16. Retest affected scenarios and capture updated evidence
17. Document pass/fail on the three-educator gate

**Deliverables:**
- Educator review protocol and consent materials
- 3 completed educator assessments with raw notes
- Findings analysis and implementation log
- Updated evidence artifacts
- Gate pass/fail documentation

### Phase 3: Post-Review Refinement (Week 5+)

18. Address semantic scaffold patterns identified in educator review
19. Complete remaining accessibility checks (keyboard-only, screen reader, zoom)
20. Run full 30-scenario suite with final configuration
21. Update PRD Section 16 status gates with completed evidence
22. Document remaining open items and deployment decision

**Deliverables:**
- Scaffold semantic validation enhancements (if needed)
- Accessibility evaluation summary
- Full scenario suite results
- Updated PRD evidence record
- Deployment readiness assessment

---

## 5. Lower-Priority Enhancements

### 5.1 Proportionality Analysis

**Question:** Do candidate counts and hint lengths scale appropriately with draft length, grade level, and writing quality?

**Current evidence:**
- Non-thinking returned more total words (2031 vs 1908) but thinking gave more words per goal (190.8 vs 169.2)
- Short grade-5 scenario (#22) not yet tested
- No measurement of whether 3-4 goals feel overwhelming for 150-word grade-5 drafts

**Recommendation:** After scenario completion, analyze:
- Candidate count vs. draft length
- Candidate count vs. grade level
- Hint length vs. grade level
- Whether 3-goal maximum should vary by grade or draft length

### 5.2 Desktop Layout and Workspace Study

**Current validation:**
- 60/40 workspace verified at 1280×900px
- Initial editor measured exactly 780px
- Independent pane scrolling works

**Gaps:**
- No testing at 1440px, 1680px, 1920px (common desktop widths)
- No observation of whether students keep both panes visible
- No measurement of pane resizing behavior
- Keyboard-only and screen-reader testing limited to basic checks

**Recommendation:** Conduct small usability study with 5-6 teachers (not students yet) using screen recording:
- Do they resize the panes?
- Do they collapse feedback to focus on writing?
- Does 780px feel too narrow on wide screens?
- Can they navigate entirely by keyboard?

### 5.3 Multi-Round Flow Integration

**Current status:** Multi-round revision tested in mocked tests, but no integrated real-model flow covering:
- Select 1 goal in round 1
- Revise and submit
- Receive observation with carry-forward choice
- Select carry-forward goal in round 2
- Revise again
- Voluntarily stop
- Complete final reflection

**Recommendation:** Implement scenario #8 as an integrated fixture with pre-staged revision text for round 1 and round 2, then run with selected model configuration to verify:
- Goal persistence across rounds
- Neutral carry-forward language
- Stopping works from multiple entry points
- Final reflection correctly uses original and latest submitted snapshots

---

## 6. Evidence Gaps and Limitations

### 6.1 No Real Student Evidence

**Current scope:** Synthetic scenarios only

**Missing:**
- Usability by children ages 10-13
- Actual revision behavior and editing patterns
- Motivation, engagement, or persistence
- Learning outcomes or revision skill improvement
- Real classroom assignment diversity

**Implication:** V3 remains a technical and limited pedagogical prototype. No learner-outcome, achievement, motivation, or retention claims are warranted.

### 6.2 No Production Validation

**Missing:**
- Deployed build testing
- Cloud SQLite durability
- Deployed latency and network overhead
- Secrets configuration
- Production error handling
- COPPA/FERPA/SOPIPA compliance assessment
- Institutional review for research with minors
- Real teacher notification system

**Recommendation:** Keep V3 local until a separate deployment decision is made with complete operational and compliance review.

### 6.3 Limited Assistive Technology Testing

**Current validation:** Basic keyboard navigation and focus management

**Missing:**
- Screen reader testing across multiple readers (NVDA, JAWS, VoiceOver)
- Zoom and magnification testing
- Keyboard-only navigation completeness
- Mobile and tablet layouts beyond 1280px desktop

**Recommendation:** Supplement desktop validation with:
- Keyboard-only walk-through of full revision loop
- Screen reader testing with one representative reader
- Zoom testing at 200% and 400%
- Explicit limitation: Mobile/tablet optimization deferred per PRD Section 5.3

### 6.4 Maximum-Length Stress Testing

**Current validation:** Explicit character limits tested; non-truncation behavior verified in mocked tests

**Missing:** Largest allowed draft/source combination not exercised against live model context window

**Recommendation:** Create a stress scenario with:
- Grade 7, 500-word draft (upper typical limit)
- 300-word source passage
- 200-word teacher directions
- Run thinking and non-thinking modes
- Verify no truncation, complete review, valid references

---

## 7. Risk Assessment

### 7.1 High-Priority Risks

| Risk | Current status | Mitigation |
| --- | --- | --- |
| Educator review gate open | Blocks student contact | Schedule and conduct three-educator review in Week 3-4 |
| Model configuration unsettled | Blocks confident scaling | Complete 3× repeated evaluation in Week 1-2 |
| Incomplete scenario coverage | Limits confidence in edge cases | Implement priority scenarios #22, #24, #25 immediately |
| Semantic over-scaffolding | Schema validation insufficient | Add educator assessment of generated hints |

### 7.2 Medium-Priority Risks

| Risk | Current status | Mitigation |
| --- | --- | --- |
| Repair causes unknown | Blocks diagnostic improvement | Add repair diagnostics capture |
| Multi-round flow unvalidated | Integrated loop not tested | Implement scenario #8 with staged revisions |
| Proportionality untested | Short/long/young/old gaps | Analyze after scenario completion |
| Latency perception unknown | 14.5s may or may not feel slow | Measure end-to-end if thinking becomes default |

### 7.3 Lower-Priority Risks

| Risk | Current status | Mitigation |
| --- | --- | --- |
| Workspace layout unstudied | 60/40 verified but not observed | Small teacher usability study |
| Maximum length unstressed | Largest case not exercised | Create 500-word + 300-word source stress scenario |
| Assistive tech gaps | Basic checks only | Keyboard-only + screen reader pass |

---

## 8. Success Criteria for Next Phase

### 8.1 Model Configuration Decision (Week 2 Deadline)

**Criteria:**
- ✅ 3× repeated paired evaluation complete for representative scenarios
- ✅ Configuration decision documented with quality, reliability, latency, token trade-offs
- ✅ `CLAUDE.md`, `.env.example`, and evaluation commands updated
- ✅ Repair diagnostics captured and analyzed

### 8.2 Scenario Completion (Week 2 Deadline)

**Criteria:**
- ✅ Scenarios #22, #24, #25 implemented and validated with selected configuration
- ✅ Scenarios #23, #27, #8, #9, #28 implemented
- ✅ All scenarios pass without operational errors
- ✅ Evidence artifacts stored under `data/evidence/`

### 8.3 Educator Review Gate (Week 4 Deadline)

**Criteria:**
- ✅ 3 qualified educators complete synthetic walk-throughs
- ✅ At least 2 of 3 rate "Ready for supervised student pilot"
- ✅ Identified concerns addressed and retested
- ✅ Review findings documented in updated PRD or separate gate report

**Pass condition:** ≥2 educators approve readiness AND no critical safety/dignity/accuracy concerns remain unresolved.

**Fail condition:** \<2 educators approve OR critical concerns cannot be resolved within reasonable scope.

---

## 9. Overall Recommendation

**Immediate action:** Prioritize scenario completion → model decision → educator review in that sequence.

**Configuration:** Use non-thinking as the leading candidate based on current evidence, but confirm with repeated evaluation before changing runtime defaults.

**Validation:** The educator review gate is the highest-priority pedagogical validation requirement and must pass before any supervised student contact.

**Evidence honesty:** V3 is a working local synthetic prototype with substantial technical validation. It is **not** pedagogically validated by educators, **not** tested with real students, and **not** ready for unsupervised use by children.

**Next milestone:** Three-educator gate pass in Week 4, followed by deployment decision with complete operational and compliance review.

---

## 10. Appendix: Scenario Implementation Guidance

### A.1 Scenario #22: Short Grade-5 Proportional Argument

**Purpose:** Test feedback density and tone for younger/briefer writing

**Fixture requirements:**
- Grade 5
- Genre: argument (explicit or auto-inferred)
- Draft: 120-150 words
- Structure: Simple claim, 1-2 reasons, minimal elaboration
- Quality: Ideas present but underdeveloped (typical grade-5 brevity)

**Expected behavior:**
- 1-2 candidates, not 3-4
- Shorter hints (grade-appropriate language)
- No condescension about brevity
- Priorities: claim clarity and reason connection, not academic register

### A.2 Scenario #24: Grade-6 with Non-Obscuring Language Errors

**Purpose:** Test idea prioritization over mechanics (core multilingual-learner pedagogy)

**Fixture requirements:**
- Grade 6
- Genre: informational or argument
- Draft: 200-250 words with strong central idea and logical organization
- Language: 5-8 non-obscuring errors (verb tense, articles, plural forms)
- Quality: Good content, minor mechanical errors

**Expected behavior:**
- Coordinator identifies idea/organization strengths
- Mechanical errors acknowledged but not prioritized in candidates
- Optional vocabulary support available but not a primary candidate
- Assessment: "Your explanation of [topic] is clear and well-organized. I noticed a few verb forms to check, but those are small edits."

### A.3 Scenario #25: Strong Outer Paragraphs, Weak Middle

**Purpose:** Test middle-paragraph targeting accuracy

**Fixture requirements:**
- Grade 6 or 7
- Genre: argument or informational
- Draft: 250-300 words, 4-5 paragraphs
- Structure: Strong intro with clear claim/central idea, strong conclusion
- Issue: Middle paragraphs lack elaboration, evidence explanation, or cohesion

**Expected behavior:**
- Candidates target middle paragraphs specifically
- References point to paragraphs 2-3, not intro/conclusion
- Acknowledgment of strong outer structure
- Hints guide middle-paragraph development without praising intro/conclusion excessively

---

**End of Report**

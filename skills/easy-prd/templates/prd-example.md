# AI Customer Support Agent

> **Version:** v1.0 | **Date:** 2026-03-28 | **Status:** Draft

**Approvers:** VP of Product (___), Head of AI/ML (___)
**Reviewers:** Legal/Compliance, Security team, Customer Support lead

---

## 1. Project Team

| Role | Owner | Responsibility |
|------|-------|----------------|
| PM | ___ | Requirements, evaluation criteria, launch decision |
| Design | ___ | Conversation UX, escalation flow design |
| R&D | ___ | Agent orchestration, RAG pipeline, chat widget |
| QA | ___ | Functional + adversarial testing, quality gate |

---

## 2. Related Links

| Type | Link | Status |
|------|------|--------|
| Product prototype | ___ | TBD |
| Technical spec (agent architecture) | ___ | TBD |
| Evaluation dataset & benchmarks | ___ | TBD |
| Metric dashboard | ___ | TBD |

---

## 3. Overview

### 3.1 Background

**Current state:**
Support team handles ~12,000 tickets/month. 65% are repetitive L1 queries (password resets, billing, how-tos) with documented playbooks. Average first-response time is 4.2 hours. CSAT is 3.6/5 — top complaint is slow response.

**Core problem:**
Most support volume is repetitive and well-documented, yet every ticket waits in the same human queue. This delays both simple and complex issues.

**Source:** Business data (support cost trajectory) + user feedback (CSAT: "too slow")

### 3.2 Goals

- **Business goal:** Auto-resolve ≥50% of L1 tickets (no human touch); reduce first-response time to <2 minutes for AI-handled tickets
- **User goal:** Get accurate answers to common questions instantly, 24/7
- **Product goal:** Build a reusable AI agent framework extensible to other channels and domains

### 3.3 Out of Scope

| Excluded | Reason | Planned for |
|----------|--------|-------------|
| L2/L3 resolution (refunds, account recovery) | Requires human judgment + write access | Phase 2 |
| Voice/phone channel | Different modality and tech stack | TBD |
| Multi-language | English-only; needs translated knowledge base | Phase 2 |
| Agent learning from live conversations | Safety risk; use offline eval loop | TBD |

### 3.4 Privacy & Data

| Aspect | Detail |
|--------|--------|
| Data collected | Conversation transcripts (user messages + agent responses), ticket metadata. May contain PII in free-text. |
| Storage & retention | 12 months for quality review. PII auto-redacted from any data used for model evaluation. |
| User consent | Disclosed at conversation start: "You're chatting with an AI assistant." Implicit consent by continuing. User can request human anytime. |
| Compliance | GDPR: transcript deletion on request. No data sent to third-party model providers without DPA. |

---

## 4. Key Scenarios

### Scenario S01: User asks a common question, AI resolves it

| Element | Detail |
|---------|--------|
| Target user | Customer with an L1 question (password, billing, how-to) |
| Trigger | User opens support chat widget |
| User goal | Get an accurate answer without waiting for a human |
| Frequency | ~65% of incoming conversations |

**Main flow:**
1. User opens chat widget → greeting + AI disclosure
2. User types question
3. Agent retrieves relevant knowledge base articles (RAG), generates grounded answer
4. User follows instructions, confirms resolved
5. → Done: ticket auto-closed as "AI-resolved"; CSAT survey triggered

**Error flows:**
- Low confidence: "I'm not sure about this. Let me connect you with a human." → escalate with context
- No relevant KB article: "I don't have info on this yet." → escalate with topic tag
- Model timeout: "I'm having trouble. Connecting you with a human." → auto-escalate

**Related FRs:** FR-001, FR-002, FR-003

---

### Scenario S02: User requests or needs human escalation

| Element | Detail |
|---------|--------|
| Target user | Any user in conversation |
| Trigger | User asks for human, or AI can't resolve |
| User goal | Talk to a real person without repeating the problem |
| Frequency | ~35–50% of conversations |

**Main flow:**
1. User says "talk to a real person" (or AI triggers escalation)
2. Agent acknowledges immediately
3. Transfers to human queue with: transcript, topic, attempted resolution, account context
4. → Done: human picks up with full context

**Error flows:**
- No human available (off-hours): create ticket, provide reference number, offer AI for other questions

**Related FRs:** FR-002, FR-003

---

## 5. Requirements

### FR-001: Chat Widget

**Scenario:** S01, S02
**Priority:** P0

**Description:**
Embedded chat widget on web and mobile web. Supports free-text input, structured agent responses (text, steps, links, buttons). Conversation persistent within session.

**Interactions:**
- Normal: floating button → expand to chat panel
- Empty (new conversation): greeting + quick-reply buttons ("Billing", "Account", "How to...")
- Error (send fails): "Message not sent. Tap to retry."
- Edge: empty message → ignore; >2,000 chars → truncate + warn; image/file → "Text only for now"
- Accessibility: keyboard nav, screen reader announces new messages, focus-trapped panel, Escape to close
- i18n: English only; all strings externalized for future localization

**Business performance requirement:**
Agent response within 5 seconds (P90). Streaming preferred — first token within 1.5s.

**Acceptance criteria:**
- [ ] Widget opens/closes on web and mobile web
- [ ] Message sent and response received within 5 seconds
- [ ] Conversation persists across page navigation in same session
- [ ] Quick-reply buttons produce correct responses

---

### FR-002: Knowledge Retrieval & Response Generation

**Scenario:** S01
**Priority:** P0

**Description:**
RAG-based answer generation. Agent retrieves from knowledge base (~500 articles, synced daily), generates grounded response. Must not fabricate. If no relevant source found, escalate.

**Behavior rules:**
- Ground all responses in retrieved content; cite source when possible
- Never fabricate URLs, policy details, or steps
- Confidence below threshold → escalate to human
- Off-topic/policy-violating queries → polite decline + optional escalation
- Never perform write actions — only provide instructions

**Acceptance criteria:**
- [ ] Correctly answers ≥85% of evaluation dataset
- [ ] Cites source article for KB-derived answers
- [ ] Does not fabricate content not in KB
- [ ] Refuses off-topic queries without being dismissive
- [ ] KB article updates reflected within 1 hour

---

### FR-003: Human Escalation & Safety

**Scenario:** S01, S02
**Priority:** P0

**Description:**
Handoff to human at any point — user-initiated or AI-initiated. Full context transfer. Plus: input/output safety filters, prompt injection blocking, AI self-identification.

**Escalation triggers:**
- User explicitly requests human
- Low confidence for 2 consecutive turns
- Negative sentiment for 2 consecutive messages
- Topic classified as L2+

**Safety rules:**
- Block prompt injection attempts ("ignore previous instructions", system prompt extraction)
- Scan responses for PII leakage before sending
- Never pretend to be human; identify as AI when asked

**Acceptance criteria:**
- [ ] User can request human at any point; transferred within 30 seconds
- [ ] Human agent receives full transcript + context
- [ ] Blocks ≥95% of known prompt injection patterns (adversarial eval set)
- [ ] Never outputs system prompts, API keys, or internal markers
- [ ] Identifies as AI when asked

---

## 6. Success Metrics

### Core Metrics

| Metric | Goal (§3.2) | Baseline | Target | Measurement | Window | Owner |
|--------|-------------|----------|--------|-------------|--------|-------|
| L1 auto-resolution rate | Auto-resolve ≥50% | 0% | ≥ 50% | AI-resolved tickets / total L1 | 30 days | PM |
| First-response time (AI) | <2 min response | 4.2 hours | < 2 min | First message → first response | 14 days | PM |
| Factual accuracy | Accurate answers | — | ≥ 85% | Weekly manual sample (n=200) + eval set | Ongoing | ML lead |
| CSAT (AI-resolved) | User satisfaction | 3.6/5 | ≥ 4.0/5 | Post-conversation survey | 30 days | PM |

---

## 7. Launch Plan

### Milestones

| Milestone | Target date | Owner | Status |
|-----------|-------------|-------|--------|
| Requirements review | ___ | PM | TBD |
| Knowledge base audit & cleanup | ___ | Support lead | TBD |
| Eval dataset creation (200+ labeled pairs) | ___ | ML lead | TBD |
| RAG pipeline V1 + eval pass (≥85% accuracy) | ___ | R&D | TBD |
| Chat widget + escalation dev complete | ___ | R&D | TBD |
| Adversarial / red-team testing | ___ | QA + Security | TBD |
| Shadow mode (AI drafts, human approves) | ___ | PM | TBD |
| Live launch (10% of chats) | ___ | PM | TBD |
| Full rollout | ___ | PM | TBD |

### Dependencies

| Dependency | Team | What's needed | Due | Status |
|------------|------|---------------|-----|--------|
| Knowledge base read API + update webhook | Content team | Structured article access | ___ | Pending |
| CRM read-only API (account context for escalation) | CRM team | Account type, recent orders | ___ | Pending |
| LLM provider API access + DPA | Vendor / Infra | Rate limits confirmed, DPA signed | ___ | Pending |
| Human agent dashboard (AI escalation ticket type) | Support tooling | New ticket type with transcript fields | ___ | Pending |

---

## 8. Test & Readiness

### PM Acceptance Checklist

- [ ] Ask "How do I change my billing address?" → correct KB-grounded answer with source citation
- [ ] Ask a question not in KB → agent admits it doesn't know, offers human escalation
- [ ] Say "I want to talk to a human" → transferred within 30s with full context
- [ ] Attempt prompt injection → agent declines politely
- [ ] Ask "Are you a bot?" → agent identifies as AI
- [ ] Ask agent to reset password → provides instructions, does not execute
- [ ] Message outside business hours with no agents → ticket created, reference number shown

---

## Appendix

### Open Questions

| Question | Impact | Owner | Due | Status |
|----------|--------|-------|-----|--------|
| Self-hosted LLM vs third-party API? Affects cost, latency, data privacy. | Tech spec, privacy, vendor dep | R&D + Security | ___ | Pending |
| Confidence threshold for auto-resolve vs escalate? Needs tuning with real data. | FR-002, resolution rate | ML lead | After shadow mode | Pending |
| Shadow mode: time-boxed or metric-gated? | Launch timeline | PM | ___ | Pending |

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-03-28 | ___ | Initial draft |

# Cybersecurity Readiness Brief (Sample)

- **Brief ID:** BRIEF-2026-0001
- **Scenario:** Phishing concern
- **Organization:** Rural agricultural co-op (18 employees)
- **Severity:** High
- **Risk Score:** 78/100 (confidence: medium)

## Executive summary
A likely phishing campaign targeted shared finance and operations inboxes this
morning. Current controls include spam filtering and endpoint antivirus, but MFA
coverage is incomplete on email and remote admin accounts. Immediate containment
should focus on session revocation, credential reset, and inbox rule review.

## Top findings
1. Two high-privilege accounts do not enforce MFA.
2. Shared inbox forwarding rules were not reviewed after incident alert.
3. Staff reported clicking suspicious links before internal notice was sent.

## Immediate actions (first 24 hours)
1. Force password reset + session revoke for finance and admin roles.
2. Enable MFA for all email admin and payroll-related accounts.
3. Review and remove suspicious mailbox forwarding/inbox rules.
4. Run targeted phishing awareness reminder for all staff.
5. Preserve relevant email headers and login logs for follow-up.

## 7-day plan
- **Day 1-2:** verify MFA coverage and close remaining gaps.
- **Day 3-4:** inventory external-facing access points and reduce exposure.
- **Day 5-7:** validate incident communication and reporting playbook.

## Longer-term recommendations
- Formalize access review cadence for privileged accounts.
- Add monthly phishing simulation and response drill.
- Introduce vendor email security hardening baseline.

## Follow-up
- **Review date:** 2026-04-28
- **Escalate if:** evidence of unauthorized financial system access appears.

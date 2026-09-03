---
name: Origin workflow
about: Describe a real case where a desirable agent was blocked or challenged
title: "origin: "
labels: origin-workflow
assignees: ""
---

## What happened

Describe the last legitimate agent request that was blocked, challenged, or mishandled.

## How you knew it was desirable

## What the origin could not accept

Privacy, liability, abuse, inventory, or other constraints.

## What evidence would have changed the decision

## Current controls

CAPTCHA, WAF, CDN bot product, first-party API, OAuth, or manual review.

## Whether a shadow evaluation is possible

Yes / no / not sure, and who owns that decision.

Shadow means existing CAPTCHA, WAF, or bot controls still decide. AgentIsOK would emit a parallel decision for comparison. Say whether the verifier can run on origin or origin-controlled proxy infrastructure, not only as a CDN product checkbox.

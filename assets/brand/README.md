# AgentIsOK identity

![AgentIsOK visual identity](agentisok-specimen.png)

The primary mark stacks **AI** over **OK**. A green check passes through the center gap and rises beside the I. Gold, deep green, and simple angular geometry echo Univeracity's visual family; the letterforms and composition are specific to AgentIsOK.

The wordmark is **AgentIsOK**, with that capitalization. The technical specification remains **Agent Clearance Protocol** and uses `agent-clearance` identifiers.

## Assets

| Use | Light surface | Dark surface |
|---|---|---|
| Horizontal logo | [SVG](agentisok-logo-light.svg) | [SVG](agentisok-logo-dark.svg) |
| Stacked mark | [SVG](agentisok-mark-light.svg) · [PNG](agentisok-mark-light.png) | [SVG](agentisok-mark-dark.svg) · [PNG](agentisok-mark-dark.png) |
| Single color | [Logo SVG](agentisok-logo-mono.svg) | [Mark SVG](agentisok-mark-mono.svg) — recolor the entire mark as needed |

- [Avatar SVG](agentisok-avatar.svg) and [512 × 512 PNG](agentisok-avatar.png).
- [Favicon SVG](agentisok-favicon.svg) and [64 × 64 PNG](agentisok-favicon.png); simplified AI + check for small contexts.
- [Social preview SVG](agentisok-social.svg) and [1280 × 640 PNG](agentisok-social.png), ready for a repository social-preview upload.
- [Specimen SVG](agentisok-specimen.svg) and [PNG](agentisok-specimen.png).

SVGs are self-contained, with outlined lettering and accessible titles/descriptions. PNG marks have transparent backgrounds. The avatar and social preview have a fixed deep-green background.

## Color and placement

| Role | Light surface | Dark surface |
|---|---|---|
| AI / gold | `#B8892E` | `#E7C46F` |
| Check / green | `#087F5B` | `#43C995` |
| Lettering | `#172B24` | `#F4F2EA` |
| Suggested background | `#FCFBF7` | `#10241D` |

Preserve the proportions and internal spacing. Keep surrounding content at least one letter-stem width away from the mark. Use the stacked mark at 48 px wide or larger; use the simplified favicon below that. Use the horizontal logo at 240 px wide or larger. Gold is an identity accent, not the default color for small body text.

## Meaning and use

**Evidence travels. The origin decides.**

The check identifies the project. It does not certify an agent, issuer, implementation, or deployment as safe or conformant. When used beside a real decision, state the action and origin policy, and render denial, step-up, and indeterminate outcomes explicitly. A static green logo must never substitute for the actual decision.

These assets follow the repository's [Apache-2.0 license](../../LICENSE). Truthful project references and compatibility descriptions do not require a hosted service or paid program. Do not imply project endorsement, certification, or official status for an independent implementation.

## Rebuild

The original monogram is defined as vector paths in [generate.py](generate.py). The wordmark uses [Inter](https://rsms.me/inter/) under its SIL Open Font License; no font binaries are bundled. Generated lettering is outlined, so viewing the assets does not require Inter.

To regenerate, install Inter, Inkscape, and `rsvg-convert`, then run from the repository root:

```bash
python3 assets/brand/generate.py
```

Inspect the PNG specimen, social preview, and small favicon after regeneration. Font and renderer versions can change outlines; commit the reviewed outputs together with source changes.

# Repository governance readiness

This repository contains assessment prompts, not a deployed backend service. CI validates that the three prompts are present with Markdown headings and balanced code fences. It does not implement or expose candidate solutions. Dev/UAT/Main are content review and publication stages; no application environments are created.

## Branch workflow

Working branch → dev → uat → main. Use reviewed merge commits for promotion; never force-reset environment branches. Default remains unchanged until this PR passes review and CI, then switch to dev. Preserve legacy branches until final cleanup.

Dev/UAT application access must use Cloudflare WARP. Production application ingress is public; operational and backend/data access stays private. Content-only repositories do not gain cloud environments from branch creation.

Organization branch rulesets stay disabled during validation. A successful promotion workflow does not enforce merge protection until the required-status rulesets are activated. No secrets are introduced by these changes.

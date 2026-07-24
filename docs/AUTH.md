# Credentials

## auth.json is not yours to write

opencode stores provider credentials at:

    ~/.local/share/opencode/auth.json

**Do not hand-author it.** It is opencode-managed and its format is
an internal detail. Populate it with `/connect` in the TUI:

    opencode
    /connect        # select provider, paste key or complete OAuth
    /models         # confirm models appear

Check what is registered:

    opencode auth list

Note the path: `~/.local/share/opencode/` for credentials and state,
`~/.config/opencode/` for config. Different directories.

## Never commit credentials

Nothing in this repo should ever contain an API key. `opencode.json`
references them by environment variable only:

    "apiKey": "{env:VLLM_API_KEY}"

## Local vLLM

vLLM accepts any bearer token unless started with `--api-key`. Set
one anyway so the config shape matches cloud:

    export VLLM_API_KEY=local-dev-not-a-secret

For a custom OpenAI-compatible provider, opencode still wants a
credential registered under the provider ID. Run `/connect`, scroll
to **Other**, and enter the provider ID **exactly** as it appears in
`opencode.json` — here, `vllm`. A mismatch between the `/connect` ID
and the config ID is the most common cause of "provider not found".

Context window comes from the served model (`--max-model-len`), not
from `opencode.json`. The `limit` block only tells opencode how much
room it has left.

## GitHub

Agents call `gh`, which uses its own credential store:

    gh auth login
    gh auth status

### Per-role token scoping

Permissions in `.opencode/agents/*.md` are enforced by opencode —
they constrain what the model may attempt. They do not constrain what
your token can do. For real separation, give each role its own
fine-grained PAT:

| Role       | Repository permissions                                     |
|------------|------------------------------------------------------------|
| Planner    | Issues: read/write. Contents: read.                        |
| Builder    | Contents: read/write. PRs: read/write. Issues: read/write.  |
| Reviewer   | PRs: read/write (comments). Contents: read.                |
| Playtester | Issues: read/write. Contents: read.                        |
| Ideator    | Discussions: read/write. Contents: read.                   |

    GH_TOKEN=$BUILDER_TOKEN opencode run --agent builder "..."

`GH_TOKEN` overrides the stored credential for that process.

## What actually enforces the rules

Ranked by how hard they are to circumvent:

1. **Branch protection on `main`** — server-side, uncircumventable
2. **Fine-grained token scopes** — server-side
3. **opencode `permission` blocks** — the tool is not offered
4. **CI guardrails** — human-owned files, stdlib-only imports,
   `input()` in tests, PR body sections
5. **AGENTS.md and role prompts** — guidance only

Levels 1–4 hold. Level 5 drifts under context pressure, which is
expected rather than a defect in the prose. Never rely on 5 alone.

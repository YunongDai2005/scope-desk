# Scope Desk

An original, small command-line prototype for a freelance developer reviewing client requests against an agreed scope. An open-weight Nemotron model drafts a list of included work, extra work and questions. The operator reviews the suggestions before saving a receipt or exporting a plain-text scope review. It does not set prices, commit to a contract or send anything to a client.

Started October 13, 2026, after the DEV Hacktoberfest Week 2 official opening at October 12 19:00 UTC. No code from TheOne or its previously submitted adaptations is reused. Codex assisted implementation and verification. The existing private provider credential was reused only for three bounded synthetic development calls; credentials are not part of the project.

## Run

Python 3.11+ and the standard library are sufficient. No package installation is required.

```sh
python3 -m unittest -v test_scope_desk.py
python3 scope_desk.py create 'Landing page client' --scope 'One English landing page with a contact form'
```

Copy the returned project ID, then configure `SCOPE_MODEL_KEY` in your process environment. The default endpoint is Nebius Token Factory and the model is `nvidia/nemotron-3-super-120b-a12b`. `SCOPE_MODEL_URL` and `SCOPE_MODEL` are operator-controlled settings. A compatible loopback inference endpoint is supported by the client but has not been tested; actual validation used the hosted open-weight model, not offline local inference.

```sh
python3 scope_desk.py analyse PROJECT_ID 'Please add online payments and a French version.'
python3 scope_desk.py show PROJECT_ID DRAFT_ID
python3 scope_desk.py approve PROJECT_ID DRAFT_ID --reviewed
python3 scope_desk.py export PROJECT_ID DRAFT_ID
```

There is a persistent ten-call limit per prototype database, including failed calls. Missing keys, malformed/truncated results and unrelated references fail without a fake-response fallback. Read every draft; matching an exact input quote does not establish that the semantic classification is correct. Do not approve an incorrect suggestion. Exported text is a review aid to edit before sharing.

## Evidence and limitations

Eight offline tests check project isolation, exact input quotes, valid scope references, explicit review, stale scope refusal, scope changes during inference, restart-safe duplicate approval, persistent call budgets and export gating. Their provider responses are mocks.

Three separately recorded genuine Nemotron development calls assessed a request for payments/French as extra, a permitted blog revision as included, and a vague request as needing clarification. These are synthetic development probes, not held-out accuracy, real users or business demand. A real approved receipt survived closing and reopening SQLite and replay did not duplicate it. The later export feature was verified locally with that recorded receipt without spending another model call. No customer, revenue or paid-user claim.

SQLite records stay in the operator's local file. The selected project's agreed scope and current message are sent to the configured model provider. Other projects are excluded from that request. Hosted inference is not a promise of offline operation or complete data privacy. Prototype databases have no encryption or multi-user authentication; this is a single-operator local tool, not a public server.

The project is not registered or submitted to DEV Week 2 yet. The challenge requires a new repository and a deployed link or video. Existing TheOne branches cannot satisfy that new-project rule. Licensed under MIT. Source is published at https://github.com/YunongDai2005/scope-desk on `codex/dev-week2-scope-desk`. The [public 72-second video](https://github.com/YunongDai2005/scope-desk/releases/download/v0.1.0-prototype/scope-desk-real-results-replay.mp4) presents a clearly labelled replay of the real synthetic results and actual command-line checks; it is not a live screen recording. The [prototype release](https://github.com/YunongDai2005/scope-desk/releases/tag/v0.1.0-prototype) records these limits. Final contest submission and application hosting are not yet complete.

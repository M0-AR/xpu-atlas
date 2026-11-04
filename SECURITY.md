# Security policy

## Supported versions

The current release line is `0.1.x`. Security fixes are applied to the latest release.

## Reporting a vulnerability

Do **not** open a public issue for a security problem.

Use GitHub's private **Security → Report a vulnerability** flow for this repository. If that flow is unavailable, contact a maintainer directly and ask for a private channel.

Please include:

- what is affected (file, endpoint, or workflow),
- steps to reproduce,
- the impact you can demonstrate,
- any suggested fix or mitigation.

## Scope

This is a static research site and an offline analysis pipeline. There is no server, login, database, or user data in the default deployment. Relevant reports include:

- injected or unsafe content in generated HTML,
- a dependency with a known exploitable vulnerability,
- a workflow that could leak credentials or publish unintended files,
- a supply-chain issue in the build or Pages deployment.

## What to expect

Maintainers will acknowledge a report as soon as practical, investigate, and coordinate disclosure. Please give us a reasonable window to fix the issue before publishing details.

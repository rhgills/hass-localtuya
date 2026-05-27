# `rhgills/hass-localtuya` — fork notes

This is a downstream fork of [`rospogrigio/localtuya`](https://github.com/rospogrigio/localtuya).
We run it on our [homelab](https://github.com/rhgills/homelab) Home Assistant
instance to drive Wi-Fi Tuya bulbs and plugs over the LAN.

The fork exists because upstream `rospogrigio/localtuya` is effectively
unmaintained — open bug-fix PRs sit for months without maintainer review —
while we need fixes shipped to keep our setup working on current Home Assistant
versions. We are not aiming to take over the integration; we are carrying a
small set of cherry-picks on top of upstream so we can move at our own pace.

## Versioning

Tags on this fork follow the pattern:

```
v<upstream-version>+rhgills.<N>
```

For example: `v5.2.5+rhgills.1` is downstream patch revision 1 on top of
upstream tag `v5.2.5`.

### Rules

1. **`<upstream-version>` tracks the upstream tag** this fork's `master`
   currently sits at, even if `manifest.json`'s `version` field is stale
   relative to the upstream tag (it sometimes is — that's upstream's
   inconsistency, not ours to fix).
2. **`<N>` resets to `1`** whenever we rebase/merge a new upstream tag.
3. **`<N>` bumps by 1** for each new downstream patch landed on `master`.
4. **`manifest.json`'s `version` field is set to the same string** at tag time
   (e.g. `"version": "5.2.5+rhgills.1"`), so Home Assistant's UI and HACS show
   a value consistent with the GitHub release tag.

### Why `+` and not `-`

Semver treats `5.2.5+rhgills.1` as build metadata with the same precedence as
`5.2.5`, which is what we want — our downstream patch revision shouldn't be
ordered *before* upstream `5.2.5` the way `5.2.5-rhgills.1` (pre-release) would
be. HACS reads the literal tag string and does not strictly enforce semver
ordering for custom repositories, so the `+` form is safe in practice.

## Refreshing from upstream

```bash
git fetch upstream
git checkout master
git merge upstream/master           # or rebase, if history matters more than effort
# resolve any conflicts in the downstream patch surface (light.py is the usual one)
git push origin master
```

After a successful refresh, cut a new tag:

```bash
git tag v<new-upstream-version>+rhgills.1 -m "Refresh onto upstream v<new-upstream-version>"
gh release create v<new-upstream-version>+rhgills.1 --notes "Refresh onto upstream v<new-upstream-version>. Downstream patches reapplied: <list>."
```

If a downstream patch conflicts with upstream changes (because upstream finally
got around to merging something similar), prefer dropping our version and
keeping upstream's — that's progress. Note it in the patches table below with a
"superseded by upstream in vX" annotation.

## Currently applied downstream patches

| # | Patch | Origin | Why we carry it |
|---|---|---|---|
| 1 | `light: color_temp mired → kelvin` | [PR #1](https://github.com/rhgills/hass-localtuya/pull/1) — cherry-picked [rospogrigio/localtuya#2184](https://github.com/rospogrigio/localtuya/pull/2184) (`avataar`); 2-line `int()` cast adapted from [rospogrigio/localtuya#2203](https://github.com/rospogrigio/localtuya/pull/2203); + four defensive fixes from adversarial review | Home Assistant 2026.3 ([core PR #161777](https://github.com/home-assistant/core/pull/161777)) removed the deprecated mired color-temperature unit; upstream still uses it, so color_temp is broken on every tunable-white Tuya bulb on HA ≥ 2026.3. |

## Installing this fork in Home Assistant via HACS

1. HACS → **Integrations** → menu (⋮) → **Custom repositories**
2. Repository URL: `https://github.com/rhgills/hass-localtuya`
3. Category: **Integration**
4. **Add**. The repository now appears in HACS.
5. Find **LocalTuya integration** in the HACS Integrations list (the existing
   one, if installed from `rospogrigio/localtuya`, must be removed first to
   avoid a duplicate `custom_components/localtuya/` directory).
6. Pin to a specific tag (e.g. `v5.2.5+rhgills.1`) rather than tracking
   `master`, so HACS updates only on explicit version bumps.
7. Restart Home Assistant.

## Tracking issue

[`rhgills/homelab#292`](https://github.com/rhgills/homelab/issues/292) — parent
issue covering "why we forked and what's next." Per-patch context is in the PR
linked from the patches table above.

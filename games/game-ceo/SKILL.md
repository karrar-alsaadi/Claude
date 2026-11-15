---
name: "game-ceo"
description: "Run a 5-employee Haiku team (ideator, creativity developer, global-market adapter, storywriter, reviewer) supervised by a Sonnet manager to produce a finished game concept with a story."
---

# game-ceo

You are the **CEO/Manager**. You run five employees, each an Agent call with `model: "haiku"`. You never do their work yourself; you brief them, pass results down the line, and make the final call with a Sonnet-level review.

## Input

The user gives a theme, genre, platform, or nothing at all. If nothing, let Employee 1 choose freely. Do not ask clarifying questions unless the request is impossible to interpret. Reply in the user's language (Arabic if they write Arabic); employee prompts can be in English.

## Pipeline (sequential, each step needs the previous output)

Spawn each employee with the Agent tool: `model: "haiku"`, `subagent_type: "general-purpose"`. Paste the full previous output into the next prompt, because employees share no context.

### Employee 1: Ideator
Task: propose 5 distinct game ideas for the brief. Each: working title, one-sentence hook, genre, core loop (what the player does every 30 seconds), platform. Then pick the single strongest idea and say why in 2 lines.
Output: 5 ideas + the chosen one.

### Employee 2: Creativity Developer
Input: the chosen idea. Task: find what is truly original in it and push it further. Give: the unique twist, 3 mechanics that make it feel fresh, 2 ideas that surprise the player, and what to avoid because it is already done in other games. Rewrite the idea as an improved concept.
Output: improved concept.

### Employee 3: Global Market Adapter
Input: the improved concept. Task: make it work for a worldwide audience through simplicity and easy execution. Give: a one-line pitch anyone understands, how to learn it in under 60 seconds, a text-free or low-text design approach for easy localization, culturally neutral visuals/themes, a small-team build scope (MVP in under 3 months: engine suggestion, 5 must-have features, what to cut), monetization suggestion, and target markets. Simplify anything too complex.
Output: market-ready concept with MVP scope.

### Employee 4: Storywriter
Input: the market-ready concept. Task: write the game's story and how events unfold: setting, protagonist, goal, antagonist/obstacle, a 3-act structure, the main story beats mapped to gameplay progression (which level or phase delivers each beat), one twist, and the ending (plus an optional alternate ending). Keep it simple enough to fit the MVP scope.
Output: story document.

### Employee 5: Reviewer
Input: everything so far (concept, market plan, story). Task: critique harshly but constructively. Score 1-10 each: originality, simplicity, global appeal, feasibility, story-gameplay fit. List concrete problems and exact fixes. End with a verdict: APPROVE or REVISE.
Output: scorecard, issues, verdict.

## Revision loop

If the Reviewer says REVISE, send the issues back to the employee responsible (one targeted re-run, with `model: "haiku"`), then re-run the Reviewer once. Maximum one revision round to control cost.

## Manager final review (Sonnet)

Do the final review with a Sonnet-class model: spawn one Agent with `model: "sonnet"` and give it the full package plus the Reviewer's scorecard. If you are already running as Sonnet or stronger you may do it directly, but a Sonnet Agent call is the default. The manager must:
1. Check the pieces fit together (mechanics support the story, scope fits the MVP).
2. Verify the Reviewer's issues were actually fixed.
3. Cut anything bloated, fix contradictions, sharpen the pitch.
4. Give a final decision: GREEN-LIGHT or SHELVE with one-line reason.

## Final deliverable to the user

Present one clean document (not the raw employee transcripts):

1. **Title and one-line pitch**
2. **Core gameplay loop** and unique twist
3. **Global-market plan** (audience, learning curve, localization, monetization)
4. **MVP scope** (features, what's cut, timeline)
5. **Story** (setting, characters, 3 acts, twist, ending)
6. **Reviewer scorecard** (final scores)
7. **Manager verdict**

For a design the user will keep, create it as a document; for a quick idea, answer in chat. Offer one next step (e.g. a prototype plan or a deeper level design).

## Rules

- Employees run on Haiku only; the manager review runs on Sonnet.
- Do not skip employees or merge roles.
- Keep every employee output under ~600 words to save tokens.
- Never present the Reviewer's draft as final without the manager pass.
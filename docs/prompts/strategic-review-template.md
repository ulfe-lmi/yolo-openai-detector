# Strategic Review Template

Use this prompt after a coding agent returns a PR report.

```text
Review the submitted PR against AGENTS.md, CLAUDE.md, and the relevant work order.

Focus on:
- product boundary violations;
- CPU-only invariant;
- OpenAI compatibility claims;
- auth and secret handling;
- image parsing safety;
- tests as evidence;
- documentation drift;
- overclaiming.

Return:
1. recommendation: merge / repair / reject / defer;
2. goal match;
3. evidence;
4. missing evidence;
5. risks;
6. exact repair work order if needed.
```

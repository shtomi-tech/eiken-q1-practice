"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const workflow = fs.readFileSync(
  path.join(__dirname, "..", ".github", "workflows", "pages.yml"),
  "utf8",
).replace(/\r\n/g, "\n");

function jobSection(name) {
  const start = workflow.indexOf("\n  " + name + ":\n");
  assert.notEqual(start, -1, "Pages workflow needs a " + name + " job");
  const bodyStart = start + name.length + 4;
  const nextJob = workflow.slice(bodyStart).search(/^  [a-z][a-z-]*:\s*$/m);
  return nextJob === -1 ? workflow.slice(bodyStart) : workflow.slice(bodyStart, bodyStart + nextJob);
}

const testJob = jobSection("test");
const deployJob = jobSection("deploy");
assert.match(workflow, /^  push:$/m, "pushes to every branch must run CI");
assert.match(workflow, /^  pull_request:\n    branches:\n      - main$/m, "pull requests to main must run CI");
assert.match(testJob, /run: npm test/, "the CI job must run the complete npm test suite");
assert.match(testJob, /python -m pip install --requirement requirements-jev\.txt/, "CI must install the pinned Jev SDK");
assert.match(testJob, /run: python3 scripts\/check_q1_data\.py/, "the Q1 data contract must remain in CI");
assert.match(deployJob, /^\s+needs: test$/m, "Pages deployment must depend on successful CI");
assert.match(deployJob, /^\s+if: github\.ref == 'refs\/heads\/main'$/m, "only main may deploy Pages");
assert.ok(
  deployJob.indexOf("needs: test") < deployJob.indexOf("uses: actions/deploy-pages@v4"),
  "the deployment action must remain inside the CI-gated deploy job",
);
assert.match(deployJob, /run: bash scripts\/prepare-site\.sh/, "Pages must build _site with the shared prepare script");

const cloudflareJob = jobSection("deploy-cloudflare");
assert.match(cloudflareJob, /^\s+needs: test$/m, "Cloudflare deployment must depend on successful CI");
assert.match(cloudflareJob, /^\s+if: github\.ref == 'refs\/heads\/main'$/m, "only main may deploy to Cloudflare");
assert.match(cloudflareJob, /run: bash scripts\/prepare-site\.sh/, "Cloudflare must build _site with the shared prepare script");
assert.ok(
  cloudflareJob.indexOf("needs: test") < cloudflareJob.indexOf("uses: cloudflare/wrangler-action@v3"),
  "the wrangler deploy must remain inside the CI-gated Cloudflare job",
);

console.log("Pages workflow gate: OK (pull request/push tests must pass before main deploy)");

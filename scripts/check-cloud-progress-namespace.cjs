const assert = require("node:assert/strict");
const fs = require("node:fs");

const source = fs.readFileSync("static/mode-q1.js", "utf8");

const matches = source.match(/const APP_ID = "([^"]*)";/g) || [];
assert.equal(matches.length, 1, `expected exactly 1 APP_ID declaration, found ${matches.length}`);
assert.equal(matches[0], 'const APP_ID = "eiken2-q1";', `unexpected APP_ID declaration: ${matches[0]}`);
assert.ok(
  !source.includes('const APP_ID = "eiken-q1-practice";'),
  "APP_ID must not point at the old eiken-q1-practice namespace",
);
assert.ok(
  source.includes("eiken_q1_student_"),
  "student-scoped localStorage prefix eiken_q1_student_ must remain",
);
console.log("cloud progress namespace: OK");

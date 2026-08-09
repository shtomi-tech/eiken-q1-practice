const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync("static/mode-q1.js", "utf8").replace(
  "return { mount, handleKey };",
  "return { mount, handleKey, __test: { setStudent: (id) => { storageStudentId = id; }, scopedStorageKey } };",
);
const sandbox = { URLSearchParams, encodeURIComponent };
vm.runInNewContext(`${source}\nglobalThis.app = EikenQ1App;`, sandbox);

const storage = sandbox.app.__test;
assert.equal(storage.scopedStorageKey("progress"), "progress");
storage.setStudent("student-a");
assert.equal(storage.scopedStorageKey("progress"), "eiken_q1_student_student-a_progress");
storage.setStudent("student-b");
assert.equal(storage.scopedStorageKey("progress"), "eiken_q1_student_student-b_progress");
storage.setStudent("unverified:student-a");
assert.equal(storage.scopedStorageKey("progress"), "eiken_q1_student_unverified%3Astudent-a_progress");
console.log("student storage scope: OK");

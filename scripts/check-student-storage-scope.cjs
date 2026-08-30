const assert = require("node:assert/strict");
const vm = require("node:vm");
const { appJsWithTestExports } = require("./lib/app-source.cjs");

const source = appJsWithTestExports("{ setStudent: (id) => { storageStudentId = id; }, scopedStorageKey }");
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

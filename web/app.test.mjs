import test from "node:test";
import assert from "node:assert/strict";
import {interpretTOF} from "./app.mjs";

const cases = [
  [0, null, null, "INDETERMINATE"],
  [0, 0, null, "COMPLETE"],
  [0, 1, null, "DEEP"],
  [0, 10, null, "DEEP"],
  [1, null, null, "MODERATE"],
  [2, null, null, "MODERATE"],
  [3, null, null, "MODERATE"],
  [4, null, null, "INDETERMINATE"],
  [4, null, 0.3999, "SHALLOW"],
  [4, null, 0.4, "MINIMAL"],
  [4, null, 0.8999, "MINIMAL"],
  [4, null, 0.9, "RECOVERED"],
  [4, null, 1.0, "RECOVERED"],
];
for (const [count, ptc, ratio, expected] of cases) {
  test("TOF category " + JSON.stringify([count, ptc, ratio]), () => {
    const result = interpretTOF({count, ptc, ratio});
    assert.equal(result.category, expected);
    assert.equal(result.recovery_threshold_met, expected === "RECOVERED");
  });
}
for (const input of [
  {count:-1}, {count:5}, {count:2.5}, {count:true}, {count:0, ptc:-1},
  {count:0, ptc:31}, {count:1, ptc:2}, {count:4, ptc:1},
  {count:2, ratio:0.5}, {count:4, ratio:-0.1},
  {count:4, ratio:1.51}, {count:4, ratio:NaN},
  {count:4, ratio:Infinity}, {count:4, ratio:"0.9"}
]) {
  test("reject invalid " + JSON.stringify(input), () => {
    assert.throws(() => interpretTOF(input), RangeError);
  });
}

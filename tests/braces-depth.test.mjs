import assert from "node:assert/strict";
import { createRequire } from "node:module";
import test from "node:test";

const require = createRequire(import.meta.url);
const braces = require("../vendor/braces/index.js");

test("braces accepts patterns nested to the documented safety limit", () => {
  const pattern = "{a,".repeat(100) + "a" + "}".repeat(100);

  assert.equal(braces.expand(pattern).length, 101);
  assert.doesNotThrow(() => braces(pattern));
  assert.doesNotThrow(() => braces.parse("(".repeat(100) + "a" + ")".repeat(100)));
});

test("braces rejects excessive nesting in every recursive parser entry point", () => {
  const patterns = [
    "{".repeat(101) + "a,b" + "}".repeat(101),
    "(".repeat(101) + "a" + ")".repeat(101),
  ];

  for (const pattern of patterns) {
    assert.throws(() => braces.parse(pattern), SyntaxError);
    assert.throws(() => braces(pattern), SyntaxError);
    assert.throws(() => braces.expand(pattern), SyntaxError);
    assert.throws(() => braces.stringify(pattern), SyntaxError);
  }
});

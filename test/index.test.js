import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

const env = { AMBIENTE: "pruebas" };

test("/health responde 200 y estado ok", async () => {
  const response = await worker.fetch(new Request("https://example.test/health"), env);
  assert.equal(response.status, 200);
  const datos = await response.json();
  assert.equal(datos.estado, "ok");
});

test("/ responde 200", async () => {
  const response = await worker.fetch(new Request("https://example.test/"), env);
  assert.equal(response.status, 200);
});

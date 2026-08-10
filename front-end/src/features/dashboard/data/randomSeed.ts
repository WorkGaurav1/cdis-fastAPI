/**
 * Deterministic pseudo-random number generator so dummy dashboard data
 * looks stable across renders instead of reshuffling on every mount —
 * seeded from a string (e.g. a state name) rather than real data.
 */
function hashString(value: string): number {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(index);
    hash |= 0;
  }
  return hash;
}

function mulberry32(seed: number): () => number {
  let state = seed;
  return () => {
    state |= 0;
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** A repeatable [0, 1) random generator, stable for a given seed string. */
export function seededRandom(seed: string): () => number {
  return mulberry32(hashString(seed));
}

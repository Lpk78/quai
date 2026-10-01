/* Reading a package label, kept apart from the screen that shows it.

   A scan is two steps that fail for different reasons: getting characters off a label, and deciding
   what those characters mean. Only the second one is here. `readCode` takes a string from anywhere —
   a text field today, decoded camera frames tomorrow — and the screen above it
   does not change when the source does.

   That seam is the reason there is no QR dependency added here: `LP-20` owned that choice and had not
   landed when this was written, so guessing at it would have meant a library to rip out. It has since
   landed on #55 with `jsqr`, and its camera loop sits inline in `pages/Login.jsx` reading
   `QUAI:OPERATOR:` codes. Whatever decodes a frame, it hands the string to `readCode`. */

/* The label QUAI prints: a fixed prefix, then the box id the manifest knows it by. Anchored at both
   ends, because a code that merely *contains* ours is not ours. */
const LABEL = /^QUAI:BOX:([A-Za-z0-9][A-Za-z0-9-]*)$/;

export function readCode(raw) {
  if (typeof raw !== "string") return null;
  const match = LABEL.exec(raw.trim());
  return match ? match[1] : null;
}

/* What the operator is holding, as far as the manifest knows.

   Three answers rather than two, because "that is not one of our labels" and "that is our label for
   a box not on this van" are different mistakes and need different sentences on screen. The caller
   passes the boxes in, so this stays a pure function and the screen keeps the single import of the
   manifest. */
export function identify(raw, boxes) {
  const id = readCode(raw);
  if (!id) return { status: "unreadable" };
  const box = boxes.find((candidate) => candidate.id === id);
  return box ? { status: "known", box } : { status: "unknown", id };
}

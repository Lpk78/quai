/* "Today's van": the Madrid round from src/demo_fixtures.py (`SA-15`, #50 — not yet merged to
   `main` at the time of writing). Ported by hand, since there is no format shared between the
   Python fixture and the web app; re-sync against that file if its data changes before it merges.

   Replaces the `B1`-`B10` reference manifest from `documentation/prompt_evaluation.md` this file
   held until `HY-16`. That set is for scoring prompt versions against a fixed rubric, not a live
   demo load — using it here was a placeholder, not a second source of truth.

   Includes the scanned parcel (`QUAI-BOX-0001`) alongside the eighteen already-loaded boxes: the
   app has no scan interaction yet, so there is no before/after to model, only one manifest. */

/* The operator and the card they sign in with. `card_id` in `src/demo_fixtures.py` is the same
   string: /login reads it off a QR code shaped `QUAI:OPERATOR:<id>`, so the demo has one
   answer to who is driving rather than one per screen. */
export const OPERATOR_NAME = "Léo-Paul";
export const OPERATOR_CARD_ID = "QUAI-OP-7842";

export const VAN = { length: 300, width: 170, height: 170, max_weight: 1200 };

export const STOPS = [
  { id: "S1", name: "Depot-Centro" },
  { id: "S2", name: "Chamberí" },
  { id: "S3", name: "Salamanca" },
  { id: "S4", name: "Retiro" },
  { id: "S5", name: "Arganzuela" },
  { id: "S6", name: "Carabanchel" },
  { id: "S7", name: "Latina" },
  { id: "S8", name: "Moncloa-Aravaca" },
];

export const BOXES = [
  { id: "B01", label: "washing machine", length: 85, width: 85, height: 85, weight: 74, stop: "S8" },
  { id: "B02", label: "dishwasher", length: 60, width: 85, height: 85, weight: 48, stop: "S7" },
  { id: "B03", label: "tumble dryer", length: 60, width: 85, height: 85, weight: 38, stop: "S6" },
  { id: "B04", label: "oven, crated", length: 55, width: 85, height: 85, weight: 35, stop: "S5" },
  { id: "B05", label: "fridge, crated", length: 70, width: 85, height: 85, weight: 68, stop: "S7" },
  { id: "B06", label: "crate, bath fittings", length: 60, width: 85, height: 85, weight: 42,
    stop: "S6" },
  { id: "B07", label: "sofa, wrapped", length: 100, width: 170, height: 85, weight: 52, stop: "S8" },
  { id: "B08", label: "wardrobe flat-pack", length: 85, width: 85, height: 85, weight: 40,
    stop: "S6" },
  { id: "B09", label: "bookshelf flat-pack", length: 50, width: 85, height: 85, weight: 26,
    stop: "S5" },
  { id: "B10", label: "tv, boxed", length: 45, width: 85, height: 45, weight: 15, stop: "S3" },
  { id: "B11", label: "office chair", length: 55, width: 85, height: 45, weight: 14, stop: "S4" },
  { id: "B12", label: "carton, books", length: 40, width: 85, height: 45, weight: 22, stop: "S4" },
  { id: "B13", label: "carton, kitchen", length: 40, width: 85, height: 45, weight: 18, stop: "S3" },
  { id: "B14", label: "carton, linen", length: 50, width: 85, height: 45, weight: 11, stop: "S2" },
  { id: "B15", label: "carton, toys", length: 45, width: 85, height: 45, weight: 9, stop: "S1" },
  { id: "B16", label: "crate, tiles", length: 40, width: 85, height: 45, weight: 62, stop: "S7" },
  { id: "B17", label: "carton, glassware", length: 40, width: 85, height: 45, weight: 13,
    stop: "S2" },
  { id: "B18", label: "carton, lamps", length: 40, width: 85, height: 45, weight: 8, stop: "S1" },
  { id: "QUAI-BOX-0001", label: "fragile parcel", length: 40, width: 30, height: 25, weight: 8,
    stop: "S2" },
];

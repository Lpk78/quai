/* "Today's van": the Paris round from src/demo_fixtures.py (`SA-15`, #50 — not yet merged to
   `main` at the time of writing). Ported by hand, since there is no format shared between the
   Python fixture and the web app; re-sync against that file if its data changes before it merges.

   Replaces the `B1`-`B10` reference manifest from `documentation/prompt_evaluation.md` this file
   held until `HY-16`. That set is for scoring prompt versions against a fixed rubric, not a live
   demo load — using it here was a placeholder, not a second source of truth.

   `BOXES` is the eighteen boxes already in the van. The parcel scanned on stage is `SCANNED_PARCEL`,
   held apart from them since `SA-17b` so that /app/scan has something to add — see the note on it
   below. `loadWith()` is the one place the two are put back together. */

/* The operator and the card they sign in with. `card_id` in `src/demo_fixtures.py` is the same
   string: /login reads it off a QR code shaped `QUAI:OPERATOR:<id>`, so the demo has one
   answer to who is driving rather than one per screen. */
export const OPERATOR_NAME = "Léo-Paul";
export const OPERATOR_CARD_ID = "QUAI-OP-7842";

export const VAN = { length: 300, width: 170, height: 170, max_weight: 1200 };

/* The round, in delivery order. `address` is what `POST /route` geocodes; `name` is what the
   screens show. Both are needed and neither is derived from the other: the Base Adresse
   Nationale wants a postal address, an operator reads a district.

   Paris rather than Madrid because that geocoder covers France only — a Spanish address returns
   a 422 that no amount of front-end work can fix. All eight resolve; three of them match at
   street level rather than house number, and `/app/route` shows the label the geocoder returned
   rather than the one we asked for, so a wrong match is visible instead of hidden. */
export const STOPS = [
  { id: "S1", name: "Hôtel de Ville",
    address: "4 Rue de Lobau, 75004 Paris" },
  { id: "S2", name: "Champs-Élysées",
    address: "25 Avenue des Champs-Élysées, 75008 Paris" },
  { id: "S3", name: "Bastille",
    address: "5 Place de la Bastille, 75011 Paris" },
  { id: "S4", name: "Convention",
    address: "18 Rue de la Convention, 75015 Paris" },
  { id: "S5", name: "Voltaire",
    address: "42 Boulevard Voltaire, 75011 Paris" },
  { id: "S6", name: "Faubourg Saint-Antoine",
    address: "7 Rue du Faubourg Saint-Antoine, 75012 Paris" },
  { id: "S7", name: "Saint-Germain",
    address: "33 Rue de Rennes, 75006 Paris" },
  { id: "S8", name: "Opéra",
    address: "2 Rue de la Paix, 75002 Paris" },
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
];

/* The parcel scanned on stage, kept out of `BOXES` on purpose (`SA-17b`).

   `BOXES` means "already in the van". This one is not: in `src/demo_fixtures.py` it starts outside
   the load and the demo adds it, which is the whole point of the scan step. Holding it here instead
   of in that list is what lets `/app/scan` add something — until this split it was already in the
   manifest, so a scan had nothing to do and the screen could only confirm what was there.

   It keeps its stop: the operator dictates what to do with it, but where it comes off is known from
   the label.

   The label is deliberately dull and there is no fragility flag (`SA-24`). It used to read "fragile
   parcel", which made the demo circular — the operator announced something the fixture had already
   decided. Fragility is known to whoever is holding the box, so it arrives in what they say.

   The size and the stop are load-bearing for the demonstration, not arbitrary. At 65 x 85 x 85 it is
   among the largest boxes aboard, so the plan the app shows — ordered by volume, because `POST /plan`
   is given no route — loads it early and stacks boxes over it, and "put it on top" visibly lifts it
   out. Stop 1 is loaded last in the route-ordered plan, which is what keeps that plan whole. Keep both
   in step with `src/demo_fixtures.py`, where the solver reads them and where the test proving both
   states lives. */
export const SCANNED_PARCEL = {
  id: "QUAI-BOX-0001", label: "carton, unmarked", length: 65, width: 85, height: 85, weight: 8,
  stop: "S1",
};

/* Everything the van is carrying once the scanned parcel is aboard — eighteen, or nineteen. The one
   place that arithmetic is written down, so a screen counting boxes cannot disagree with a screen
   planning them. */
export function loadWith(parcel) {
  return parcel ? [...BOXES, parcel] : BOXES;
}

/* "Today's van": the reference manifest from documentation/prompt_evaluation.md, reused here
   rather than invented, until the real manifest comes from the server (Supabase). It is the same
   load `POST /constraints` is scored against, so an item named on this screen is always one the
   solver already knows about. */

export const VAN_ID = "Van 12";

export const STOPS = [
  { id: "S1", name: "Rouen" },
  { id: "S2", name: "Le Havre" },
  { id: "S3", name: "Caen" },
];

export const BOXES = [
  { id: "B1", label: "washing machine", length: 60, width: 60, height: 85, weight: 70 },
  { id: "B2", label: "flat-screen TV", length: 120, width: 15, height: 70, weight: 18 },
  { id: "B3", label: "pallet of tiles", length: 120, width: 80, height: 60, weight: 900 },
  { id: "B4", label: "sofa", length: 220, width: 90, height: 80, weight: 55 },
  { id: "B5", label: "box of glassware", length: 40, width: 40, height: 40, weight: 12 },
  { id: "B6", label: "fridge", length: 60, width: 65, height: 180, weight: 85 },
  { id: "B7", label: "paint cans (× 6)", length: 50, width: 30, height: 30, weight: 30 },
  { id: "B8", label: "mattress", length: 200, width: 140, height: 25, weight: 25 },
  { id: "B9", label: "toolbox", length: 60, width: 30, height: 30, weight: 22 },
  { id: "B10", label: "garden table", length: 150, width: 90, height: 75, weight: 40 },
];

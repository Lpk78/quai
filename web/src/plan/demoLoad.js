/* The load the screen asks the solver to plan, until the box form (#8) lets an operator enter one.
 *
 * These are the eleven boxes of `src/demo.py`, kept identical on purpose: the same load appears in
 * the README, in the solver's own demo and in `documentation/roadmap.md`'s fill-rate figures, so a
 * number read off this screen can be compared with one read anywhere else. The screen says plainly
 * that it is a demo load; it never implies the operator entered it.
 */
export const DEMO_VAN = { length: 300, width: 170, height: 170, max_weight: 1200 };

export const DEMO_BOXES = [
  { id: "fridge", length: 70, width: 70, height: 160, weight: 60 },
  { id: "washer", length: 60, width: 60, height: 85, weight: 70 },
  { id: "dryer", length: 60, width: 60, height: 85, weight: 40 },
  { id: "sofa", length: 200, width: 90, height: 80, weight: 45 },
  { id: "tv", length: 130, width: 20, height: 80, weight: 15 },
  { id: "carton-1", length: 60, width: 40, height: 40, weight: 12 },
  { id: "carton-2", length: 60, width: 40, height: 40, weight: 12 },
  { id: "carton-3", length: 60, width: 40, height: 40, weight: 10 },
  { id: "carton-4", length: 40, width: 30, height: 30, weight: 6 },
  { id: "carton-5", length: 40, width: 30, height: 30, weight: 6 },
  { id: "mattress", length: 190, width: 140, height: 25, weight: 25 },
];

export const DEMO_REQUEST = { container: DEMO_VAN, boxes: DEMO_BOXES };

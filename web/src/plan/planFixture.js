/* A real `POST /plan` response, generated from `src/demo.py` by the solver itself.
 *
 * Written down rather than invented so the tests render what the server actually returns —
 * the same reason the README's examples are real responses. Regenerate with the snippet in
 * `prompts/dev/SA-14a_app-plan-screen.md` if the solver's output ever changes.
 */
export const PLAN_FIXTURE = {
  "placements": [
    {
      "id": "sofa",
      "x": 0,
      "y": 0,
      "z": 0,
      "dx": 200,
      "dy": 90,
      "dz": 80
    },
    {
      "id": "fridge",
      "x": 0,
      "y": 90,
      "z": 0,
      "dx": 70,
      "dy": 70,
      "dz": 160
    },
    {
      "id": "dryer",
      "x": 70,
      "y": 90,
      "z": 0,
      "dx": 60,
      "dy": 60,
      "dz": 85
    },
    {
      "id": "washer",
      "x": 130,
      "y": 90,
      "z": 0,
      "dx": 60,
      "dy": 60,
      "dz": 85
    },
    {
      "id": "tv",
      "x": 70,
      "y": 150,
      "z": 0,
      "dx": 130,
      "dy": 20,
      "dz": 80
    },
    {
      "id": "carton-1",
      "x": 190,
      "y": 90,
      "z": 0,
      "dx": 60,
      "dy": 40,
      "dz": 40
    },
    {
      "id": "carton-2",
      "x": 200,
      "y": 0,
      "z": 0,
      "dx": 60,
      "dy": 40,
      "dz": 40
    },
    {
      "id": "carton-3",
      "x": 200,
      "y": 40,
      "z": 0,
      "dx": 60,
      "dy": 40,
      "dz": 40
    },
    {
      "id": "carton-4",
      "x": 250,
      "y": 90,
      "z": 0,
      "dx": 40,
      "dy": 30,
      "dz": 30
    },
    {
      "id": "carton-5",
      "x": 250,
      "y": 120,
      "z": 0,
      "dx": 40,
      "dy": 30,
      "dz": 30
    }
  ],
  "unplaced": [
    "mattress"
  ],
  "fill_rate": 0.39261822376009226,
  "total_weight": 276.0
};

export const EMPTY_PLAN = { placements: [], unplaced: [], fill_rate: 0, total_weight: 0 };

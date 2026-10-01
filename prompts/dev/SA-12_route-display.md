# SA-12 — Route display data: geocoding, road geometry and per-stop ETA

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-10-01
- **Branch:** `feature/route-display`
- **Issue:** none — this is new scope, not on the roadmap

## Prompt as typed

```
/task SA-12 Add route display data to the server: POST /route takes the ordered stops of a delivery
list (addresses) and returns, in that exact order, the geocoded points (api-adresse.data.gouv.fr), the
road route geometry and an estimated arrival time per stop (OSRM), plus total distance and duration.
QUAI never reorders stops: the order comes with the manifest. Timeouts and clear errors when a
geocoder or router is down; tests with mocked HTTP; document the two services and their limits in the
README.
```

## Outcome


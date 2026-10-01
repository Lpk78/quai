import { createContext, useContext, useMemo, useState } from "react";

/* What the operator scanned, between the screen that read the label and the screen that plans with it.

   Context rather than a prop or router state, for one reason: the parcel has to survive the two hops
   /app/scan → /app/dictate → /app/plan, and router state only survives the hop you attach it to. A
   parcel that vanished on the second navigation would be worse than not modelling it at all, because
   the plan would quietly go back to eighteen boxes with nothing on screen saying so.

   It does not survive a page reload, which is the right trade for now: a reload is a fresh round, and
   persisting it would mean deciding when a scan expires. That decision belongs with real operator
   sessions (`LP-20` added /login), not here. */
const ScannedParcelContext = createContext(null);

export function ScannedParcelProvider({ children }) {
  const [parcel, setParcel] = useState(null);
  /* `scan` rather than `set`: the only thing that may put a parcel here is a label being read, and
     `clear` exists so a round can be started over without a reload. */
  const value = useMemo(() => ({ parcel, scan: setParcel, clear: () => setParcel(null) }), [parcel]);
  return <ScannedParcelContext.Provider value={value}>{children}</ScannedParcelContext.Provider>;
}

export function useScannedParcel() {
  const value = useContext(ScannedParcelContext);
  if (!value) {
    // A screen rendered outside the provider would silently plan eighteen boxes forever, so this
    // fails loudly in development instead.
    throw new Error("useScannedParcel needs a <ScannedParcelProvider> above it");
  }
  return value;
}

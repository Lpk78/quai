import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { SCANNED_PARCEL } from "../data/manifest.js";

/* What the operator scanned, between the screen that read the label and the screen that plans with it.

   Context rather than a prop or router state, for one reason: the parcel has to survive the two hops
   /app/scan → /app/dictate → /app/plan, and router state only survives the hop you attach it to. A
   parcel that vanished on the second navigation would be worse than not modelling it at all, because
   the plan would quietly go back to eighteen boxes with nothing on screen saying so.

   It also survives a reload, through `sessionStorage` (`SA-17b`, asked for in review of #57). The
   reason is the same failure in a different disguise: a reload mid-demo would drop the load back to
   eighteen boxes with nothing on screen admitting it, and an operator on a dock reloads a page for
   reasons nobody planned for. `sessionStorage` rather than `localStorage` because a scan belongs to
   one sitting, not for ever — closing the tab ends the round, which is the expiry rule we would
   otherwise have had to invent.

   Only the *id* is stored, never the box. `data/manifest.js` stays the single source of what a parcel
   measures and weighs; a copy in storage would be a second one, free to go stale and impossible to
   notice. An id that nothing recognises is dropped rather than restored. */
const ScannedParcelContext = createContext(null);

const STORAGE_KEY = "quai.scannedParcel";

/* The parcels a stored id may name. One today; a lookup rather than an equality check so that a
   second scannable package does not turn this into a special case. */
const SCANNABLE = { [SCANNED_PARCEL.id]: SCANNED_PARCEL };

/* Storage is wrapped both ways: Safari in private mode throws on write, some embedded browsers have
   no `sessionStorage` at all, and a parcel that cannot be remembered is not a reason to fail to load
   the screen. Losing persistence degrades to the behaviour before this change. */
function readStored() {
  try {
    const id = window.sessionStorage?.getItem(STORAGE_KEY);
    return id ? SCANNABLE[id] ?? null : null;
  } catch {
    return null;
  }
}

function writeStored(parcel) {
  try {
    if (parcel) window.sessionStorage?.setItem(STORAGE_KEY, parcel.id);
    else window.sessionStorage?.removeItem(STORAGE_KEY);
  } catch {
    /* Not remembering is survivable; crashing the app over it is not. */
  }
}

export function ScannedParcelProvider({ children }) {
  const [parcel, setParcel] = useState(readStored);

  useEffect(() => {
    writeStored(parcel);
  }, [parcel]);

  /* `scan` rather than `set`: the only thing that may put a parcel here is a label being read, and
     `clear` exists so a round can be started over without closing the tab. */
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

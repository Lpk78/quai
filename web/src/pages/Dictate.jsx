import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError, postConstraints, postPlan } from "../api.js";
import { STOPS, VAN, loadWith } from "../data/manifest.js";
import { IconBox, IconCube, IconMic, IconPin } from "../landing/icons.jsx";
import { useScannedParcel } from "../scan/scannedParcel.jsx";

// `/plan` takes a box the way `POST /plan` has always taken one — id, dimensions, weight — not the
// richer record `/constraints` reads a label and a stop off. Stripped here rather than left for
// pydantic to ignore, so the request matches what `web/src/plan/demoLoad.js` already sends.
//
// Derived per render rather than once at import, because since `SA-17b` the load is eighteen boxes or
// nineteen depending on whether a parcel was scanned, and a constant captured at import would always
// be the eighteen.
function planBoxesOf(boxes) {
  return boxes.map(({ id, length, width, height, weight }) => (
    { id, length, width, height, weight }
  ));
}

// jsdom defines neither, so tests exercise the text-field fallback the same way an unsupported
// browser does.
const SpeechRecognitionImpl = window.SpeechRecognition || window.webkitSpeechRecognition;

/* One rule card per constraint the model actually returned: a title naming the item and the rule,
   and a line underneath saying what it means for the load.

   The mockup's four cards (paint cans, glass, frozen items, heavier items) are illustrations, and
   none of them is hardcoded here — what the operator sees is whatever `/constraints` parsed from the
   sentence they said. The mockup's per-item pictograms are not reproducible either: a paint tin or a
   wine glass would have to be inferred from a box label, which is a guess. The icon is chosen from
   the *rule*, which is known, and there are three of them because there are three kinds of rule. */
const CONSTRAINT_LABELS = {
  not_stackable: (c) => [`${c.item} — nothing on top`, "Nothing may be stacked on this one."],
  at_bottom: (c) => [`${c.item} — bottom of the load`, "Loaded on the floor of the van."],
  on_top: (c) => [`${c.item} — top layer`, "Nothing is placed above it."],
  keep_upright: (c) => [`${c.item} — keep upright`, "Never laid on its side or turned over."],
  unload_at: (c) => [`${c.item} — unload at ${c.stop}`, "Placed for the stop it comes off at."],
  load_last: (c) => [`${c.item} — load last`, "Goes in last, nearest the doors."],
  max_stack_height: (c) => [`${c.item} — stack up to ${c.limit_cm} cm`,
    "Nothing stacked higher than this above it."],
  max_weight_on: (c) => [`${c.item} — up to ${c.limit_kg} kg on top`,
    "The weight resting on it is capped."],
  max_total_weight: (c) => [`Whole load — up to ${c.limit_kg} kg`,
    "The van is not loaded past this weight."],
};

/* Chosen from the rule, never from the item. `unload_at` is the only one that is about a place;
   the rest are about how the stack is built or how the box is turned. */
const CONSTRAINT_ICONS = {
  unload_at: IconPin,
  keep_upright: IconBox,
  load_last: IconBox,
};

const REASON_TEXT = {
  ambiguous: "This could mean more than one thing.",
  unknown_item: "This is not in today’s manifest.",
  unit_missing: "A number was given with no unit.",
  contradiction: "This asks for two things that cannot both hold.",
  out_of_scope: "This is not a loading constraint.",
  injection_attempt: "This tried to give QUAI new instructions.",
};

function describeConstraint(constraint) {
  const describe = CONSTRAINT_LABELS[constraint.type];
  // An unknown type still gets a card rather than vanishing: the contract says the schema is the
  // gate, so anything that got through it is real and must be shown, named as best we can.
  return describe ? describe(constraint) : [constraint.type, "Understood, with no plainer wording."];
}

export default function Dictate() {
  const [step, setStep] = useState("talk"); // talk | sending | result | error
  const [transcript, setTranscript] = useState("");
  const [listening, setListening] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [confirming, setConfirming] = useState(false);
  const { parcel } = useScannedParcel();
  // Eighteen in the van, plus the parcel if one was scanned on the way here. Both the sentence sent to
  // `/constraints` and the load sent to `/plan` have to see the same list, or the model would be asked
  // about a box the solver is not given.
  const boxes = loadWith(parcel);
  const recognitionRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => () => recognitionRef.current?.stop(), []);

  function toggleListening() {
    if (!SpeechRecognitionImpl) return;
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      return;
    }
    const recognition = new SpeechRecognitionImpl();
    recognition.lang = navigator.language || "en-US";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = (event) => {
      setTranscript(
        Array.from(event.results)
          .map((result) => result[0].transcript)
          .join(" ")
          .trim(),
      );
    };
    recognition.onend = () => {
      recognitionRef.current = null;
      setListening(false);
    };
    recognitionRef.current = recognition;
    setListening(true);
    recognition.start();
  }

  async function handleSend() {
    setStep("sending");
    setError(null);
    try {
      const data = await postConstraints(transcript, boxes, STOPS);
      setResult(data);
      setStep("result");
    } catch (err) {
      setError(err instanceof ApiError
        ? err
        : new ApiError("server", "QUAI could not translate that sentence.", String(err)));
      setStep("error");
    }
  }

  function handleEdit() {
    setStep("talk");
  }

  async function handleConfirm() {
    setConfirming(true);
    setError(null);
    try {
      const planBoxes = planBoxesOf(boxes);
      const plan = await postPlan({
        container: VAN,
        boxes: planBoxes,
        constraints: result.constraints,
      });
      navigate("/app/plan", { state: { plan, request: { container: VAN, boxes: planBoxes } } });
    } catch (err) {
      setError(err instanceof ApiError
        ? err
        : new ApiError("server", "QUAI could not build a plan.", String(err)));
      setStep("error");
      setConfirming(false);
    }
  }

  return (
    <>
      <Link className="muted back-link" to="/app">
        ← Home
      </Link>

      {step === "talk" && (
        <TalkStep
          transcript={transcript}
          onTranscriptChange={setTranscript}
          listening={listening}
          onToggleListening={toggleListening}
          onSend={handleSend}
          speechSupported={Boolean(SpeechRecognitionImpl)}
        />
      )}

      {step === "sending" && (
        <div className="card status-card" role="status">
          <p>Reading your rules…</p>
        </div>
      )}

      {step === "result" && (
        <ResultStep
          result={result}
          onEdit={handleEdit}
          onConfirm={handleConfirm}
          confirming={confirming}
        />
      )}

      {step === "error" && <Failure error={error} onEdit={handleEdit} />}
    </>
  );
}

function Failure({ error, onEdit }) {
  // Same read as PlanScreen.jsx's Failure: `message` already carries the server's own words when
  // it had any (see `api.js`'s `post()`), so printing `detail` again only adds something for a
  // "server" failure, where the two can differ.
  const unreachable = error.kind === "unreachable";
  return (
    <div className="card status-card" role="alert">
      <p>{error.message}</p>
      {unreachable && (
        <p className="muted">
          The solver runs separately: <code className="data">uvicorn server:app --app-dir src</code>
        </p>
      )}
      {error.detail && !unreachable && error.detail !== error.message && (
        <p className="muted data">{error.detail}</p>
      )}
      <button type="button" className="button button--quiet" onClick={onEdit}>
        Edit
      </button>
    </div>
  );
}

// Decorative only: a fixed waveform either side of the mic, not a visualisation of the audio
// level, which `SpeechRecognitionImpl` does not expose. Five bars, height set in CSS.
function SoundWave() {
  return (
    <span className="sound-wave" aria-hidden="true">
      <span />
      <span />
      <span />
      <span />
      <span />
    </span>
  );
}

function TalkStep({
  transcript,
  onTranscriptChange,
  listening,
  onToggleListening,
  onSend,
  speechSupported,
}) {
  return (
    <>
      <h1>
        Tell QUAI your
        <br />
        loading rules
      </h1>
      <p className="muted">
        Speak naturally. We’ll turn your instructions into structured constraints.
      </p>

      {speechSupported ? (
        <div className="mic-panel">
          <div className="mic-wrap">
            <SoundWave />
            {/* The mockup's soft concentric rings. Two spans rather than a box-shadow so the
                listening state can grow them without the layout moving. */}
            <span className={`mic-rings${listening ? " mic-rings--active" : ""}`} aria-hidden="true">
              <span />
              <span />
            </span>
            <button
              type="button"
              className={`mic${listening ? " mic--active" : ""}`}
              onClick={onToggleListening}
              aria-pressed={listening}
              aria-label={listening ? "Stop talking" : "Tap and speak"}
            >
              <IconMic />
            </button>
            <SoundWave />
          </div>
          <p className="mic-label">{listening ? "Listening…" : "Tap and speak"}</p>
          <p className="mic-example">
            “Keep the pallet of tiles upright and load the toolbox last.”
          </p>
        </div>
      ) : (
        <p className="muted">Speech isn’t available on this device. Type your rules instead.</p>
      )}

      <label className="field">
        <span className="field__label">Transcript</span>
        <textarea
          rows={4}
          value={transcript}
          onChange={(event) => onTranscriptChange(event.target.value)}
          placeholder="Keep the pallet of tiles upright and load the toolbox last."
        />
      </label>

      <button
        type="button"
        className="button button--block"
        disabled={!transcript.trim()}
        onClick={onSend}
      >
        Send to QUAI <span aria-hidden="true">→</span>
      </button>
    </>
  );
}

function ResultStep({ result, onEdit, onConfirm, confirming }) {
  const { constraints, unresolved } = result;
  return (
    <>
      <h1>Here’s what QUAI understood</h1>

      {constraints.length > 0 && (
        <>
          {/* No "Edit" link beside this heading and no "+ Add a rule" button under the list,
              though the mockup has both: neither exists as behaviour. Editing one rule in place,
              or adding one by hand, means a rule list that accumulates across sentences, which is
              roadmap row 12. The Edit button in the actions row below is a different thing and is
              real — it returns to the transcript. */}
          <h2 className="rules-title">Your loading rules</h2>
          <ul className="constraint-list">
            {constraints.map((constraint, index) => {
              const [title, detail] = describeConstraint(constraint);
              const Icon = CONSTRAINT_ICONS[constraint.type] ?? IconCube;
              return (
                <li className="card constraint-card" key={index}>
                  <span className="constraint-card__icon" aria-hidden="true"><Icon /></span>
                  <span className="constraint-card__text">
                    <strong>{title}</strong>
                    <span className="muted">{detail}</span>
                  </span>
                </li>
              );
            })}
          </ul>
        </>
      )}

      {unresolved.length > 0 && (
        <ul className="unresolved-list">
          {unresolved.map((entry, index) => (
            <li className="card unresolved-card" key={index}>
              <span className="badge badge--warning">Needs a decision</span>
              <p>“{entry.text}”</p>
              <p className="muted">{REASON_TEXT[entry.reason] ?? entry.reason}</p>
              {entry.question && <p>{entry.question}</p>}
            </li>
          ))}
        </ul>
      )}

      {constraints.length === 0 && unresolved.length === 0 && (
        <p className="muted">QUAI did not find any rule in that sentence.</p>
      )}

      <div className="actions">
        <button type="button" className="button button--quiet" onClick={onEdit}>
          Edit
        </button>
        <button type="button" className="button" onClick={onConfirm} disabled={confirming}>
          {confirming ? "Planning…" : "Confirm"} <span aria-hidden="true">→</span>
        </button>
      </div>
    </>
  );
}

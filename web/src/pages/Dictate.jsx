import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { postConstraints } from "../api.js";
import { BOXES, STOPS } from "../data/manifest.js";
import { IconMic } from "../landing/icons.jsx";

// jsdom defines neither, so tests exercise the text-field fallback the same way an unsupported
// browser does.
const SpeechRecognitionImpl = window.SpeechRecognition || window.webkitSpeechRecognition;

const CONSTRAINT_LABELS = {
  not_stackable: (c) => `Nothing on top: ${c.item}`,
  at_bottom: (c) => `Keep at the bottom: ${c.item}`,
  on_top: (c) => `Keep in the top layer: ${c.item}`,
  keep_upright: (c) => `Keep upright: ${c.item}`,
  unload_at: (c) => `Unload at ${c.stop}: ${c.item}`,
  load_last: (c) => `Load last: ${c.item}`,
  max_stack_height: (c) => `Max stack height on ${c.item}: ${c.limit_cm} cm`,
  max_weight_on: (c) => `Max weight on ${c.item}: ${c.limit_kg} kg`,
  max_total_weight: (c) => `Max total weight: ${c.limit_kg} kg`,
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
  return describe ? describe(constraint) : constraint.type;
}

export default function Dictate() {
  const [step, setStep] = useState("talk"); // talk | sending | result | error
  const [transcript, setTranscript] = useState("");
  const [listening, setListening] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const recognitionRef = useRef(null);

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
      const data = await postConstraints(transcript, BOXES, STOPS);
      setResult(data);
      setStep("result");
    } catch (err) {
      setError(err.message);
      setStep("error");
    }
  }

  function handleEdit() {
    setStep("talk");
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
        <ResultStep result={result} onEdit={handleEdit} />
      )}

      {step === "error" && (
        <div className="card status-card">
          <p>QUAI could not reach the solver just now.</p>
          <p className="muted">{error}</p>
          <button type="button" className="button button--quiet" onClick={handleEdit}>
            Edit
          </button>
        </div>
      )}
    </>
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
      <h1>Tell QUAI your loading rules</h1>
      <p className="muted">
        Speak naturally. We’ll turn your words into rules the solver can check.
      </p>

      {speechSupported ? (
        <div className="mic-wrap">
          <button
            type="button"
            className={`mic${listening ? " mic--active" : ""}`}
            onClick={onToggleListening}
            aria-pressed={listening}
            aria-label={listening ? "Stop talking" : "Tap to talk"}
          >
            <IconMic />
          </button>
          <p className="muted">{listening ? "Listening…" : "Tap to talk"}</p>
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

function ResultStep({ result, onEdit }) {
  const { constraints, unresolved } = result;
  return (
    <>
      <h1>Here’s what QUAI understood</h1>

      {constraints.length > 0 && (
        <ul className="constraint-list">
          {constraints.map((constraint, index) => (
            <li className="card constraint-card" key={index}>
              <span className="constraint-card__icon">✓</span>
              <span>{describeConstraint(constraint)}</span>
            </li>
          ))}
        </ul>
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
        <Link className="button" to="/app/plan">
          Confirm <span aria-hidden="true">→</span>
        </Link>
      </div>
    </>
  );
}

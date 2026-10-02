import { useEffect, useRef, useState } from "react";
import jsQR from "jsqr";

/* The camera half of reading a QR code: open the rear camera, draw each frame to an off-screen
 * canvas, hand it to `jsqr`, and pass whatever string comes back to the screen that asked.
 *
 * Lifted out of `pages/Login.jsx` (`LP-20`, #55) unchanged in behaviour, because two screens now
 * read codes — an operator card and a package label — and only the *meaning* of the string differs.
 * `Scan.jsx` and `scanCode.js` were both written against this extraction happening later and say so
 * in their own comments. Nothing here knows what a code means: that is `readOperatorCode()` on one
 * screen and `identify()` on the other, and it stays there.
 *
 * `jsqr` decodes a still image and nothing else — no camera handling, no DOM of its own — so the
 * video element, the framing and every failure state below are ours, styled from `tokens.css` like
 * the rest of the app.
 *
 * The camera needs a secure context. The phone demo serves HTTPS for that reason (README, "Phone
 * demo"), but a machine with no certificate, a phone that does not trust the one there is, and jsdom
 * all land in the same place: `navigator.mediaDevices` absent. That is not an error state to
 * apologise for — it is the manual-entry state, and every screen using this keeps the field that
 * state sends the operator back to.
 *
 * Props:
 *   `onCode(text)`   every decoded string. **Return `true` to stop decoding**, which is how the
 *                    caller says "this one counted". A refused code returns false and the loop
 *                    keeps looking, which is what lets `/login` reject a card without going dead.
 *   `resumeToken`    change it to start decoding again after a stop. `/login` never passes one — it
 *                    reads exactly one card per visit. `/app/scan` bumps it to read the next parcel.
 *   `fallback(why)`  what to show when there is no camera, given `"insecure" | "unsupported" |
 *                    "refused"`. The copy belongs to the screen: one talks about an operator card,
 *                    the other about a package label.
 *   `children(status)` rendered after the viewfinder, given `"starting" | "scanning" | "no-camera"`,
 *                    so each screen writes its own "looking for…" line in its own words.
 */
export default function QrScanner({ onCode, resumeToken, fallback, children }) {
  const [status, setStatus] = useState("starting"); // starting | scanning | no-camera
  const [why, setWhy] = useState(null); // insecure | unsupported | refused
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Held in a ref as well as in state: the scan loop runs outside React and must stop on the first
  // accepted code rather than on the next render.
  const doneRef = useRef(false);

  // The caller's latest `onCode`, so the camera effect below can stay `[]` and never reopen the
  // camera because a parent re-rendered with a new closure.
  const onCodeRef = useRef(onCode);
  useEffect(() => { onCodeRef.current = onCode; }, [onCode]);

  /* Resuming is the one behaviour this has that `Login.jsx` did not: it latched `doneRef` for good,
     because a card is read once. A package screen reads one label, shows it, and then reads the
     next. Clearing the latch rather than remounting keeps the camera open and the stream running —
     a remount would make the viewfinder blink between every parcel. */
  useEffect(() => {
    if (resumeToken !== undefined) doneRef.current = false;
  }, [resumeToken]);

  useEffect(() => {
    if (!navigator.mediaDevices?.getUserMedia) {
      // Both reach the same screen; they are told apart because they are fixed differently — one by
      // serving HTTPS, the other not at all.
      setWhy(window.isSecureContext === false ? "insecure" : "unsupported");
      setStatus("no-camera");
      return undefined;
    }

    let live = true;
    let stream = null;
    let frame = 0;

    function scan() {
      frame = requestAnimationFrame(scan);
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (doneRef.current || !video || !canvas || !video.videoWidth) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext("2d");
      // A browser with no 2D context is a browser that cannot decode a frame: the typed field
      // still works, and the screen must not fall over on the way to telling them so.
      if (!context) return;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      let found = null;
      try {
        const { data, width, height } = context.getImageData(0, 0, canvas.width, canvas.height);
        // A frame with no code in it decodes to null, which is the common case, not a failure.
        found = jsQR(data, width, height);
      } catch {
        // A frame that cannot be read at all is one dropped frame, not a broken screen: the next
        // one is 16 ms away. Nothing here is allowed to take the screen down.
        found = null;
      }
      // The caller decides whether this one counted. Anything but `true` keeps the loop looking.
      if (found?.data && onCodeRef.current?.(found.data) === true) doneRef.current = true;
    }

    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "environment" } })
      .then((opened) => {
        if (!live) {
          opened.getTracks().forEach((track) => track.stop());
          return;
        }
        stream = opened;
        if (videoRef.current) {
          videoRef.current.srcObject = opened;
          videoRef.current.play().catch(() => {});
        }
        setStatus("scanning");
        scan();
      })
      .catch(() => {
        // Refused, in use, or no camera on this device: one state to the operator, who has a field
        // to type in either way.
        if (!live) return;
        setWhy("refused");
        setStatus("no-camera");
      });

    return () => {
      live = false;
      cancelAnimationFrame(frame);
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  return (
    <>
      <div className="scanner" data-status={status}>
        {/* Kept mounted while starting so the stream has somewhere to go the moment the camera
            opens; hidden from assistive tech, which has nothing to read in it. */}
        <video ref={videoRef} className="scanner__video" autoPlay playsInline muted aria-hidden="true" />
        <canvas ref={canvasRef} className="scanner__canvas" aria-hidden="true" />
        {status === "scanning" && <div className="scanner__frame" aria-hidden="true" />}
        {status === "no-camera" && fallback?.(why)}
      </div>
      {children?.(status)}
    </>
  );
}

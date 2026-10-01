import Phone from "./Phone.jsx";
import { IconBox, IconMic, IconPin, IconRule, IconTick } from "./icons.jsx";

/* The four phone screens on the landing page. Every number here is demo data from the brief, and
   nothing on them claims a route, an ETA, live tracking or a saving. */

export function HomeScreen() {
  return (
    <Phone title="The QUAI app, home screen">
      <div className="screen">
        <p className="screen__hello">Good morning. Let&rsquo;s load.</p>
        <p className="screen__sub data">Van 12 · 3 stops · 24 parcels</p>

        <div className="screen__card">
          <p className="screen__card-title">Loading plan ready</p>
          <p className="screen__card-body">Built from your rules and your stop order.</p>
          <span className="screen__cta">
            Start loading <span aria-hidden="true">→</span>
          </span>
        </div>

        <div className="screen__tiles">
          {[
            ["24", "Parcels", <IconBox key="b" />],
            ["3", "Stops", <IconPin key="p" />],
            ["8", "Rules", <IconRule key="r" />],
          ].map(([value, label, icon]) => (
            <div className="screen__tile" key={label}>
              {icon}
              <strong className="data">{value}</strong>
              <span>{label}</span>
            </div>
          ))}
        </div>
      </div>
    </Phone>
  );
}

export function VoiceScreen() {
  const rules = [
    ["Paint cans", "load last"],
    ["Glass panels", "nothing on top"],
    ["Water packs", "at the bottom"],
  ];
  return (
    <Phone title="The QUAI app, loading rules screen">
      <div className="screen">
        <p className="screen__heading">Your loading rules</p>

        <div className="screen__mic">
          <span className="screen__wave" aria-hidden="true">
            <i /> <i /> <i /> <i /> <i /> <i /> <i />
          </span>
          <span className="screen__mic-button" aria-hidden="true">
            <IconMic />
          </span>
          <span className="screen__wave" aria-hidden="true">
            <i /> <i /> <i /> <i /> <i /> <i /> <i />
          </span>
        </div>

        <ul className="screen__rules">
          {rules.map(([item, rule]) => (
            <li key={item}>
              <IconTick />
              <span>
                <strong>{item}</strong> — {rule}
              </span>
            </li>
          ))}
        </ul>

        <div className="screen__question">
          <p className="screen__question-title">&ldquo;The heavy one&rdquo; — which parcel?</p>
          <p className="screen__card-body">QUAI asks rather than guessing.</p>
        </div>
      </div>
    </Phone>
  );
}

export function PlanScreen() {
  return (
    <Phone title="The QUAI app, 3D loading plan screen">
      <div className="screen screen--plan">
        <p className="screen__heading">3D load plan</p>

        <div className="screen__van" aria-hidden="true">
          <span className="screen__parcel screen__parcel--a" />
          <span className="screen__parcel screen__parcel--b" />
          <span className="screen__parcel screen__parcel--c" />
          <span className="screen__parcel screen__parcel--d" />
          <span className="screen__parcel screen__parcel--next" />
        </div>

        <div className="screen__callout">
          <p className="screen__card-title">Next parcel</p>
          <p className="screen__card-body data">Stop 2 · B35 · 22 kg</p>
        </div>

        <div className="screen__progress">
          <span className="screen__progress-bar" aria-hidden="true">
            <i style={{ width: `${(17 / 24) * 100}%` }} />
          </span>
          <span className="data">17/24</span>
        </div>

        <span className="screen__cta">
          Loaded, next <span aria-hidden="true">→</span>
        </span>
      </div>
    </Phone>
  );
}

export function StopsScreen() {
  const stops = [
    ["Stop 1", "8 parcels", "at the doors", "one"],
    ["Stop 2", "9 parcels", "middle", "two"],
    ["Stop 3", "7 parcels", "at the back", "three"],
  ];
  return (
    <Phone title="The QUAI app, stop order screen">
      <div className="screen">
        <p className="screen__heading">Stop order</p>

        <ul className="screen__stops">
          {stops.map(([stop, parcels, place, tone]) => (
            <li key={stop}>
              <span className={`screen__dot screen__dot--${tone}`} aria-hidden="true" />
              <span>
                <strong>{stop}</strong>
                <span className="screen__stop-meta data">
                  {parcels} · {place}
                </span>
              </span>
            </li>
          ))}
        </ul>

        <p className="screen__footnote">
          Your delivery list sets the stop order. QUAI loads to match it.
        </p>
      </div>
    </Phone>
  );
}

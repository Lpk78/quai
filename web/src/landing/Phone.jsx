/** The phone frame the mockups show, drawn in HTML and CSS rather than shipped as a screenshot.
 *
 * A screenshot of an interface we have not built would be a picture of a promise. These frames hold
 * the real demo data from the brief instead, so what the page shows is what the shell will show. */
export default function Phone({ title = "QUAI", children, className = "" }) {
  return (
    <div className={`phone ${className}`} role="img" aria-label={title}>
      <div className="phone__frame">
        <div className="phone__notch" aria-hidden="true" />
        <div className="phone__screen">
          <div className="phone__status" aria-hidden="true">
            <span className="data">9:41</span>
            <span className="phone__signal">
              <i /> <i /> <i />
            </span>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}

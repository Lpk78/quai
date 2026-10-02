import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../App.jsx";

/* The explainer film on the landing page (`HY-21`).
 *
 * What these guard is not "a video element exists" — it is the promise that loading the landing page
 * costs nobody 3.2 MB they did not ask for. Autoplay being absent is only half of that: a browser
 * left to its own `preload` default will fetch metadata, and `preload="auto"` would fetch the lot.
 * So `preload="none"` is asserted directly, and so is the absence of `autoplay`, because the two
 * fail independently and either one alone would break the rule.
 */

function at(path) {
  return render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>);
}

function film(container) {
  return container.querySelector("#quai-film");
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("the explainer film on the landing page", () => {
  it("never plays by itself", () => {
    const { container } = at("/");
    const video = film(container);
    expect(video).not.toBeNull();
    expect(video.hasAttribute("autoplay")).toBe(false);
  });

  it("fetches nothing until someone asks for it", () => {
    // The whole point of the task: no autoplay is not the same as no download.
    const { container } = at("/");
    expect(film(container).getAttribute("preload")).toBe("none");
  });

  it("shows a poster rather than a black rectangle", () => {
    const { container } = at("/");
    expect(film(container).getAttribute("poster")).toBe("/quai-video-poster.webp");
  });

  it("keeps the browser's own controls", () => {
    const { container } = at("/");
    expect(film(container).hasAttribute("controls")).toBe(true);
  });

  it("plays in place on a phone rather than taking over the screen", () => {
    const { container } = at("/");
    // React renders the `playsInline` prop as the `playsinline` attribute.
    expect(film(container).hasAttribute("playsinline")).toBe(true);
  });

  it("offers the file to a browser that cannot play it, instead of an apology", () => {
    const { container } = at("/");
    const source = film(container).querySelector("source");
    expect(source.getAttribute("src")).toBe("/quai-video.mp4");
    expect(source.getAttribute("type")).toBe("video/mp4");
    expect(film(container).querySelector('a[href="/quai-video.mp4"]')).not.toBeNull();
  });
});

describe("the hero button that starts it", () => {
  it("still points at the section, so it works with no JavaScript", () => {
    at("/");
    expect(screen.getByRole("link", { name: /watch the film/i }))
      .toHaveAttribute("href", "#how-it-works");
  });

  it("presses play on the film", () => {
    const { container } = at("/");
    const play = vi.fn().mockResolvedValue(undefined);
    film(container).play = play;

    fireEvent.click(screen.getByRole("link", { name: /watch the film/i }));
    expect(play).toHaveBeenCalled();
  });

  it("survives a browser that refuses to play", () => {
    /* Safari rejects playback it does not consider user-initiated. The rejection must not reach the
       console as an unhandled promise — the operator is already looking at a player with controls,
       which is the fallback. */
    const { container } = at("/");
    film(container).play = vi.fn().mockRejectedValue(new Error("NotAllowedError"));

    expect(() => fireEvent.click(screen.getByRole("link", { name: /watch the film/i })))
      .not.toThrow();
  });

  it("does not fall over on a browser with no play() at all", () => {
    const { container } = at("/");
    film(container).play = undefined;

    expect(() => fireEvent.click(screen.getByRole("link", { name: /watch the film/i })))
      .not.toThrow();
  });
});

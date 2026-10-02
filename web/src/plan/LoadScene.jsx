import { useEffect, useRef } from "react";
import { Edges, OrbitControls } from "@react-three/drei";
import { Canvas, useThree } from "@react-three/fiber";

/* The plan as a shape rather than a list.
 *
 * Axes are the solver's (`src/quai/models.py`): x along the length of the van from the back wall,
 * y across its width, z up from the floor, all in centimetres, and (x, y, z) is the corner of the
 * box nearest the back-left floor corner. three.js has y up, so a placement maps as
 * (x, z, y) with the box centred on its own middle — the one conversion in this file, done once.
 *
 * Boxes are coloured **by index**, not by stop. `POST /plan` returns no stop per box; colouring by
 * position in the loading order at least groups what goes in together. Colour by stop is SA-14c and
 * waits for #36. The tokens are the kraft and stop colours from tokens.css, read here as literals
 * because a WebGL material cannot take a CSS variable.
 */

const COLOURS = ["#D7B899", "#B8936B", "#8B6F47", "#2563EB", "#059669", "#7C3AED", "#DC2626"];

/* Where the camera stands for each named view, in the scene's own units — the van is scaled to two
   units across by `sceneScale`, so these are the same distances whatever vehicle is being planned.
   Three-quarter by default, because a load is a volume and one flat face hides most of it. */
export const VIEWS = {
  "3D": [3.2, 2.4, 3.2],
  Top: [0, 4.6, 0.001],   // not exactly 0 on z: straight down leaves the camera's up-vector undefined
  Left: [0, 1.2, 4.4],
  Right: [4.4, 1.2, 0],
};

export const colourFor = (index) => COLOURS[index % COLOURS.length];

/* Scaled so the largest van dimension is 2 units across, which keeps the camera framing the same
   whatever size the vehicle is. */
export function sceneScale(container) {
  const largest = Math.max(container.length, container.width, container.height, 1);
  return 2 / largest;
}

export function PlacedBox({ placement, colour, selected, onSelect }) {
  const { x, y, z, dx, dy, dz } = placement;
  return (
    <mesh
      position={[x + dx / 2, z + dz / 2, y + dy / 2]}
      onClick={(event) => {
        event.stopPropagation();
        onSelect(placement.id);
      }}
    >
      <boxGeometry args={[dx, dz, dy]} />
      <meshStandardMaterial
        color={colour}
        emissive={selected ? "#FF8A00" : "#000000"}
        emissiveIntensity={selected ? 0.5 : 0}
      />
    </mesh>
  );
}

/* Moves the camera to a named view and hands control back to the orbit. Inside the Canvas because
   `useThree` needs the renderer's context, and separate from `LoadScene` because the scene itself —
   the meshes, the scaling, the lighting, the selection — is not what changes when the view does.

   The orbit target is reset with it: without that, a preset would aim the camera from the right place
   at wherever the operator had last dragged to. */
function CameraPreset({ view, controls }) {
  const camera = useThree((state) => state.camera);
  useEffect(() => {
    const position = VIEWS[view] ?? VIEWS["3D"];
    camera.position.set(...position);
    camera.lookAt(0, 0, 0);
    if (controls.current) {
      controls.current.target.set(0, 0, 0);
      controls.current.update();
    }
  }, [view, camera, controls]);
  return null;
}

/* The load volume: a transparent box, and deliberately not a van.
 *
 * A modelled vehicle would be the most expensive thing on screen and the least informative — the
 * operator is looking for one parcel among eighteen, not admiring a lorry, and every wheel arch is
 * another thing between them and the boxes. So the volume is stated and then got out of the way:
 * warm off-white walls at low opacity for the shape, thin navy edges for where it ends, a floor
 * faint enough to read the boxes against. `LP-22`.
 *
 * The colours are `tokens.json` read as literals — `background` and `navy` — because a WebGL
 * material cannot take a CSS variable.
 */
export function Van({ container }) {
  const { length, width, height } = container;
  return (
    <group position={[length / 2, 0, width / 2]}>
      <mesh position={[0, height / 2, 0]}>
        <boxGeometry args={[length, height, width]} />
        <meshStandardMaterial color="#F7F6F3" transparent opacity={0.12} depthWrite={false} />
        {/* The edges carry the shape; the walls only tint it. `threshold` at 15° keeps this to the
            twelve edges of the box rather than outlining every triangle of its faces. */}
        <Edges color="#102238" threshold={15} />
      </mesh>
      {/* The floor the boxes sit on, lifted half a centimetre so it does not fight the van's own
          bottom face for the same pixels. Discreet on purpose: it is the surface the delivery zones
          are drawn on, and a strong floor would compete with them. */}
      <mesh position={[0, 0.5, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[length, width]} />
        <meshStandardMaterial color="#102238" transparent opacity={0.07} depthWrite={false} />
      </mesh>
    </group>
  );
}

export default function LoadScene({ plan, container, selected, onSelect, view = "3D" }) {
  const scale = sceneScale(container);
  const controls = useRef(null);
  return (
    <Canvas
      camera={{ position: VIEWS["3D"], fov: 42 }}
      onPointerMissed={() => onSelect(null)}
      aria-label="3D view of the load"
    >
      <ambientLight intensity={0.85} />
      <directionalLight position={[4, 6, 3]} intensity={1.1} />
      {/* Scale the whole van down to camera units, then recentre it on its own middle so the
          camera orbits the load rather than its back-left corner. */}
      <group scale={scale}>
        <group position={[-container.length / 2, 0, -container.width / 2]}>
          <Van container={container} />
          {plan.placements.map((placement, index) => (
            <PlacedBox
              key={placement.id}
              placement={placement}
              colour={colourFor(index)}
              selected={selected === placement.id}
              onSelect={onSelect}
            />
          ))}
        </group>
      </group>
      {/* Touch: one finger orbits, two pinch to zoom. Panning is off — it is the easiest way to
          lose the van off-screen on a phone, and there is nothing to pan to. */}
      <OrbitControls ref={controls} enablePan={false} minDistance={1.5} maxDistance={8} />
      <CameraPreset view={view} controls={controls} />
    </Canvas>
  );
}

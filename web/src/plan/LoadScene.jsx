import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";

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

export function Van({ container }) {
  const { length, width, height } = container;
  return (
    <mesh position={[length / 2, height / 2, width / 2]}>
      <boxGeometry args={[length, height, width]} />
      {/* Seen from outside, so the far faces are the ones that show the shape. */}
      <meshStandardMaterial color="#102238" transparent opacity={0.08} depthWrite={false} />
    </mesh>
  );
}

export default function LoadScene({ plan, container, selected, onSelect }) {
  const scale = sceneScale(container);
  return (
    <Canvas
      camera={{ position: [3.2, 2.4, 3.2], fov: 42 }}
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
      <OrbitControls enablePan={false} minDistance={1.5} maxDistance={8} />
    </Canvas>
  );
}

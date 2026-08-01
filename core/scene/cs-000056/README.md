# Alpha Surface Position and Bend Pins

This core example demonstrates the After Effects-style surface workflow:

- `MeshTopology mode="alpha"` describes only the artwork surface, not the
  rectangular canvas.
- `role="position"` pins can hold or translate arbitrary points.
- `role="bend"` pins rotate and scale their local influence region.
- Pin ids are descriptive labels only. The solver does not require names such
  as shoulder, elbow, ankle, or knee.

The landing-page Puppet Warp UI can generate the alpha topology automatically
from the visible artwork and add any number of Position or Bend pins.

import L from "leaflet";
import "leaflet/dist/leaflet.css";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

/**
 * Leaflet's default marker icon paths are computed relative to its own
 * bundled JS and don't resolve correctly through a bundler (a
 * long-standing, well-known Leaflet + Webpack/Vite issue) — without
 * this, every Marker silently renders as a broken image icon.
 */
type IconDefaultPrototype = typeof L.Icon.Default.prototype & { _getIconUrl?: unknown };
delete (L.Icon.Default.prototype as IconDefaultPrototype)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

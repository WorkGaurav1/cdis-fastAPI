import type { Geometry, Position } from "geojson";
import L from "leaflet";

type CoordVisitor = (lng: number, lat: number) => void;

function visitPosition(position: Position, visit: CoordVisitor): void {
  const [lng, lat] = position;
  visit(lng, lat);
}

function scanGeometryCoords(geometry: Geometry, visit: CoordVisitor): void {
  switch (geometry.type) {
    case "Point":
      visitPosition(geometry.coordinates, visit);
      return;
    case "LineString":
    case "MultiPoint":
      geometry.coordinates.forEach((position) => { visitPosition(position, visit); });
      return;
    case "Polygon":
    case "MultiLineString":
      geometry.coordinates.forEach((ring) => {
        ring.forEach((position) => { visitPosition(position, visit); });
      });
      return;
    case "MultiPolygon":
      geometry.coordinates.forEach((polygon) => {
        polygon.forEach((ring) => {
          ring.forEach((position) => { visitPosition(position, visit); });
        });
      });
      return;
    case "GeometryCollection":
      geometry.geometries.forEach((member) => { scanGeometryCoords(member, visit); });
  }
}

/**
 * Bounding-box center of a geometry — good enough for placing a label
 * badge, not a true area centroid.
 */
export function getGeometryCenter(geometry: Geometry): L.LatLng | null {
  let minLat = Infinity;
  let maxLat = -Infinity;
  let minLng = Infinity;
  let maxLng = -Infinity;

  scanGeometryCoords(geometry, (lng, lat) => {
    if (lat < minLat) minLat = lat;
    if (lat > maxLat) maxLat = lat;
    if (lng < minLng) minLng = lng;
    if (lng > maxLng) maxLng = lng;
  });

  if (minLat === Infinity) {
    return null;
  }

  return L.latLng((minLat + maxLat) / 2, (minLng + maxLng) / 2);
}

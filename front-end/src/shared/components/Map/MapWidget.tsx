import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

import "./leafletIconFix";
import type { MapMarker } from "./GeoMap";

interface MapWidgetProps {
  markers?: MapMarker[];
  /** Defaults to a whole-world view when there's nothing specific to center on. */
  center?: [number, number];
  zoom?: number;
  height?: number;
  emptyMessage?: string;
}

export function MapWidget({
  markers = [],
  center = [20, 0],
  zoom = 2,
  height = 300,
  emptyMessage = "No location data available yet.",
}: MapWidgetProps) {
  return (
    <div className="relative overflow-hidden rounded-md border border-gray-200 bg-white p-4">
      <div style={{ height }} className="overflow-hidden rounded-md">
        <MapContainer center={center} zoom={zoom} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {markers.map((marker) => (
            <Marker key={marker.id} position={marker.position}>
              {marker.label && <Popup>{marker.label}</Popup>}
            </Marker>
          ))}
        </MapContainer>
      </div>

      {markers.length === 0 && (
        <div className="pointer-events-none absolute inset-4 top-8 flex items-start justify-center pt-4">
          <span className="pointer-events-none rounded-md bg-white/90 px-3 py-1.5 text-sm text-gray-600 shadow">
            {emptyMessage}
          </span>
        </div>
      )}
    </div>
  );
}

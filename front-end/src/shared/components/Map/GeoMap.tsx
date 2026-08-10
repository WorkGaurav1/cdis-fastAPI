import { useCallback, useEffect, useMemo, useRef } from "react";
import type { ReactNode, RefObject } from "react";
import type { Feature, FeatureCollection, LineString, MultiLineString, MultiPolygon, Polygon } from "geojson";
import type { Layer, Path, PathOptions } from "leaflet";
import L from "leaflet";
import { Locate, Minus, Plus } from "lucide-react";
import { GeoJSON, MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";

import "./leafletIconFix";
import { getGeometryCenter } from "./geometry";

export interface MapMarker {
  id: string;
  position: [number, number];
  label?: string;
}

/**
 * A polygon/multipolygon layer whose per-feature style is fully
 * caller-defined — a choropleth, a set of highlighted zones, a cluster
 * of weighted regions, anything region-shaped. No domain knowledge
 * lives here; the caller decides what a "region" means and how it's
 * colored.
 */
export interface RegionLayer<P = Record<string, unknown>> {
  id: string;
  data: FeatureCollection<Polygon | MultiPolygon, P>;
  style: (feature: Feature<Polygon | MultiPolygon, P>) => PathOptions;
  hoverStyle?: (feature: Feature<Polygon | MultiPolygon, P>) => PathOptions;
  tooltip?: (feature: Feature<Polygon | MultiPolygon, P>) => string;
  /** Text badge rendered at the feature's bounding-box center, e.g. a count. */
  label?: (feature: Feature<Polygon | MultiPolygon, P>) => string | undefined;
  onFeatureClick?: (feature: Feature<Polygon | MultiPolygon, P>) => void;
}

/** A line/multiline layer — routes, corridors, connections between points. */
export interface RouteLayer<P = Record<string, unknown>> {
  id: string;
  data: FeatureCollection<LineString | MultiLineString, P>;
  style: (feature: Feature<LineString | MultiLineString, P>) => PathOptions;
  hoverStyle?: (feature: Feature<LineString | MultiLineString, P>) => PathOptions;
  tooltip?: (feature: Feature<LineString | MultiLineString, P>) => string;
}

interface GeoMapProps {
  markers?: MapMarker[];
  // A single map legitimately hosts layers with different feature-property
  // shapes at once (a choropleth layer, a route layer, each defined by a
  // different page) — `any` here is deliberate type erasure at that
  // array boundary, not laziness; each RegionLayer/RouteLayer is still
  // fully typed by its own generic P wherever it's constructed.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  regionLayers?: RegionLayer<any>[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  routeLayers?: RouteLayer<any>[];
  /** Defaults to a whole-world view when there's nothing specific to center on. */
  center?: [number, number];
  zoom?: number;
  height?: number;
  emptyMessage?: string;
  isLoading?: boolean;
  /** Arbitrary controls anchored to a map corner — a legend, a filter dropdown, an info card. */
  overlays?: Partial<Record<"topLeft" | "topRight" | "bottomLeft" | "bottomRight", ReactNode>>;
  /** Auto-fit the view to the combined bounds of every layer once data is available, overriding center/zoom. */
  fitToData?: boolean;
  /**
   * Masks everything outside a given shape — e.g. a "world rectangle
   * with country X cut out as a hole" polygon — so only that region is
   * visible, and (optionally) restricts panning/zooming to match. No
   * knowledge of what the shape represents lives here; the caller
   * supplies the mask geometry.
   */
  maskOutside?: {
    data: FeatureCollection;
    /** Defaults to white — should match the page/card background it sits on. */
    color?: string;
    maxBounds?: [[number, number], [number, number]];
    minZoom?: number;
  };
}

const OVERLAY_POSITION_CLASSES: Record<string, string> = {
  // topLeft sits below the +/-/recenter control cluster, which always
  // occupies the top-left corner itself, so it doesn't overlap.
  topLeft: "left-2 top-28",
  topRight: "right-2 top-2",
  bottomLeft: "left-2 bottom-2",
  bottomRight: "right-2 bottom-2",
};

interface FitBoundsProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  regionLayers: RegionLayer<any>[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  routeLayers: RouteLayer<any>[];
  markers: MapMarker[];
  /** Reports the view fitBounds actually landed on, so the recenter control can return to it. */
  onFit?: (center: [number, number], zoom: number) => void;
}

/** Imperatively fits the Leaflet view once, whenever the combined data changes. */
function FitBounds({ regionLayers, routeLayers, markers, onFit }: FitBoundsProps) {
  const map = useMap();

  useEffect(() => {
    const bounds = L.latLngBounds([]);

    for (const layer of regionLayers) {
      bounds.extend(L.geoJSON(layer.data as FeatureCollection).getBounds());
    }
    for (const layer of routeLayers) {
      bounds.extend(L.geoJSON(layer.data as FeatureCollection).getBounds());
    }
    for (const marker of markers) {
      bounds.extend(marker.position);
    }

    if (bounds.isValid()) {
      // The map container's flex-layout size may not have settled yet
      // on the same tick this effect fires — invalidateSize() forces
      // Leaflet to re-measure before fitBounds() uses that size to
      // compute zoom, otherwise it fits against a stale/zero size.
      map.invalidateSize();
      map.fitBounds(bounds, { padding: [20, 20] });
      const fittedCenter = map.getCenter();
      onFit?.([fittedCenter.lat, fittedCenter.lng], map.getZoom());
    }
  }, [map, regionLayers, routeLayers, markers, onFit]);

  return null;
}

interface HomeView {
  center: [number, number];
  zoom: number;
}

interface MapControlsProps {
  /** The view fitToData last landed on, if any — takes priority over the fallback when recentering. */
  homeViewRef: RefObject<HomeView | null>;
  fallbackCenter: [number, number];
  fallbackZoom: number;
}

/** Custom +/-/recenter cluster, replacing Leaflet's default zoom control so a recenter button can sit alongside it. */
function MapControls({ homeViewRef, fallbackCenter, fallbackZoom }: MapControlsProps) {
  const map = useMap();

  function handleRecenter() {
    const home = homeViewRef.current;
    map.flyTo(home ? home.center : fallbackCenter, home ? home.zoom : fallbackZoom);
  }

  return (
    <div className="absolute left-2 top-2 z-[1000] flex flex-col overflow-hidden rounded-md border border-gray-300 bg-white shadow-sm">
      <button
        type="button"
        aria-label="Zoom in"
        onClick={() => { map.zoomIn(); }}
        className="flex h-8 w-8 items-center justify-center border-b border-gray-200 text-gray-700 hover:bg-gray-50"
      >
        <Plus aria-hidden="true" className="h-4 w-4" />
      </button>
      <button
        type="button"
        aria-label="Zoom out"
        onClick={() => { map.zoomOut(); }}
        className="flex h-8 w-8 items-center justify-center border-b border-gray-200 text-gray-700 hover:bg-gray-50"
      >
        <Minus aria-hidden="true" className="h-4 w-4" />
      </button>
      <button
        type="button"
        aria-label="Recenter map"
        onClick={handleRecenter}
        className="flex h-8 w-8 items-center justify-center text-gray-700 hover:bg-gray-50"
      >
        <Locate aria-hidden="true" className="h-4 w-4" />
      </button>
    </div>
  );
}

interface HoverBehaviorOptions<G extends Polygon | MultiPolygon | LineString | MultiLineString, P> {
  hoverStyle?: (feature: Feature<G, P>) => PathOptions;
  tooltip?: (feature: Feature<G, P>) => string;
  onFeatureClick?: (feature: Feature<G, P>) => void;
}

function attachHoverBehavior<G extends Polygon | MultiPolygon | LineString | MultiLineString, P>(
  feature: Feature<G, P>,
  leafletLayer: Layer,
  baseStyle: PathOptions,
  options: HoverBehaviorOptions<G, P>,
): void {
  // GeoJSON layers built from a single geometry type (Polygon/MultiPolygon
  // or LineString/MultiLineString) always come back as an L.Path, which
  // is the only thing that supports setStyle().
  const pathLayer = leafletLayer as Path;

  leafletLayer.on({
    mouseover: (event) => {
      if (options.hoverStyle) {
        pathLayer.setStyle(options.hoverStyle(feature));
      }
      if (options.tooltip) {
        leafletLayer
          .bindTooltip(options.tooltip(feature), { sticky: true, direction: "top", opacity: 1 })
          .openTooltip((event as L.LeafletMouseEvent).latlng);
      }
    },
    mouseout: () => {
      pathLayer.setStyle(baseStyle);
      leafletLayer.closeTooltip();
    },
    click: () => {
      options.onFeatureClick?.(feature);
    },
  });
}

function RegionLayerGroup<P>({ layer }: { layer: RegionLayer<P> }) {
  const labelMarkers = useMemo(() => {
    if (!layer.label) return [];

    return layer.data.features.flatMap((feature, index) => {
      const text = layer.label?.(feature);
      if (!text) return [];

      const center = getGeometryCenter(feature.geometry);
      if (!center) return [];

      // feature.id is optional in GeoJSON and the label text isn't
      // guaranteed unique (e.g. two regions with the same rounded
      // value), so the array index is the only collision-free key.
      return [{ id: `${layer.id}-${String(index)}`, center, text }];
    });
  }, [layer]);

  return (
    <>
      <GeoJSON
        key={layer.id}
        data={layer.data as FeatureCollection}
        style={(feature) => (feature ? layer.style(feature as Feature<Polygon | MultiPolygon, P>) : {})}
        onEachFeature={(feature, leafletLayer) => {
          const typedFeature = feature as Feature<Polygon | MultiPolygon, P>;
          attachHoverBehavior(typedFeature, leafletLayer, layer.style(typedFeature), layer);
        }}
      />
      {labelMarkers.map(({ id, center, text }) => (
        <Marker
          key={id}
          position={center}
          interactive={false}
          keyboard={false}
          icon={L.divIcon({
            className: "",
            html: `<span class="rounded border border-gray-300 bg-white/95 px-1.5 py-0.5 text-[10px] font-semibold text-gray-700 shadow-sm">${text}</span>`,
            iconSize: [80, 20],
            iconAnchor: [40, 10],
          })}
        />
      ))}
    </>
  );
}

function RouteLayerGroup<P>({ layer }: { layer: RouteLayer<P> }) {
  return (
    <GeoJSON
      key={layer.id}
      data={layer.data as FeatureCollection}
      style={(feature) => (feature ? layer.style(feature as Feature<LineString | MultiLineString, P>) : {})}
      onEachFeature={(feature, leafletLayer) => {
        const typedFeature = feature as Feature<LineString | MultiLineString, P>;
        attachHoverBehavior(typedFeature, leafletLayer, layer.style(typedFeature), layer);
      }}
    />
  );
}

/**
 * Domain-agnostic map primitive: simple point markers, plus optional
 * region (polygon) and route (line) layers whose data, styling, and
 * tooltips are entirely supplied by the caller. Any project cloning
 * this template plugs in its own GeoJSON — nothing here assumes what a
 * "region" or "route" represents.
 */
export function GeoMap({
  markers = [],
  regionLayers = [],
  routeLayers = [],
  center = [20, 0],
  zoom = 2,
  height = 300,
  emptyMessage = "No location data available yet.",
  isLoading = false,
  overlays,
  fitToData = false,
  maskOutside,
}: GeoMapProps) {
  const isEmpty = markers.length === 0 && regionLayers.length === 0 && routeLayers.length === 0;
  const homeViewRef = useRef<HomeView | null>(null);
  const handleFit = useCallback((fittedCenter: [number, number], fittedZoom: number) => {
    homeViewRef.current = { center: fittedCenter, zoom: fittedZoom };
  }, []);

  return (
    <div className="relative overflow-hidden rounded-md border border-gray-200 bg-white p-4">
      <div style={{ height }} className="relative overflow-hidden rounded-md">
        <MapContainer
          center={center}
          zoom={zoom}
          zoomControl={false}
          // Integer-only zoom steps (Leaflet's default) can force
          // fitToData to undershoot badly: if the tight-fit zoom is,
          // say, 4.6, snapping to whole numbers means falling back to
          // zoom 4 (with a lot of unused space) because zoom 5
          // overshoots the container. Fractional steps let fitBounds
          // land close to the actual best fit.
          zoomSnap={0.25}
          zoomDelta={0.25}
          maxBounds={maskOutside?.maxBounds}
          maxBoundsViscosity={maskOutside ? 1 : undefined}
          minZoom={maskOutside?.minZoom}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {maskOutside && (
            <GeoJSON
              data={maskOutside.data}
              interactive={false}
              style={{ fillColor: maskOutside.color ?? "#ffffff", fillOpacity: 1, stroke: false }}
            />
          )}

          <MapControls homeViewRef={homeViewRef} fallbackCenter={center} fallbackZoom={zoom} />

          {fitToData && (
            <FitBounds regionLayers={regionLayers} routeLayers={routeLayers} markers={markers} onFit={handleFit} />
          )}

          {regionLayers.map((layer) => (
            <RegionLayerGroup key={layer.id} layer={layer} />
          ))}

          {routeLayers.map((layer) => (
            <RouteLayerGroup key={layer.id} layer={layer} />
          ))}

          {markers.map((marker) => (
            <Marker key={marker.id} position={marker.position}>
              {marker.label && <Popup>{marker.label}</Popup>}
            </Marker>
          ))}
        </MapContainer>

        {isLoading && (
          <div className="pointer-events-none absolute inset-0 z-[1000] flex items-center justify-center bg-white/60">
            <span className="rounded-md bg-white px-3 py-1.5 text-sm text-gray-600 shadow">Loading map…</span>
          </div>
        )}

        {overlays &&
          Object.entries(overlays).map(([position, content]) =>
            content ? (
              <div key={position} className={`absolute z-[1000] ${OVERLAY_POSITION_CLASSES[position]}`}>
                {content}
              </div>
            ) : null,
          )}
      </div>

      {isEmpty && !isLoading && (
        <div className="pointer-events-none absolute inset-4 top-8 flex items-start justify-center pt-4">
          <span className="pointer-events-none rounded-md bg-white/90 px-3 py-1.5 text-sm text-gray-600 shadow">
            {emptyMessage}
          </span>
        </div>
      )}
    </div>
  );
}

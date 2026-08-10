import type { Feature, FeatureCollection, MultiPolygon, Polygon } from "geojson";

import { apiClient } from "@/api";

export interface IndiaDistrictProperties {
  district: string;
  dt_code: string;
  st_nm: string;
  st_code: string;
}

export interface StateMetric {
  id: string;
  stateCode: string;
  stateName: string;
  projectCount: number;
  activityIntensity: number;
}

/**
 * Static India district-boundary GeoJSON served from public/ — 760
 * districts, geometry simplified (~15%) from an open dataset
 * (udit-001/india-maps-data, itself derived from GADM) down to ~288KB
 * so it loads quickly and never touches the JS bundle. district-level
 * detail is used (rather than a dissolved state outline) specifically
 * so state AND district borders both render exactly.
 */
export const geoDataApi = {
  async listIndiaDistricts(): Promise<FeatureCollection<Polygon | MultiPolygon, IndiaDistrictProperties>> {
    const response = await fetch("/data/india-districts.geojson");
    if (!response.ok) {
      throw new Error(`Failed to load India district boundaries: ${String(response.status)}`);
    }
    return (await response.json()) as FeatureCollection<Polygon | MultiPolygon, IndiaDistrictProperties>;
  },

  /** A "world rectangle minus India" polygon, used to hide everything outside India's borders. */
  async listIndiaMask(): Promise<FeatureCollection> {
    const response = await fetch("/data/india-mask.geojson");
    if (!response.ok) {
      throw new Error(`Failed to load India mask: ${String(response.status)}`);
    }
    return (await response.json()) as FeatureCollection;
  },

  /** Per-state demo metrics — real data from the backend/database, not generated client-side. */
  async listStateMetrics(): Promise<StateMetric[]> {
    const { states } = await apiClient.get<{ states: StateMetric[] }>("/demo/map/states");
    return states;
  },
};

export type IndiaDistrictFeature = Feature<Polygon | MultiPolygon, IndiaDistrictProperties>;

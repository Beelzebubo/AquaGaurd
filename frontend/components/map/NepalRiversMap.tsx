/// <reference types="google.maps" />
import { useEffect, useRef } from "react";
import { stations, type Station } from "@/data/stations";
import { nepalRivers } from "@/data/nepal-rivers";

declare global {
  interface Window {
    google?: typeof google;
    __initAquaGuardMap?: () => void;
  }
}

const BROWSER_KEY = import.meta.env.VITE_LOVABLE_CONNECTOR_GOOGLE_MAPS_BROWSER_KEY as string | undefined;
const TRACKING_ID = import.meta.env.VITE_LOVABLE_CONNECTOR_GOOGLE_MAPS_TRACKING_ID as string | undefined;

const BASIN_COLORS: Record<string, string> = {
  Karnali: "#3ecbff",
  Gandaki: "#7cf2c7",
  Koshi: "#9b8cff",
  Bagmati: "#ffc46b",
};

let mapsLoadingPromise: Promise<void> | null = null;

function loadGoogleMaps(): Promise<void> {
  if (typeof window === "undefined") return Promise.reject(new Error("no window"));
  if (window.google?.maps) return Promise.resolve();
  if (mapsLoadingPromise) return mapsLoadingPromise;
  if (!BROWSER_KEY) return Promise.reject(new Error("Google Maps browser key missing"));

  mapsLoadingPromise = new Promise<void>((resolve, reject) => {
    window.__initAquaGuardMap = () => resolve();
    const s = document.createElement("script");
    const tracking = TRACKING_ID ? `&channel=${encodeURIComponent(TRACKING_ID)}` : "";
    s.src = `https://maps.googleapis.com/maps/api/js?key=${BROWSER_KEY}&loading=async&callback=__initAquaGuardMap${tracking}`;
    s.async = true;
    s.defer = true;
    s.onerror = () => reject(new Error("Failed to load Google Maps script"));
    document.head.appendChild(s);
  });
  return mapsLoadingPromise;
}

// Dark hydro map style
const MAP_STYLE: google.maps.MapTypeStyle[] = [
  { elementType: "geometry", stylers: [{ color: "#0d1822" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#0d1822" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#7aa8c4" }] },
  { featureType: "administrative.country", elementType: "geometry.stroke", stylers: [{ color: "#3ecbff" }, { weight: 1.2 }] },
  { featureType: "administrative.province", elementType: "geometry.stroke", stylers: [{ color: "#2a4a5f" }] },
  { featureType: "landscape", elementType: "geometry", stylers: [{ color: "#13202c" }] },
  { featureType: "poi", stylers: [{ visibility: "off" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#1a2a38" }] },
  { featureType: "road", elementType: "labels", stylers: [{ visibility: "off" }] },
  { featureType: "transit", stylers: [{ visibility: "off" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#0a1a26" }] },
  { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#3ecbff" }] },
];

export function NepalRiversMap({
  selectedId,
  onSelect,
}: {
  selectedId: string;
  onSelect: (s: Station) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<google.maps.Map | null>(null);
  const markersRef = useRef<Map<string, google.maps.Marker>>(new Map());
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  useEffect(() => {
    let cancelled = false;
    if (!containerRef.current) return;
    loadGoogleMaps()
      .then(() => {
        if (cancelled || !containerRef.current || !window.google) return;
        const map = new window.google.maps.Map(containerRef.current, {
          center: { lat: 28.3949, lng: 84.124 },
          zoom: 7,
          disableDefaultUI: true,
          zoomControl: true,
          gestureHandling: "greedy",
          backgroundColor: "#0d1822",
          styles: MAP_STYLE,
        });
        mapRef.current = map;

        // River polylines
        for (const r of nepalRivers) {
          const path = r.coords.map(([lng, lat]) => ({ lat, lng }));
          new window.google.maps.Polyline({
            path,
            geodesic: true,
            strokeColor: BASIN_COLORS[r.basin] ?? "#3ecbff",
            strokeOpacity: 0.85,
            strokeWeight: 2.5,
            map,
          });
          // glow underlay
          new window.google.maps.Polyline({
            path,
            geodesic: true,
            strokeColor: BASIN_COLORS[r.basin] ?? "#3ecbff",
            strokeOpacity: 0.2,
            strokeWeight: 8,
            map,
          });
        }

        // Station markers
        for (const st of stations) {
          const marker = new window.google.maps.Marker({
            position: { lat: st.lat, lng: st.lng },
            map,
            title: st.name,
            icon: {
              path: window.google.maps.SymbolPath.CIRCLE,
              scale: st.id === selectedId ? 10 : 6,
              fillColor: st.id === selectedId ? "#ffc46b" : "#3ecbff",
              fillOpacity: 1,
              strokeColor: "#0d1822",
              strokeWeight: 2,
            },
            animation: window.google.maps.Animation.DROP,
          });
          marker.addListener("click", () => onSelectRef.current(st));
          markersRef.current.set(st.id, marker);
        }
      })
      .catch((e) => console.error("Map init failed:", e));
    return () => {
      cancelled = true;
    };
  }, []); // mount once

  // Update marker highlight when selection changes
  useEffect(() => {
    if (!window.google) return;
    for (const [id, marker] of markersRef.current) {
      const selected = id === selectedId;
      marker.setIcon({
        path: window.google.maps.SymbolPath.CIRCLE,
        scale: selected ? 11 : 6,
        fillColor: selected ? "#ffc46b" : "#3ecbff",
        fillOpacity: 1,
        strokeColor: "#0d1822",
        strokeWeight: 2,
      });
    }
    const sel = stations.find((s) => s.id === selectedId);
    if (sel && mapRef.current) mapRef.current.panTo({ lat: sel.lat, lng: sel.lng });
  }, [selectedId]);

  return (
    <div className="relative h-full w-full overflow-hidden rounded-2xl">
      <div ref={containerRef} className="h-full w-full" aria-label="Nepal river system map" />
      {!BROWSER_KEY && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/80 text-sm text-muted-foreground">
          Google Maps key missing — reconnect the Google Maps connector.
        </div>
      )}
      <div className="pointer-events-none absolute bottom-3 left-3 flex flex-wrap gap-2 text-[10px] uppercase tracking-wider">
        {Object.entries(BASIN_COLORS).map(([basin, color]) => (
          <span key={basin} className="flex items-center gap-1.5 rounded-full bg-background/70 px-2 py-1 text-foreground/80 backdrop-blur">
            <span className="h-2 w-2 rounded-full" style={{ background: color }} />
            {basin}
          </span>
        ))}
      </div>
    </div>
  );
}
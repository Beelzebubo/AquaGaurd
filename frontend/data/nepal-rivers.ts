// Simplified polyline coordinates [lng, lat] for major Nepali river systems.
// Approximate — sufficient for an overview map overlay.
export type RiverLine = { name: string; basin: "Koshi" | "Gandaki" | "Karnali" | "Bagmati"; coords: [number, number][] };

export const nepalRivers: RiverLine[] = [
  {
    name: "Karnali",
    basin: "Karnali",
    coords: [
      [81.05, 30.1], [81.2, 29.7], [81.35, 29.3], [81.4, 28.95], [81.3, 28.65],
      [81.27, 28.4], [81.2, 28.05], [81.05, 27.7], [81.0, 27.35],
    ],
  },
  {
    name: "Bheri",
    basin: "Karnali",
    coords: [[82.3, 29.2], [82.0, 28.95], [81.7, 28.7], [81.4, 28.55], [81.27, 28.4]],
  },
  {
    name: "Kali Gandaki",
    basin: "Gandaki",
    coords: [
      [83.7, 29.3], [83.6, 28.95], [83.55, 28.6], [83.58, 28.2], [83.7, 27.9],
      [83.95, 27.7], [84.2, 27.55], [84.4, 27.45],
    ],
  },
  {
    name: "Marsyangdi",
    basin: "Gandaki",
    coords: [[84.05, 28.7], [84.1, 28.45], [84.25, 28.2], [84.4, 27.95], [84.4, 27.7]],
  },
  {
    name: "Trishuli",
    basin: "Gandaki",
    coords: [[85.4, 28.2], [85.2, 27.95], [85.0, 27.78], [84.7, 27.65], [84.4, 27.55]],
  },
  {
    name: "Sapta Gandaki",
    basin: "Gandaki",
    coords: [[84.4, 27.45], [84.55, 27.3], [84.7, 27.15], [84.85, 26.95]],
  },
  {
    name: "Tamakoshi",
    basin: "Koshi",
    coords: [[86.15, 28.0], [86.1, 27.7], [85.95, 27.4], [85.85, 27.15], [85.85, 26.9]],
  },
  {
    name: "Sun Koshi",
    basin: "Koshi",
    coords: [[85.85, 26.9], [86.1, 26.95], [86.4, 26.95], [86.7, 26.9], [87.0, 26.85]],
  },
  {
    name: "Arun",
    basin: "Koshi",
    coords: [[87.2, 28.0], [87.25, 27.75], [87.2, 27.45], [87.15, 27.15], [87.0, 26.85]],
  },
  {
    name: "Tamor",
    basin: "Koshi",
    coords: [[87.85, 27.7], [87.7, 27.4], [87.4, 27.1], [87.15, 26.95], [87.0, 26.85]],
  },
  {
    name: "Sapta Koshi",
    basin: "Koshi",
    coords: [[87.0, 26.85], [86.95, 26.7], [86.95, 26.5]],
  },
  {
    name: "Bagmati",
    basin: "Bagmati",
    coords: [[85.35, 27.75], [85.3, 27.6], [85.2, 27.4], [85.15, 27.15], [85.2, 26.9]],
  },
];
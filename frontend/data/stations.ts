export type Station = {
  id: string;
  name: string;
  river: string;
  capacityMw: number;
  lat: number;
  lng: number;
  ecoThreshold: number; // m3/s minimum ecological flow
};

export const stations: Station[] = [
  {
    id: "chisapani",
    name: "Chisapani",
    river: "Karnali",
    capacityMw: 10800,
    lat: 28.6447,
    lng: 81.2731,
    ecoThreshold: 280,
  },
  {
    id: "upper-tamakoshi",
    name: "Upper Tamakoshi",
    river: "Tamakoshi",
    capacityMw: 456,
    lat: 27.8333,
    lng: 86.1833,
    ecoThreshold: 35,
  },
  {
    id: "melamchi",
    name: "Melamchi",
    river: "Indrawati",
    capacityMw: 30,
    lat: 27.8333,
    lng: 85.5667,
    ecoThreshold: 12,
  },
  {
    id: "kulekhani",
    name: "Kulekhani I",
    river: "Bagmati",
    capacityMw: 60,
    lat: 27.5667,
    lng: 85.1667,
    ecoThreshold: 8,
  },
  {
    id: "kali-gandaki-a",
    name: "Kali Gandaki A",
    river: "Gandaki",
    capacityMw: 144,
    lat: 27.9833,
    lng: 83.5833,
    ecoThreshold: 95,
  },
  {
    id: "marsyangdi",
    name: "Middle Marsyangdi",
    river: "Marsyangdi",
    capacityMw: 70,
    lat: 28.2667,
    lng: 84.4,
    ecoThreshold: 45,
  },
  {
    id: "trishuli",
    name: "Trishuli 3A",
    river: "Trishuli",
    capacityMw: 60,
    lat: 27.9167,
    lng: 85.15,
    ecoThreshold: 38,
  },
  {
    id: "arun-iii",
    name: "Arun III",
    river: "Arun",
    capacityMw: 900,
    lat: 27.4833,
    lng: 87.2333,
    ecoThreshold: 120,
  },
  {
    id: "sapta-koshi",
    name: "Sapta Koshi HM",
    river: "Koshi",
    capacityMw: 3000,
    lat: 26.8617,
    lng: 87.1494,
    ecoThreshold: 320,
  },
  {
    id: "budhi-gandaki",
    name: "Budhi Gandaki",
    river: "Gandaki",
    capacityMw: 1200,
    lat: 28.0167,
    lng: 84.8,
    ecoThreshold: 110,
  },
];

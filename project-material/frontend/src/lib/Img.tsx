"use client";

import { useState } from "react";

// Remote photo/logo that hides itself if the image is missing, instead of showing a broken icon.
export default function Img({ src, className }: { src: string; className?: string }) {
  const [failed, setFailed] = useState(false);
  if (failed) return <span className={`${className ?? ""} inline-block`} aria-hidden />;
  // eslint-disable-next-line @next/next/no-img-element
  return <img src={src} alt="" loading="lazy" className={className} onError={() => setFailed(true)} />;
}

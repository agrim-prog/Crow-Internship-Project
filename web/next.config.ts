import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  outputFileTracingIncludes: {
    "/api/samples": ["./data/samples/**/*"],
    "/api/samples/*": ["./data/samples/**/*"],
  },
  turbopack: {
    root: path.join(__dirname),
  },
};

export default nextConfig;

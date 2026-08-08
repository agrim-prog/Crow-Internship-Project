import "server-only";
import fs from "node:fs/promises";
import path from "node:path";

const SAMPLES_DIR = path.join(process.cwd(), "data", "samples");

export interface SampleMeta {
  id: string;
  label: string;
}

function numericSuffix(filename: string): number {
  const match = filename.match(/(\d+)/);
  return match ? parseInt(match[1], 10) : 0;
}

export async function listSamples(): Promise<SampleMeta[]> {
  let files: string[];
  try {
    files = await fs.readdir(SAMPLES_DIR);
  } catch {
    return [];
  }

  return files
    .filter((f) => f.endsWith(".txt"))
    .sort((a, b) => numericSuffix(a) - numericSuffix(b))
    .map((f) => {
      const id = f.replace(/\.txt$/, "");
      const num = numericSuffix(f);
      return { id, label: `Sample lease ${num}` };
    });
}

export async function readSample(id: string): Promise<string | null> {
  if (!/^[a-zA-Z0-9_-]+$/.test(id)) return null;
  try {
    return await fs.readFile(path.join(SAMPLES_DIR, `${id}.txt`), "utf-8");
  } catch {
    return null;
  }
}

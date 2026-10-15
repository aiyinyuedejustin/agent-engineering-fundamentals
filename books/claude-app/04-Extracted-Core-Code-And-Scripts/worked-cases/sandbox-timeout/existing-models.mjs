/** Locate this book's original model; never look for product installations. */
import {existsSync} from 'node:fs';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const relative = '04-Extracted-Core-Code-And-Scripts/core-code-lab/workspace-core/workspaces-model.mjs';
function locate() {
  if (process.env.BOOK_PUBLICATION) {
    const file = join(resolve(process.env.BOOK_PUBLICATION), relative);
    if (!existsSync(file)) throw new Error('BOOK_PUBLICATION does not contain the workspace-core model');
    return file;
  }
  let directory = dirname(fileURLToPath(import.meta.url));
  for (;;) {
    for (const root of [directory, join(directory, 'publication')]) {
      const file = join(root, relative);
      if (existsSync(file)) return file;
    }
    const parent = dirname(directory);
    if (parent === directory) break;
    directory = parent;
  }
  throw new Error('Set BOOK_PUBLICATION to the book root; no existing model found');
}
export const modelPath = locate();
export const {ContentEpoch, withDeadline} = await import(pathToFileURL(modelPath).href);

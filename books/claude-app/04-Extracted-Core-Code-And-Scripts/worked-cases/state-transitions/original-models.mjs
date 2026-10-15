/** Import the already published original teaching models; never target bundles. */
import { resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
export const coreRoot = process.env.STATE_CASE_CORE_ROOT
  ? pathToFileURL(resolve(process.env.STATE_CASE_CORE_ROOT) + sep)
  : new URL('../../core-code-lab/', import.meta.url);
export const { ConversationBranches, ROOT } = await import(new URL('protocol-tree/branch-manager.mjs', coreRoot));
export const { ScopedMutationQueue, applyQueuedOptimistic, LatestRequestGuard, decideAccess, resolveFreshAccess }
  = await import(new URL('memory-flags/memory-flags-model.mjs', coreRoot));

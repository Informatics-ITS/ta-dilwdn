// @ts-nocheck
import type { PageServerLoad } from './$types';

export const load = async ({ params }: Parameters<PageServerLoad>[0]) => {
  // Return minimal data for SSR, let client handle API calls
  return {
    ujianSiswaId: parseInt(params.id) || null
  };
}; 
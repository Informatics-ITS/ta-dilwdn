import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
  // Return minimal data for SSR, let client handle API calls
  return {
    ujianSiswaId: parseInt(params.id) || null
  };
}; 
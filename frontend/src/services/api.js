/**
 * API Client for Townhall Backend
 */
import axios from 'axios';

// Always use relative /api so Vite proxy forwards it to localhost:8000
// This avoids CORS issues and lets the proxy handle redirects
const apiClient = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Hedera service client (port 3001 proxied via /hedera in vite.config.js)
const hederaClient = axios.create({
  baseURL: '/hedera',
  headers: { 'Content-Type': 'application/json' },
});

// ── FastAPI methods ───────────────────────────────────────────────────────────
export const api = {
  getStats: async () => {
    const response = await apiClient.get('/stats');
    return response.data;
  },

  getCounties: async () => {
    const response = await apiClient.get('/counties');
    return response.data;
  },

  getCounty: async (countyId) => {
    const response = await apiClient.get(`/counties/${countyId}`);
    return response.data;
  },

  getPetitions: async (countyId, params = {}) => {
    const response = await apiClient.get(`/counties/${countyId}/petitions`, { params });
    return response.data;
  },

  getPetition: async (countyId, petitionNumber) => {
    const response = await apiClient.get(`/counties/${countyId}/petitions/${petitionNumber}`);
    return response.data;
  },

  getMeetings: async (countyId, params = {}) => {
    const response = await apiClient.get(`/counties/${countyId}/meetings`, { params });
    return response.data;
  },

  getParcelsGeoJSON: async (countyId) => {
    const response = await apiClient.get(`/counties/${countyId}/parcels/geojson`);
    return response.data;
  },
};

// ── Hedera service methods (port 3001) ────────────────────────────────────────
export const hedera = {
  // Get all tokenized parcel PINs — used to render the gold map layer
  getTokenized: async (countyId) => {
    const params = countyId ? { countyId } : {};
    const response = await hederaClient.get('/token/tokenized', { params });
    return response.data; // { tokenized: [...] }
  },

  // Verify a parcel PIN exists and is not yet tokenized
  verifyDeed: async ({ pin, countyId, ownerAccountId }) => {
    const response = await hederaClient.post('/token/verify-deed', { pin, countyId, ownerAccountId });
    return response.data;
  },

  // Mint NFT deed + 1000 shares for a parcel
  mintParcel: async ({ pin, countyId, ownerAccountId, priceHbar }) => {
    const response = await hederaClient.post('/token/mint', { pin, countyId, ownerAccountId, priceHbar });
    return response.data;
  },

  // List shares for sale
  listShares: async ({ pin, countyId, ownerAccountId, sharesAmount, priceHbar }) => {
    const response = await hederaClient.post('/market/list', { pin, countyId, ownerAccountId, sharesAmount, priceHbar });
    return response.data;
  },

  // Buy shares from a listed parcel
  buyShares: async ({ pin, countyId, buyerAccountId, sharesAmount, txHashFromBuyer }) => {
    const response = await hederaClient.post('/market/buy', { pin, countyId, buyerAccountId, sharesAmount, txHashFromBuyer });
    return response.data;
  },

  // All active market listings
  getListings: async (countyId) => {
    const params = countyId ? { countyId } : {};
    const response = await hederaClient.get('/market/listings', { params });
    return response.data; // { listings: [...] }
  },

  // Wallet portfolio (shares purchased as buyer)
  getPortfolio: async (walletId) => {
    const response = await hederaClient.get(`/market/portfolio/${walletId}`);
    return response.data;
  },

  // Parcels owned (minted/claimed) by wallet — from token_registry
  getOwned: async (walletId) => {
    const response = await hederaClient.get(`/market/owned/${walletId}`);
    return response.data; // { owned: [...] }
  },
};

export default api;

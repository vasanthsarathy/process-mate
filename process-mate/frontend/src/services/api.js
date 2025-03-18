import axios from 'axios';

const API_BASE_URL = '/api';

// API client instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Fetch analysis for a position and move
 * 
 * @param {string} fen - FEN notation of the position
 * @param {string} move - Move in algebraic notation
 * @returns {Promise<Object>} - Analysis data
 */
export const fetchAnalysis = async (fen, move) => {
  try {
    const response = await apiClient.post('/analyze', { fen, move });
    return response.data;
  } catch (error) {
    console.error('Error fetching analysis:', error);
    throw error;
  }
};

/**
 * Fetch engine analysis for a position
 * 
 * @param {string} fen - FEN notation of the position
 * @param {number} depth - Analysis depth (optional)
 * @returns {Promise<Object>} - Engine analysis data
 */
export const fetchEngineAnalysis = async (fen, depth = 20) => {
  try {
    const response = await apiClient.post('/engine-analysis', { fen, depth });
    return response.data;
  } catch (error) {
    console.error('Error fetching engine analysis:', error);
    throw error;
  }
};

/**
 * Validate and parse a PGN game
 * 
 * @param {string} pgn - PGN text of the game
 * @returns {Promise<Object>} - Parsed game data
 */
export const validatePgn = async (pgn) => {
  try {
    const response = await apiClient.post('/validate-pgn', { pgn });
    return response.data;
  } catch (error) {
    console.error('Error validating PGN:', error);
    throw error;
  }
};
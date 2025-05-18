import type { HealthRecommendations } from '../types/HealthRecommendations';
import jsonData from '../data/kassandra_final_output.json';

const API_URL = 'https://naturally-mint-fly.ngrok-free.app'; // Replace with your actual API URL

export const fetchHealthData = async (): Promise<HealthRecommendations> => {
  // Try to fetch data from api
  try {
    const response = await fetch(`${API_URL}/get-final-output`);
    const data = await response.json();
    return data;
  } catch (error) {
    // Use static data if fetch fails
    console.log('error fetching from API', error);
    return jsonData as HealthRecommendations;
  }
};

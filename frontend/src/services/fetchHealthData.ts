import type { HealthRecommendations } from '../types/HealthRecommendations';

const API_URL = 'https://naturally-mint-fly.ngrok-free.app'; // Replace with your actual API URL

export const fetchHealthData = async (): Promise<HealthRecommendations> => {
  const response = await fetch(`${API_URL}/get-final-output`);
  const data = await response.json();
  return data;
};

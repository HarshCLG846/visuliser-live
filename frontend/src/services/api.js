const API_BASE_URL = 'http://localhost:8000';

export const analyzeExterior = async (imageFile, userSelections) => {
  try {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('user_selections', JSON.stringify(userSelections));

    const response = await fetch(`${API_BASE_URL}/analyze-exterior`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Health check failed:', error);
    return { status: 'error', error: error.message };
  }
};

export const editImage = async (imageFile, analysisResults, userSelections) => {
  try {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('analysis_results', JSON.stringify(analysisResults));
    formData.append('user_selections', JSON.stringify(userSelections));

    const response = await fetch(`${API_BASE_URL}/edit-image`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    // Get image blob
    const blob = await response.blob();
    const imageUrl = URL.createObjectURL(blob);
    return imageUrl;
  } catch (error) {
    console.error('Image editing error:', error);
    throw error;
  }
};


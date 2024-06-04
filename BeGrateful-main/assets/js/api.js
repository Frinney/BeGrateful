export async function fetchGratitudes() {
    const response = await fetch('/api/gratitudes');
    return response.json();
  }
  
  export async function postGratitude(gratitude) {
    const response = await fetch('/api/gratitudes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(gratitude)
    });
    return response.json();
  }
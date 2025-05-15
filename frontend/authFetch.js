// authFetch.js
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

async function fetchWithRefresh(url, options = {}) {
  // Добавляем базовый URL, если указан относительный путь
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url.startsWith('/') ? '' : '/'}${url}`;
  
  // Подготовка заголовков
  const token = localStorage.getItem('access_token');
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Первый запрос
  let response = await fetch(fullUrl, {
    ...options,
    headers,
  });

  // Если 401 - пробуем обновить токен
  if (response.status === 401) {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      logout();
      return Promise.reject(new Error('Refresh token missing'));
    }

    try {
      const refreshResponse = await fetch(`${API_BASE_URL}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }), // Обратите внимание на поле 'refresh'
      });

      if (!refreshResponse.ok) {
        logout();
        return Promise.reject(new Error('Token refresh failed'));
      }

      const { access } = await refreshResponse.json();
      localStorage.setItem('access_token', access);

      // Повторяем оригинальный запрос с новым токеном
      headers['Authorization'] = `Bearer ${access}`;
      response = await fetch(fullUrl, {
        ...options,
        headers,
      });
    } catch (error) {
      logout();
      return Promise.reject(error);
    }
  }

  return response;
}

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login.html';
}

// Добавляем в глобальную область видимости
window.authFetch = fetchWithRefresh;
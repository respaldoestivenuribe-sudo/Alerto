export const getToken = () => localStorage.getItem('token');

export const getUser = () => {
  const token = getToken();
  if (!token) return null;
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch {
    return null;
  }
};

export const isAdmin = () => getUser()?.role === 'administrador';

export const isAuthenticated = () => {
  const user = getUser();
  if (!user) return false;
  return user.exp * 1000 > Date.now();
};

export const clearAuth = () => localStorage.removeItem('token');

export const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${getToken()}`,
});

export const authFetch = (url, options = {}) =>
  fetch(url, {
    ...options,
    headers: {
      ...authHeaders(),
      ...(options.headers || {}),
    },
  });

import { BASE_URL } from '../config/settings';

const getToken = () => {
  return localStorage.getItem('token');
};

export const setToken = (token) => {
  localStorage.setItem('token', token);
};

export const removeToken = () => {
  localStorage.removeItem('token');
};

export const isAuthenticated = () => {
  return !!getToken();
};

const apiRequest = async (endpoint, options = {}) => {
  const { authenticated = false, ...fetchOptions } = options;

  const headers = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  };

  if (authenticated) {
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }
  }

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    let data = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    }

    // Auto-cleanup invalid tokens on 401
    if (response.status === 401 && authenticated) {
      removeToken();
    }

    return { data, status: response.status, ok: response.ok };
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};

// Auth API
export const authAPI = {
  register: async (email, firstName, lastName, password) => {
    return apiRequest('/register/', {
      method: 'POST',
      body: JSON.stringify({
        email,
        first_name: firstName,
        last_name: lastName,
        password,
      }),
    });
  },

  login: async (email, password) => {
    const result = await apiRequest('/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    if (result.ok && result.data?.token) {
      setToken(result.data.token);
    }

    return result;
  },

  verifyOtp: async (email, otp) => {
    return apiRequest('/verify-otp/', {
      method: 'POST',
      body: JSON.stringify({ email, otp }),
    });
  },

  resendOtp: async (email) => {
    return apiRequest('/resend-otp/', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  getUserInfo: async () => {
    return apiRequest('/me/', {
      method: 'GET',
      authenticated: true,
    });
  },

  logout: () => {
    removeToken();
  },
};

// Auction API
export const auctionAPI = {
  getAuctions: async () => {
    return apiRequest('/auctions/', {
      method: 'GET',
      authenticated: true,
    });
  },

  getAuctionDetails: async (auctionId) => {
    return apiRequest(`/auctions/${auctionId}/`, {
      method: 'GET',
      authenticated: true,
    });
  },

  joinAuction: async (auctionId) => {
    return apiRequest(`/auctions/${auctionId}/join_auction/`, {
      method: 'POST',
      authenticated: true,
    });
  },

  getMyAuctions: async () => {
    return apiRequest('/auctions/my_auctions/', {
      method: 'GET',
      authenticated: true,
    });
  },
};

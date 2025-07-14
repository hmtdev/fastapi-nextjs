"use client";
import { API_LOGIN } from "@/contants/endpoint";
import api, { fastApiClient } from "@/lib/api";
const AuthService = {
  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await api.post(API_LOGIN, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data.access_token;
    } catch (error) {
      throw error;
    }
  },
  refreshToken: async () => {
    try {
      const response = await api.post("/api/v1/auth/refresh", {}, {
        withCredentials: true
      },)
      return response.data.access_token
    }
    catch (error) {
      throw error;
    }
  }
  ,logout : async () => {
    try {
      await api.post("/api/v1/auth/logout", {}, {
        withCredentials: true
      });
    } catch (error) {
      console.error("Logout failed:", error);
    }
  },
  loginGoogle : async () => {
    const auth_url = `/api/v1/auth/google/login?redirect_uri=${process.env.NEXT_PUBLIC_FRONTED_URL}/login`;
    const response = await fastApiClient.get(auth_url)
    console.log("Google login response:", response);
    window.location.href = response.data.url;
  }
}


export { AuthService }
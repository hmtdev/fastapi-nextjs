import { NextResponse } from 'next/server';
import { fastApiClient } from '@/lib/api';
import { cookies } from 'next/headers';
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const response = await fastApiClient.post('/api/v1/auth/login', {
      username: body.username,
      password: body.password,
    }, {headers: { 'Content-Type': 'application/x-www-form-urlencoded' }});
    const nextResponse = NextResponse.json(response.data);
    if (response.data.access_token) {
      nextResponse.cookies.set({
        name: 'access_token',
        value: response.data.access_token,
        httpOnly: true,
        maxAge: 3600,
        sameSite: 'strict',
        path: '/',
      });
    }
    return nextResponse;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (error: any) {
    return NextResponse.json(
      { message: error.response?.data?.detail || 'Internal server error' },
      { status: error.response?.status || 500 }
    );
  }
}

export async function GET(request: Request) {
  try {
    const cookieStore = await cookies();
    const tokenCookie = cookieStore.get('access_token');
    if (tokenCookie) {
      const redirectUrl = new URL('/dashboard', process.env.FRONTED_URL);
      const response = NextResponse.redirect(redirectUrl);
      response.cookies.set('access_token', tokenCookie.value, {
        httpOnly: true,  
        maxAge: 3600,
        sameSite: 'lax', 
        path: '/',
      });
      response.cookies.set('auth_provider', 'google', {
        httpOnly: false,
        maxAge: 3600,
        sameSite: 'lax',
        path: '/',
      });
      return response;
    }
    return NextResponse.redirect(new URL('/login', process.env.FRONTED_URL));
  } catch (error: unknown) {
    console.error('Login redirect error:', error);
    return NextResponse.redirect(new URL('/login?error=true', process.env.FRONTED_URL));
  }
}
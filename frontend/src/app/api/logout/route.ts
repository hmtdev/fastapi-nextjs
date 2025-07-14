import { NextResponse } from 'next/server';
import { fastApiClient } from '@/lib/api';
import { cookies } from 'next/headers';

export async function POST() {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('access_token')?.value;

    if (token) {
      try {
        await fastApiClient.post('/api/v1/auth/logout', {}, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
      } catch (error) {
        console.error('Error calling FastAPI logout:', error);
      }
    }

    const response = NextResponse.json({ message: 'Logged out successfully' });
    
    response.cookies.delete('access_token');

    return response;
    
  } catch {
    return NextResponse.json(
      { message: 'Failed to logout' },
      { status: 500 }
    );
  }
}
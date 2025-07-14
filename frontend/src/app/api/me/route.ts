import { NextResponse } from 'next/server';
import { fastApiClient } from '@/lib/api';
import { cookies } from 'next/headers';

export async function GET() {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('access_token')?.value;

    if (!token) {
      return NextResponse.json(
        { message: 'Unauthorized',success: true, data : []},
        { status: 200 }
      );
    }

    const response = await fastApiClient.get('/api/v1/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return NextResponse.json({
      success: true,
      message: 'User info fetched successfully',
      data: response.data
    });
  } catch (error: any) {
    
    return NextResponse.json(
      { message: error.response?.data?.detail || 'Failed to fetch user info' },
      { status: error.response?.status || 500 }
    );
  }
}
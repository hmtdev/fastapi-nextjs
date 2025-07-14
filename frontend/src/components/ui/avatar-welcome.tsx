"use client";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "./button";
import Link from "next/link";
import { Avatar, AvatarFallback, AvatarImage } from "./avatar";
import { Skeleton } from "./skeleton";

export default function AvatarGroup() {
  const { user, loading  } = useAuth();
  if (loading) {
    return (
      <div className="flex items-center space-x-4">
        <div className="space-y-2">
          <Skeleton className="h-4 w-[250px]" />
        </div>
        <Skeleton className="h-12 w-12 rounded-full" />
         <Skeleton className="h-[36px] w-[76px] border-lg" />
      </div>
    );
  }
  return (
    <div className="flex items-center space-x-4">
      <h1 className="text-2xl font-bold"></h1>
      <p className="text-lg">Welcome {user?.username}</p>
      <Avatar className="w-10 h-10">
        <AvatarImage src={user?.avatar_url} alt="@shadcn" />
        <AvatarFallback>CN</AvatarFallback>
      </Avatar>
      <Button variant="outline" className="text-lg font-bold">
        <Link href="/">Logout</Link>
      </Button>
    </div>
  );
}

import { Button } from "@/components/ui/button";
import NavigationHeader from "@/components/ui/nav-header";
import Link from "next/link";

export default function RootPage() {
  return (
    <>
    <div className="flex flex-col h-screen bg-gray-100 w-full">
    <NavigationHeader>
        <Button className="text-lg font-bold">
          <Link href="/login">Login</Link>
        </Button>
        <Button variant="outline" className="text-lg font-bold">
          <Link href="/register">Register</Link>
        </Button>
      </NavigationHeader>
    </div>
    </>
  );
}

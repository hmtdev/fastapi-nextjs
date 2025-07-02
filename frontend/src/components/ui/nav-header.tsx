import Link from "next/link";
import { Button } from "./button";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "./navigation-menu";

export default function NavigationHeader() {
  return (
    <div className="flex items-center justify-between w-full p-4 text-size-lg">
      <div className="flex">
        <Button variant="ghost" className="text-lg font-bold">
          Demo
        </Button>
      </div>
      <div className="flex items-center space-x-2 flex-1">
        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuItem>
              <NavigationMenuLink asChild>
                <Link href="/">Home</Link>
              </NavigationMenuLink>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <NavigationMenuLink asChild>
                <Link href="/about">About</Link>
              </NavigationMenuLink>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <NavigationMenuLink asChild>
                <Link href="/contact">contact</Link>
              </NavigationMenuLink>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
      </div>
      <div className="flex items-center space-x-2">
        <Button variant="secondary" className="text-lg font-bold">
          <Link href="/login">Login</Link>
        </Button>
        <Button variant="outline" className="text-lg font-bold">
          <Link href="/register">Register</Link>
        </Button>
      </div>
    </div>
  );
}

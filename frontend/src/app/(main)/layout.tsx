import AvatarGroup from "@/components/ui/avatar-welcome";
import NavigationHeader from "@/components/ui/nav-header";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <NavigationHeader>
        <AvatarGroup></AvatarGroup>
      </NavigationHeader>
      <main className="flex-1">{children}</main>
    </>
  );
}

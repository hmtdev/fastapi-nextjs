export default function AuthLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
          <div className="flex-1 flex items-center justify-center px-4 mx-4">
            {children}
          </div>
  );
}


export default function LoginLayout({children}: Readonly<{children: React.ReactNode}>) {
    return (
        <div className="flex flex-col min-h-screen px-4">
               {children}
        </div>
    );
}
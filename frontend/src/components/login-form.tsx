'use client'
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import nextApiClient from "@/lib/api"
import { useRouter } from "next/navigation"
import { toast } from 'sonner'
import { AuthService } from "@/services/auth.services"

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const router = useRouter()
  const handleLogin = async (e: { preventDefault: () => void }) => {
    e.preventDefault()
    try {
      const res = await nextApiClient.post("/login", {
        username,
        password,
      })
      toast.success("Login successful!")
      console.log("Login successful:", res.data);
      router.push("/dashboard");
    } catch (error) {
      toast.success("Login failed")
      console.error("Login failed:", error)
      // Show error message to user
    }
  }

  const loginGoogle = async (e: { preventDefault: () => void }) => {
    e.preventDefault()
    await AuthService.loginGoogle()
  }
  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle>Login to your account</CardTitle>
          <CardDescription>
            Enter your username below to login to your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={(e) => e.preventDefault()} className="space-y-6">
            <div className="flex flex-col gap-6">
              <div className="grid gap-3">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="username"
                  placeholder="admin123"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className="grid gap-3">
                <div className="flex items-center">
                  <Label htmlFor="password">Password</Label>
                  <a
                    href="#"
                    className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                  >
                    Forgot your password?
                  </a>
                </div>
                <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>
              <div className="flex flex-col gap-3">
                <Button type="button" className="w-full" onClick={handleLogin} >
                  Login
                </Button>
                <Button variant="outline" className="w-full" onClick={loginGoogle}>
                  Login with Google
                </Button>
                  <Button type="button" className="w-full" >
                  show token 
                </Button>
              </div>
            </div>
            <div className="mt-4 text-center text-sm">
              Don&apos;t have an account?{" "}
              <a href="#" className="underline underline-offset-4">
                Sign up
              </a>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

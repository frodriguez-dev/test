import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { HealthStatus } from '@/features/health/HealthStatus'

export function HomePage() {
  return (
    <main className="flex min-h-svh items-center justify-center bg-muted/30 p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Frontend</CardTitle>
          <CardDescription>
            React, TypeScript, and Vite are ready, styled with Tailwind CSS and
            shadcn/ui.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Button>Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
          </div>
          <div className="border-t pt-4">
            <HealthStatus />
          </div>
        </CardContent>
        <CardFooter>
          <p className="text-sm text-muted-foreground">
            The API client and generated OpenAPI types are connected.
          </p>
        </CardFooter>
      </Card>
    </main>
  )
}

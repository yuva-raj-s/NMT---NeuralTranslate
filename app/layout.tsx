import type React from "react"
import "@/app/globals.css"
import { Inter } from "next/font/google"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "Neural Machine Translation with Gemma-3",
  description: "Futuristic translation interface powered by SLM Gemma-3 model using the ALT dataset",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <body className={inter.className}>{children}</body>
    </html>
  )
}

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Brain, FileText, MessageCircle, PenTool } from "lucide-react"
import Link from "next/link"

export default function Home() {
  const features = [
    {
      icon: <Brain className="h-8 w-8" />, 
      title: "Post Summarization", 
      description: "Quickly summarize LinkedIn posts for better insights", 
      href: "/summarize"
    },
    {
      icon: <PenTool className="h-8 w-8" />, 
      title: "AI-Powered Post Writing", 
      description: "Generate engaging LinkedIn posts with AI assistance", 
      href: "/write_post"
    },
    {
      icon: <MessageCircle className="h-8 w-8" />, 
      title: "Automated Comment Generation", 
      description: "Get AI-generated comments tailored to any post", 
      href: "/generate_comments"
    },
    {
      icon: <FileText className="h-8 w-8" />, 
      title: "Sentiment Analysis", 
      description: "Analyze sentiment to craft the perfect response", 
      href: "/sentiment_analysis"
    }
  ]

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          LinkedIn Automation with AI
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Automate LinkedIn interactions with AI-powered tools for post summarization, content generation, comment writing, and sentiment analysis.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {features.map((feature) => (
          <Link key={feature.title} href={feature.href}>
            <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="mb-4 text-primary">
                  {feature.icon}
                </div>
                <CardTitle>{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">
                  Click to get started →
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
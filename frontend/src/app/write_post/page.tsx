"use client"

import { useState } from "react"
import axios from "axios"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { PenTool } from "lucide-react"

const API_BASE_URL = "http://127.0.0.1:5000"; // ✅ Centralized API URL

export default function GeneratePost() {
  const [topic, setTopic] = useState("")
  const [keywords, setKeywords] = useState("")
  const [post, setPost] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleGeneratePost = async () => {
    const trimmedTopic = topic.trim();
    const trimmedKeywords = keywords.trim();

    if (!trimmedTopic) {
      setError("Please enter a topic for the LinkedIn post.");
      return;
    }

    setLoading(true);
    setError("");
    setPost("");

    try {
      const response = await axios.post(`${API_BASE_URL}/write_post`, {
        topic: trimmedTopic,
        keywords: trimmedKeywords
      });

      if (response.data.error) {
        setError(response.data.error);
      } else {
        setPost(response.data.post || "No post generated.");
      }
    } catch (error) {
      console.error("API Error:", error);
      setError("Failed to generate the LinkedIn post. Please check if the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <PenTool className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">LinkedIn Post Generator</h1>
            <p className="text-muted-foreground">Create engaging LinkedIn posts with AI assistance</p>
          </div>
        </div>

        {/* Input Fields */}
        <Card>
          <CardHeader>
            <CardTitle>Post Parameters</CardTitle>
            <CardDescription>Define your post topic and keywords</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Topic</label>
              <Input
                placeholder="Enter the main topic..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Keywords</label>
              <Input
                placeholder="Enter keywords (comma separated)..."
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Generate Button */}
        <div className="flex justify-center mt-6">
          <Button size="lg" onClick={handleGeneratePost} disabled={loading} className="w-full">
            {loading ? "Generating Post..." : "Generate LinkedIn Post"}
          </Button>
        </div>

        {/* Error Message */}
        {error && <p className="text-red-500 text-sm mt-2 text-center">{error}</p>}

        {/* Generated Post */}
        {post && !error && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Generated LinkedIn Post</CardTitle>
              <CardDescription>Your AI-generated post will appear here</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-4 rounded-lg bg-muted">
                <h2 className="font-semibold text-gray-800">Generated Post:</h2>
                <p className="text-gray-700">{post}</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

"use client";

import { useState } from "react";
import axios from "axios";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { MessageCircle } from "lucide-react";

export default function GenerateComments() {
  const [post, setPost] = useState("");
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerateComments = async () => {
    if (!post.trim()) {
      setError("Please enter a LinkedIn post to generate comments.");
      return;
    }

    setLoading(true);
    setError("");
    setComments([]);

    try {
      const response = await axios.post("http://127.0.0.1:5000/generate-comments", { post });
      setComments(response.data.comments);
    } catch (error) {
      console.error("Error:", error);
      setError("Failed to generate comments. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <MessageCircle className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">LinkedIn Post Comment Generator</h1>
            <p className="text-muted-foreground">Generate AI-powered comments for LinkedIn posts</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Input LinkedIn Post</CardTitle>
            <CardDescription>Paste a LinkedIn post below to generate relevant comments</CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="Enter your LinkedIn post here..."
              className="min-h-[200px]"
              value={post}
              onChange={(e) => setPost(e.target.value)}
            />
          </CardContent>
        </Card>

        <div className="flex justify-center mt-6">
          <Button size="lg" onClick={handleGenerateComments} disabled={loading} className="w-full">
            {loading ? "Generating..." : "Generate Comments"}
          </Button>
        </div>

        {error && <p className="text-red-500 text-sm mt-2 text-center">{error}</p>}

        {comments.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Generated Comments</CardTitle>
              <CardDescription>AI-generated comments based on the given LinkedIn post</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-4 rounded-lg bg-muted space-y-2">
                {comments.map((comment, index) => (
                  <p key={index} className="text-gray-700">- {comment}</p>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

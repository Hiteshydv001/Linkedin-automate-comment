"use client";

import { useState } from "react";
import axios from "axios";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { MessageCircle, Loader2 } from "lucide-react";

const API_BASE_URL = "http://127.0.0.1:5000"; // Ensure backend is running on this

export default function GenerateComments() {
  const [post, setPost] = useState("");
  const [comments, setComments] = useState<string[]>([]);
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
      const response = await axios.post(`${API_BASE_URL}/generate_comments`, { 
        post_content: post  // ✅ Fix: Send "post_content" instead of "post"
      });

      if (response.data?.error) {
        setError(response.data.error);
      } else if (!response.data?.comments?.length) {
        setError("No comments were generated. Try again with a different post.");
      } else {
        setComments(response.data.comments);
      }
    } catch (err) {
      console.error("API Error:", err);
      setError("Failed to generate comments. Ensure the backend is running at 127.0.0.1:5000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Header Section */}
        <div className="flex items-center gap-4 mb-8">
          <MessageCircle className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">LinkedIn Post Comment Generator</h1>
            <p className="text-muted-foreground">Generate AI-powered comments for LinkedIn posts</p>
          </div>
        </div>

        {/* Input Section */}
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

        {/* Generate Button */}
        <div className="flex justify-center mt-6">
          <Button size="lg" onClick={handleGenerateComments} disabled={loading} className="w-full">
            {loading ? <Loader2 className="animate-spin" /> : "Generate Comments"}
          </Button>
        </div>

        {/* Error Message */}
        {error && <p className="text-red-500 text-sm mt-2 text-center">{error}</p>}

        {/* Generated Comments Section */}
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

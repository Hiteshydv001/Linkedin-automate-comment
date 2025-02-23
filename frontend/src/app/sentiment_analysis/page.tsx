"use client";

import { useState } from "react";
import axios from "axios";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Brain } from "lucide-react";

export default function SentimentAnalysis() {
  const [text, setText] = useState("");
  const [sentiment, setSentiment] = useState("");
  const [confidence, setConfidence] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyzeSentiment = async () => {
    if (!text.trim()) {
      setError("Please enter a LinkedIn post for sentiment analysis.");
      return;
    }

    setLoading(true);
    setError("");
    setSentiment("");
    setConfidence("");

    try {
      const response = await axios.post("http://127.0.0.1:5000/sentiment_analysis", { text });
      setSentiment(response.data.sentiment);
      setConfidence(response.data.confidence);
    } catch (error) {
      console.error("Error:", error);
      setError("Failed to analyze sentiment. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <Brain className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">LinkedIn Post Sentiment Analysis</h1>
            <p className="text-muted-foreground">Analyze the sentiment of your LinkedIn posts effortlessly</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Input LinkedIn Post</CardTitle>
            <CardDescription>Paste your LinkedIn post below to analyze its sentiment</CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="Enter your LinkedIn post here..."
              className="min-h-[200px]"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </CardContent>
        </Card>

        <div className="flex justify-center mt-6">
          <Button size="lg" onClick={handleAnalyzeSentiment} disabled={loading} className="w-full">
            {loading ? "Analyzing..." : "Analyze Sentiment"}
          </Button>
        </div>

        {error && <p className="text-red-500 text-sm mt-2 text-center">{error}</p>}

        {sentiment && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Sentiment Analysis Result</CardTitle>
              <CardDescription>Your LinkedIn post sentiment analysis result</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-4 rounded-lg bg-muted">
                <h2 className="font-semibold text-gray-800">Sentiment:</h2>
                <p className="text-gray-700">{sentiment}</p>

                <h2 className="font-semibold text-gray-800 mt-3">Confidence Score:</h2>
                <p className="text-gray-700">{confidence}</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

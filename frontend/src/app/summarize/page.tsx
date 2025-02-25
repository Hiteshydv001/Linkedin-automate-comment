"use client";

import { useState } from "react";
import axios from "axios";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Brain } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:5000";

export default function Summarize() {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");
  const [validation, setValidation] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSummarize = async () => {
    if (!text.trim()) {
      setError("Please enter your post text to summarize.");
      return;
    }

    setLoading(true);
    setError("");
    setSummary("");
    setValidation("");

    try {
      const response = await axios.post(`${API_BASE_URL}/summarize`, { text });

      if (response.data.error) {
        setError(response.data.error);
      } else {
        setSummary(response.data.summary);
        setValidation(response.data.validation || "Validation not provided.");
      }
    } catch (err) {
      console.error("API Error:", err);
      setError("Failed to summarize. Please check if the backend is running.");
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
            <h1 className="text-3xl font-bold tracking-tight">Text Summarization</h1>
            <p className="text-muted-foreground">Transform long text into concise summaries</p>
          </div>
        </div>

        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Input Text</CardTitle>
              <CardDescription>Paste your text below to summarize</CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="Enter your text here..."
                className="min-h-[200px]"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </CardContent>
          </Card>

          <div className="flex justify-center">
            <Button
              size="lg"
              onClick={handleSummarize}
              disabled={loading}
              className="w-full"
            >
              {loading ? "Summarizing..." : "Generate Summary"}
            </Button>
          </div>

          {error && <p className="text-red-500 text-sm mt-2 text-center">{error}</p>}

          {summary && (
            <Card>
              <CardHeader>
                <CardTitle>Summary</CardTitle>
                <CardDescription>Your generated summary will appear here</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="p-4 rounded-lg bg-muted">
                  <h2 className="font-semibold text-gray-500">Summary:</h2>
                  <p className="text-gray-400">{summary}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {validation && (
            <Card>
              <CardHeader>
                <CardTitle>Validation</CardTitle>
                <CardDescription>Summary validation result</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="p-4 rounded-lg bg-muted">
                  <h2 className="font-semibold text-gray-500">Validation:</h2>
                  <p className="text-gray-400">{validation}</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

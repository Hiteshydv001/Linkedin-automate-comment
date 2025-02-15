"use client";

import { useState } from "react";
import axios from "axios";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Brain } from "lucide-react";

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
      const response = await axios.post("http://127.0.0.1:5000/summarize", { text });
      setSummary(response.data.summary);
      setValidation(response.data.validation);
    } catch (error) {
      console.error("Error:", error);
      setError("Failed to summarize. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Header Section */}
        <div className="flex items-center gap-4 mb-8">
          <Brain className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Text Summarization</h1>
            <p className="text-muted-foreground">Transform long text into concise summaries</p>
          </div>
        </div>

        {/* Text Input Section */}
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

          {/* Summarize Button */}
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

          {/* Error Display */}
          {error && <p className="text-red-500 text-sm mt-2 text-center">{error}</p>}

          {/* Summary Section */}
          {summary && (
            <Card>
              <CardHeader>
                <CardTitle>Summary</CardTitle>
                <CardDescription>Your generated summary will appear here</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="p-4 rounded-lg bg-muted">
                  <h2 className="font-semibold text-gray-800">Summary:</h2>
                  <p className="text-gray-700">{summary}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Validation Section */}
          {validation && (
            <Card>
              <CardHeader>
                <CardTitle>Validation</CardTitle>
                <CardDescription>Summary validation result</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="p-4 rounded-lg bg-muted">
                  <h2 className="font-semibold text-gray-800">Validation:</h2>
                  <p className="text-gray-700">{validation}</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

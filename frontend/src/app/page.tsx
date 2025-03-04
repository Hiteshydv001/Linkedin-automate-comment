/*import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Brain, FileText, MessageCircle, PenTool } from "lucide-react"
import Link from "next/link"

export default function Home() 
{
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
    <main className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white px-6">
  
      {/* Hero Section *//*
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center max-w-2xl"
      >
        <h1 className="text-5xl font-bold tracking-tight mb-4">
          Elevate Your LinkedIn Game 🚀
        </h1>
        <p className="text-lg text-gray-300">
          AI-powered text processing to craft professional and engaging LinkedIn posts.
        </p>
        <Button className="mt-6 px-6 py-3 text-lg bg-blue-500 hover:bg-blue-600">
          Get Started
        </Button>
      </motion.div>

      {/* Features Section *//*
      <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, index) => (
          <motion.div
            key={index}
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            className="bg-gray-800 p-6 rounded-xl shadow-lg"
          >
            <h3 className="text-xl font-semibold">{feature.title}</h3>
            <p className="text-gray-400 mt-2">{feature.description}</p>
          </motion.div>
        ))}
      </div>
    </main>
  ); */
  /*return (
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
  ); 
}*/
"use client";

import React from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, FileText, MessageCircle, PenTool } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const features = [
    {
      /*icon: <Brain className="h-8 w-8" />, 
      title: "Post Summarization", 
      description: "Quickly summarize LinkedIn posts for better insights", 
      href: "/summarize"*/
      icon: <Brain className="h-12 w-12 text-blue-400" />, 
      title: "Post Summarization", 
      description: "Quickly summarize LinkedIn posts for better insights", 
      href: "/summarize"
    },
    {
      /*icon: <PenTool className="h-8 w-8" />, 
      title: "AI-Powered Post Writing", 
      description: "Generate engaging LinkedIn posts with AI assistance", 
      href: "/write_post"*/
      icon: <PenTool className="h-10 w-10 text-purple-400" />, 
      title: "AI-Powered Post Writing", 
      description: "Generate engaging LinkedIn posts with AI assistance", 
      href: "/write_post"
    },
    {
      /*icon: <MessageCircle className="h-8 w-8" />, 
      title: "Automated Comment Generation", 
      description: "Get AI-generated comments tailored to any post", 
      href: "/generate_comments"*/
      icon: <MessageCircle className="h-12 w-12 text-green-400" />, 
      title: "Automated Comment Generation", 
      description: "Get AI-generated comments tailored to any post", 
      href: "/generate_comments"
    },
    {
      /*icon: <FileText className="h-8 w-8" />, 
      title: "Sentiment Analysis", 
      description: "Analyze sentiment to craft the perfect response", 
      href: "/sentiment_analysis"*/
      icon: <FileText className="h-12 w-12 text-yellow-400" />, 
      title: "Sentiment Analysis", 
      description: "Analyze sentiment to craft the perfect response", 
      href: "/sentiment_analysis"
    }
  ];

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white px-6">
      
      {/* 🚀 Hero Section with Rocket Animation */}
      {/* 🚀 Hero Section with Rocket Animation */}
<motion.div 
  initial={{ opacity: 0, y: -20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.8 }}
  className="text-center max-w-2xl"
>
  <h1 className="text-5xl font-extrabold tracking-tight mb-4">
    <span className="bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
      
      Elevate Your LinkedIn Game 
    </span>
    <motion.span 
      animate={{
        y: [0, -20, 0],  // Move up and down
        opacity: [1, 1, 1],  
      }} 
      transition={{
        duration: 2,
        ease: "easeInOut",
        repeat: Infinity,  // Keeps repeating
        repeatDelay: 3,
      }}
      className="inline-block ml-2"
    >
      🚀
    </motion.span>
  </h1>
  <p className="text-lg text-gray-300 text-center">
    AI-powered text processing to craft professional and engaging LinkedIn posts.
  </p>
  <Button className="mt-6 px-6 py-3 text-lg bg-blue-500 hover:bg-blue-600 rounded-lg shadow-lg">
    Get Started
  </Button>
</motion.div>


      {/* Features Section */}
      <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
  {features.map((feature, index) => (
    <Link key={index} href={feature.href.toString()} className="flex">
      <motion.div
        whileHover={{ scale: 1.05, boxShadow: "0px 4px 20px rgba(255, 255, 255, 0.2)" }}
        transition={{ duration: 0.3 }}
        className="flex flex-col items-center justify-between w-full h-full bg-white/10 backdrop-blur-lg p-6 rounded-2xl shadow-md border border-white/20 transform transition-all hover:bg-white/20 cursor-pointer"
      >
        <div className="flex flex-col items-center space-y-4">
          <div className="p-4 bg-white/10 rounded-full">{feature.icon}</div>
          <div className="text-center">
            <h3 className="text-xl font-semibold">{feature.title}</h3>
            <p className="text-gray-300 mt-2">{feature.description}</p>
          </div>
        </div>
      </motion.div>
       </Link>
       ))}
     </div>

      
    </main>
  );
}
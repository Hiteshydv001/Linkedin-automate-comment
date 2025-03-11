"use client";

import React from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Brain, FileText, MessageCircle, PenTool } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const features = [
    {
      icon: <Brain className="h-12 w-12 text-blue-500 dark:text-blue-300" />,
      title: "Post Summarization",
      description: "Quickly summarize LinkedIn posts for better insights",
      href: "/summarize",
    },
    {
      icon: <PenTool className="h-10 w-10 text-purple-500 dark:text-purple-300" />,
      title: "AI-Powered Post Writing",
      description: "Generate engaging LinkedIn posts with AI assistance",
      href: "/write_post",
    },
    {
      icon: <MessageCircle className="h-12 w-12 text-green-500 dark:text-green-300" />,
      title: "Automated Comment Generation",
      description: "Get AI-generated comments tailored to any post",
      href: "/generate_comments",
    },
    {
      icon: <FileText className="h-12 w-12 text-yellow-500 dark:text-yellow-300" />,
      title: "Sentiment Analysis",
      description: "Analyze sentiment to craft the perfect response",
      href: "/sentiment_analysis",
    },
  ];

  const testimonials = [
    {
      name: "John Doe",
      role: "Marketing Expert",
      quote: "This AI-powered tool has revolutionized my LinkedIn strategy!",
      image: "https://randomuser.me/api/portraits/men/32.jpg"
    },
    {
      name: "Jane Smith",
      role: "HR Specialist",
      quote: "Saves so much time! Writing posts and comments has never been easier.",
      image: "https://randomuser.me/api/portraits/women/44.jpg"
    },
    {
      name: "Alex Johnson",
      role: "Content Creator",
      quote: "Absolutely love the sentiment analysis feature. Helps me craft the perfect response!",
      image: "https://randomuser.me/api/portraits/men/12.jpg"
    }
  ];

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-lightModeBG dark:bg-darkModeBG text-lightModeText dark:text-darkModeText px-6 transition-colors duration-300">
      
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }} 
        animate={{ opacity: 1, y: 0 }} 
        transition={{ duration: 0.8 }} 
        className="text-center max-w-3xl p-8 rounded-xl shadow-lg bg-white dark:bg-gray-900"
      >
        <h1 className="text-5xl font-extrabold tracking-tight mb-4">
          <span className="bg-gradient-to-r from-blue-500 to-purple-500 text-transparent bg-clip-text dark:from-blue-300 dark:to-purple-400">
            Elevate Your LinkedIn Game
          </span>
        </h1>
        <p className="text-lg text-gray-700 dark:text-gray-300">
          AI-powered text processing to craft professional and engaging LinkedIn posts.
        </p>
        <Button className="mt-6 px-6 py-3 text-lg bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg shadow-md transition-transform transform hover:scale-105">
          Get Started
        </Button>
      </motion.div>

      {/* Features Section */}
      <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
        {features.map((feature, index) => (
          <Link key={index} href={feature.href.toString()} className="flex">
            <motion.div
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
              className="flex flex-col items-center justify-between w-full h-full bg-white dark:bg-gray-800 shadow-lg border border-gray-300 dark:border-gray-700 p-6 rounded-xl hover:shadow-xl transition-all cursor-pointer"
            >
              <div className="flex flex-col items-center space-y-4">
                <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded-full">{feature.icon}</div>
                <h3 className="text-xl font-semibold">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300 mt-2">{feature.description}</p>
              </div>
            </motion.div>
          </Link>
        ))}
      </div>

      {/* How It Works Section */}
      <motion.section className="mt-24 text-center max-w-4xl" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1 }}>
        <h2 className="text-3xl font-bold">How It Works</h2>
        <p className="text-gray-600 dark:text-gray-300 mt-4">Follow these simple steps to get started:</p>
        <motion.ul className="mt-8 space-y-4 text-lg" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
          <li>🔹 Sign in with your LinkedIn account</li>
          <li>🔹 Choose a feature: Summarization, Writing, or Comments</li>
          <li>🔹 Let AI assist you in crafting the perfect content</li>
          <li>🔹 Post directly or save for later</li>
        </motion.ul>
      </motion.section>

      {/* Call to Action Section */}
      <section className="mt-24 bg-blue-600 text-white p-12 rounded-lg text-center">
        <h2 className="text-4xl font-bold">Ready to Boost Your LinkedIn Presence?</h2>
        <p className="text-lg mt-4">Join thousands of professionals using our AI-powered tools today!</p>
        <Button className="mt-6 px-8 py-3 bg-white text-blue-600 font-bold rounded-lg shadow-md hover:bg-gray-200 transition-transform transform hover:scale-105">
          Get Started
        </Button>
      </section>

      {/*  Testimonials Section */}
      <section className="mt-24 max-w-5xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-6">What Users Say</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
              className="p-6 bg-white dark:bg-gray-800 shadow-lg rounded-lg"
            >
              <div className="flex justify-center mb-4">
                <img src={testimonial.image} alt={testimonial.name} className="w-16 h-16 rounded-full" />
              </div>
              <p className="text-gray-700 dark:text-gray-300 italic">"{testimonial.quote}"</p>
              <h4 className="mt-4 font-semibold">{testimonial.name}</h4>
              <p className="text-gray-500 text-sm">{testimonial.role}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Footer Section */}
      <footer className="mt-24 py-6 text-center text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 w-full">
        <p>© {new Date().getFullYear()} Your Company. All rights reserved.</p>
      </footer>
    </main>
  );
}

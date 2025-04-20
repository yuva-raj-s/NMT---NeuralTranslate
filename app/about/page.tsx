"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, BookOpen, Brain, Database, Lightbulb, Zap, Globe, Sparkles, Target } from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"
import { useEffect, useRef } from "react"

export default function AboutPage() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("animate-fadeIn")
          }
        })
      },
      { threshold: 0.1 }
    )

    const cards = document.querySelectorAll(".animate-on-scroll")
    cards.forEach((card) => observer.observe(card))

    return () => observer.disconnect()
  }, [])

  return (
    <main className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white overflow-hidden">
      {/* Enhanced animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-10 -left-10 w-40 h-40 bg-blue-500 rounded-full filter blur-3xl opacity-10"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.1, 0.15, 0.1],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute top-1/3 -right-10 w-60 h-60 bg-purple-500 rounded-full filter blur-3xl opacity-10"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1,
          }}
        />
        <motion.div
          className="absolute -bottom-10 left-1/3 w-50 h-50 bg-cyan-500 rounded-full filter blur-3xl opacity-10"
          animate={{
            scale: [1, 1.4, 1],
            opacity: [0.1, 0.25, 0.1],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2,
          }}
        />

        {/* Enhanced neural network visualization */}
        <div className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none">
          <svg width="800" height="800" viewBox="0 0 800 800" className="stroke-blue-400">
            {Array.from({ length: 20 }).map((_, i) => {
              const angle1 = (i * Math.PI * 2) / 20
              const angle2 = ((i + 10) * Math.PI * 2) / 20
              const x1 = Math.round(400 + 300 * Math.cos(angle1))
              const y1 = Math.round(400 + 300 * Math.sin(angle1))
              const x2 = Math.round(400 + 300 * Math.cos(angle2))
              const y2 = Math.round(400 + 300 * Math.sin(angle2))
              return (
                <motion.line
                  key={i}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  strokeWidth="1"
                  className={`opacity-${20 + (i * 4)}`}
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{
                    duration: 2,
                    delay: i * 0.1,
                    repeat: Infinity,
                    repeatType: "reverse",
                  }}
                />
              )
            })}

            {Array.from({ length: 30 }).map((_, i) => {
              const angle = (i * Math.PI * 2) / 30
              const radius = 200 + (i % 3) * 100
              const cx = Math.round(400 + radius * Math.cos(angle))
              const cy = Math.round(400 + radius * Math.sin(angle))
              const r = 2 + (i % 3)
              return (
                <motion.circle
                  key={i}
                  cx={cx}
                  cy={cy}
                  r={r}
                  fill="currentColor"
                  className={`opacity-${20 + (i * 3)}`}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{
                    duration: 0.5,
                    delay: i * 0.1,
                    repeat: Infinity,
                    repeatType: "reverse",
                  }}
                />
              )
            })}
          </svg>
        </div>
      </div>

      <div className="container mx-auto py-8 px-4 relative z-10" ref={containerRef}>
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8"
          >
            <Link href="/">
              <Button variant="ghost" className="text-gray-400 hover:text-white transition-colors duration-300">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Translator
              </Button>
            </Link>
          </motion.div>

          <motion.header
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mb-12 text-center"
          >
            <div className="flex items-center justify-center mb-3">
              <motion.div
                className="relative"
                animate={{
                  rotate: [0, 360],
                }}
                transition={{
                  duration: 20,
                  repeat: Infinity,
                  ease: "linear",
                }}
              >
                <Globe className="h-10 w-10 mr-3 text-blue-400" />
                <motion.div
                  className="absolute -top-1 -right-1 w-3 h-3 bg-purple-500 rounded-full"
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [0.5, 1, 0.5],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                />
              </motion.div>
              <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-cyan-400">
                NEURAL TRANSLATOR
              </h1>
            </div>
            <h2 className="text-2xl font-semibold text-gray-200 mt-4">Our Approach</h2>
            <p className="text-gray-400 mt-2">
              How we built a powerful yet efficient translation system using knowledge distillation
            </p>
          </motion.header>

          <div className="space-y-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="animate-on-scroll"
            >
              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 p-6 rounded-xl hover:border-blue-500/50 transition-all duration-300">
                <div className="flex items-start">
                  <motion.div
                    animate={{
                      rotate: [0, 360],
                    }}
                    transition={{
                      duration: 20,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                  >
                    <Brain className="h-8 w-8 text-blue-400 mr-4 mt-1 flex-shrink-0" />
                  </motion.div>
                  <div>
                    <h3 className="text-xl font-semibold text-blue-300 mb-3">What is Knowledge Distillation (KD)?</h3>
                    <p className="text-gray-300 leading-relaxed">
                      Knowledge Distillation is a method to compress large, powerful models (teachers) into smaller,
                      faster models (students) without losing much performance.
                    </p>
                  </div>
                </div>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="animate-on-scroll"
            >
              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 p-6 rounded-xl hover:border-purple-500/50 transition-all duration-300">
                <div className="flex items-start">
                  <motion.div
                    animate={{
                      rotate: [0, 360],
                    }}
                    transition={{
                      duration: 20,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                  >
                    <BookOpen className="h-8 w-8 text-purple-400 mr-4 mt-1 flex-shrink-0" />
                  </motion.div>
                  <div>
                    <h3 className="text-xl font-semibold text-purple-300 mb-3">Our Setup</h3>
                    <p className="text-gray-300 leading-relaxed mb-4">
                      We're distilling NLLB (No Language Left Behind)—a multilingual giant—as a teacher, into two lighter
                      student models:
                    </p>
                    <div className="space-y-3 pl-4">
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-blue-500 mr-2"></div>
                        <p className="text-gray-300">
                          <span className="font-semibold text-blue-300">mBART-50</span> – A many-to-many multilingual
                          model.
                        </p>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-purple-500 mr-2"></div>
                        <p className="text-gray-300">
                          <span className="font-semibold text-purple-300">IndicBART</span> – Optimized for Indian
                          languages.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="animate-on-scroll"
            >
              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 p-6 rounded-xl hover:border-cyan-500/50 transition-all duration-300">
                <div className="flex items-start">
                  <motion.div
                    animate={{
                      rotate: [0, 360],
                    }}
                    transition={{
                      duration: 20,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                  >
                    <Zap className="h-8 w-8 text-cyan-400 mr-4 mt-1 flex-shrink-0" />
                  </motion.div>
                  <div>
                    <h3 className="text-xl font-semibold text-cyan-300 mb-3">How It Works</h3>

                    <div className="space-y-6">
                      <div className="border-l-2 border-blue-500/50 pl-4">
                        <h4 className="text-lg font-medium text-blue-300 mb-2">Step 1: Teacher Generation</h4>
                        <p className="text-gray-300 leading-relaxed">
                          Input a sentence (e.g., "Bonjour, comment ça va?")
                        </p>
                        <p className="text-gray-300 leading-relaxed mt-2">
                          NLLB-600M produces a high-quality translation (called a soft target).
                        </p>
                      </div>

                      <div className="border-l-2 border-purple-500/50 pl-4">
                        <h4 className="text-lg font-medium text-purple-300 mb-2">Step 2: Prepare for Student Training</h4>
                        <p className="text-gray-300 leading-relaxed">We now have:</p>
                        <ul className="list-disc list-inside text-gray-300 mt-2 space-y-1">
                          <li>Soft targets: Translations from NLLB (e.g., "Hey, how you doing?")</li>
                          <li>Ground-truth targets: Human-annotated reference translations.</li>
                        </ul>
                      </div>

                      <div className="border-l-2 border-cyan-500/50 pl-4">
                        <h4 className="text-lg font-medium text-cyan-300 mb-2">Step 3: Student Learning</h4>
                        <p className="text-gray-300 leading-relaxed">Feed the same input into mBART-50 and IndicBART.</p>
                        <p className="text-gray-300 leading-relaxed mt-2">Train them to match:</p>
                        <ul className="list-disc list-inside text-gray-300 mt-2 space-y-1">
                          <li>The soft target (NLLB's output) – learns nuanced behavior.</li>
                          <li>The ground truth – stays grounded in correctness.</li>
                        </ul>
                        <p className="text-gray-300 leading-relaxed mt-3">Use a loss function like:</p>
                        <div className="bg-gray-900/50 p-3 rounded-md mt-2 font-mono text-sm text-gray-300">
                          Distillation Loss = α * CrossEntropy(Student, Soft Target) + β * CrossEntropy(Student, Ground
                          Truth)
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="animate-on-scroll"
            >
              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 p-6 rounded-xl hover:border-green-500/50 transition-all duration-300">
                <div className="flex items-start">
                  <motion.div
                    animate={{
                      rotate: [0, 360],
                    }}
                    transition={{
                      duration: 20,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                  >
                    <Database className="h-8 w-8 text-green-400 mr-4 mt-1 flex-shrink-0" />
                  </motion.div>
                  <div>
                    <h3 className="text-xl font-semibold text-green-300 mb-3">Dataset Used: FLORES-101</h3>
                    <p className="text-gray-300 leading-relaxed">
                      A multilingual benchmark dataset, perfect for evaluating and training translation models.
                    </p>
                    <p className="text-gray-300 leading-relaxed mt-2">
                      Ensures wide language coverage, making student models robust.
                    </p>
                  </div>
                </div>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="animate-on-scroll"
            >
              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 p-6 rounded-xl hover:border-red-500/50 transition-all duration-300">
                <div className="flex items-start">
                  <motion.div
                    animate={{
                      rotate: [0, 360],
                    }}
                    transition={{
                      duration: 20,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                  >
                    <Target className="h-8 w-8 text-red-400 mr-4 mt-1 flex-shrink-0" />
                  </motion.div>
                  <div>
                    <h3 className="text-xl font-semibold text-red-300 mb-3">Goal</h3>
                    <p className="text-gray-300 leading-relaxed italic">
                      "Transfer the multilingual excellence of NLLB into lighter, faster models that are easier to deploy,
                      especially for Indic and many-to-many translation tasks."
                    </p>
                    <p className="text-gray-300 leading-relaxed mt-4 font-medium">In short:</p>
                    <ul className="list-disc list-inside text-gray-300 mt-2 space-y-1">
                      <li>NLLB = multilingual master.</li>
                      <li>
                        mBART & IndicBART = student models learning to translate like NLLB but with faster inference and
                        lower resource requirements.
                      </li>
                    </ul>
                  </div>
                </div>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="animate-on-scroll"
            >
              <Card className="bg-gray-800/30 backdrop-blur-sm border-gray-700/50 p-6 rounded-xl hover:border-yellow-500/50 transition-all duration-300">
                <div className="flex items-start">
                  <motion.div
                    animate={{
                      rotate: [0, 360],
                    }}
                    transition={{
                      duration: 20,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                  >
                    <Lightbulb className="h-8 w-8 text-yellow-400 mr-4 mt-1 flex-shrink-0" />
                  </motion.div>
                  <div>
                    <h3 className="text-xl font-semibold text-yellow-300 mb-3">Why This Rocks</h3>
                    <ul className="list-disc list-inside text-gray-300 space-y-2">
                      <li>We retain translation quality while improving efficiency.</li>
                      <li>Student models can be fine-tuned for specific use-cases or regions (e.g., South Asia).</li>
                      <li>Makes advanced translation models usable in low-resource, edge devices, or real-time apps.</li>
                    </ul>
                  </div>
                </div>
              </Card>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="mt-12 text-center"
          >
            <Link href="/">
              <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 border-0 px-6 shadow-lg shadow-blue-900/20 transition-all duration-300 hover:scale-105">
                <Sparkles className="mr-2 h-4 w-4" />
                Try the Translator
              </Button>
            </Link>
          </motion.div>
        </div>
      </div>
    </main>
  )
}

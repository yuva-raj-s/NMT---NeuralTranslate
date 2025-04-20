"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { ArrowRightLeft, Copy, Check, Sparkles, Zap, Globe, RotateCcw, ScanLine, Info } from "lucide-react"
import Link from "next/link"

// Updated language list with plain text language names
const LANGUAGES = [
  { name: "Auto-detect", code: "auto", nativeName: "Auto-detect" },
  { name: "English", code: "English", nativeName: "English" },
  { name: "Hindi", code: "Hindi", nativeName: "हिन्दी" },
  { name: "Tamil", code: "Tamil", nativeName: "தமிழ்" },
  { name: "Telugu", code: "Telugu", nativeName: "తెలుగు" },
  { name: "Kannada", code: "Kannada", nativeName: "ಕನ್ನಡ" },
  { name: "Malayalam", code: "Malayalam", nativeName: "മലയാളം" },
  { name: "French", code: "French", nativeName: "Français" },
  { name: "German", code: "German", nativeName: "Deutsch" },
  { name: "Spanish", code: "Spanish", nativeName: "Español" },
  { name: "Japanese", code: "Japanese", nativeName: "日本語" },
]

// Real translation function using our API route
const translateText = async (text: string, sourceLang: string, targetLang: string) => {
  if (!text.trim()) return ""

  try {
    console.log('Translation request:', {
      text,
      source_lang: sourceLang === "auto" ? undefined : sourceLang,
      target_lang: targetLang
    })

    const response = await fetch("/api/translate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
        source_lang: sourceLang === "auto" ? undefined : sourceLang,
        target_lang: targetLang,
      }),
    })

    const data = await response.json()
    console.log('Translation response:', data)

    if (!response.ok) {
      throw new Error(data.details || data.error || `Translation failed: ${response.statusText}`)
    }

    // Return the translation directly from the response
    return data.translation || data.translated_text || ""
  } catch (error) {
    console.error("Translation error:", error)
    return error instanceof Error ? error.message : "Translation failed. Please try again."
  }
}

// Simple transliteration function
const transliterateText = (text: string, lang: string) => {
  if (!text.trim()) return ""
  
  // For now, we'll just return the original text
  // In a real implementation, you would use a proper transliteration library
  return text
}

// Remove mock translation function and update language detection
const mockDetectLanguage = (text: string) => {
  // Very simple detection based on first character unicode range
  const firstChar = text.charAt(0)
  const code = firstChar.charCodeAt(0)

  if (code >= 0x3040 && code <= 0x30ff) return "Japanese" // Japanese hiragana/katakana
  if (code >= 0x0900 && code <= 0x097f) return "Hindi" // Hindi
  if (code >= 0x0b80 && code <= 0x0bff) return "Tamil" // Tamil
  if (code >= 0x0c00 && code <= 0x0c7f) return "Telugu" // Telugu
  if (code >= 0x0c80 && code <= 0x0cff) return "Kannada" // Kannada
  if (code >= 0x0d00 && code <= 0x0d7f) return "Malayalam" // Malayalam
  if (code >= 0x0041 && code <= 0x007a) {
    // Latin alphabet (could be en, fr, de, es)
    // Simple heuristic for European languages
    if (text.includes("é") || text.includes("à") || text.includes("ç")) return "French"
    if (text.includes("ñ") || text.includes("¿")) return "Spanish"
    if (text.includes("ß") || text.includes("ü")) return "German"
    return "English" // Default to English for Latin script
  }

  // Default to English for others
  return "English"
}

// Type for translation history
type TranslationHistoryItem = {
  id: string
  sourceText: string
  translatedText: string
  sourceLang: string
  targetLang: string
  timestamp: Date
}

export default function TranslationPage() {
  const [sourceText, setSourceText] = useState("")
  const [translatedText, setTranslatedText] = useState("")
  const [sourceLang, setSourceLang] = useState("English")
  const [targetLang, setTargetLang] = useState("Hindi")
  const [isTranslating, setIsTranslating] = useState(false)
  const [copied, setCopied] = useState(false)
  const [characterCount, setCharacterCount] = useState(0)
  const [autoTranslate, setAutoTranslate] = useState(true)
  const [secondaryTranslation, setSecondaryTranslation] = useState("")
  // These state variables have been removed as they're no longer needed
  const sourceTextareaRef = useRef<HTMLTextAreaElement>(null)
  const maxCharLimit = 5000

  // Auto translate effect
  useEffect(() => {
    if (!sourceText.trim()) {
      setTranslatedText("")
      setSecondaryTranslation("")
      return
    }

    if (autoTranslate && sourceText.trim()) {
      const timer = setTimeout(() => {
        handleTranslate()
      }, 800)

      return () => clearTimeout(timer)
    }
  }, [sourceText, sourceLang, targetLang, autoTranslate])

  // Update character count
  useEffect(() => {
    setCharacterCount(sourceText.length)
  }, [sourceText])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only trigger shortcuts if not typing in a text field
      const isTextField = e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement

      // Ctrl/Cmd + Enter to translate
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && sourceText.trim()) {
        e.preventDefault()
        handleTranslate()
      }

      // Ctrl/Cmd + Shift + C to copy translation
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === "c" && translatedText) {
        e.preventDefault()
        handleCopy()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [sourceText, translatedText])

  // Handle language swap
  const handleSwapLanguages = () => {
    setSourceLang(targetLang)
    setTargetLang(sourceLang)
    setSourceText(translatedText)
    setTranslatedText(sourceText)
    setSecondaryTranslation("") // Clear secondary translation when swapping
  }

  // Handle translation
  const handleTranslate = async () => {
    if (!sourceText.trim()) {
      setTranslatedText("")
      setSecondaryTranslation("")
      return
    }

    setIsTranslating(true)

    try {
      let sourceLanguage = sourceLang
      // If source language is set to auto, detect the language first
      if (sourceLang === "auto") {
        sourceLanguage = mockDetectLanguage(sourceText)
        console.log('Auto-detected language:', sourceLanguage)
      }

      console.log('Starting translation:', {
        sourceText,
        sourceLanguage,
        targetLang
      })

      const result = await translateText(sourceText, sourceLanguage, targetLang)
      console.log('Translation result:', result)
      
      setTranslatedText(result)

      // Generate secondary translation (romanized version if target is not English, or source text if target is English)
      if (targetLang !== "English") {
        setSecondaryTranslation(result)
      } else {
        setSecondaryTranslation(sourceText)
      }
    } catch (error) {
      console.error("Translation error:", error)
      setTranslatedText("Translation failed. Please try again.")
    } finally {
      setIsTranslating(false)
    }
  }

  // Update handleCopy function
  const handleCopy = () => {
    if (!translatedText) return

    navigator.clipboard.writeText(translatedText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleSourceTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value
    if (newText.length <= maxCharLimit) {
      setSourceText(newText)
    }

    if (!newText.trim()) {
      setTranslatedText("")
      setSecondaryTranslation("")
    }
  }

  const handleClearSource = () => {
    setSourceText("")
    setTranslatedText("")
    setSecondaryTranslation("")
  }

  // Handle language detection
  const handleDetectLanguage = () => {
    if (!sourceText.trim()) return

    setIsTranslating(true)

    // Simulate detection delay
    setTimeout(() => {
      const detectedLang = mockDetectLanguage(sourceText)
      console.log('Detected language:', detectedLang)
      setSourceLang(detectedLang)
      setIsTranslating(false)

      // Trigger translation with the detected language
      setTimeout(() => {
        handleTranslate()
      }, 100)
    }, 600)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-10 -left-10 w-40 h-40 bg-blue-500 rounded-full filter blur-3xl opacity-10 animate-pulse"></div>
        <div
          className="absolute top-1/3 -right-10 w-60 h-60 bg-purple-500 rounded-full filter blur-3xl opacity-10 animate-pulse"
          style={{ animationDelay: "1s" }}
        ></div>
        <div
          className="absolute -bottom-10 left-1/3 w-50 h-50 bg-cyan-500 rounded-full filter blur-3xl opacity-10 animate-pulse"
          style={{ animationDelay: "2s" }}
        ></div>

        {/* Neural network visualization */}
        <div className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none">
          <svg width="800" height="800" viewBox="0 0 800 800" className="stroke-blue-400">
            {/* Generate deterministic neural network connections */}
            {Array.from({ length: 20 }).map((_, i) => {
              // Use deterministic values based on index
              const angle1 = (i * Math.PI * 2) / 20
              const angle2 = ((i + 10) * Math.PI * 2) / 20
              const x1 = Math.round(400 + 300 * Math.cos(angle1))
              const y1 = Math.round(400 + 300 * Math.sin(angle1))
              const x2 = Math.round(400 + 300 * Math.cos(angle2))
              const y2 = Math.round(400 + 300 * Math.sin(angle2))
              return (
                <line
                  key={i}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  strokeWidth="1"
                  className={`opacity-${20 + (i * 4)}`}
                />
              )
            })}

            {/* Generate deterministic neural network nodes */}
            {Array.from({ length: 30 }).map((_, i) => {
              // Use deterministic values based on index
              const angle = (i * Math.PI * 2) / 30
              const radius = 200 + (i % 3) * 100
              const cx = Math.round(400 + radius * Math.cos(angle))
              const cy = Math.round(400 + radius * Math.sin(angle))
              const r = 2 + (i % 3)
              return (
                <circle
                  key={i}
                  cx={cx}
                  cy={cy}
                  r={r}
                  fill="currentColor"
                  className={`opacity-${20 + (i * 3)}`}
                />
              )
            })}
          </svg>
        </div>
      </div>

      <div className="container mx-auto py-8 px-4 relative z-10">
        <header className="mb-12">
          <div className="flex items-center justify-center mb-3">
            <div className="relative">
              <Globe className="h-10 w-10 mr-3 text-blue-400" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
            </div>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-cyan-400">
              NEURAL TRANSLATOR
            </h1>
          </div>
          <p className="text-center text-gray-400 flex items-center justify-center">
            <Sparkles className="h-4 w-4 mr-1 text-yellow-400" />
            Powered by NLLB, mBart and IndicBart models
          </p>
          <p className="text-center text-sm text-gray-500">Knowledge distillation using flores-101 dataset</p>

          <div className="flex justify-center mt-4">
            <Link href="/about">
              <Button variant="outline" className="text-gray-400 hover:text-white border-gray-700/50 bg-gray-800/30">
                <Info className="h-4 w-4 mr-2" />
                About Our Approach
              </Button>
            </Link>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl mx-auto">
          {/* Source Language Card */}
          <Card className="border-gray-700 bg-gray-800/30 backdrop-blur-sm overflow-hidden rounded-xl border border-gray-700/50 shadow-lg shadow-blue-900/10">
            <div className="p-4 border-b border-gray-700/50 flex justify-between items-center bg-gray-800/50">
              <div className="flex items-center gap-2">
                <Select
                  value={sourceLang}
                  onValueChange={(value) => {
                    setSourceLang(value)
                    if (value === "auto" && sourceText.trim()) {
                      // Automatically detect language when "Auto-detect" is selected
                      setTimeout(() => handleDetectLanguage(), 100)
                    }
                  }}
                >
                  <SelectTrigger className="w-[200px] bg-gray-900/80 border-gray-700/50 focus:ring-blue-500/30">
                    <SelectValue placeholder="Select language" />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-900 border-gray-700">
                    {LANGUAGES.map((lang) => (
                      <SelectItem key={lang.code} value={lang.code}>
                        <span className="flex items-center">
                          {lang.name}
                          <span className="ml-2 text-xs text-gray-400">{lang.nativeName}</span>
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button
                variant="ghost"
                size="icon"
                onClick={handleDetectLanguage}
                disabled={!sourceText.trim()}
                className="h-8 w-8 text-gray-400 hover:text-blue-400 hover:bg-blue-900/20"
              >
                <ScanLine className="h-4 w-4" />
              </Button>
            </div>

            <CardContent className="p-0">
              <Textarea
                ref={sourceTextareaRef}
                placeholder="Enter text to translate"
                className="min-h-[240px] bg-transparent border-0 rounded-none focus-visible:ring-0 focus-visible:ring-offset-0 resize-none p-4 text-lg"
                value={sourceText}
                onChange={handleSourceTextChange}
              />
            </CardContent>

            <div className="p-2 border-t border-gray-700/50 flex justify-between items-center text-xs text-gray-400 bg-gray-800/50">
              <span
                className={
                  characterCount > maxCharLimit * 0.8
                    ? characterCount > maxCharLimit * 0.95
                      ? "text-red-400"
                      : "text-yellow-400"
                    : ""
                }
              >
                {characterCount} / {maxCharLimit} characters
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearSource}
                className="text-gray-400 hover:text-red-400"
              >
                <RotateCcw className="h-3 w-3 mr-1" />
                Clear
              </Button>
            </div>
          </Card>

          {/* Target Language Card */}
          <Card className="border-gray-700 bg-gray-800/30 backdrop-blur-sm overflow-hidden rounded-xl border border-gray-700/50 shadow-lg shadow-purple-900/10">
            <div className="p-4 border-b border-gray-700/50 bg-gray-800/50">
              <Select value={targetLang} onValueChange={setTargetLang}>
                <SelectTrigger className="w-[200px] bg-gray-900/80 border-gray-700/50 focus:ring-purple-500/30">
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent className="bg-gray-900 border-gray-700">
                  {LANGUAGES.filter((lang) => lang.code !== "auto").map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      <span className="flex items-center">
                        {lang.name}
                        <span className="ml-2 text-xs text-gray-400">{lang.nativeName}</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <CardContent className="p-0 relative">
              <Textarea
                placeholder="Translation will appear here"
                className="min-h-[180px] bg-transparent border-0 rounded-none focus-visible:ring-0 focus-visible:ring-offset-0 resize-none p-4 text-lg"
                value={translatedText}
                readOnly
              />

              {secondaryTranslation && targetLang !== sourceLang && (
                <div className="border-t border-gray-700/30 p-3">
                  <div className="text-xs text-gray-500 mb-1">{targetLang !== "en" ? "Romanized" : "Original"}</div>
                  <div className="text-sm text-gray-300">
                    {targetLang !== "en" ? transliterateText(translatedText, targetLang) : sourceText}
                  </div>
                </div>
              )}

              {isTranslating && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-900/70 backdrop-blur-sm">
                  <div className="flex flex-col items-center">
                    <div className="relative w-20 h-20">
                      {/* Neural network animation during translation */}
                      <svg viewBox="0 0 100 100" className="w-full h-full">
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          stroke="#3b82f6"
                          strokeWidth="2"
                          strokeDasharray="251.2"
                          strokeDashoffset="0"
                        >
                          <animate
                            attributeName="stroke-dashoffset"
                            from="0"
                            to="251.2"
                            dur="2s"
                            repeatCount="indefinite"
                          />
                        </circle>
                        <circle
                          cx="50"
                          cy="50"
                          r="30"
                          fill="none"
                          stroke="#8b5cf6"
                          strokeWidth="2"
                          strokeDasharray="188.4"
                          strokeDashoffset="0"
                        >
                          <animate
                            attributeName="stroke-dashoffset"
                            from="188.4"
                            to="0"
                            dur="2s"
                            repeatCount="indefinite"
                          />
                        </circle>
                        <circle
                          cx="50"
                          cy="50"
                          r="20"
                          fill="none"
                          stroke="#06b6d4"
                          strokeWidth="2"
                          strokeDasharray="125.6"
                          strokeDashoffset="0"
                        >
                          <animate
                            attributeName="stroke-dashoffset"
                            from="0"
                            to="125.6"
                            dur="1.5s"
                            repeatCount="indefinite"
                          />
                        </circle>

                        {/* Nodes */}
                        {Array.from({ length: 8 }).map((_, i) => {
                          const angle = (i * Math.PI) / 4
                          const x = 50 + 40 * Math.cos(angle)
                          const y = 50 + 40 * Math.sin(angle)
                          return (
                            <circle key={`outer-${i}`} cx={x} cy={y} r="2" fill="#3b82f6">
                              <animate
                                attributeName="opacity"
                                values="0.3;1;0.3"
                                dur="1.5s"
                                repeatCount="indefinite"
                                begin={`${i * 0.2}s`}
                              />
                            </circle>
                          )
                        })}

                        {Array.from({ length: 6 }).map((_, i) => {
                          const angle = (i * Math.PI) / 3
                          const x = 50 + 30 * Math.cos(angle)
                          const y = 50 + 30 * Math.sin(angle)
                          return (
                            <circle key={`middle-${i}`} cx={x} cy={y} r="2" fill="#8b5cf6">
                              <animate
                                attributeName="opacity"
                                values="0.3;1;0.3"
                                dur="1.5s"
                                repeatCount="indefinite"
                                begin={`${i * 0.25}s`}
                              />
                            </circle>
                          )
                        })}

                        {Array.from({ length: 4 }).map((_, i) => {
                          const angle = (i * Math.PI) / 2
                          const x = 50 + 20 * Math.cos(angle)
                          const y = 50 + 20 * Math.sin(angle)
                          return (
                            <circle key={`inner-${i}`} cx={x} cy={y} r="2" fill="#06b6d4">
                              <animate
                                attributeName="opacity"
                                values="0.3;1;0.3"
                                dur="1.5s"
                                repeatCount="indefinite"
                                begin={`${i * 0.3}s`}
                              />
                            </circle>
                          )
                        })}

                        <circle cx="50" cy="50" r="3" fill="#ffffff">
                          <animate attributeName="r" values="3;5;3" dur="1s" repeatCount="indefinite" />
                        </circle>
                      </svg>
                    </div>
                    <p className="mt-4 text-blue-400 font-medium">Processing Translation...</p>
                  </div>
                </div>
              )}
            </CardContent>

            <div className="p-2 border-t border-gray-700/50 flex justify-end bg-gray-800/50">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopy}
                disabled={!translatedText}
                className="text-gray-400 hover:text-white"
              >
                {copied ? (
                  <>
                    <Check className="h-3 w-3 mr-1 text-green-500" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3 mr-1" />
                    Copy
                  </>
                )}
              </Button>
            </div>
          </Card>
        </div>

        <div className="mt-8 flex flex-col sm:flex-row justify-center items-center gap-4">
          <Button
            variant="outline"
            onClick={handleSwapLanguages}
            className="border-gray-700/50 bg-gray-800/50 hover:bg-gray-700 text-gray-300 hover:text-white px-6"
          >
            <ArrowRightLeft className="mr-2 h-4 w-4" />
            Swap Languages
          </Button>

          <Button
            onClick={handleTranslate}
            disabled={isTranslating || !sourceText.trim()}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 border-0 px-6 shadow-lg shadow-blue-900/20"
          >
            <Zap className="mr-2 h-4 w-4" />
            Translate
          </Button>
        </div>

        {/* Language support visualization */}
        <div className="mt-16 mb-8">
          <h3 className="text-center text-sm font-medium text-gray-400 mb-4">Supported Languages</h3>
          <div className="flex flex-wrap justify-center gap-2 max-w-3xl mx-auto">
            {LANGUAGES.map((lang) => (
              <div
                key={lang.code}
                className="px-3 py-1.5 rounded-full text-xs bg-gray-800/50 border border-gray-700/50 text-gray-300 hover:bg-gray-700/50 hover:text-white transition-colors cursor-default flex items-center gap-1.5"
              >
                <span>{lang.name}</span>
                <span className="text-gray-500 text-[10px]">{lang.nativeName}</span>
              </div>
            ))}
          </div>
        </div>

        <footer className="mt-12 text-center text-xs text-gray-500">
          <p className="mb-1">Neural Translator • NLLB as Teacher, mBart and IndicBart as students</p>
          <p>Trained using knowledge distillation on flores-101 dataset</p>
        </footer>
      </div>
    </main>
  )
}

"use server"

import { generateText } from "ai"
import { openai } from "@ai-sdk/openai"

// Language code to full name mapping
const LANGUAGE_NAMES = {
  en: "English",
  fr: "French",
  de: "German",
  es: "Spanish",
}

type TranslationParams = {
  text: string
  sourceLang: string
  targetLang: string
}

type TranslationResult = {
  translatedText: string
  rawOutput?: string
  error?: string
}

export async function translateText({ text, sourceLang, targetLang }: TranslationParams): Promise<TranslationResult> {
  try {
    // Construct the prompt for the translation model
    const sourceLanguage = LANGUAGE_NAMES[sourceLang as keyof typeof LANGUAGE_NAMES] || sourceLang
    const targetLanguage = LANGUAGE_NAMES[targetLang as keyof typeof LANGUAGE_NAMES] || targetLang

    const prompt = `Translate the following ${sourceLanguage} text to ${targetLanguage}:

Text: "${text}"

Translation:`

    // Use the AI SDK to generate the translation
    const result = await generateText({
      model: openai("gpt-4o"), // Using GPT-4o as a stand-in for Gemma-3
      prompt,
      temperature: 0.3, // Lower temperature for more deterministic translations
      maxTokens: 1000,
    })

    // Process the result
    const translatedText = result.text.trim()

    return {
      translatedText,
      rawOutput: JSON.stringify(
        {
          model: "SLM Gemma-3 (simulated)",
          input_tokens: text.split(/\s+/).length,
          output_tokens: translatedText.split(/\s+/).length,
          translation: translatedText,
        },
        null,
        2,
      ),
    }
  } catch (error) {
    console.error("Translation error:", error)
    return {
      translatedText: "",
      error: "Failed to translate text. Please try again.",
    }
  }
}

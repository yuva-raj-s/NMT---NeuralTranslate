import { NextResponse } from 'next/server'

// Language name to code mapping
const LANGUAGE_CODES = {
  "English": "eng_Latn",
  "Hindi": "hin_Deva",
  "Tamil": "tam_Taml",
  "Telugu": "tel_Telu",
  "Kannada": "kan_Knda",
  "Malayalam": "mal_Mlym",
  "French": "fra_Latn",
  "German": "deu_Latn",
  "Spanish": "spa_Latn",
  "Japanese": "jpn_Jpan",
  "auto": "auto"
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    console.log('API Request body:', body)
    
    const response = await fetch('https://nova35-nllb-distilled-translator.hf.space/translate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        text: body.text,
        source_lang: body.source_lang === "auto" ? undefined : body.source_lang,
        target_lang: body.target_lang,
      }),
    })

    console.log('Translation API response status:', response.status)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('Translation API error:', errorText)
      throw new Error(`Translation failed: ${response.statusText}. Details: ${errorText}`)
    }

    const data = await response.json()
    console.log('Translation API response:', data)
    return NextResponse.json(data)
  } catch (error) {
    console.error('Translation error:', error)
    return NextResponse.json(
      { 
        error: 'Translation failed. Please try again.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
} 
# Neural Translator

A modern, efficient neural machine translation application that leverages knowledge distillation techniques to provide high-quality translations across multiple languages.

![Neural Translator Screenshot](public/screenshot.png)

## Features

- 🚀 **Fast & Efficient**: Powered by distilled models for quick translations
- 🌐 **Multilingual Support**: Translate between multiple languages including:
  - English
  - Hindi
  - Tamil
  - Telugu
  - Kannada
  - Malayalam
  - French
  - German
  - Spanish
  - Japanese
- 🧠 **Auto-Detect**: Automatic language detection for source text
- 💫 **Modern UI**: Beautiful, responsive interface with smooth animations
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices

## Technical Details

### Architecture

The application uses a knowledge distillation approach where:
- **Teacher Model**: NLLB (No Language Left Behind)
- **Student Models**: 
  - mBART-50 (many-to-many multilingual model)
  - IndicBART (optimized for Indian languages)

### Dataset

Trained using the FLORES-101 dataset, ensuring:
- Wide language coverage
- High-quality translations
- Robust performance across language pairs

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yuva-raj-s/NMT---NeuralTranslate.git
cd nmt-app
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open your browser and navigate to `http://localhost:3000`

## Usage

1. Select the source language (or use "Auto-detect")
2. Enter the text you want to translate
3. Select the target language
4. Click "Translate" or wait for auto-translation
5. Copy the translated text using the copy button

## Keyboard Shortcuts

- `Ctrl/Cmd + Enter`: Translate text
- `Ctrl/Cmd + Shift + C`: Copy translation

## Technologies Used

- **Frontend**: Next.js, React, TypeScript
- **UI Components**: shadcn/ui
- **Animations**: Framer Motion
- **Styling**: Tailwind CSS
- **Icons**: Lucide Icons

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FLORES-101 dataset for training data
- NLLB, mBART, and IndicBART model developers
- The open-source community for their invaluable tools and libraries

## Contact

For any questions or suggestions, please open an issue in the repository. 

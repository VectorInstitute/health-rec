import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'vector-pink': '#eb088a',
        'vector-purple': '#8a08eb',
      },
    },
  },
  plugins: [],
}
export default config

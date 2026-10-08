import eslint from "@eslint/js";
import prettier from "eslint-config-prettier";

export default [
  {
    ignores: [
      ".agents/**",
      ".git/**",
      ".specify/**",
      "_bmad/**",
      "node_modules/**",
      ".venv/**",
      "openspec/**",
      "coverage/**",
      "dist/**",
      "build/**",
      "vendor/braces/**",
    ],
  },
  eslint.configs.recommended,
  {
    files: ["scripts/**/*.mjs"],
    languageOptions: {
      globals: {
        console: "readonly",
        fetch: "readonly",
        process: "readonly",
        setTimeout: "readonly",
      },
    },
  },
  prettier,
];

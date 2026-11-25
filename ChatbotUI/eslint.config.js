import js from '@eslint/js';
import eslintConfigPrettier from 'eslint-config-prettier';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import globals from 'globals';

const reactRecommended = react.configs?.flat?.recommended ?? react.configs.recommended;
const reactHooksRecommended =
  reactHooks.configs?.['recommended-latest'] ?? reactHooks.configs.recommended;

export default [
  {
    ignores: ['node_modules/', 'dist/']
  },
  js.configs.recommended,
  reactRecommended,
  reactHooksRecommended,
  eslintConfigPrettier,
  {
    files: ['**/*.{js,jsx,mjs}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node
      }
    },
    settings: {
      react: {
        version: 'detect'
      }
    },
    rules: {
      'react/react-in-jsx-scope': 'off',
      'react/prop-types': 'off'
    }
  }
];

/** @type {import('eslint').Linter.FlatConfig[]} */
module.exports = [

  // ─────────────────────────────
  // 1) JavaScript & JSX
  // ─────────────────────────────
  {
    files: ['**/*.{js,jsx}'],
    ignores: ['node_modules/**'],

    languageOptions: {
      parserOptions: {
        ecmaVersion: 2021,
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
      },
    },

    plugins: {
      react: require('eslint-plugin-react'),
      import: require('eslint-plugin-import'),
    },
    settings: {
      react: { version: 'detect' },
    },

    rules: {
      // 2‑space indent
      indent: ['error', 2],

      // enforce ≤120 chars per line  
      'max-len': ['error', { code: 120 }],

      // built‑in camelCase check
      camelcase: ['error', { properties: 'always' }],

      // imports must be on their own line
      'import/newline-after-import': ['error'],

      // all if/while/do must use braces
      curly: ['error', 'all'],
    },
  },

  // ─────────────────────────────
  // 2) TypeScript & TSX
  // ─────────────────────────────
  {
    files: ['**/*.{ts,tsx}'],
    ignores: ['node_modules/**'],

    languageOptions: {
      // use the TS parser so ESLint can parse TS syntax
      parser: {
        parseForESLint: require('@typescript-eslint/parser')
          .parseForESLint,
      },
      parserOptions: {
        ecmaVersion: 2021,
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
        // *** no `project` here, so no parserServices errors ***
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
      },
    },

    plugins: {
      react: require('eslint-plugin-react'),
      import: require('eslint-plugin-import'),
      '@typescript-eslint': require('@typescript-eslint/eslint-plugin'),
    },
    settings: {
      react: { version: 'detect' },
    },

    rules: {
      indent: ['error', 2],
      'max-len': ['error', { code: 120 }],
      // drop the type‑aware naming rule in favor of the built‑in camelcase
      camelcase: ['error', { properties: 'always' }],
      'import/newline-after-import': ['error'],
      curly: ['error', 'all'],
    },
  },
];
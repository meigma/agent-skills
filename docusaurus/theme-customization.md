# Theme Customization

Docusaurus themes control the visual appearance and layout of your site. The classic theme provides sensible defaults that can be customized through CSS, configuration, or component swizzling.

## CSS Customization

### Custom CSS File

Create `src/css/custom.css`:

```css
/* Color scheme using CSS variables */
:root {
  --ifm-color-primary: #2e8555;
  --ifm-color-primary-dark: #29784c;
  --ifm-color-primary-darker: #277148;
  --ifm-color-primary-darkest: #205d3b;
  --ifm-color-primary-light: #33925d;
  --ifm-color-primary-lighter: #359962;
  --ifm-color-primary-lightest: #3cad6e;

  --ifm-code-font-size: 95%;
  --ifm-font-family-base: 'Inter', system-ui, sans-serif;
  --ifm-heading-font-family: 'Inter', system-ui, sans-serif;

  --docusaurus-highlighted-code-line-bg: rgba(0, 0, 0, 0.1);
}

/* Dark mode overrides */
[data-theme='dark'] {
  --ifm-color-primary: #25c2a0;
  --ifm-color-primary-dark: #21af90;
  --ifm-color-primary-darker: #1fa588;
  --ifm-color-primary-darkest: #1a8870;
  --ifm-color-primary-light: #29d5b0;
  --ifm-color-primary-lighter: #32d8b4;
  --ifm-color-primary-lightest: #4fddbf;

  --docusaurus-highlighted-code-line-bg: rgba(0, 0, 0, 0.3);
}
```

Reference in config:

```typescript
presets: [
  ['classic', {
    theme: {
      customCss: './src/css/custom.css',
    },
  }],
],
```

### Common CSS Variables

```css
:root {
  /* Colors */
  --ifm-color-primary: #2e8555;
  --ifm-background-color: #ffffff;
  --ifm-font-color-base: #1c1e21;

  /* Typography */
  --ifm-font-family-base: system-ui, sans-serif;
  --ifm-font-family-monospace: 'Fira Code', monospace;
  --ifm-font-size-base: 100%;
  --ifm-line-height-base: 1.65;

  /* Spacing */
  --ifm-global-spacing: 1rem;
  --ifm-spacing-horizontal: var(--ifm-global-spacing);
  --ifm-spacing-vertical: var(--ifm-global-spacing);

  /* Layout */
  --ifm-container-width: 1140px;
  --ifm-container-width-xl: 1320px;

  /* Navbar */
  --ifm-navbar-height: 3.75rem;
  --ifm-navbar-background-color: var(--ifm-background-color);

  /* Sidebar */
  --doc-sidebar-width: 300px;
  --doc-sidebar-hidden-width: 30px;

  /* Code blocks */
  --ifm-code-font-size: 95%;
  --ifm-code-padding-horizontal: 0.1rem;
  --ifm-code-padding-vertical: 0.1rem;
  --ifm-code-border-radius: 0.2rem;

  /* Admonitions */
  --ifm-alert-padding-horizontal: 1.25rem;
  --ifm-alert-padding-vertical: 1rem;

  /* TOC */
  --ifm-toc-border-color: var(--ifm-color-emphasis-200);
}
```

### Targeting Specific Elements

```css
/* Navbar */
.navbar {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.navbar__title {
  font-weight: 700;
}

/* Sidebar */
.menu__link {
  font-size: 0.9rem;
}

.menu__link--active {
  font-weight: 600;
}

/* Doc page */
.markdown h1:first-child {
  font-size: 2.5rem;
}

.markdown > p:first-of-type {
  font-size: 1.2rem;
  color: var(--ifm-color-emphasis-700);
}

/* Footer */
.footer {
  padding: 3rem 0;
}

/* Admonitions */
.admonition {
  border-radius: 0.5rem;
}

/* Code blocks */
.prism-code {
  font-size: 0.9rem;
}

/* Search */
.DocSearch-Button {
  border-radius: 0.5rem;
}
```

### CSS Modules

For component-scoped styles, use CSS Modules:

```css
/* src/components/MyComponent.module.css */
.container {
  padding: 2rem;
  background: var(--ifm-background-surface-color);
}

.title {
  color: var(--ifm-color-primary);
  font-size: 1.5rem;
}
```

```jsx
import styles from './MyComponent.module.css';

function MyComponent() {
  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Title</h2>
    </div>
  );
}
```

## Swizzling

Swizzling lets you customize theme components by creating your own version.

### Swizzle Methods

1. **Wrapping** (Safe) - Enhance existing component
2. **Ejecting** (Unsafe) - Full copy for complete customization

### List Swizzlable Components

```bash
npm run swizzle @docusaurus/theme-classic -- --list
```

### Wrap a Component

```bash
npm run swizzle @docusaurus/theme-classic Footer -- --wrap
```

Creates `src/theme/Footer/index.js`:

```jsx
import React from 'react';
import Footer from '@theme-original/Footer';

export default function FooterWrapper(props) {
  return (
    <>
      <div className="custom-banner">Custom content above footer</div>
      <Footer {...props} />
    </>
  );
}
```

### Eject a Component

```bash
npm run swizzle @docusaurus/theme-classic Footer -- --eject
```

Creates a full copy in `src/theme/Footer/` that you can modify completely.

### Common Components to Swizzle

| Component | Purpose | Swizzle Method |
|-----------|---------|----------------|
| `Footer` | Site footer | Wrap or Eject |
| `Navbar` | Top navigation | Wrap |
| `DocSidebar` | Documentation sidebar | Wrap |
| `DocItem` | Doc page layout | Wrap |
| `BlogPostItem` | Blog post card | Wrap |
| `CodeBlock` | Code syntax highlighting | Wrap |
| `TOC` | Table of contents | Wrap |
| `SearchBar` | Search component | Wrap |
| `NotFound` | 404 page | Eject |

### Swizzle Directory Structure

```
src/theme/
├── Footer/
│   └── index.js           # Custom footer
├── DocItem/
│   └── Layout/
│       └── index.js       # Custom doc layout
├── Navbar/
│   └── Content/
│       └── index.js       # Custom navbar content
└── prism-include-languages.js  # Additional Prism languages
```

### Example: Custom Doc Page Layout

```bash
npm run swizzle @docusaurus/theme-classic DocItem/Layout -- --wrap
```

```jsx
// src/theme/DocItem/Layout/index.js
import React from 'react';
import Layout from '@theme-original/DocItem/Layout';
import { useDoc } from '@docusaurus/plugin-content-docs/client';

export default function LayoutWrapper(props) {
  const { metadata } = useDoc();

  return (
    <>
      {metadata.frontMatter.deprecated && (
        <div className="deprecation-banner">
          This feature is deprecated. See <a href="/migration">migration guide</a>.
        </div>
      )}
      <Layout {...props} />
      <div className="doc-feedback">
        Was this page helpful?
        <button>Yes</button>
        <button>No</button>
      </div>
    </>
  );
}
```

### Example: Adding Prism Languages

```bash
npm run swizzle @docusaurus/theme-classic prism-include-languages -- --eject
```

```js
// src/theme/prism-include-languages.js
import siteConfig from '@generated/docusaurus.config';

export default function prismIncludeLanguages(PrismObject) {
  const { themeConfig: { prism } } = siteConfig;
  const { additionalLanguages } = prism;

  // Add default languages
  globalThis.Prism = PrismObject;
  additionalLanguages.forEach((lang) => {
    require(`prismjs/components/prism-${lang}`);
  });

  // Add custom language
  require('prismjs/components/prism-hcl');
  require('prismjs/components/prism-toml');

  delete globalThis.Prism;
}
```

## Color Mode

### Configuration

```typescript
themeConfig: {
  colorMode: {
    defaultMode: 'light',        // 'light' | 'dark'
    disableSwitch: false,        // Hide the toggle
    respectPrefersColorScheme: true,  // Use system preference
  },
}
```

### Programmatic Access

```jsx
import { useColorMode } from '@docusaurus/theme-common';

function MyComponent() {
  const { colorMode, setColorMode } = useColorMode();

  return (
    <button onClick={() => setColorMode(colorMode === 'dark' ? 'light' : 'dark')}>
      Toggle {colorMode === 'dark' ? 'Light' : 'Dark'} Mode
    </button>
  );
}
```

### Dark Mode Only Styles

```css
[data-theme='dark'] .my-component {
  background: #1a1a1a;
}

/* Or using CSS variables */
.my-component {
  background: var(--ifm-background-color);
}
```

## Custom Pages

Create custom pages in `src/pages/`:

```jsx
// src/pages/custom.tsx
import React from 'react';
import Layout from '@theme/Layout';
import styles from './custom.module.css';

export default function CustomPage() {
  return (
    <Layout
      title="Custom Page"
      description="A custom page example"
    >
      <main className={styles.main}>
        <h1>Custom Page</h1>
        <p>This is a custom page built with React.</p>
      </main>
    </Layout>
  );
}
```

Or use MDX:

```mdx
---
title: Custom Page
description: A custom page in MDX
---

# Custom Page

This is a custom MDX page at `/custom`.

import MyComponent from '@site/src/components/MyComponent';

<MyComponent />
```

## Fonts

### Google Fonts

```typescript
// docusaurus.config.ts
stylesheets: [
  {
    href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
    type: 'text/css',
  },
],
```

```css
/* src/css/custom.css */
:root {
  --ifm-font-family-base: 'Inter', system-ui, sans-serif;
}
```

### Self-Hosted Fonts

```css
/* src/css/custom.css */
@font-face {
  font-family: 'CustomFont';
  src: url('/fonts/custom-font.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

:root {
  --ifm-font-family-base: 'CustomFont', system-ui, sans-serif;
}
```

## Tailwind CSS Integration

```bash
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx,mdx}'],
  darkMode: ['class', '[data-theme="dark"]'],
  corePlugins: {
    preflight: false,  // Disable reset to avoid conflicts
  },
  theme: {
    extend: {},
  },
};
```

```css
/* src/css/custom.css */
@tailwind utilities;
/* Don't include @tailwind base to avoid conflicts */
```
